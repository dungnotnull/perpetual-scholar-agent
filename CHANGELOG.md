# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- RL training pipeline integration
- LoRA fine-tuning automation
- Multi-domain support
- Web-based monitoring dashboard
- Collaborative knowledge sharing

## [0.1.0] - 2025-01-09

### Added

#### Core Infrastructure
- Initial project structure and architecture
- Docker-based development environment
- SQLite database for knowledge storage
- FAISS vector index for semantic search
- APScheduler for task orchestration
- Redis for event bus (optional)

#### Knowledge Ingestion
- crawl4ai multi-source crawler
- arXiv API integration for academic papers
- GitHub Trending API integration
- Medium/Dev.to RSS feed parsing
- Paper metadata extraction and storage
- Content deduplication and filtering

#### Reasoning Engine
- Ollama local SLM integration
- Qwen2.5-Coder-7B-Instruct support
- DeepSeek-Coder-7B fallback support
- Prompt templates for code generation
- Paper summarization pipeline
- LLM provider abstraction layer

#### Sandbox Environment
- Docker SDK integration for container management
- Ephemeral container creation and cleanup
- Resource limits (CPU: 2 cores, RAM: 4GB)
- Execution timeout enforcement (300s)
- Network isolation controls
- Filesystem sandboxing

#### Reward Engine
- pytest-benchmark integration
- Performance metric collection (throughput, latency)
- Baseline comparison logic
- Reward calculation: `(new_metric - baseline) / baseline`
- CodeBERT-based code similarity scoring
- Benchmark result storage

#### RL Loop
- Stable-Baselines3 PPO integration
- Action space definition: {fetch_paper, generate_code, run_benchmark, store_lesson, skip}
- State representation: (paper_embedding, baseline_score, sandbox_available)
- Policy network training infrastructure
- Experience replay buffer
- Training checkpoint management

#### Self-Improvement
- HuggingFace PEFT integration
- LoRA fine-tuning pipeline
- trl library for RLHF-style training
- Lesson extraction and validation
- Verified lesson buffer (≥50 entries trigger fine-tuning)
- Model versioning and rollback

#### Knowledge Storage
- SQLite database for structured data
- JSON storage for lessons and experiments
- FAISS index for vector search
- sentence-transformers embedding model (all-MiniLM-L6-v2)
- Lesson deduplication
- Semantic similarity search

#### Orchestration
- APScheduler-based daily tasks
- Configurable task intervals
- Event bus for component communication
- Task priority management
- Failure recovery and retry logic

#### Development Tools
- pytest-based testing framework
- Integration test suite
- Docker Compose for local development
- Environment variable configuration
- Logging infrastructure
- Git hooks for code quality

#### Documentation
- Comprehensive README.md
- Architecture documentation (PROJECT-detail.md)
- Phase tracking (PROJECT-DEVELOPMENT-PHASE-TRACKING.md)
- Research knowledge base (SECOND-KNOWLEDGE-BRAIN.md)
- API documentation
- Development setup guide

#### Production Readiness
- MIT License
- CODE_OF_CONDUCT.md (Contributor Covenant v2.1)
- CONTRIBUTING.md (contributor guidelines)
- SECURITY.md (security policy)
- CHANGELOG.md (this file)
- ISSUE_TEMPLATE.md (bug report template)
- PULL_REQUEST_TEMPLATE.md (PR template)
- SUPPORT.md (support documentation)

### Configuration

#### Environment Variables
- `DOMAIN_FOCUS`: Technical domain to focus on (default: backend-performance)
- `OLLAMA_BASE_URL`: Ollama server URL (default: http://localhost:11434)
- `OLLAMA_MODEL`: Primary model (default: Qwen/Qwen2.5-Coder-7B-Instruct)
- `ANTHROPIC_API_KEY`: Optional Claude API key
- `OPENAI_API_KEY`: Optional GPT-4o API key
- `DOCKER_CPU_LIMIT`: Sandbox CPU limit (default: 2)
- `DOCKER_MEMORY_LIMIT`: Sandbox memory limit (default: 4g)
- `SANDBOX_TIMEOUT`: Execution timeout in seconds (default: 300)
- `LORA_BUFFER_SIZE`: Lessons before fine-tuning (default: 50)
- `LORA_CADENCE_DAYS`: Days between fine-tuning cycles (default: 7)

#### Docker Services
- `perpetual-scholar-agent`: Main application container
- `ollama`: Local SLM service
- `redis`: Event bus (optional)
- `postgres`: Database (optional, SQLite default)

### Dependencies

#### Python Libraries
- `crawl4ai`: Web crawling and content extraction
- `arxiv`: arXiv API client
- `PyGithub`: GitHub API client
- `feedparser`: RSS/Atom feed parsing
- `ollama`: Ollama Python client
- `anthropic`: Claude API client
- `openai`: OpenAI API client
- `docker`: Docker SDK for Python
- `pytest-benchmark`: Benchmarking framework
- `hyperfine`: External benchmark runner
- `sentence-transformers`: Text embedding models
- `faiss-cpu`: Vector similarity search
- `stable-baselines3`: RL algorithms
- `peft`: Parameter-Efficient Fine-Tuning
- `trl`: Transformer Reinforcement Learning
- `APScheduler`: Task scheduling
- `redis`: Redis client (optional)

#### HuggingFace Models
- `Qwen/Qwen2.5-Coder-7B-Instruct`: Primary code SLM
- `deepseek-ai/deepseek-coder-7b-instruct-v1.5`: Fallback code SLM
- `sentence-transformers/all-MiniLM-L6-v2`: Embedding model
- `microsoft/codebert-base`: Code similarity model

### Performance

#### Benchmarks
- Paper ingestion: ~100 papers/hour
- Code generation: 10-30 seconds per solution
- Benchmark execution: 1-5 minutes per experiment
- LoRA fine-tuning: 2-4 hours on consumer GPU
- Vector search: <100ms per query

#### Resource Usage
- Idle: 2GB RAM, 0.1 CPU
- Active ingestion: 4GB RAM, 1 CPU
- Benchmark execution: 6GB RAM, 2 CPU
- Fine-tuning: 8GB RAM, 1 GPU (recommended)

### Known Issues

#### Current Limitations
- Single-threaded paper ingestion
- No GPU acceleration for embedding
- Manual database migration required
- Limited error recovery in RL training
- No web UI (CLI only)
- No multi-agent collaboration

#### Planned Fixes
- Multi-process ingestion pipeline
- GPU-accelerated FAISS index
- Automated database migrations
- Robust RL training recovery
- Web-based monitoring dashboard
- Multi-agent knowledge sharing

### Migration Notes

#### From Development to v0.1.0
No breaking changes from initial development setup.

### Security

#### Vulnerability Reporting
See SECURITY.md for vulnerability reporting process.

#### Security Features
- Docker sandbox isolation
- No user data collection
- Ephemeral data handling
- API key protection
- Network isolation controls

### Deprecations

None in this release.

### Contributors

- Initial development by Perpetual Scholar Agent team
- Community contributors (see CONTRIBUTORS.md)

### Links

- Repository: [GitHub](https://github.com/your-org/perpetual-scholar-agent)
- Documentation: [Project Wiki](https://github.com/your-org/perpetual-scholar-agent/wiki)
- Issues: [GitHub Issues](https://github.com/your-org/perpetual-scholar-agent/issues)
- Discussions: [GitHub Discussions](https://github.com/your-org/perpetual-scholar-agent/discussions)

---

## Version Format

- **MAJOR**: Breaking changes or major milestones
- **MINOR**: New features, backward compatible
- **PATCH**: Bug fixes, backward compatible

## Release Cadence

- **Major releases**: Every 6-12 months
- **Minor releases**: Every 1-3 months
- **Patch releases**: As needed (bug fixes)

## Future Roadmap

### v0.2.0 (Q2 2025)
- Multi-domain support
- GPU-accelerated processing
- Web-based monitoring dashboard
- Improved RL algorithms

### v0.3.0 (Q3 2025)
- Multi-agent collaboration
- Cloud deployment support
- Advanced fine-tuning techniques
- Performance optimization

### v1.0.0 (Q4 2025)
- Production-ready stability
- Comprehensive testing suite
- Full documentation
- Security audit complete
