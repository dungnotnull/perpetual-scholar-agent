# PROJECT-DEVELOPMENT-PHASE-TRACKING.md — perpetual-scholar-agent

## Overview

| Phase | Name | Timeline | Status |
|---|---|---|---|
| 0 | Research & Environment Setup | Week 1–2 | ✅ Complete |
| 1 | MVP — Core Loop Working | Week 3–6 | ✅ Complete |
| 2 | ML/AI Integration (RL + Embeddings) | Week 7–10 | ✅ Complete |
| 3 | External LLM API Integration | Week 11–12 | ✅ Complete |
| 4 | Self-Improving Knowledge Loop (LoRA + Auto-Update) | Week 13–14 | ✅ Complete |
| 5 | Testing, Polish & Deployment | Week 15–16 | ✅ Complete |

---

## Phase 0: Research & Environment Setup (Week 1–2) ✅

### Goal
Establish a reproducible development environment, understand the full dependency graph, and validate that each individual component can be run in isolation before wiring them together.

### Task List

- [x] Create Python 3.11+ virtual environment and `pyproject.toml` with all dependencies
- [x] Install and verify Ollama with `Qwen2.5-Coder-7B-Instruct` model loaded
- [x] Set up Docker Desktop and verify Python Docker SDK can create/destroy containers
- [x] Verify `crawl4ai` can successfully scrape arXiv abstract pages
- [x] Verify `arxiv-py` can retrieve last-24h papers for cs.DB category
- [x] Verify `PyGithub` can fetch GitHub Trending (Python, Go)
- [x] Run `pytest-benchmark` inside a Docker container manually and retrieve metrics
- [x] Set up SQLite schema: `experiments`, `lessons`, `seen_items` tables (6 tables total)
- [x] Initialize FAISS flat index and verify add/search operations
- [x] Create `.env.example` with all required config keys (50+ keys)
- [x] Write `docker/sandbox.Dockerfile` base image (python:3.12-slim + pytest-benchmark)
- [x] Document local setup in `README.md`

### Deliverables ✅
- ✅ Working dev environment with all dependencies specified in `requirements.txt` and `pyproject.toml`
- ✅ Validated Docker sandbox that can run Python benchmarks (`docker/sandbox.Dockerfile`)
- ✅ SQLite schema initialized (6 tables: seen_items, experiments, lessons, finetune_runs, rl_policy_checkpoints, metrics_history)
- ✅ FAISS index initialized and searchable with add/search/save/reload operations

---

## Phase 1: MVP — Core Loop Working (Week 3–6) ✅

### Goal
Build the end-to-end pipeline from paper ingestion to lesson storage, without the RL policy or LoRA loop.

### Task List

**Ingestion Pipeline**
- [x] `ingestion/arxiv_fetcher.py`: fetch last-24h papers for configurable arXiv categories
- [x] `ingestion/github_fetcher.py`: fetch GitHub Trending repos, extract README summaries
- [x] `ingestion/rss_fetcher.py`: parse Medium Engineering, Hacker News RSS feeds
- [x] `ingestion/deduplicator.py`: SHA-256 hash check against `seen_items` SQLite table
- [x] `ingestion/embedder.py`: embed items with `all-MiniLM-L6-v2`, compute domain similarity score

**Reasoning Pipeline**
- [x] `reasoning/summarizer.py`: Ollama prompt → extract {technique_name, problem, algorithm, pseudocode}
- [x] `reasoning/code_generator.py`: Ollama prompt → generate runnable Python benchmark code
- [x] `reasoning/prompts.py`: store all system prompts as string constants

**Sandbox Execution**
- [x] `sandbox/executor.py`: Docker SDK — create container, copy code, run, capture stdout + exit code
- [x] `sandbox/benchmark_harness.py`: parse pytest-benchmark JSON output → {ops_per_sec, latency_p50, latency_p99}
- [x] `sandbox/resource_limits.py`: enforce CPU, RAM, timeout limits per container
- [x] `sandbox/baseline_store.py`: SQLite-backed store of baseline metrics per domain

**Reward Engine**
- [x] `reward/calculator.py`: `(new - baseline) / baseline`, clamped to [-1, +1]
- [x] `reward/lesson_writer.py`: package (technique, code, metrics, reward, source_url) → SQLite + FAISS

**Orchestration (basic)**
- [x] `orchestrator/pipeline.py`: wire ingestion → reasoning → sandbox → reward → storage as one callable
- [x] `orchestrator/cli.py`: `python -m agent run --once` triggers single pipeline cycle

---

## Phase 2: ML/AI Integration — Smart Features (Week 7–10) ✅

### Goal
Replace naive paper processing with an RL policy (PPO) that learns which papers yield highest-reward experiments. Integrate FAISS-based lesson retrieval for few-shot code generation.

### Task List

**RL Environment**
- [x] `rl/environment.py`: OpenAI Gym-compatible environment (Box(387,) obs, Discrete(5) actions)
- [x] `rl/policy.py`: PPO policy (MLP [256, 128, 64]) via Stable-Baselines3 with RewardLoggingCallback
- [x] `rl/checkpoint.py`: save/load policy checkpoints to `./models/rl_policy/`

**Lesson-Augmented Code Generation**
- [x] `reasoning/lesson_retriever.py`: FAISS top-k search → retrieve relevant prior lessons
- [x] `code_generator.py` updated to include retrieved lessons in context prompt (few-shot examples)

**Domain Prioritization**
- [x] `ingestion/embedder.py`: cosine similarity between paper embedding and `DOMAIN_FOCUS_EMBEDDING`

**Metrics & Monitoring**
- [x] `monitoring/metrics.py`: track per-session stats with SessionMetrics + Prometheus endpoint
- [x] `monitoring/reporter.py`: Markdown weekly digest generator

---

## Phase 3: External LLM API Integration (Week 11–12) ✅

### Goal
Add Claude API and GPT-4o as optional backends for paper summarization and code generation. Implement the full pluggable LLM client with graceful fallback.

### Task List

- [x] `llm/backend.py`: unified async interface with `generate(prompt, system)` method + `judge_code_quality()`
- [x] `llm/ollama_backend.py`: Ollama HTTP client with healthcheck, model listing, pull, generate, embeddings
- [x] `llm/claude_backend.py`: Anthropic SDK client with `generate()` and `judge_code()` methods
- [x] `llm/openai_backend.py`: OpenAI SDK client with `generate()` method
- [x] `llm/backend.py`: fallback chain (ollama → claude → openai) with retry logic
- [x] `LLM_PROVIDER` and `LLM_FALLBACK_CHAIN` env vars in `.env.example`
- [x] `reward/llm_judge.py`: send (code, technique_description) to LLM → score code quality 0–10
- [x] `resilience.py`: retry decorators (retry_network, retry_http, retry_llm) + CircuitBreaker class
- [x] Combined reward: `combined_reward = 0.7 * benchmark_reward + 0.3 * llm_judge_score`

---

## Phase 4: Self-Improving Knowledge Loop (Week 13–14) ✅

### Goal
Complete the self-improvement loop: LoRA fine-tuning triggered automatically from verified lessons, and SECOND-KNOWLEDGE-BRAIN.md auto-updated weekly.

### Task List

**LoRA Fine-tuning Pipeline**
- [x] `finetune/dataset_exporter.py`: query SQLite for lessons since last fine-tune, format as JSONL
- [x] `finetune/trainer.py`: `trl.SFTTrainer` with QLoRA config (r=16, alpha=32, 4-bit quantization)
- [x] `finetune/adapter_manager.py`: save versioned adapter, update symlink, list versions, cleanup old
- [x] `finetune/ollama_reloader.py`: call Ollama `POST /api/create` to register updated model
- [x] `finetune/trigger.py`: check lesson count + time-since-last-finetune; enqueue job if threshold met

**SECOND-KNOWLEDGE-BRAIN Auto-Update**
- [x] `reporting/brain_updater.py`: render top-10 lessons from SQLite → Markdown table → append to brain file

**Orchestration (full)**
- [x] `orchestrator/scheduler.py`: register all cron jobs (daily ingestion, weekly fine-tune, weekly brain update, weekly report)
- [x] `python -m agent start` command: starts APScheduler daemon with graceful SIGTERM handler

---

## Phase 5: Testing, Polish & Deployment (Week 15–16) ✅

### Goal
Harden the system for continuous unattended operation: structured logging, observability, graceful error handling, FastAPI dashboard, and deployment configs.

### Task List

**Structured Logging**
- [x] `logging_config.py`: structlog JSON logging configured for all modules with quiet third-party loggers

**Error Handling & Resilience**
- [x] `resilience.py`: retry decorators with tenacity (retry_network, retry_http, retry_llm)
- [x] `resilience.py`: CircuitBreaker class (failure threshold, sliding window, cooldown)
- [x] Global sandbox circuit breaker: pauses experiments if failure rate > 50% in 1 hour
- [x] Graceful Docker container cleanup on SIGTERM in scheduler.py

**Observability**
- [x] `monitoring/metrics.py`: SessionMetrics tracking + Prometheus-format `/metrics` endpoint
- [x] `monitoring/reporter.py`: weekly Markdown digest with aggregate stats and top techniques

**FastAPI Dashboard**
- [x] `dashboard.py`: `GET /` — live experiment feed (last 20 experiments, HTML)
- [x] `dashboard.py`: `GET /lessons` — paginated lesson browser with search
- [x] `dashboard.py`: `GET /lessons/{id}` — full lesson detail including verified code
- [x] `dashboard.py`: `GET /stats` — JSON aggregate stats
- [x] `dashboard.py`: `GET /reports/latest` — latest weekly digest Markdown
- [x] `dashboard.py`: `GET /metrics` — Prometheus-format metrics
- [x] `python -m agent dashboard` CLI command to start the dashboard server

**Deployment**
- [x] `Dockerfile`: multi-stage build for agent container with health check
- [x] `docker-compose.yml`: agent + Ollama + Redis + Prometheus + Grafana
- [x] `monitoring/prometheus.yml`: Prometheus scrape config
- [x] `psa-agent.service`: systemd unit file for bare-metal deployment
- [x] `.gitignore`: complete ignore rules for Python/ML projects
- [x] `.env.example`: 50+ configuration keys with documentation
- [x] `README.md`: full quickstart guide, architecture diagram, CLI reference, config table

---

## Total Estimated Effort

| Phase | Hours | Status |
|---|---|---|
| Phase 0 | 16 | ✅ Complete |
| Phase 1 | 48 | ✅ Complete |
| Phase 2 | 40 | ✅ Complete |
| Phase 3 | 20 | ✅ Complete |
| Phase 4 | 32 | ✅ Complete |
| Phase 5 | 32 | ✅ Complete |
| **Total** | **188 hours (~5 months part-time @ 10h/week)** | **All phases complete** |

---

## Project File Inventory

### Core Application (agent/)

| File | Phase | Purpose |
|------|-------|---------|
| `__init__.py` | 0 | Package initialization with version |
| `__main__.py` | 1+5 | CLI entry point (run/start/verify/init/dashboard) |
| `logging_config.py` | 5 | Structured JSON logging via structlog |
| `resilience.py` | 5 | Retry decorators + CircuitBreaker pattern |
| `dashboard.py` | 5 | FastAPI dashboard (6 endpoints) |
| `config/settings.py` | 0 | Pydantic Settings (50+ env vars) |
| `database/schema.py` | 0 | SQLite schema (6 tables + indexes) |
| `vectorstore/faiss_index.py` | 0 | FAISS flat L2 index management |
| `ingestion/arxiv_fetcher.py` | 1 | arXiv paper fetching |
| `ingestion/github_fetcher.py` | 1 | GitHub Trending fetching |
| `ingestion/rss_fetcher.py` | 1 | RSS/Atom feed parsing |
| `ingestion/deduplicator.py` | 1 | SHA-256 dedup against seen_items |
| `ingestion/embedder.py` | 1+2 | all-MiniLM-L6-v2 embedding + domain priority |
| `reasoning/summarizer.py` | 1 | LLM paper summarization |
| `reasoning/code_generator.py` | 1 | LLM benchmark code generation |
| `reasoning/lesson_retriever.py` | 2 | FAISS top-k lesson retrieval |
| `reasoning/prompts.py` | 1 | System prompts (4 templates) |
| `sandbox/executor.py` | 1+5 | Docker container lifecycle with retry + cleanup |
| `sandbox/benchmark_harness.py` | 1 | Parse pytest-benchmark JSON |
| `sandbox/resource_limits.py` | 1 | Container resource constraints |
| `sandbox/baseline_store.py` | 1 | Baseline metric persistence |
| `reward/calculator.py` | 1 | Reward computation (benchmark + LLM) |
| `reward/lesson_writer.py` | 1+4 | SQLite + FAISS lesson storage |
| `reward/llm_judge.py` | 3 | LLM code quality scoring |
| `rl/environment.py` | 2 | Gymnasium env (387-dim obs, 5 actions) |
| `rl/policy.py` | 2 | PPO with RewardLoggingCallback + EvalCallback |
| `rl/checkpoint.py` | 2 | Checkpoint save/load + DB tracking |
| `finetune/dataset_exporter.py` | 4 | Lessons → JSONL for SFTTrainer |
| `finetune/trainer.py` | 4 | QLoRA fine-tuning (4-bit, r=16, alpha=32) |
| `finetune/adapter_manager.py` | 4 | Versioned adapters + symlink + cleanup |
| `finetune/trigger.py` | 4 | Auto-trigger (50 lessons or 7 days) |
| `finetune/ollama_reloader.py` | 4 | Reload Ollama model with adapter |
| `llm/backend.py` | 3 | Unified async interface + fallback + judge |
| `llm/ollama_backend.py` | 3 | Ollama client (generate, embed, healthcheck) |
| `llm/claude_backend.py` | 3 | Anthropic Claude client + judge |
| `llm/openai_backend.py` | 3 | OpenAI GPT client |
| `orchestrator/pipeline.py` | 1+5 | E2E cycle with circuit breaker + metrics |
| `orchestrator/scheduler.py` | 4+5 | APScheduler daemon + SIGTERM handler |
| `monitoring/metrics.py` | 2+5 | SessionMetrics + Prometheus endpoint |
| `monitoring/reporter.py` | 2+5 | Weekly digest generator |
| `reporting/brain_updater.py` | 4 | SECOND-KNOWLEDGE-BRAIN.md auto-updater |

### Infrastructure

| File | Purpose |
|------|---------|
| `Dockerfile` | Agent container image with health check |
| `docker-compose.yml` | Agent + Ollama + Redis + Prometheus + Grafana |
| `docker/sandbox.Dockerfile` | Ephemeral benchmark image (python:3.12-slim) |
| `docker/fixtures/baselines.py` | Baseline benchmark implementations |
| `monitoring/prometheus.yml` | Prometheus scrape configuration |
| `psa-agent.service` | Systemd service unit file |
| `.env.example` | 50+ configuration keys |
| `.gitignore` | Complete Python/ML gitignore |
| `pyproject.toml` | Project metadata + all dependencies |
| `requirements.txt` | Pip-compatible requirements |
| `README.md` | Full quickstart + architecture + CLI reference |
