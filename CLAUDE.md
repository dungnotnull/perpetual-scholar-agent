# CLAUDE.md — perpetual-scholar-agent

## Project Identity
- **Name**: perpetual-scholar-agent
- **Tagline**: An autonomous 24/7 self-evolving agent that masters a specialized technical domain through continuous research, sandbox experimentation, and reinforcement-learning-driven self-improvement
- **Status**: Phase 0 — Research & Environment Setup
- **Cluster**: B — Autonomous Agent Actors (alongside Folder 2: autonomous-solopreneur-agent)

---

## Core Problem

Modern technical domains evolve faster than any human expert can track. A backend engineer who reads 2–3 papers a week still falls months behind the state of the art. This agent closes that gap by operating as a tireless digital researcher: it scrapes academic and engineering sources daily, reproduces every promising technique inside an isolated Docker sandbox, benchmarks the result against a known baseline, and — when the technique proves superior — stores it as a verified "lesson" in its growing knowledge base. Over weeks and months the agent accumulates a corpus of empirically validated techniques that no human could replicate at the same speed. Periodic LoRA fine-tuning of its local SLM internalizes those lessons directly into the model's weights, making each generation of the agent measurably smarter than the last.

---

## Architecture Summary

| Layer | Component | Technology |
|---|---|---|
| Knowledge Ingestion | Multi-source crawler | crawl4ai, arxiv-py, GitHub REST API |
| Reasoning | Local SLM host | Ollama (Qwen2.5-Coder-7B / DeepSeek-Coder-7B) |
| Exploration | Code generation & execution | Docker SDK, Python subprocess |
| Reward Engine | Benchmark harness | pytest-benchmark, hyperfine, custom metrics |
| RL Loop | Policy optimization | Stable-Baselines3 (PPO), Q-table for discrete actions |
| Self-Improvement | Fine-tuning pipeline | LoRA via Hugging Face PEFT + trl |
| Knowledge Storage | Persistent lesson store | SQLite + JSON + vector index (FAISS) |
| Orchestration | Scheduler & event bus | APScheduler, Redis (optional) |

---

## Key Technical Decisions

1. **Domain scoping**: Default domain is Backend Performance Optimization (database sharding, caching strategies, async I/O patterns). Domain is configurable via `DOMAIN_FOCUS` env var.
2. **Sandbox isolation**: All experimental code runs inside ephemeral Docker containers with hard CPU/RAM/network limits. The host filesystem is never touched by experimental code.
3. **RL action space**: Actions = {fetch_paper, generate_code, run_benchmark, store_lesson, skip}. State = (paper embedding, current baseline score, sandbox availability).
4. **Reward signal**: `reward = (new_metric - baseline_metric) / baseline_metric`. Positive if improvement > 5%, negative if degradation > 5%, zero otherwise.
5. **LoRA fine-tuning cadence**: Triggered automatically when the verified-lesson buffer accumulates ≥ 50 new entries or every 7 days, whichever comes first.
6. **Pluggable LLM backend**: Primary = local Ollama; optional upgrade to Claude API or GPT-4o via `LLM_PROVIDER` env var for harder reasoning tasks.
7. **Privacy-first**: No user data involved. All scraped content is ephemeral; only benchmark results + lesson summaries are persisted.

---

## External LLM API Integrations

| Provider | Purpose | Config Key |
|---|---|---|
| Ollama (local) | Primary code generation & reasoning | `OLLAMA_BASE_URL`, `OLLAMA_MODEL` |
| Claude API (Anthropic) | Optional high-quality paper summarization | `ANTHROPIC_API_KEY`, `CLAUDE_MODEL` |
| OpenAI GPT-4o | Optional fallback reasoning | `OPENAI_API_KEY`, `GPT_MODEL` |

---

## HuggingFace Models in Use

| Model ID | Purpose | Link |
|---|---|---|
| `Qwen/Qwen2.5-Coder-7B-Instruct` | Primary local SLM for code generation | https://huggingface.co/Qwen/Qwen2.5-Coder-7B-Instruct |
| `deepseek-ai/deepseek-coder-7b-instruct-v1.5` | Fallback code SLM | https://huggingface.co/deepseek-ai/deepseek-coder-7b-instruct-v1.5 |
| `sentence-transformers/all-MiniLM-L6-v2` | Paper & lesson embedding for FAISS index | https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2 |
| `microsoft/codebert-base` | Code similarity scoring in reward engine | https://huggingface.co/microsoft/codebert-base |

---

## Current Active Development Tasks

- [ ] Set up project skeleton and Docker-based dev environment
- [ ] Implement crawl4ai multi-source ingestion pipeline (arXiv, GitHub Trending, Medium)
- [ ] Build Docker sandbox executor with timeout and resource limits
- [ ] Implement benchmark harness for throughput/latency measurement
- [ ] Design RL environment (state, action, reward) with Stable-Baselines3 PPO
- [ ] Integrate Ollama local SLM for code generation from paper summaries
- [ ] Build FAISS-backed lesson knowledge base
- [ ] Implement LoRA fine-tuning pipeline with PEFT + trl
- [ ] Build APScheduler-based daily orchestration loop
- [ ] Write integration tests and RL training smoke tests

---

## Related Files
- `PROJECT-detail.md` — Full technical specification and architecture
- `PROJECT-DEVELOPMENT-PHASE-TRACKING.md` — Phase-by-phase development roadmap
- `SECOND-KNOWLEDGE-BRAIN.md` — Research papers, SOTA models, self-update protocol
