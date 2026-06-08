# PROJECT-detail.md — perpetual-scholar-agent

## Executive Summary

perpetual-scholar-agent is a fully autonomous, 24/7-running AI system that selects a narrow technical domain (default: Backend Performance Optimization / Clean Architecture) and works to master it through an endless loop of research ingestion, sandbox experimentation, empirical benchmarking, and RL-guided self-improvement. Unlike a static RAG system that merely retrieves documents, this agent *executes* the techniques it discovers, measures their real-world impact, and internalizes only the ones that are proven to work. Periodic LoRA fine-tuning closes the loop by updating the agent's own local SLM with the distilled knowledge, creating a compound-growth intelligence curve.

---

## Problem Statement

**The knowledge-velocity gap**: The volume of technical literature (arXiv alone publishes ~2,000 CS papers/day as of 2024) far exceeds any individual's reading bandwidth. A senior backend engineer can realistically review 5–10 papers/week. Meanwhile, GitHub accumulates thousands of novel algorithm implementations daily.

**The theory-practice gap**: Even when engineers read papers, they rarely have time to reproduce experiments and verify that a published technique works on *their* stack. Papers often omit implementation details that change real-world performance by 10–100×.

**The knowledge-retention gap**: Individual engineers leave companies, retire, or forget. Institutional engineering knowledge is often trapped in tribal memory.

This agent addresses all three gaps: it reads at machine speed, reproduces experiments automatically, and stores verified lessons in a persistent, queryable knowledge base that grows indefinitely.

---

## Target Users & Use Cases

| User | Use Case |
|---|---|
| Engineering teams | Deploy agent as an internal R&D assistant that surfaces verified performance improvements |
| Individual developers | Run locally as a personalized "night shift" that learns while you sleep |
| AI researchers | Use as an experimental platform for studying RL-driven code evolution |
| CTOs / Tech leads | Receive weekly digest reports of verified techniques the agent has learned |

---

## Architecture Overview

```
┌──────────────────────────────────────────────────────────────────────┐
│                     PERPETUAL SCHOLAR AGENT                          │
│                                                                      │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │                  INGESTION LAYER                             │    │
│  │  crawl4ai   │  arxiv-py   │  GitHub API   │  RSS Feeds      │    │
│  │  arXiv cs.DC/cs.DB/cs.PF  │  GitHub Trend │  Medium/HN      │    │
│  └────────────────────┬────────────────────────────────────────┘    │
│                       │ raw articles / papers                        │
│  ┌────────────────────▼────────────────────────────────────────┐    │
│  │                  REASONING LAYER                             │    │
│  │  Local SLM (Ollama: Qwen2.5-Coder-7B)                       │    │
│  │  ├── Paper summarizer → technique extraction                 │    │
│  │  ├── Code generator → sandbox-ready implementation           │    │
│  │  └── Lesson writer → structured lesson JSON                  │    │
│  │  [Optional upgrade: Claude API / GPT-4o]                     │    │
│  └────────────────────┬────────────────────────────────────────┘    │
│                       │ generated code                               │
│  ┌────────────────────▼────────────────────────────────────────┐    │
│  │            EXPLORATION & VERIFICATION LAYER                  │    │
│  │  Docker Sandbox (ephemeral container per experiment)         │    │
│  │  ├── Resource limits: 2 CPU, 2GB RAM, 60s timeout            │    │
│  │  ├── Benchmark harness: pytest-benchmark / hyperfine         │    │
│  │  └── Metrics: throughput (ops/s), latency (p50/p99), memory  │    │
│  └────────────────────┬────────────────────────────────────────┘    │
│                       │ (new_metric, baseline_metric, success_flag)  │
│  ┌────────────────────▼────────────────────────────────────────┐    │
│  │                   RL REWARD ENGINE                           │    │
│  │  PPO / Q-Learning (Stable-Baselines3)                        │    │
│  │  reward = (new - baseline) / baseline                        │    │
│  │  +reward → store lesson, update policy                       │    │
│  │  -reward → log failure, update policy (avoid action)         │    │
│  └────────────────────┬────────────────────────────────────────┘    │
│                       │                                              │
│  ┌────────────────────▼────────────────────────────────────────┐    │
│  │              KNOWLEDGE BASE LAYER                            │    │
│  │  SQLite: lessons, experiments, metrics history               │    │
│  │  FAISS: vector index over lesson embeddings                  │    │
│  │  SECOND-KNOWLEDGE-BRAIN.md: human-readable research log      │    │
│  └────────────────────┬────────────────────────────────────────┘    │
│                       │ every 50 lessons or 7 days                   │
│  ┌────────────────────▼────────────────────────────────────────┐    │
│  │              SELF-IMPROVEMENT LAYER                          │    │
│  │  LoRA fine-tuning (Hugging Face PEFT + trl)                  │    │
│  │  Training data: verified (code, lesson) pairs                │    │
│  │  Output: updated adapter weights → reload Ollama model       │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                                                                      │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │              ORCHESTRATION LAYER                             │    │
│  │  APScheduler: daily ingestion cron, weekly fine-tune cron    │    │
│  │  Redis (optional): task queue for parallel sandbox runs      │    │
│  │  Dashboard: FastAPI + simple HTML — live metrics & log       │    │
│  └─────────────────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────────────┘
```

---

## Tech Stack

| Component | Technology | Source |
|---|---|---|
| Crawler | crawl4ai | https://github.com/unclecode/crawl4ai |
| arXiv access | arxiv-py | https://github.com/lukasschwab/arxiv.py |
| GitHub API | PyGithub | https://github.com/PyGithub/PyGithub |
| Local SLM | Ollama + Qwen2.5-Coder-7B | https://ollama.com |
| Code execution | Docker SDK for Python | https://docker-py.readthedocs.io |
| Benchmarking | pytest-benchmark, hyperfine | pip, https://github.com/sharkdp/hyperfine |
| RL framework | Stable-Baselines3 | https://github.com/DLR-RM/stable-baselines3 |
| LoRA fine-tuning | Hugging Face PEFT + trl | https://github.com/huggingface/peft |
| Embeddings | sentence-transformers | https://www.sbert.net |
| Vector index | FAISS | https://github.com/facebookresearch/faiss |
| Persistent storage | SQLite (aiosqlite) | stdlib |
| Scheduler | APScheduler | https://apscheduler.readthedocs.io |
| Task queue | Redis + RQ (optional) | https://python-rq.org |
| Dashboard | FastAPI + Jinja2 | https://fastapi.tiangolo.com |
| Config | python-dotenv, Pydantic Settings | pip |

---

## ML/DL Models

### Primary Models

| Model | HuggingFace ID | Role | Fine-tuning Plan |
|---|---|---|---|
| Qwen2.5-Coder-7B-Instruct | `Qwen/Qwen2.5-Coder-7B-Instruct` | Code generation from paper summaries | LoRA on verified (prompt, code) pairs |
| DeepSeek-Coder-7B | `deepseek-ai/deepseek-coder-7b-instruct-v1.5` | Fallback code SLM | LoRA on verified (prompt, code) pairs |
| all-MiniLM-L6-v2 | `sentence-transformers/all-MiniLM-L6-v2` | Lesson & paper embeddings | No fine-tuning needed |
| CodeBERT-base | `microsoft/codebert-base` | Code similarity scoring | No fine-tuning needed |

### RL Model Details

- **Algorithm**: PPO (Proximal Policy Optimization) via Stable-Baselines3
- **State space**: (paper_embedding[384], baseline_score[1], sandbox_available[1], queue_depth[1]) → 387-dim vector
- **Action space**: Discrete(5) = {FETCH_PAPER, GENERATE_CODE, RUN_BENCHMARK, STORE_LESSON, SKIP}
- **Reward function**: `(new_metric - baseline) / baseline` clamped to [-1.0, +1.0]
- **Policy network**: MLP with layers [256, 128, 64]
- **Training**: Online learning — policy updated after each episode (one paper → benchmark cycle)

### LoRA Fine-tuning Details

- **Method**: LoRA (r=16, alpha=32, dropout=0.05) applied to attention layers
- **Training framework**: Hugging Face `trl` SFTTrainer
- **Dataset format**: `{"prompt": "<paper_summary>", "completion": "<verified_code>"}`
- **Trigger**: ≥50 new verified lessons OR 7 days elapsed
- **Duration**: ~2–4 hours on a single RTX 3090 (7B model, 50 examples)

---

## External LLM API Integration

```python
# llm_backend.py — pluggable LLM client
import os

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama")  # ollama | claude | openai

async def generate(prompt: str, system: str = "") -> str:
    if LLM_PROVIDER == "ollama":
        return await _ollama_generate(prompt, system)
    elif LLM_PROVIDER == "claude":
        return await _claude_generate(prompt, system)
    elif LLM_PROVIDER == "openai":
        return await _openai_generate(prompt, system)
    raise ValueError(f"Unknown provider: {LLM_PROVIDER}")
```

Fallback chain: `ollama` → `claude` → `openai` (first healthy provider wins).

---

## Feature Specification

### MVP Features

- [x] Multi-source ingestion: arXiv (cs.DB, cs.DC, cs.PF), GitHub Trending (Python, Go), Medium Engineering RSS
- [x] Paper summarizer: extract technique name, problem solved, algorithm description, pseudo-code
- [x] Code generator: produce runnable Python/Go implementation from technique summary
- [x] Docker sandbox executor: ephemeral container, resource-limited, 60s timeout, returns stdout + metrics
- [x] Benchmark harness: measure throughput (ops/s) and latency (p50, p99) vs. baseline implementation
- [x] Reward calculator: `(new - baseline) / baseline`
- [x] Lesson storage: SQLite table + FAISS vector index
- [x] Daily orchestration cron via APScheduler
- [x] CLI dashboard: list recent experiments, success rate, top lessons

### Advanced Features

- [ ] RL policy (PPO): learns which paper types yield highest-reward experiments, prioritizes them
- [ ] LoRA fine-tuning pipeline: auto-triggered, reloads Ollama adapter after training
- [ ] Multi-domain support: configurable `DOMAIN_FOCUS` with domain-specific benchmark suites
- [ ] Cross-agent learning: ingest lessons from public agent GitHub repos (with crawl4ai)
- [ ] Weekly digest report: Markdown summary of top 10 lessons with benchmark numbers
- [ ] FastAPI dashboard: live experiment log, reward curve chart, lesson browser
- [ ] Lesson export: SECOND-KNOWLEDGE-BRAIN.md auto-updated with new verified lessons
- [ ] Notification: email/Slack webhook when a breakthrough technique (reward > 0.3) is found

---

## Full E2E Data Flow

1. **APScheduler fires daily ingestion job** at 02:00 UTC
2. **Ingestion pipeline** queries arXiv API (last 24h, cs.DB + cs.DC + cs.PF), fetches GitHub Trending (Python + Go), scrapes Medium Engineering RSS
3. **Deduplication**: each item is hashed; duplicates against SQLite `seen_items` table are dropped
4. **Embedding + prioritization**: each item is embedded with `all-MiniLM-L6-v2`; cosine similarity to domain focus vector determines priority score
5. **RL agent selects action**: given current state (paper embedding, queue depth, baseline score), PPO policy chooses `GENERATE_CODE`
6. **Local SLM (Ollama)** receives structured prompt: `{system: "You are a backend performance expert…", user: "<paper_summary>; write a runnable Python benchmark"}`. Returns code string.
7. **Docker sandbox executor** builds ephemeral container from `python:3.12-slim`, copies code, runs `pytest-benchmark` for 30s, captures `ops_per_sec` and `latency_p99`
8. **Reward engine** compares metrics vs. baseline stored in SQLite; computes scalar reward
9. If `reward > 0.05`: lesson JSON `{technique, code, metrics, reward, source_url}` inserted into SQLite + FAISS index
10. If `reward < -0.05`: failure record logged; RL agent receives negative reward; technique deprioritized
11. **PPO policy updated** with (state, action, reward, next_state) via Stable-Baselines3 online learning step
12. **LoRA trigger check**: if `len(new_lessons_since_last_finetune) >= 50`, schedule fine-tuning job
13. **Fine-tuning job** (if triggered): exports (prompt, code) pairs from SQLite, runs `trl.SFTTrainer` with LoRA config, saves adapter to `./models/lora_adapter_v{n}/`, reloads Ollama model with new adapter
14. **Weekly report job** (Sundays 06:00 UTC): queries top-10 lessons by reward score, renders Markdown digest, appends to `SECOND-KNOWLEDGE-BRAIN.md`

---

## Privacy & Security

- All scraped content is third-party public data; no user PII is involved
- Docker sandbox containers run with `--network=none` (no outbound internet access)
- All persistent data stored locally in `./data/` directory (SQLite + FAISS index)
- No data is sent to external APIs unless `LLM_PROVIDER` is explicitly set to `claude` or `openai`
- API keys stored in `.env` file (never committed to git); loaded via `python-dotenv`
- LoRA adapter weights stored locally; never uploaded

---

## Key Python/JS Dependencies

```toml
[tool.poetry.dependencies]
python = "^3.12"
crawl4ai = "^0.4"
arxiv = "^2.1"
PyGithub = "^2.3"
docker = "^7.0"
stable-baselines3 = "^2.3"
torch = "^2.3"
transformers = "^4.42"
peft = "^0.11"
trl = "^0.9"
sentence-transformers = "^3.0"
faiss-cpu = "^1.8"          # use faiss-gpu if CUDA available
aiosqlite = "^0.20"
apscheduler = "^3.10"
fastapi = "^0.111"
uvicorn = "^0.30"
pydantic-settings = "^2.3"
python-dotenv = "^1.0"
httpx = "^0.27"
anthropic = "^0.29"         # optional — Claude API
openai = "^1.35"            # optional — GPT-4o fallback
```

---

## Improvement Suggestions

1. **Multi-domain parallelism**: Run separate agent instances per domain (backend, ML, security) with a shared FAISS index for cross-domain insight transfer.
2. **Adversarial code testing**: After benchmark success, run static analysis (bandit, ruff) and fuzzing (Atheris) on generated code before storing — prevents learning insecure patterns.
3. **Peer-to-peer lesson sharing**: Publish verified lesson embeddings to a public IPFS node; other agent instances can subscribe, creating a distributed knowledge network (connects to Folder 1's P2P mesh).
4. **Curriculum RL**: Implement a staged curriculum — start with trivial optimizations to build a solid baseline, then progressively tackle harder papers — reducing wasted sandbox cycles on unsolvable problems.
5. **Human-in-the-loop review gate**: For lessons with reward > 0.5, send a Slack/email notification asking a human to review before the lesson is included in LoRA training data.
6. **Knowledge decay**: Implement a TTL on old lessons; re-benchmark quarterly to detect if a once-superior technique has been superseded by newer approaches.
7. **LLM judge integration**: Use Claude API to evaluate code quality beyond raw benchmarks (readability, maintainability, correctness) as a secondary reward signal.
