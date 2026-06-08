# =============================================================================
# perpetual-scholar-agent — sandbox Dockerfile
# Ephemeral execution environment for running untrusted benchmark code.
# Built as: docker build -t psa-sandbox:latest -f docker/sandbox.Dockerfile docker/
# =============================================================================

FROM python:3.12-slim

# Prevent interactive prompts
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies for C extensions (some benchmarks need them)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        gcc \
        && rm -rf /var/lib/apt/lists/*

# Install Python benchmarking tools
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir \
        pytest==8.2.* \
        pytest-benchmark==4.0.* \
        pytest-asyncio==0.23.* \
        numpy==1.26.* \
        httpx==0.27.*

# Create non-root user for running benchmarks
RUN groupadd -r sandbox && useradd -r -g sandbox -m sandbox

# Working directory for benchmark code
WORKDIR /sandbox

# Copy any baseline benchmark fixtures
COPY fixtures/ /sandbox/fixtures/

# Switch to non-root user
USER sandbox

# Default: run pytest with benchmark output in JSON format
ENTRYPOINT ["python", "-m", "pytest", \
            "--benchmark-only", \
            "--benchmark-json=/sandbox/results/benchmark_results.json", \
            "--benchmark-warmup=5", \
            "--benchmark-min-rounds=30", \
            "-v"]

# Healthcheck: verify pytest is importable
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD python -c "import pytest; print('healthy')" || exit 1
