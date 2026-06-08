# SECOND-KNOWLEDGE-BRAIN.md — perpetual-scholar-agent

> This file is both a static foundation and a living document. The static sections below were written during project initialization. The **Knowledge Update Log** at the bottom is appended automatically by the agent's weekly brain-update job.

---

## Core Concepts & Theoretical Foundations

### Reinforcement Learning for Code Generation

RL-driven code evolution treats the act of writing and testing code as a Markov Decision Process (MDP). The agent occupies a *state* (a representation of the current knowledge context and available resources), selects an *action* (e.g., generate code for this technique), and receives a *reward* based on the empirical outcome (benchmark improvement). The policy — which action to take from each state — is optimized over time to maximize cumulative reward.

**Key concepts**:
- **Proximal Policy Optimization (PPO)**: A policy-gradient algorithm that limits the size of each policy update to prevent catastrophic forgetting. Essential for this agent because the environment distribution shifts as the paper queue changes daily.
- **Q-Learning**: Tabular RL algorithm suitable for discrete, low-dimensional state spaces. Useful as a lightweight alternative to PPO for early experiments.
- **Exploration vs. Exploitation**: The agent must balance trying new paper types (exploration) against repeating techniques it knows to be high-reward (exploitation). Epsilon-greedy or UCB exploration strategies manage this.
- **Curriculum Learning**: Ordering experiences from simple to complex accelerates learning. For this agent, this means prioritizing well-known benchmark domains (sorting, hashing) before obscure distributed systems papers.

### Parameter-Efficient Fine-Tuning (PEFT)

Full fine-tuning of a 7B-parameter model requires 14+ GB VRAM and hours of compute. PEFT methods, particularly **LoRA (Low-Rank Adaptation)**, dramatically reduce these requirements by freezing the base model weights and training only small rank-decomposition matrices inserted into attention layers.

**LoRA mechanics**: For a weight matrix W ∈ ℝ^(d×k), LoRA adds ΔW = BA where B ∈ ℝ^(d×r) and A ∈ ℝ^(r×k), with r << min(d,k). Only A and B are trained. For a 7B model with r=16, this reduces trainable parameters by ~100×.

**Key concepts**:
- **Rank r**: Controls adapter capacity. r=8 for narrow tasks, r=16–32 for broader knowledge.
- **Alpha scaling**: `alpha/r` scales the LoRA update. Common: alpha=2r.
- **Target modules**: Typically q_proj, v_proj (query/value projections) in each transformer layer.

### Empirical Benchmark Methodology

A benchmark is only valid if it measures what it claims to measure and is reproducible. Key principles:
- **Warmup runs**: Discard first N iterations to eliminate JIT compilation and cache cold-start effects.
- **Statistical significance**: Report median + IQR rather than mean + std; microbenchmarks have right-skewed distributions.
- **Isolation**: Disable CPU frequency scaling, close background processes, run in Docker with pinned CPUs.
- **Metric selection**: Throughput (ops/s) for batch workloads; p50/p99 latency for request-response systems.

### Self-Improving Agent Architectures

**Reflexion (Shinn et al., 2023)**: Agents that verbally reflect on task failures and store reflections in episodic memory. The perpetual-scholar-agent generalizes this: instead of verbal reflection, it stores empirical benchmark failures as negative examples to avoid in future LoRA training.

**Constitutional AI (Anthropic, 2022)**: Self-critique loop where a model evaluates its own outputs against a set of principles before finalizing. The LLM judge component in this project is an adaptation of this idea.

---

## Key Research Papers

| Title | Authors | Year | Venue | Link | Relevance |
|---|---|---|---|---|---|
| Proximal Policy Optimization Algorithms | Schulman et al. | 2017 | arXiv | https://arxiv.org/abs/1707.06347 | Core RL algorithm used for policy optimization |
| LoRA: Low-Rank Adaptation of Large Language Models | Hu et al. | 2021 | ICLR 2022 | https://arxiv.org/abs/2106.09685 | Foundation for the LoRA fine-tuning loop |
| Reflexion: Language Agents with Verbal Reinforcement Learning | Shinn et al. | 2023 | NeurIPS 2023 | https://arxiv.org/abs/2303.11366 | Inspiration for failure-driven self-improvement |
| CodeRL: Mastering Code Generation through Pretrained Models and Deep Reinforcement Learning | Le et al. | 2022 | NeurIPS 2022 | https://arxiv.org/abs/2207.01780 | RL applied directly to code generation quality |
| Execution-Based Code Generation using Deep Reinforcement Learning | Shojaee et al. | 2023 | TMLR | https://arxiv.org/abs/2301.13816 | Reward from code execution results — directly applicable |
| AlphaCode: Competition-Level Code Generation with Large Language Models | Li et al. | 2022 | Science | https://arxiv.org/abs/2203.07814 | Large-scale code generation; sampling + filtering strategy applicable to sandbox runs |
| Self-Play Fine-Tuning Converts Weak Language Models to Strong Language Models | Chen et al. | 2024 | ICML 2024 | https://arxiv.org/abs/2401.01335 | Self-play RLHF loop applicable to agent's self-improvement cycle |
| QLoRA: Efficient Finetuning of Quantized LLMs | Dettmers et al. | 2023 | NeurIPS 2023 | https://arxiv.org/abs/2305.14314 | 4-bit quantized LoRA — reduces VRAM requirement for fine-tuning the local SLM |
| Curriculum Learning for Language Models | Xu et al. | 2020 | arXiv | https://arxiv.org/abs/2108.02170 | Curriculum strategies for ordering training examples |
| Constitutional AI: Harmlessness from AI Feedback | Bai et al. | 2022 | arXiv | https://arxiv.org/abs/2212.08073 | Basis for LLM-judge secondary reward signal |
| Voyager: An Open-Ended Embodied Agent with Large Language Models | Wang et al. | 2023 | arXiv | https://arxiv.org/abs/2305.16291 | LLM agent that continuously acquires new skills via code execution — strongest conceptual parallel |
| SWE-bench: Can Language Models Resolve Real-World GitHub Issues? | Jimenez et al. | 2024 | ICLR 2024 | https://arxiv.org/abs/2310.06770 | Benchmark methodology for code agents |

---

## State-of-the-Art ML/DL Models

| Model | HuggingFace ID | Benchmark | Notes |
|---|---|---|---|
| Qwen2.5-Coder-7B-Instruct | `Qwen/Qwen2.5-Coder-7B-Instruct` | HumanEval 88.4% | Best 7B code model as of late 2024; default SLM |
| DeepSeek-Coder-V2-Lite-Instruct | `deepseek-ai/DeepSeek-Coder-V2-Lite-Instruct` | HumanEval 81.1% | 16B MoE with 2.4B active params; strong alternative |
| CodeLlama-7b-Instruct | `codellama/CodeLlama-7b-Instruct-hf` | HumanEval 34.8% | Older but well-understood; useful as baseline |
| StarCoder2-7b | `bigcode/starcoder2-7b` | HumanEval 35.4% | Apache 2.0 license; trained on The Stack |
| all-MiniLM-L6-v2 | `sentence-transformers/all-MiniLM-L6-v2` | SBERT benchmarks | 384-dim, fast, good for semantic similarity |
| CodeBERT-base | `microsoft/codebert-base` | CodeSearchNet | Used for code similarity scoring in reward engine |
| nomic-embed-code | `nomic-ai/nomic-embed-code` | CoIR benchmark | New (2024); purpose-built code embedding model |

**Papers with Code leaderboards to monitor**:
- https://paperswithcode.com/task/code-generation (HumanEval, MBPP, SWE-bench)
- https://paperswithcode.com/task/code-completion

---

## Tools, Libraries & Frameworks

| Tool | GitHub | Version | Use Case |
|---|---|---|---|
| crawl4ai | https://github.com/unclecode/crawl4ai | ^0.4 | Multi-source web crawler for research paper discovery |
| arxiv-py | https://github.com/lukasschwab/arxiv.py | ^2.1 | arXiv API client — structured paper metadata |
| PyGithub | https://github.com/PyGithub/PyGithub | ^2.3 | GitHub Trending and repo README fetching |
| Docker SDK for Python | https://docker-py.readthedocs.io | ^7.0 | Programmatic Docker container lifecycle management |
| Stable-Baselines3 | https://github.com/DLR-RM/stable-baselines3 | ^2.3 | PPO implementation; well-tested, clean API |
| Gymnasium | https://github.com/Farama-Foundation/Gymnasium | ^0.29 | OpenAI Gym successor; defines RL environment interface |
| Hugging Face PEFT | https://github.com/huggingface/peft | ^0.11 | LoRA adapter training |
| trl (Transformer RL) | https://github.com/huggingface/trl | ^0.9 | SFTTrainer for supervised fine-tuning |
| FAISS | https://github.com/facebookresearch/faiss | ^1.8 | Billion-scale vector similarity search |
| sentence-transformers | https://www.sbert.net | ^3.0 | Easy embedding generation |
| pytest-benchmark | https://pytest-benchmark.readthedocs.io | ^4.0 | Statistical microbenchmarking inside Docker sandboxes |
| hyperfine | https://github.com/sharkdp/hyperfine | latest | CLI benchmarking tool for system-level commands |
| APScheduler | https://apscheduler.readthedocs.io | ^3.10 | In-process cron scheduler for daily/weekly jobs |
| structlog | https://www.structlog.org | ^24.1 | Structured JSON logging |
| tenacity | https://tenacity.readthedocs.io | ^8.3 | Retry logic with exponential backoff |
| Prometheus client | https://github.com/prometheus/client_python | ^0.20 | Metrics exposition endpoint |

---

## Self-Update Protocol

### Overview

The agent automatically updates this file's **Knowledge Update Log** section weekly, using the lesson reporter component (`reporting/brain_updater.py`). The ingestion pipeline also continuously crawls new papers and populates the SQLite lesson store.

### Target Sources

| Source | Type | Crawl4ai Config | arXiv Categories |
|---|---|---|---|
| arXiv | Academic papers | `AsyncWebCrawler` with arXiv Atom feed | cs.DB, cs.DC, cs.PF, cs.LG, cs.SE |
| Papers with Code | Model benchmarks | RSS feed at https://paperswithcode.com/latest | N/A (scraped) |
| GitHub Trending | Code repositories | GitHub REST API — trending/{language} | N/A |
| Medium Engineering blogs | Technical articles | crawl4ai RSS scraper | N/A |
| Hacker News | Discussion + links | HN Algolia API (top stories, tag: performance) | N/A |
| HuggingFace Papers | Daily paper digest | https://huggingface.co/papers RSS | N/A |

### Domain-Specific Search Queries

**For default domain: Backend Performance Optimization**
```
arxiv queries:
  - "database query optimization reinforcement learning"
  - "cache eviction policy machine learning"
  - "async I/O performance benchmark"
  - "distributed systems consensus latency"
  - "B-tree vs LSM-tree write amplification"

GitHub search:
  - "language:python topic:performance-optimization stars:>100"
  - "language:go topic:high-performance stars:>100"

HN search:
  - "performance" AND ("latency" OR "throughput") in last 7 days
```

### Configuring a Different Domain

Set `DOMAIN_FOCUS` env var to a natural-language description of the desired domain:
```
DOMAIN_FOCUS="machine learning model inference optimization and quantization"
```
The agent will embed this string and use cosine similarity to prioritize ingested papers.

### Update Frequency

- **Ingestion pipeline**: daily at 02:00 UTC (fetches last 24h of papers)
- **SECOND-KNOWLEDGE-BRAIN.md update**: weekly on Sunday at 06:00 UTC
- **LoRA fine-tuning**: triggered when ≥50 new verified lessons accumulate, or every 7 days

### Format for New Entries (Knowledge Update Log)

```markdown
### [YYYY-MM-DD] Week N Update

**New Lessons Verified**: {count}
**Top Technique This Week**: {technique_name} (reward: {reward:.2f})
**Paper Source**: {paper_title} — {paper_url}
**Benchmark Result**: {baseline_metric} → {new_metric} (+{pct:.1f}%)
**Summary**: {one_sentence_summary}
```

---

## Knowledge Update Log

> Entries below are appended automatically by `reporting/brain_updater.py`. Do not edit manually.

### [2026-06-03] Initial Entry — Project Initialization

**Status**: Knowledge base initialized. No experiments run yet.
**Next update**: After first successful experiment cycle completes.
**Action**: Begin Phase 0 environment setup.
