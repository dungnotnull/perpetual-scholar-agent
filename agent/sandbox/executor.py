"""Sandbox execution: Docker container lifecycle manager with retry and cleanup."""
from __future__ import annotations

import io
import json
import logging
import shutil
import tempfile
from pathlib import Path
import tarfile
from typing import Any, Dict, Optional

import docker
from docker.errors import ImageNotFound, APIError as DockerAPIError

from agent.config.settings import settings
from agent.sandbox.resource_limits import ResourceLimits

logger = logging.getLogger(__name__)


class SandboxExecutor:
    """Manages ephemeral Docker containers for executing untrusted benchmark code.

    Each experiment gets its own container with strict resource limits and network
    isolation. Containers are always cleaned up after execution, even on timeout or error.

    The executor maintains a reference to the Docker client and can optionally reuse
    it across multiple runs for efficiency.
    """

    def __init__(self, image: Optional[str] = None, limits: Optional[ResourceLimits] = None):
        self.image = image or settings.sandbox_docker_image
        self.limits = limits or ResourceLimits.from_settings()
        self.client = docker.from_env()
        self._containers_created: list[str] = []

    def execute(
        self,
        code: str,
        timeout: Optional[int] = None,
        extra_files: Optional[Dict[str, str]] = None,
        resource_limits: Optional[ResourceLimits] = None,
    ) -> Dict[str, Any]:
        """Execute Python code inside an ephemeral Docker container.

        Creates a fresh container, copies the code in, runs pytest-benchmark,
        captures output and benchmark JSON, then destroys the container.

        Args:
            code: Python source code to execute.
            timeout: Execution timeout in seconds. Defaults to settings.
            extra_files: Optional dict of {filename: content} to include.
            resource_limits: Override default resource limits.

        Returns:
            Dict with keys: exit_code, stdout, stderr, timed_out, benchmark_results.
        """
        timeout = timeout or self.limits.timeout_seconds
        limits = resource_limits or self.limits
        container = None
        temp_dir = tempfile.mkdtemp(prefix="psa_sandbox_")

        try:
            container = self.client.containers.create(
                image=self.image,
                command=[
                    "python", "-m", "pytest",
                    "/sandbox/benchmark_test.py",
                    "--benchmark-only",
                    "--benchmark-json=/sandbox/results/benchmark_results.json",
                    f"--benchmark-warmup={settings.benchmark_warmup_iterations}",
                    f"--benchmark-min-rounds={settings.benchmark_measure_iterations}",
                    "-v",
                ],
                mem_limit=limits.memory_mb_to_docker(),
                nano_cpus=limits.cpu_count * 1_000_000_000,
                network_disabled=limits.network_disabled,
                pids_limit=limits.pids_limit,
                detach=True,
                labels={"psa.sandbox": "true", "psa.created": "auto"},
            )
            self._containers_created.append(container.id)

            # Copy test code into container
            self._copy_code_to_container(container, code, "benchmark_test.py", temp_dir)

            # Copy extra files if any
            if extra_files:
                for filename, content in extra_files.items():
                    self._copy_code_to_container(container, content, filename, temp_dir)

            # Create results directory
            container.exec_run("mkdir -p /sandbox/results")

            # Start and wait with timeout
            container.start()
            logger.info("sandbox_container_started", extra={"container_id": container.id[:12]})

            try:
                result = container.wait(timeout=timeout)
                exit_code = result.get("StatusCode", -1)
            except Exception as wait_err:
                logger.warning("sandbox_container_timeout", extra={"error": str(wait_err)})
                try:
                    container.kill()
                except Exception:
                    pass
                exit_code = -1

            timed_out = exit_code == 137 or exit_code == -1

            # Capture logs
            stdout = container.logs(stdout=True, stderr=False).decode("utf-8", errors="replace")
            stderr = container.logs(stdout=False, stderr=True).decode("utf-8", errors="replace")

            # Retrieve benchmark JSON
            benchmark_results = self._retrieve_benchmark_json(container)

            logger.info(
                "sandbox_execution_complete",
                extra={
                    "container_id": container.id[:12],
                    "exit_code": exit_code,
                    "timed_out": timed_out,
                    "stdout_len": len(stdout),
                    "has_benchmark_results": benchmark_results is not None,
                },
            )

            return {
                "exit_code": exit_code,
                "stdout": stdout,
                "stderr": stderr,
                "timed_out": timed_out,
                "benchmark_results": benchmark_results,
            }

        except ImageNotFound:
            logger.error("sandbox_image_not_found", extra={"image": self.image})
            return {
                "exit_code": -1, "stdout": "", "stderr": f"Image not found: {self.image}",
                "timed_out": False, "benchmark_results": None,
            }
        except DockerAPIError as e:
            logger.error("sandbox_docker_error", extra={"error": str(e)})
            return {
                "exit_code": -1, "stdout": "", "stderr": f"Docker error: {e}",
                "timed_out": False, "benchmark_results": None,
            }
        except Exception as e:
            logger.error("sandbox_execution_failed", extra={"error": str(e)})
            return {
                "exit_code": -1, "stdout": "", "stderr": str(e),
                "timed_out": False, "benchmark_results": None,
            }
        finally:
            # Always clean up container
            if container:
                try:
                    container.remove(force=True)
                    if container.id in self._containers_created:
                        self._containers_created.remove(container.id)
                except Exception:
                    pass
            # Clean up temp directory
            shutil.rmtree(temp_dir, ignore_errors=True)

    def _copy_code_to_container(self, container, code: str, filename: str, temp_dir: str) -> None:
        """Copy code string into container as a file using tar archive."""
        file_path = Path(temp_dir) / filename
        file_path.write_text(code, encoding="utf-8")

        tar_stream = io.BytesIO()
        with tarfile.open(fileobj=tar_stream, mode="w") as tar:
            data = file_path.read_bytes()
            info = tarfile.TarInfo(name=filename)
            info.size = len(data)
            tar.addfile(info, io.BytesIO(data))
        tar_stream.seek(0)

        container.put_archive("/sandbox", tar_stream)

    def _retrieve_benchmark_json(self, container) -> Optional[Dict]:
        """Try to retrieve benchmark_results.json from the container."""
        try:
            bits, stat = container.get_archive("/sandbox/results/benchmark_results.json")
            tar_data = b"".join(bits)

            with tarfile.open(fileobj=io.BytesIO(tar_data)) as tar:
                for member in tar.getmembers():
                    if "benchmark_results.json" in member.name:
                        f = tar.extractfile(member)
                        if f:
                            return json.loads(f.read().decode("utf-8"))
        except Exception:
            pass

        # Fallback: try parsing from stdout
        return None

    def cleanup_all(self) -> int:
        """Remove all PSA sandbox containers (cleanup utility).

        Returns:
            Number of containers removed.
        """
        count = 0

        # Clean tracked containers
        for cid in list(self._containers_created):
            try:
                c = self.client.containers.get(cid)
                c.remove(force=True)
                count += 1
            except Exception:
                pass
        self._containers_created.clear()

        # Also clean any orphaned containers
        containers = self.client.containers.list(
            filters={"label": "psa.sandbox=true"},
            all=True,
        )
        for c in containers:
            try:
                c.remove(force=True)
                count += 1
            except Exception:
                pass

        logger.info("sandbox_cleanup_complete", extra={"containers_removed": count})
        return count

    def healthcheck(self) -> bool:
        """Check if the sandbox Docker image exists and daemon is accessible."""
        try:
            self.client.ping()
            self.client.images.get(self.image)
            return True
        except (DockerAPIError, ImageNotFound):
            logger.warning("sandbox_healthcheck_failed", extra={"image": self.image})
            return False

    def build_image(self) -> bool:
        """Build the sandbox Docker image from the Dockerfile.

        Returns:
            True if build succeeded.
        """
        dockerfile_dir = Path(__file__).parent.parent.parent / "docker"
        if not (dockerfile_dir / "sandbox.Dockerfile").exists():
            logger.error("sandbox_dockerfile_not_found", extra={"path": str(dockerfile_dir)})
            return False

        logger.info("sandbox_building_image", extra={"image": self.image})
        try:
            image, build_logs = self.client.images.build(
                path=str(dockerfile_dir),
                dockerfile="sandbox.Dockerfile",
                tag=self.image,
                rm=True,
            )
            for log in build_logs:
                if "stream" in log:
                    logger.debug("docker_build", extra={"log": log["stream"].strip()})
            logger.info("sandbox_image_built", extra={"image_id": image.id})
            return True
        except Exception as e:
            logger.error("sandbox_build_failed", extra={"error": str(e)})
            return False



