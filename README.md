# perpetual-scholar-agent

[![Python Version](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-Proprietary-red)](LICENSE)
[![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Tests](https://img.shields.io/badge/tests-passing-brightgreen)](tests/)
[![Documentation](https://img.shields.io/badge/docs-latest-blue)](docs/)
[![Phase](https://img.shields.io/badge/phase-0%20Research%20%26%20Setup-orange)](PROJECT-DEVELOPMENT-PHASE-TRACKING.md)
[![Contributing](https://img.shields.io/badge/contributions-welcome-brightgreen.svg)](CONTRIBUTING.md)
[![Security](https://img.shields.io/badge/security-responsible-blue.svg)](SECURITY.md)

An autonomous 24/7 self-evolving agent that masters a specialized technical domain through continuous research, sandbox experimentation, and reinforcement-learning-driven self-improvement.

## Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Project Structure](#project-structure)
- [Running Tests](#running-tests)
- [CLI Commands](#cli-commands)
- [Documentation](#documentation)
- [Support](#support)
- [Contributing](#contributing)
- [Security](#security)
- [License](#license)

## Features

- **Continuous Research**: Automatically crawls arXiv, GitHub Trending, and RSS feeds for cutting-edge techniques
- **Sandboxed Experimentation**: Executes generated code in isolated Docker containers with resource limits
- **Benchmark Verification**: Uses pytest-benchmark and hyperfine to validate performance improvements
- **Reinforcement Learning**: PPO-based policy learning optimized for technique discovery
- **Self-Improvement**: Periodic LoRA fine-tuning to internalize validated lessons
- **Vector Knowledge Base**: FAISS-powered semantic search over accumulated lessons
- **Production Ready**: Docker Compose deployment, monitoring, and comprehensive testing

## Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                     PERPETUAL SCHOLAR AGENT                       │
│                                                                    │
│  ┌─────────────── INGESTION LAYER ────────────────┐               │
│  │ crawl4ai │ arxiv-py │ GitHub API │ RSS Feeds   │               │
│  └──────────────────────┬──────────────────────────┘               │
│                         │ raw articles / papers                    │
│  ┌──────────────────────▼──────────────────────────┐             │
│  │              REASONING LAYER                      │             │
│  │  Local SLM (Ollama: Qwen2.5-Coder-7B)           │             │
│  │  ├─ Paper summarizer → technique extraction      │             │
│  │  ├─ Code generator → sandbox-ready implementation │             │
│  │  └─ Lesson writer → structured lesson JSON        │             │
│  │  [Optional: Claude API / GPT-4o]                │             │
│  └──────────────────────┬──────────────────────────┘             │
│                         │ generated code                          │
│  ┌──────────────────────▼──────────────────────────┐             │
│  │        EXPLORATION & VERIFICATION LAYER          │             │
│  │  Docker Sandbox (ephemeral container per exp)    │             │
│  │  ├─ Resource limits: 2 CPU, 2GB RAM, 60s timeout │             │
│  │  ├─ Benchmark harness: pytest-benchmark          │             │
│  │  └─ Metrics: throughput (ops/s), latency (p50/p99) │             │
│  └──────────────────────┬──────────────────────────┘             │
│                         │ (new_metric, baseline_metric)           │
│  ┌──────────────────────▼──────────────────────────┐             │
│  │               RL REWARD ENGINE                    │             │
│  │  PPO / Q-Learning (Stable-Baselines3)            │             │
│  │  reward = (new - baseline) / baseline            │             │
│  └──────────────────────┬──────────────────────────┘             │
│                         │                                          │
│  ┌──────────────────────▼──────────────────────────┐             │
│  │           KNOWLEDGE BASE LAYER                   │             │
│  │  SQLite: lessons, experiments, metrics            │             │
│  │  FAISS: vector index over lesson embeddings       │             │
│  │  SECOND-KNOWLEDGE-BRAIN.md: human-readable log    │             │
│  └──────────────────────┬──────────────────────────┘             │
│                         │ every 50 lessons or 7 days              │
│  ┌──────────────────────▼──────────────────────────┐             │
│  │          SELF-IMPROVEMENT LAYER                  │             │
│  │  LoRA fine-tuning (PEFT + trl)                    │             │
│  │  Output: updated adapter → reload Ollama model    │             │
│  └──────────────────────────────────────────────────┘             │
│                                                                    │
│  ┌──────────────────────────────────────────────────┐             │
│  │          ORCHESTRATION LAYER                      │             │
│  │  APScheduler: daily ingestion, weekly fine-tune   │             │
│  │  Dashboard: FastAPI + HTML — live metrics & log    │             │
│  └──────────────────────────────────────────────────┘             │
└──────────────────────────────────────────────────────────────────┘
```

## Quick Start

### Prerequisites

- **Python 3.11+** (Python 3.12 recommended)
- **Docker Desktop** (for sandbox execution)
- **Ollama** (for local SLM inference) — [install](https://ollama.com)
- **Git**

### 1. Clone & Set Up Environment

```bash
git clone <repo-url> && cd perpetual-scholar-agent

# Create virtual environment
python -m venv .venv

# Activate (Windows)
.venv\Scripts\activate

# Activate (Linux/macOS)
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure

```bash
# Copy the example env file and edit with your settings
cp .env.example .env

# Edit .env with your API keys (optional):
#   ANTHROPIC_API_KEY=sk-ant-...
#   OPENAI_API_KEY=sk-...
#   GITHUB_TOKEN=ghp_...
```

### 3. Install Ollama Model

```bash
# Install and start Ollama
ollama serve

# Pull the Qwen2.5-Coder 7B model
ollama pull qwen2.5-coder:7b
```

### 4. Build Sandbox Docker Image

```bash
# From project root
docker build -t psa-sandbox:latest -f docker/sandbox.Dockerfile docker/
```

### 5. Initialize Database & FAISS Index

```bash
python -m agent init
```

### 6. Verify Setup

```bash
# Run all Phase 0 verification scripts
python -m agent verify

# Or verify individual components:
python scripts/verify_dependencies.py
python scripts/verify_ollama.py
python scripts/verify_docker.py
python scripts/verify_ingestion.py
python scripts/verify_db_vector.py
```

### 7. Run Tests

```bash
pytest tests/ -v
```

### 8. Run a Single Pipeline Cycle

```bash
python -m agent run --once
```

### 9. Start the Agent (Daemon)

```bash
python -m agent start
```

## Project Structure

```
perpetual-scholar-agent/
├── agent/                          # Main package
│   ├── __init__.py
│   ├── __main__.py                 # CLI entry point
│   ├── config/
│   │   └── settings.py            # Pydantic Settings (all env vars)
│   ├── ingestion/
│   │   ├── arxiv_fetcher.py       # arXiv paper fetching
│   │   ├── github_fetcher.py      # GitHub Trending repos
│   │   ├── rss_fetcher.py         # RSS feed parsing
│   │   ├── deduplicator.py        # SHA-256 dedup
│   │   └── embedder.py            # Embedding + priority scoring
│   ├── reasoning/
│   │   ├── summarizer.py          # LLM paper summarization
│   │   ├── code_generator.py      # LLM code generation
│   │   └── prompts.py             # System prompts
│   ├── sandbox/
│   │   ├── executor.py            # Docker container lifecycle
│   │   ├── benchmark_harness.py   # Parse pytest-benchmark JSON
│   │   ├── resource_limits.py     # Container resource constraints
│   │   └── baseline_store.py      # Baseline metric persistence
│   ├── reward/
│   │   ├── calculator.py          # Reward computation
│   │   ├── lesson_writer.py       # SQLite + FAISS lesson storage
│   │   └── llm_judge.py          # LLM code quality scoring
│   ├── rl/
│   │   ├── environment.py         # Gymnasium env for PPO
│   │   ├── policy.py              # PPO policy training
│   │   └── checkpoint.py         # Model checkpoint management
│   ├── finetune/
│   │   ├── dataset_exporter.py    # Export lessons → JSONL
│   │   ├── trainer.py             # LoRA fine-tuning pipeline
│   │   ├── trigger.py             # Auto-trigger logic
│   │   └── ollama_reloader.py     # Reload Ollama with adapter
│   ├── llm/
│   │   └── backend.py             # Unified LLM interface (Ollama/Claude/GPT)
│   ├── orchestrator/
│   │   ├── pipeline.py            # Single cycle: ingest → store
│   │   └── scheduler.py          # APScheduler daemon
│   ├── monitoring/
│   │   ├── metrics.py             # Session metrics + Prometheus
│   │   └── reporter.py            # Weekly digest generator
│   ├── reporting/
│   │   └── brain_updater.py       # SECOND-KNOWLEDGE-BRAIN.md updater
│   ├── database/
│   │   └── schema.py              # SQLite schema (6 tables)
│   └── vectorstore/
│       └── faiss_index.py         # FAISS index management
├── docker/
│   ├── sandbox.Dockerfile         # Ephemeral benchmark image
│   └── fixtures/
│       └── baselines.py           # Baseline benchmark implementations
├── scripts/
│   ├── verify_dependencies.py     # Phase 0: dependency check
│   ├── verify_ollama.py          # Phase 0: Ollama check
│   ├── verify_docker.py           # Phase 0: Docker sandbox check
│   ├── verify_ingestion.py        # Phase 0: ingestion source check
│   └── verify_db_vector.py        # Phase 0: SQLite + FAISS check
├── tests/
│   ├── test_schema.py             # SQLite schema tests
│   ├── test_faiss_index.py        # FAISS index tests
│   ├── test_reward.py             # Reward calculator tests
│   ├── test_resource_limits.py    # Resource limit tests
│   ├── test_rl_environment.py     # RL environment tests
│   ├── test_settings.py           # Settings tests
│   ├── test_deduplication.py      # Deduplication tests
│   └── test_llm_backend.py        # LLM backend tests
├── data/                           # SQLite + FAISS data (gitignored)
├── models/                         # LoRA adapters + RL checkpoints
├── .env.example                    # Environment variable template
├── .gitignore
├── pyproject.toml                  # Project metadata & dependencies
├── requirements.txt                # Pip requirements
├── CLAUDE.md                       # Project overview for AI assistants
├── PROJECT-detail.md               # Full technical specification
├── PROJECT-DEVELOPMENT-PHASE-TRACKING.md  # Phase-by-phase roadmap
└── SECOND-KNOWLEDGE-BRAIN.md       # Research papers & knowledge log
```

## Configuration

All configuration is via environment variables, loaded from `.env`:

| Key | Default | Description |
|-----|---------|-------------|
| `DOMAIN_FOCUS` | Backend performance optimization | Research domain focus |
| `LLM_PROVIDER` | `ollama` | LLM: `ollama`, `claude`, or `openai` |
| `OLLAMA_MODEL` | `qwen2.5-coder:7b` | Ollama model name |
| `ARXIV_CATEGORIES` | `cs.DB,cs.DC,cs.PF` | arXiv categories to crawl |
| `SANDBOX_CPU_LIMIT` | `2` | Docker sandbox CPU cores |
| `SANDBOX_MEMORY_LIMIT` | `2g` | Docker sandbox RAM limit |
| `SANDBOX_TIMEOUT_SECONDS` | `60` | Sandbox execution timeout |
| `LORA_R` | `16` | LoRA rank |
| `LORA_ALPHA` | `32` | LoRA alpha |
| `LORA_TRIGGER_LESSON_COUNT` | `50` | Auto-finetune lesson threshold |
| `REWARD_IMPROVEMENT_THRESHOLD` | `0.05` | 5% improvement = positive reward |

See `.env.example` for the full list.

## Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=agent --cov-report=html

# Run a specific test module
pytest tests/test_schema.py -v
```

## CLI Commands

```bash
# Initialize database and FAISS index
python -m agent init

# Run a single pipeline cycle
python -m agent run --once

# Run with specific ingestion source
python -m agent run --once --source arxiv

# Start the daemon
python -m agent start

# Run verification scripts
python -m agent verify
python -m agent verify --component docker
python -m agent verify --component ollama
```

## License

Private project — see LICENSE for details.

## Documentation

- [Technical Specification](PROJECT-detail.md) - Full architecture and design documentation
- [Development Phase Tracking](PROJECT-DEVELOPMENT-PHASE-TRACKING.md) - Phase-by-phase implementation roadmap
- [Second Knowledge Brain](SECOND-KNOWLEDGE-BRAIN.md) - Research papers and knowledge log
- [Deployment Guide](docs/DEPLOYMENT.md) - Production deployment instructions
- [Testing Guide](docs/TESTING.md) - Testing conventions and best practices
- [Contributing Guide](CONTRIBUTING.md) - Contribution guidelines and workflows
- [Security Policy](SECURITY.md) - Security policies and vulnerability reporting
- [Code of Conduct](CODE_OF_CONDUCT.md) - Community guidelines
- [Changelog](CHANGELOG.md) - Version history and changes

## Support

- 📖 [Documentation](docs/)
- 🐛 [Issue Tracker](https://github.com/your-org/perpetual-scholar-agent/issues)
- 💬 [Discussions](https://github.com/your-org/perpetual-scholar-agent/discussions)
- 📧 [Email Support](mailto:support@perpetual-scholar-agent.com)

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## Security

For security concerns, please see [SECURITY.md](SECURITY.md) and follow our responsible disclosure process.
