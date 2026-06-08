# Production Readiness & Open Source Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Transform the project from feature-complete codebase to production-ready open-source project with licensing, CI/CD, code quality enforcement, comprehensive documentation, and full test coverage (with mocked model execution).

**Architecture:** Add 9 configuration/documentation files to existing codebase: LICENSE, CODE_OF_CONDUCT.md, CONTRIBUTING.md, SECURITY.md, CHANGELOG.md, .github/workflows/ci.yml, .pre-commit-config.yaml, docs/DEPLOYMENT.md, docs/TESTING.md. Initialize git repository. All model-dependent operations (LLM calls, RL training, LoRA fine-tuning) will be mocked to save resources.

**Tech Stack:** MIT License, GitHub Actions, Ruff (linter/formatter), pre-commit hooks, pytest, pytest-cov, safety

---

## Task 1: Initialize Git Repository

**Files:**
- Create: `.git/` (repository initialization)
- Create: `.gitignore` (update if needed)

- [ ] **Step 1: Initialize git repository**

```bash
git init
```

Expected: "Initialized empty Git repository in D:/perpetual-scholar-agent/.git/"

- [ ] **Step 2: Create .gitignore**

```bash
cat > .gitignore << 'EOF'
# perpetual-scholar-agent

*.pyc
__pycache__/
*.py[cod]
*$py.class
*.so
*.egg-info/
dist/
build/
*.egg

# Virtual environment
.venv/
venv/
ENV/

# IDE
.idea/
.vscode/
*.swp
*.swo

# Environment / secrets
.env
.env.local
.env.*.local

# Data (local SQLite + FAISS)
data/*.db
data/*.faiss
data/*.json
data/reports/

# Models (LoRA adapters + RL checkpoints)
models/lora_adapter_v*/
models/rl_policy/
models/tensorboard/

# Docker volumes
docker/volumes/

# OS
.DS_Store
Thumbs.db

# Logs
*.log
logs/

# Test artifacts
.pytest_cache/
htmlcov/
.coverage
coverage.xml

# Jupyter
.ipynb_checkpoints/

# Claude
.claude/
EOF
```

- [ ] **Step 3: Stage all existing files**

```bash
git add .
```

- [ ] **Step 4: Create initial commit**

```bash
git commit -m "Initial commit: perpetual-scholar-agent v0.1.0"
```

Expected: Commit created with SHA hash

---

## Task 2: Add LICENSE (MIT)

**Files:**
- Create: `LICENSE`

- [ ] **Step 1: Write LICENSE file**

```bash
cat > LICENSE << 'EOF'
MIT License

Copyright (c) 2025 perpetual-scholar-agent contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
EOF
```

- [ ] **Step 2: Commit LICENSE**

```bash
git add LICENSE
git commit -m "feat: add MIT License"
```

---

## Task 3: Add CODE_OF_CONDUCT.md

**Files:**
- Create: `CODE_OF_CONDUCT.md`

- [ ] **Step 1: Write CODE_OF_CONDUCT.md**

```bash
cat > CODE_OF_CONDUCT.md << 'EOF'
# Contributor Covenant Code of Conduct

## Our Pledge

We as members, contributors, and leaders pledge to make participation in our
community a harassment-free experience for everyone, regardless of age, body
size, visible or invisible disability, ethnicity, sex characteristics, gender
identity and expression, level of experience, education, socio-economic status,
nationality, personal appearance, race, religion, or sexual identity
and orientation.

We pledge to act and interact in ways that contribute to an open, welcoming,
diverse, inclusive, and healthy community.

## Our Standards

Examples of behavior that contributes to a positive environment for our
community include:

* Demonstrating empathy and kindness toward other people
* Being respectful of differing opinions, viewpoints, and experiences
* Giving and gracefully accepting constructive feedback
* Accepting responsibility and apologizing to those affected by our mistakes,
  and learning from the experience
* Focusing on what is best not just for us as individuals, but for the
  overall community

Examples of unacceptable behavior include:

* The use of sexualized language or imagery, and sexual attention or
  advances of any kind
* Trolling, insulting or derogatory comments, and personal or political attacks
* Public or private harassment
* Publishing others' private information, such as a physical or email address,
  without their explicit permission
* Other conduct which could reasonably be considered inappropriate in a
  professional setting

## Enforcement Responsibilities

Community leaders are responsible for clarifying and enforcing our standards of
acceptable behavior and will take appropriate and fair corrective action in
response to any behavior that they deem inappropriate, threatening, offensive,
or harmful.

Community leaders have the right and responsibility to remove, edit, or reject
comments, commits, code, wiki edits, issues, and other contributions that are
not aligned to this Code of Conduct, and will communicate reasons for moderation
decisions when appropriate.

## Scope

This Code of Conduct applies within all community spaces, and also applies when
an individual is officially representing the community in public spaces.
Examples of representing our community include using an official e-mail address,
posting via an official social media account, or acting as an appointed
representative at an online or offline event.

## Enforcement

Instances of abusive, harassing, or otherwise unacceptable behavior may be
reported to the community leaders responsible for enforcement at
[INSERT CONTACT METHOD].

All complaints will be reviewed and investigated promptly and fairly.

All community leaders are obligated to respect the privacy and security of
the reporter of any incident.

## Attribution

This Code of Conduct is adapted from the [Contributor Covenant][homepage],
version 2.1, available at
https://www.contributor-covenant.org/version/2/1/code_of_conduct.html.

Community Impact Guidelines were inspired by
[Mozilla's code of conduct enforcement ladder][Mozilla CoC].

For answers to common questions about this code of conduct, see the FAQ at
https://www.contributor-covenant.org/faq. Translations are available at
https://www.contributor-covenant.org/translations.

[homepage]: https://www.contributor-covenant.org
[Mozilla CoC]: https://github.com mozilla/diversity
EOF
```

- [ ] **Step 2: Commit CODE_OF_CONDUCT.md**

```bash
git add CODE_OF_CONDUCT.md
git commit -m "docs: add Contributor Covenant Code of Conduct v2.1"
```

---

## Task 4: Add CONTRIBUTING.md

**Files:**
- Create: `CONTRIBUTING.md`

- [ ] **Step 1: Write CONTRIBUTING.md**

```bash
cat > CONTRIBUTING.md << 'EOF'
# Contributing to perpetual-scholar-agent

Thank you for your interest in contributing! This document provides guidelines
for contributing to the project.

## Getting Started

### Prerequisites

- Python 3.11 or higher
- Docker Desktop (for sandbox execution)
- Ollama with Qwen2.5-Coder-7B-Instruct model (optional, can use mocked mode)
- Git

### Development Setup

1. Clone the repository:
```bash
git clone https://github.com/your-org/perpetual-scholar-agent.git
cd perpetual-scholar-agent
```

2. Create a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

4. Install pre-commit hooks:
```bash
pre-commit install
```

5. Copy environment configuration:
```bash
cp .env.example .env
# Edit .env with your configuration
```

6. Initialize the database:
```bash
python -m agent init
```

## Development Workflow

### Branching

- `main` — Production branch
- `develop` — Development branch (if applicable)
- `feature/your-feature-name` — Feature branches
- `fix/your-bug-fix` — Bug fix branches
- `docs/your-documentation` — Documentation changes

### Making Changes

1. Create a feature branch:
```bash
git checkout -b feature/your-feature-name
```

2. Make your changes with pre-commit hooks:
```bash
# Pre-commit hooks will run automatically on commit
git add .
git commit -m "feat: add your feature description"
```

3. Push to your fork:
```bash
git push origin feature/your-feature-name
```

4. Create a Pull Request on GitHub

### Commit Message Convention

Use conventional commits:

- `feat:` — New feature
- `fix:` — Bug fix
- `docs:` — Documentation changes
- `test:` — Adding or updating tests
- `refactor:` — Code refactoring
- `style:` — Code style changes (formatting, etc.)
- `chore:` — Maintenance tasks

Examples:
```
feat: add support for GitHub Trending ingestion
fix: resolve Docker container cleanup issue
docs: update deployment guide for systemd
test: add integration tests for RL environment
```

## Code Style

We use [Ruff](https://docs.astral.sh/ruff/) for linting and formatting.

### Configuration

Ruff is configured in `pyproject.toml`. Key settings:
- Line length: 100 characters
- Python version: 3.11+
- Enable all rules by default, select specific exclusions

### Running Manually

```bash
# Check linting
ruff check .

# Format code
ruff format .

# Fix auto-fixable issues
ruff check --fix .
```

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=agent --cov-report=html

# Run specific test file
pytest tests/test_something.py

# Run with verbose output
pytest -v
```

### Coverage Requirements

- Minimum coverage: 80%
- Goal coverage: 90%
- Critical paths: 100%

New features must include tests with at least 80% coverage for the changed code.

### Test Organization

- `tests/unit/` — Unit tests for individual functions/classes
- `tests/integration/` — Integration tests for component interactions
- `tests/e2e/` — End-to-end tests for full workflows

### Mocking

Model-dependent operations (LLM calls, Docker execution, RL training) are mocked by default using `pytest fixtures` and `unittest.mock`.

## Pull Request Guidelines

### Before Submitting

1. **Code quality:**
   - All tests pass: `pytest`
   - Coverage meets minimum: `pytest --cov=agent`
   - Linting passes: `ruff check .`
   - Formatting applied: `ruff format .`

2. **Documentation:**
   - Update relevant documentation
   - Add docstrings to new functions/classes
   - Update CHANGELOG.md for user-facing changes

3. **Commits:**
   - Clean commit history (squash WIP commits)
   - Conventional commit messages
   - No merge commits

### Pull Request Template

When creating a PR, use this template:

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Tests added/updated
- [ ] All tests pass
- [ ] Coverage meets requirements

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] CHANGELOG.md updated (if applicable)
- [ ] No merge conflicts
```

## Getting Help

- GitHub Issues: Report bugs and request features
- GitHub Discussions: Ask questions and discuss ideas
- Documentation: Check `docs/` directory

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
EOF
```

- [ ] **Step 2: Commit CONTRIBUTING.md**

```bash
git add CONTRIBUTING.md
git commit -m "docs: add contributor guidelines"
```

---

## Task 5: Add SECURITY.md

**Files:**
- Create: `SECURITY.md`

- [ ] **Step 1: Write SECURITY.md**

```bash
cat > SECURITY.md << 'EOF'
# Security Policy

## Supported Versions

Currently, only the latest version of perpetual-scholar-agent is supported with
security updates.

| Version | Supported          |
|---------|--------------------|
| 0.1.x   | :white_check_mark: |

## Reporting a Vulnerability

If you discover a security vulnerability, please report it responsibly.

### How to Report

**Do NOT** create a public GitHub issue for security vulnerabilities.

Instead, send an email to: **security@perpetual-scholar-agent.org**

Replace with your actual security contact email.

### What to Include

Please include:
- Description of the vulnerability
- Steps to reproduce the issue
- Potential impact of the vulnerability
- Any suggested mitigations (if known)

### Response Timeline

- **Acknowledgment:** Within 48 hours
- **Initial Assessment:** Within 7 days
- **Resolution:** As soon as practicable based on severity

### Disclosure Process

1. Report is received and acknowledged
2. Team investigates and validates the issue
3. Fix is developed and tested
4. Security advisory is published
5. Fixed version is released
6. Coordinated public disclosure (if applicable)

## Security Best Practices

When deploying perpetual-scholar-agent in production:

1. **Environment Variables:** Never commit `.env` files or secrets
2. **Docker Security:** Keep base images updated, run containers as non-root
3. **Network Isolation:** Run the agent in isolated network environments
4. **Sandbox Execution:** The agent uses Docker sandboxes - ensure proper resource limits
5. **LLM API Keys:** Rotate API keys regularly, use key management services
6. **Monitoring:** Enable Prometheus metrics and monitor for anomalies
7. **Updates:** Keep dependencies updated for security patches

## Dependency Security

We use automated security scanning via CI/CD:
- `safety` checks for known vulnerabilities in dependencies
- GitHub Actions Dependabot (to be enabled)
- Regular dependency updates

## Private Key Handling

The agent may handle:
- LLM API keys (OpenAI, Anthropic)
- GitHub tokens for repo access
- Database credentials

These should:
- Never be committed to version control
- Be stored as environment variables
- Be rotated periodically
- Have minimal required permissions

## Security Audits

This project has not undergone a formal security audit. We welcome security
research and responsible disclosure.

## Contact

For security-related questions not related to vulnerabilities:
- Open a GitHub Discussion with the "security" tag
- Email: security@perpetual-scholar-agent.org
EOF
```

- [ ] **Step 2: Commit SECURITY.md**

```bash
git add SECURITY.md
git commit -m "docs: add security policy and vulnerability reporting"
```

---

## Task 6: Add CHANGELOG.md

**Files:**
- Create: `CHANGELOG.md`

- [ ] **Step 1: Write CHANGELOG.md**

```bash
cat > CHANGELOG.md << 'EOF'
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Production-ready open-source infrastructure
- MIT License
- Contributor Covenant Code of Conduct
- GitHub Actions CI/CD pipeline
- Ruff code quality enforcement
- Comprehensive documentation for contributors and operators

## [0.1.0] - 2025-01-08

### Added
- Initial release of perpetual-scholar-agent
- Multi-source knowledge ingestion (arXiv, GitHub Trending, RSS feeds)
- Local SLM integration (Ollama with Qwen2.5-Coder-7B-Instruct)
- Docker sandbox execution with resource limits (2 CPU, 2GB RAM, 60s timeout)
- RL-based paper selection (PPO via Stable-Baselines3)
- LoRA fine-tuning pipeline with QLoRA (r=16, alpha=32, 4-bit quantization)
- FastAPI dashboard with live experiment feed
- Prometheus metrics and monitoring
- Weekly digest reports and auto-updating SECOND-KNOWLEDGE-BRAIN.md
- Pluggable LLM backends (Ollama, Claude API, OpenAI GPT-4o)
- Automatic fine-tuning triggers (50 lessons or 7 days)
- Comprehensive error handling with circuit breakers and retry logic
- Structured JSON logging via structlog

### Infrastructure
- Docker Compose stack (agent, Ollama, Redis, Prometheus, Grafana)
- Systemd service unit for bare-metal deployment
- Multi-stage Dockerfile with health checks
- SQLite schema with 6 tables (experiments, lessons, seen_items, finetune_runs, rl_policy_checkpoints, metrics_history)
- FAISS vector index for lesson embeddings
- APScheduler for orchestration

### Documentation
- README.md with architecture diagram and quickstart
- PROJECT-detail.md with full technical specification
- PROJECT-DEVELOPMENT-PHASE-TRACKING.md with phase-by-phase roadmap
- SECOND-KNOWLEDGE-BRAIN.md for research findings
- CONTRIBUTING.md with contributor guidelines
- SECURITY.md with vulnerability reporting
- CODE_OF_CONDUCT.md with community standards

### Dependencies
- Python 3.11+
- PyTorch 2.3+, Transformers 4.42+, PEFT 0.11+, trl 0.9+
- Stable-Baselines3 2.3+ with Gymnasium 0.29+
- sentence-transformers 3.0+ with FAISS 1.8+
- FastAPI 0.111+ with Uvicorn 0.30+
- Docker SDK 7.0+
- crawl4ai 0.4+, arxiv 2.1+, PyGithub 2.3+
- aiosqlite 0.20+, APScheduler 3.10+
- structlog 24.1+, tenacity 8.3+
- Optional: Anthropic 0.29+, OpenAI 1.35+

[Unreleased]: https://github.com/your-org/perpetual-scholar-agent/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/your-org/perpetual-scholar-agent/releases/tag/v0.1.0
EOF
```

- [ ] **Step 2: Commit CHANGELOG.md**

```bash
git add CHANGELOG.md
git commit -m "docs: add changelog with v0.1.0 release notes"
```

---

## Task 7: Add GitHub Actions CI/CD

**Files:**
- Create: `.github/workflows/ci.yml`
- Modify: `requirements.txt` (add dev dependencies)

- [ ] **Step 1: Create .github/workflows directory**

```bash
mkdir -p .github/workflows
```

- [ ] **Step 2: Write CI/CD workflow**

```bash
cat > .github/workflows/ci.yml << 'EOF'
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
  workflow_dispatch:

jobs:
  lint:
    name: Lint
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: 'pip'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install ruff

      - name: Run Ruff
        run: |
          ruff check .
          ruff format --check .

  test:
    name: Test
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.11', '3.12']
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
          cache: 'pip'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt

      - name: Install test dependencies
        run: |
          pip install pytest pytest-cov pytest-benchmark pytest-asyncio

      - name: Run tests with coverage
        run: |
          pytest --cov=agent --cov-report=xml --cov-report=term

      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v4
        with:
          file: ./coverage.xml
          flags: unittests
          name: codecov-umbrella
          fail_ci_if_error: false

  security:
    name: Security
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: 'pip'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install safety

      - name: Run safety check
        run: |
          safety check --json
        continue-on-error: true
EOF
```

- [ ] **Step 3: Create requirements-dev.txt**

```bash
cat > requirements-dev.txt << 'EOF'
# Development dependencies
-r requirements.txt

# Testing
pytest>=8.2
pytest-cov>=5.0
pytest-benchmark>=4.0
pytest-asyncio>=0.23
pytest-mock>=3.14

# Code quality
ruff>=0.6.0

# Pre-commit
pre-commit>=3.8

# Security
safety>=3.2

# Type checking (optional)
mypy>=1.11
types-requests>=2.32.0
EOF
```

- [ ] **Step 4: Update pyproject.toml with Ruff config**

```bash
cat > pyproject.toml << 'EOF'
[tool.poetry]
name = "perpetual-scholar-agent"
version = "0.1.0"
description = "An autonomous 24/7 self-evolving agent that masters a specialized technical domain through continuous research, sandbox experimentation, and reinforcement-learning-driven self-improvement"
authors = ["perpetual-scholar-agent"]
readme = "README.md"
packages = [{include = "agent"}]

[tool.poetry.dependencies]
python = "^3.11"
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
faiss-cpu = "^1.8"
aiosqlite = "^0.20"
apscheduler = "^3.10"
fastapi = "^0.111"
uvicorn = "^0.30"
pydantic-settings = "^2.3"
python-dotenv = "^1.0"
httpx = "^0.27"
anthropic = "^0.29"
openai = "^1.35"
structlog = "^24.1"
tenacity = "^8.3"
prometheus-client = "^0.20"
gymnasium = "^0.29"

[tool.poetry.group.dev.dependencies]
pytest = "^8.2"
pytest-cov = "^5.0"
pytest-benchmark = "^4.0"
pytest-asyncio = "^0.23"
pytest-mock = "^3.14"
ruff = "^0.6.0"
pre-commit = "^3.8"
safety = "^3.2"
mypy = "^1.11"

[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W", "UP"]
ignore = ["E501"]

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
skip-magic-trailing-comma = false

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = "test_*.py"
python_classes = "Test*"
python_functions = "test_*"
addopts = "-v --cov=agent --cov-report=term-missing --cov-report=html"
markers = [
    "unit: Unit tests",
    "integration: Integration tests",
    "e2e: End-to-end tests",
    "slow: Slow-running tests"
]

[tool.coverage.run]
source = ["agent"]
omit = [
    "*/tests/*",
    "*/test_*.py",
]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise AssertionError",
    "raise NotImplementedError",
    "if __name__ == .__main__.:",
    "if TYPE_CHECKING:",
]

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
EOF
```

- [ ] **Step 5: Commit CI/CD configuration**

```bash
git add .github/workflows/ci.yml requirements-dev.txt pyproject.toml
git commit -m "feat: add GitHub Actions CI/CD pipeline with Ruff configuration"
```

---

## Task 8: Add Pre-Commit Hooks

**Files:**
- Create: `.pre-commit-config.yaml`

- [ ] **Step 1: Write .pre-commit-config.yaml**

```bash
cat > .pre-commit-config.yaml << 'EOF'
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.6.0
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format

  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.6.0
    hooks:
      - id: end-of-file-fixer
      - id: trailing-whitespace
      - id: check-added-large-files
        args: [--maxkb=500]
      - id: check-json
      - id: check-yaml
      - id: check-toml
      - id: check-merge-conflict
      - id: debug-statements
EOF
```

- [ ] **Step 2: Commit pre-commit configuration**

```bash
git add .pre-commit-config.yaml
git commit -m "feat: add pre-commit hooks with Ruff"
```

---

## Task 9: Add docs/DEPLOYMENT.md

**Files:**
- Create: `docs/DEPLOYMENT.md`

- [ ] **Step 1: Write docs/DEPLOYMENT.md**

```bash
cat > docs/DEPLOYMENT.md << 'EOF'
# Deployment Guide

This guide covers deploying perpetual-scholar-agent to production environments.

## Prerequisites

### Required

- **Docker:** 20.10+ with Docker Compose v2
- **Python:** 3.11+ (for development/debugging)
- **Ollama:** Latest version with Qwen2.5-Coder-7B-Instruct model
- **Git:** For cloning the repository

### Optional

- **Redis:** For distributed caching (optional, defaults to in-memory)
- **Prometheus:** For metrics collection (included in docker-compose)
- **Grafana:** For metrics visualization (included in docker-compose)

## Quick Start (Docker Compose)

### 1. Clone Repository

```bash
git clone https://github.com/your-org/perpetual-scholar-agent.git
cd perpetual-scholar-agent
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your configuration
```

Key environment variables:

```bash
# LLM Configuration
OLLAMA_BASE_URL=http://ollama:11434
OLLAMA_MODEL=qwen2.5-coder:7b-instruct

# Optional: External LLM APIs
# ANTHROPIC_API_KEY=your-key-here
# OPENAI_API_KEY=your-key-here

# Domain Focus
DOMAIN_FOCUS=backend-performance-optimization

# Sandbox Limits
SANDBOX_CPU_LIMIT=2
SANDBOX_MEMORY_LIMIT=2g
SANDBOX_TIMEOUT_SECONDS=60

# Fine-tuning Trigger
FINETUNE_LESSON_THRESHOLD=50
FINETUNE_TIME_THRESHOLD_DAYS=7
```

### 3. Start Services

```bash
docker compose up -d
```

This starts:
- Agent service (perpetual-scholar-agent)
- Ollama (local SLM)
- Redis (caching, optional)
- Prometheus (metrics)
- Grafana (visualization, optional)

### 4. Initialize the Database

```bash
docker compose exec agent python -m agent init
```

### 5. Start the Scheduler

```bash
docker compose exec agent python -m agent start
```

Or run a single pipeline cycle:

```bash
docker compose exec agent python -m agent run --once
```

### 6. Access Dashboard

Open http://localhost:8000 in your browser.

## Bare Metal Deployment

### System Requirements

- **OS:** Ubuntu 22.04+ or similar Linux distribution
- **CPU:** 4+ cores recommended (2 for agent, 2 for Ollama)
- **RAM:** 8GB+ minimum (4GB for Ollama model, 2GB for agent, 2GB buffer)
- **Storage:** 20GB+ for models, database, and logs

### Installation Steps

#### 1. Install Dependencies

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install -y python3.11 python3.11-venv docker.io docker-compose

# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull the model
ollama pull qwen2.5-coder:7b-instruct
```

#### 2. Create User and Directory

```bash
sudo useradd -r -s /bin/bash perpetual-scholar
sudo mkdir -p /opt/perpetual-scholar-agent
sudo chown perpetual-scholar:perpetual-scholar /opt/perpetual-scholar-agent
```

#### 3. Deploy Application

```bash
# As perpetual-scholar user
cd /opt/perpetual-scholar-agent
git clone https://github.com/your-org/perpetual-scholar-agent.git .
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Configure environment
cp .env.example .env
nano .env  # Edit configuration

# Initialize database
python -m agent init
```

#### 4. Install Systemd Service

```bash
sudo cp psa-agent.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable psa-agent
sudo systemctl start psa-agent
```

#### 5. Check Status

```bash
sudo systemctl status psa-agent
journalctl -u psa-agent -f  # Follow logs
```

## Production Checklist

Before deploying to production:

- [ ] **Environment Variables:** All secrets configured, no defaults
- [ ] **Database:** SQLite database initialized and backed up
- [ ] **LLM Model:** Ollama model pulled and tested
- [ ] **Resource Limits:** Docker/container limits configured appropriately
- [ ] **Monitoring:** Prometheus metrics endpoint accessible
- [ ] **Logging:** Structured logs configured and rotating
- [ ] **Backup Strategy:** Database and models backup plan in place
- [ ] **Security:** Firewall rules configured, TLS enabled for web endpoints
- [ ] **Updates:** Auto-update strategy for dependencies defined

## Monitoring

### Prometheus Metrics

Access metrics at `http://localhost:8000/metrics`

Key metrics to monitor:
- `psa_experiments_total` — Total experiments run
- `psa_experiments_success_total` — Successful experiments
- `psa_experiments_failed_total` — Failed experiments
- `psa_lessons_stored_total` — Total lessons stored
- `psa_finetune_runs_total` — Fine-tuning runs completed

### Grafana Dashboards

1. Access Grafana at http://localhost:3000
2. Default credentials: admin/admin (change on first login)
3. Add Prometheus as data source: http://prometheus:9090
4. Import dashboard from `monitoring/grafana-dashboard.json`

### Log Aggregation

Logs are output in JSON format via structlog. For production:

```bash
# View logs
journalctl -u psa-agent -f

# Export to log aggregation service
journalctl -u psa-agent -o json | tail -f
```

## Backup and Restore

### Database Backup

```bash
# Backup SQLite database
cp data/perpetual_scholar.db data/backups/perpetual_scholar_$(date +%Y%m%d_%H%M%S).db

# Automated backup script
cat > /etc/cron.daily/perpetual-scholar-backup << 'EOF'
#!/bin/bash
cd /opt/perpetual-scholar-agent
tar -czf /opt/backups/perpetual-scholar-$(date +%Y%m%d).tar.gz data/
find /opt/backups -mtime +30 -delete
EOF
chmod +x /etc/cron.daily/perpetual-scholar-backup
```

### Model Backup

```bash
# Backup LoRA adapters
tar -czf backups/lora_adapters_$(date +%Y%m%d).tar.gz models/lora_adapter_v*/

# Backup RL policy checkpoints
tar -czf backups/rl_policy_$(date +%Y%m%d).tar.gz models/rl_policy/
```

### Restore

```bash
# Stop service
sudo systemctl stop psa-agent

# Restore database
cp data/backups/perpetual_scholar_YYYYMMDD_HHMMSS.db data/perpetual_scholar.db

# Start service
sudo systemctl start psa-agent
```

## Troubleshooting

### Agent Won't Start

**Symptom:** Service fails to start or exits immediately

**Check:**
```bash
# Check service status
sudo systemctl status psa-agent

# View logs
journalctl -u psa-agent -n 50

# Common issues:
# - Ollama not running: systemctl status ollama
# - Database not initialized: python -m agent init
# - Port already in use: netstat -tulpn | grep 8000
```

### Ollama Connection Refused

**Symptom:** "Connection refused" errors from LLM backend

**Fix:**
```bash
# Check Ollama status
systemctl status ollama

# Restart Ollama
systemctl restart ollama

# Verify model is available
ollama list

# Pull model if missing
ollama pull qwen2.5-coder:7b-instruct
```

### High Memory Usage

**Symptom:** Agent or Ollama consuming excessive memory

**Fix:**
- Reduce sandbox resource limits in `.env`
- Limit RL checkpoint history: `RL_CHECKPOINT_HISTORY=5`
- Clear old database records: See Database Maintenance

### Experiments Failing

**Symptom:** All experiments failing with sandbox errors

**Check:**
```bash
# Docker daemon running
docker ps

# Sandbox image exists
docker images | grep sandbox

# Rebuild sandbox image if needed
docker build -t psa-sandbox:latest -f docker/sandbox.Dockerfile .
```

## Security Considerations

### Network Isolation

- Run agent in isolated network (Docker network or VLAN)
- Restrict Ollama to localhost only
- Use firewall rules to limit inbound connections

### API Key Management

- Store API keys as environment variables, never in code
- Rotate keys regularly
- Use secret management services (HashiCorp Vault, AWS Secrets Manager)

### Container Security

```bash
# Run containers as non-root user
# Add to Dockerfile:
USER nobody

# Use read-only filesystem
docker run --read-only ...

# Drop capabilities
docker run --cap-drop=ALL ...
```

## Scaling

### Horizontal Scaling

For multiple agent instances:

1. Use shared database (PostgreSQL instead of SQLite)
2. Use shared cache (Redis cluster)
3. Use distributed task queue (Celery + Redis)
4. Load balance dashboard instances

### Vertical Scaling

For single-instance optimization:

1. Increase CPU/RAM allocation
2. Use GPU for Ollama (if available)
3. Optimize batch sizes in RL training
4. Increase fine-tuning thresholds

## Updates

### Update Procedure

```bash
# Stop service
sudo systemctl stop psa-agent

# Pull latest code
git pull origin main

# Update dependencies
source .venv/bin/activate
pip install -r requirements.txt

# Run database migrations (if applicable)
python -m agent migrate

# Restart service
sudo systemctl start psa-agent
```

### Rolling Updates

For zero-downtime updates:

1. Deploy new version alongside old
2. Verify new instance healthy
3. Switch traffic (load balancer or DNS)
4. Deprecate old instance

## Support

For deployment issues:
- GitHub Discussions: https://github.com/your-org/perpetual-scholar-agent/discussions
- Documentation: https://github.com/your-org/perpetual-scholar-agent/wiki
EOF
```

- [ ] **Step 2: Commit deployment guide**

```bash
git add docs/DEPLOYMENT.md
git commit -m "docs: add production deployment guide"
```

---

## Task 10: Add docs/TESTING.md

**Files:**
- Create: `docs/TESTING.md`

- [ ] **Step 1: Write docs/TESTING.md**

```bash
cat > docs/TESTING.md << 'EOF'
# Testing Guide

This document describes the testing strategy, conventions, and guidelines for perpetual-scholar-agent.

## Overview

We use a three-tier testing approach:
- **Unit Tests:** Test individual functions and classes in isolation
- **Integration Tests:** Test component interactions with mocked external services
- **E2E Tests:** Test full workflows with mocked components

All model-dependent operations (LLM calls, Docker execution, RL training) are mocked by default to enable fast, reliable testing without resource-intensive operations.

## Test Organization

```
tests/
├── unit/              # Unit tests for individual modules
│   ├── test_ingestion/
│   ├── test_reasoning/
│   ├── test_sandbox/
│   ├── test_reward/
│   ├── test_rl/
│   └── test_finetune/
├── integration/       # Integration tests for component interactions
│   ├── test_pipeline.py
│   └── test_orchestrator.py
├── e2e/              # End-to-end tests
│   ├── test_full_cycle.py
│   └── test_dashboard.py
├── fixtures/         # Shared test fixtures
│   ├── conftest.py
│   └── mocks.py
└── __init__.py
```

## Running Tests

### Run All Tests

```bash
pytest
```

### Run Specific Test File

```bash
pytest tests/unit/test_ingestion/test_arxiv_fetcher.py
```

### Run with Coverage

```bash
pytest --cov=agent --cov-report=html --cov-report=term
```

Coverage report will be generated in `htmlcov/index.html`.

### Run by Marker

```bash
# Unit tests only
pytest -m unit

# Integration tests only
pytest -m integration

# Skip slow tests
pytest -m "not slow"
```

### Run in Verbose Mode

```bash
pytest -v
```

## Coverage Requirements

- **Minimum:** 80% line coverage
- **Goal:** 90% line coverage
- **Critical paths:** 100% coverage

Critical paths include:
- Ingestion pipeline (all sources)
- Reasoning pipeline (summarization, code generation)
- Sandbox execution and safety limits
- Reward calculation and lesson storage
- RL environment and policy training
- LoRA fine-tuning triggers
- Dashboard endpoints

## Test Writing Guidelines

### Naming Conventions

- Test files: `test_<module>.py`
- Test classes: `Test<ClassName>`
- Test functions: `test_<what_is_tested>_<expected_result>`

### Test Structure

Arrange-Act-Assert (AAA) pattern:

```python
def test_arxiv_fetcher_returns_papers():
    # Arrange
    fetcher = ArXivFetcher(categories=["cs.DB"])
    fetcher.mock_api = Mock()  # Mock external API

    # Act
    papers = fetcher.fetch_last_24h()

    # Assert
    assert len(papers) > 0
    assert all("title" in p for p in papers)
```

### Fixtures

Use fixtures for common setup:

```python
# tests/fixtures/conftest.py
@pytest.fixture
def mock_ollama_backend():
    with patch("agent.llm.ollama_backend.OllamaBackend") as mock:
        mock.return_value.generate.return_value = "Test response"
        yield mock

@pytest.fixture
def test_database(tmp_path):
    db_path = tmp_path / "test.db"
    init_database(db_path)
    yield db_path
    os.unlink(db_path)
```

### Mocking Strategy

**LLM Backends:**
```python
def test_summarizer_with_mocked_llm():
    backend = Mock()
    backend.generate.return_value = json.dumps({
        "technique_name": "Test Technique",
        "problem": "Test problem",
        "algorithm": "Test algorithm",
        "pseudocode": "def test(): pass"
    })

    summarizer = PaperSummarizer(backend=backend)
    result = summarizer.summarize("Test paper content")

    assert result["technique_name"] == "Test Technique"
```

**Docker Execution:**
```python
def test_sandbox_executor_with_mocked_docker():
    with patch("docker.from_env") as mock_docker:
        mock_container = Mock()
        mock_container.wait.return_value = {"StatusCode": 0}
        mock_container.logs.return_value = b"Test output"
        mock_docker.return_value.containers.run.return_value = mock_container

        executor = SandboxExecutor()
        result = executor.run_code("print('test')")

        assert result["exit_code"] == 0
        assert "Test output" in result["output"]
```

**RL Training:**
```python
def test_rl_policy_with_mocked_training():
    with patch("stable_baselines3.PPO") as mock_ppo:
        mock_model = Mock()
        mock_ppo.return_value = mock_model

        policy = RLPolicy()
        policy.train(total_timesteps=1000)

        mock_model.learn.assert_called_once()
```

## Integration Tests

Integration tests verify component interactions:

```python
# tests/integration/test_pipeline.py
def test_full_pipeline_with_mocks():
    # Setup all mocks
    with patch("agent.ingestion.arxiv_fetcher.ArXivFetcher") as mock_fetcher, \
         patch("agent.reasoning.summarizer.PaperSummarizer") as mock_summarizer, \
         patch("agent.sandbox.executor.SandboxExecutor") as mock_executor:

        # Configure mocks
        mock_fetcher.return_value.fetch.return_value = [test_paper]
        mock_summarizer.return_value.summarize.return_value = test_summary
        mock_executor.return_value.run.return_value = test_result

        # Run pipeline
        pipeline = Pipeline()
        result = pipeline.run_cycle()

        # Verify full flow
        assert result["papers_processed"] == 1
        assert result["experiments_run"] == 1
```

## E2E Tests

End-to-end tests verify complete workflows:

```python
# tests/e2e/test_full_cycle.py
def test_daily_cycle_e2e():
    """Test complete daily cycle with all components mocked"""
    with TemporaryDirectory() as tmpdir:
        # Setup
        os.environ["DATA_DIR"] = tmpdir
        init_database(os.path.join(tmpdir, "test.db"))

        # Mock all external services
        mock_all_external_services()

        # Run scheduler
        scheduler = Scheduler()
        scheduler.run_daily_cycle()

        # Verify results
        lessons = LessonStore().get_all()
        assert len(lessons) > 0
        assert all("verified" in l["metadata"] for l in lessons)
```

## Test Data

### Fixtures Directory

Store test data in `tests/fixtures/data/`:

```
tests/fixtures/data/
├── papers/           # Sample paper content
│   ├── arxiv_sample.json
│   └── github_sample.json
├── code/             # Sample code snippets
│   └── benchmark_example.py
└── expected/         # Expected outputs
    └── summaries.json
```

### Using Test Data

```python
import json
from pathlib import Path

def test_with_sample_paper():
    sample_path = Path(__tests__/fixtures/data/papers/arxiv_sample.json)
    with open(sample_path) as f:
        paper = json.load(f)

    result = process_paper(paper)
    assert result["status"] == "success"
```

## Continuous Integration

Tests run automatically on:
- Push to `main` branch
- Pull requests to any branch
- Manual workflow dispatch

CI runs:
1. Linting (Ruff)
2. All tests with coverage
3. Security scan (Safety)

See `.github/workflows/ci.yml` for configuration.

## Common Test Patterns

### Async Tests

```python
@pytest.mark.asyncio
async def test_async_component():
    result = await async_function()
    assert result is not None
```

### Parametrized Tests

```python
@pytest.mark.parametrize("input,expected", [
    ("input1", "output1"),
    ("input2", "output2"),
])
def test_multiple_cases(input, expected):
    assert process(input) == expected
```

### Exception Testing

```python
def test_invalid_input_raises_error():
    with pytest.raises(ValueError, match="Invalid input"):
        process_invalid_input("")
```

### Database Testing

```python
def test_with_in_memory_db():
    """Use in-memory SQLite for fast tests"""
    with TemporaryDatabase() as db:
        store = LessonStore(db)
        store.add(test_lesson)

        lessons = store.get_all()
        assert len(lessons) == 1
```

## Debugging Tests

### Run Single Test

```bash
pytest tests/unit/test_something.py::TestClassName::test_method_name -v
```

### Drop into Debugger

```python
def test_with_breakpoint():
    result = some_function()
    breakpoint()  # Python 3.7+
    assert result == expected
```

Then run: `pytest --capture=no -s tests/test_file.py::test_with_breakpoint`

### Print Output

```bash
pytest -s  # Show print statements
pytest --capture=no  # Don't capture output
```

## Best Practices

1. **Test behavior, not implementation** — Focus on what the code does, not how
2. **One assertion per test** — Keep tests focused and readable
3. **Use descriptive names** — Test names should describe what they test
4. **Mock external dependencies** — Never call real external services in tests
5. **Clean up after tests** — Use fixtures and teardown methods
6. **Keep tests fast** — Unit tests should run in <1 second each
7. **Test edge cases** — Include empty inputs, None values, boundary conditions
8. **Avoid test interdependence** — Each test should be independent

## When Tests Fail

1. **Run locally first** — Verify the failure is reproducible locally
2. **Check recent changes** — Did you modify related code?
3. **Check mocks** — Are mocks configured correctly?
4. **Check test data** — Is test data valid and current?
5. **Check dependencies** — Did a dependency version change?
6. **Isolate the test** — Run the failing test alone to rule out interactions
7. **Debug** — Use pytest's pdb support: `pytest --pdb`

## Contributing Tests

When adding new features:

1. Write tests first (TDD approach)
2. Ensure coverage >80% for new code
3. Add integration tests for component interactions
4. Update this document if adding new test patterns

For questions about testing, open a GitHub Discussion with the "testing" tag.
EOF
```

- [ ] **Step 2: Commit testing guide**

```bash
git add docs/TESTING.md
git commit -m "docs: add testing guide and conventions"
```

---

## Task 11: Add Mock Infrastructure

**Files:**
- Create: `tests/fixtures/mocks.py`
- Create: `tests/fixtures/conftest.py`

- [ ] **Step 1: Create tests/fixtures directory**

```bash
mkdir -p tests/fixtures
```

- [ ] **Step 2: Write tests/fixtures/mocks.py**

```bash
cat > tests/fixtures/mocks.py << 'EOF'
"""
Mock fixtures for testing perpetual-scholar-agent.

All external dependencies (LLMs, Docker, databases) are mocked to enable
fast, reliable testing without resource-intensive operations.
"""

from unittest.mock import Mock, MagicMock, patch
from typing import Any, Dict
import json


class MockOllamaBackend:
    """Mock Ollama backend for testing."""

    def __init__(self):
        self.generate_call_count = 0
        self.embed_call_count = 0

    def generate(self, prompt: str, system: str = "") -> str:
        """Return predetermined response for testing."""
        self.generate_call_count += 1

        # Return different responses based on prompt context
        if "summarize" in prompt.lower() or "extract" in prompt.lower():
            return json.dumps({
                "technique_name": "Mock Technique",
                "problem": "Test problem statement",
                "algorithm": "Test algorithm description",
                "pseudocode": "def mock_technique():\n    pass",
                "domain_relevance": 0.85
            })
        elif "generate code" in prompt.lower():
            return json.dumps({
                "code": """
import pytest

def test_mock_benchmark():
    '''Mock benchmark for testing.'''
    assert True
    performance = 1.0
    return performance
""",
                "language": "python",
                "dependencies": ["pytest"]
            })
        else:
            return "Mock response"

    def embed(self, text: str) -> list:
        """Return deterministic mock embedding."""
        self.embed_call_count += 1
        # Return deterministic 384-dim embedding (all-MiniLM-L6-v2 size)
        return [0.1] * 384

    def healthcheck(self) -> bool:
        """Always return healthy for testing."""
        return True

    def list_models(self) -> list:
        """Return mock model list."""
        return ["qwen2.5-coder:7b-instruct"]


class MockClaudeBackend:
    """Mock Claude API backend for testing."""

    def __init__(self):
        self.generate_call_count = 0

    def generate(self, prompt: str, system: str = "") -> str:
        """Return predetermined response."""
        self.generate_call_count += 1
        return json.dumps({
            "technique_name": "Claude Mock Technique",
            "problem": "Test problem",
            "algorithm": "Test algorithm",
            "pseudocode": "def claude_mock(): pass"
        })

    def judge_code_quality(self, code: str, description: str) -> float:
        """Return mock code quality score."""
        return 8.5


class MockOpenAIBackend:
    """Mock OpenAI API backend for testing."""

    def __init__(self):
        self.generate_call_count = 0

    def generate(self, prompt: str, system: str = "") -> str:
        """Return predetermined response."""
        self.generate_call_count += 1
        return "Mock OpenAI response"


class MockDockerClient:
    """Mock Docker client for testing sandbox execution."""

    def __init__(self):
        self.containers_created = 0
        self.containers_removed = 0

    class MockContainer:
        def __init__(self, exit_code=0, stdout=b"Mock output", stderr=b""):
            self.exit_code = exit_code
            self.stdout = stdout
            self.stderr = stderr

        def wait(self):
            return {"StatusCode": self.exit_code}

        def logs(self):
            return self.stdout

        def remove(self, force=True):
            pass

    def containers(self):
        """Return mock containers interface."""
        mock = Mock()

        def run(*args, **kwargs):
            self.containers_created += 1
            # Return successful mock container
            return self.MockContainer(
                exit_code=0,
                stdout=b'{"pytest_benchmark": {"ops_per_sec": 1000.0}}',
                stderr=b""
            )

        mock.run = run
        return mock


class MockPPOPolicy:
    """Mock PPO policy for RL testing."""

    def __init__(self):
        self.predict_call_count = 0
        self.learn_call_count = 0

    def predict(self, observation, deterministic=True):
        """Return mock action."""
        self.predict_call_count += 1
        return 1, {}  # action, states

    def learn(self, total_timesteps):
        """Mock training - just record call."""
        self.learn_call_count += 1
        return self


class MockLoRATrainer:
    """Mock LoRA trainer for fine-tuning testing."""

    def __init__(self):
        self.train_call_count = 0

    def train(self):
        """Mock training - record call and return dummy adapter."""
        self.train_call_count += 1
        return "/tmp/mock_adapter_v1"

    def save_adapter(self, path):
        """Mock save - just record path."""
        return True


def get_mock_backend(backend_type="ollama"):
    """Get mock backend instance by type."""
    backends = {
        "ollama": MockOllamaBackend(),
        "claude": MockClaudeBackend(),
        "openai": MockOpenAIBackend()
    }
    return backends.get(backend_type, MockOllamaBackend())


def mock_paper_response():
    """Return mock paper/arXiv API response."""
    return {
        "id": "2301.00001",
        "title": "Mock Paper Title",
        "authors": ["Author One", "Author Two"],
        "summary": "This is a mock paper summary for testing.",
        "published": "2025-01-01T00:00:00Z",
        "categories": ["cs.DB", "cs.AI"],
        "url": "https://arxiv.org/abs/2301.00001"
    }


def mock_github_repo_response():
    """Return mock GitHub Trending repo response."""
    return {
        "name": "mock-repo",
        "full_name": "user/mock-repo",
        "description": "Mock repository for testing",
        "language": "Python",
        "stars": 1000,
        "url": "https://github.com/user/mock-repo",
        "readme": "# Mock README\n\nThis is a mock README for testing."
    }


def mock_benchmark_result():
    """Return mock benchmark execution result."""
    return {
        "exit_code": 0,
        "output": '{"ops_per_sec": 1500.0, "latency_p50": 0.001, "latency_p99": 0.005}',
        "metrics": {
            "ops_per_sec": 1500.0,
            "latency_p50": 0.001,
            "latency_p99": 0.005
        },
        "duration_seconds": 5.2
    }


def mock_lesson():
    """Return mock lesson object."""
    return {
        "id": "mock-lesson-001",
        "technique_name": "Mock Technique",
        "problem": "Test problem",
        "algorithm": "Test algorithm",
        "code": "def mock(): pass",
        "metrics": {
            "ops_per_sec": 1500.0,
            "baseline_ops_per_sec": 1000.0
        },
        "reward": 0.5,
        "source_url": "https://arxiv.org/abs/2301.00001",
        "timestamp": "2025-01-08T12:00:00Z",
        "verified": True
    }


def setup_common_mocks():
    """
    Setup all common mocks for testing.

    Returns a dictionary of mock patches that can be used as context managers.
    """
    return {
        "ollama": patch("agent.llm.ollama_backend.OllamaBackend", MockOllamaBackend),
        "claude": patch("agent.llm.claude_backend.ClaudeBackend", MockClaudeBackend),
        "docker": patch("docker.from_env", return_value=MockDockerClient()),
        "ppo": patch("stable_baselines3.PPO", return_value=MockPPOPolicy()),
    }
EOF
```

- [ ] **Step 3: Write tests/fixtures/conftest.py**

```bash
cat > tests/fixtures/conftest.py << 'EOF'
"""
Pytest configuration and shared fixtures for perpetual-scholar-agent tests.
"""

import pytest
import tempfile
import os
from pathlib import Path
import sys

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


@pytest.fixture
def temp_dir():
    """Provide temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def temp_db_path(temp_dir):
    """Provide temporary database path."""
    db_path = os.path.join(temp_dir, "test.db")
    yield db_path
    if os.path.exists(db_path):
        os.unlink(db_path)


@pytest.fixture
def mock_env_vars(temp_dir):
    """Provide mock environment variables."""
    os.environ["DATA_DIR"] = temp_dir
    os.environ["DATABASE_PATH"] = os.path.join(temp_dir, "test.db")
    os.environ["FAISS_INDEX_PATH"] = os.path.join(temp_dir, "test.faiss")
    os.environ["MODELS_DIR"] = os.path.join(temp_dir, "models")
    yield
    # Cleanup
    for key in ["DATA_DIR", "DATABASE_PATH", "FAISS_INDEX_PATH", "MODELS_DIR"]:
        os.environ.pop(key, None)


@pytest.fixture
def sample_paper():
    """Provide sample paper data for testing."""
    return {
        "id": "2301.00001",
        "title": "Test Paper: Advanced Database Optimization",
        "authors": ["Jane Doe", "John Smith"],
        "summary": "This paper presents a novel approach to database optimization using machine learning techniques.",
        "published": "2025-01-01T00:00:00Z",
        "categories": ["cs.DB", "cs.AI"],
        "url": "https://arxiv.org/abs/2301.00001"
    }


@pytest.fixture
def sample_github_repo():
    """Provide sample GitHub repo data for testing."""
    return {
        "name": "fast-ql",
        "full_name": "user/fast-ql",
        "description": "A fast query language for time-series databases",
        "language": "Python",
        "stars": 1250,
        "url": "https://github.com/user/fast-ql",
        "readme": "# FastQL\n\nA revolutionary query language that provides 10x performance improvement over traditional SQL for time-series data."
    }


@pytest.fixture
def sample_benchmark_code():
    """Provide sample benchmark code for testing."""
    return '''
import pytest

def test_index_performance():
    """Test that custom index provides performance improvement."""
    # Setup
    data = list(range(10000))

    # Custom index implementation
    custom_index = build_custom_index(data)

    # Benchmark: lookup performance
    import time
    start = time.time()
    for _ in range(1000):
        result = custom_index.lookup(5000)
    elapsed = time.time() - start

    # Assert reasonable performance
    assert elapsed < 0.1  # Should complete in <100ms
    assert result == 5000
'''


@pytest.fixture
def sample_lesson(sample_paper):
    """Provide sample lesson data for testing."""
    return {
        "id": "lesson-001",
        "technique_name": "Custom Index Optimization",
        "problem": "Time-series databases suffer from slow query performance on large datasets.",
        "algorithm": "Implement a custom B-tree variant optimized for time-series data patterns.",
        "code": "def build_custom_index(data): pass",
        "metrics": {
            "ops_per_sec": 2500.0,
            "latency_p50": 0.0005,
            "latency_p99": 0.002
        },
        "baseline_metrics": {
            "ops_per_sec": 1000.0,
            "latency_p50": 0.001,
            "latency_p99": 0.005
        },
        "reward": 1.5,
        "source_url": sample_paper["url"],
        "timestamp": "2025-01-08T12:00:00Z",
        "verified": True
    }


@pytest.fixture
def mock_embeddings():
    """Provide mock embedding vectors."""
    import random
    return [random.random() for _ in range(384)]


# Pytest configuration
def pytest_configure(config):
    """Configure pytest markers."""
    config.addinivalue_line(
        "markers", "unit: Unit tests"
    )
    config.addinivalue_line(
        "markers", "integration: Integration tests"
    )
    config.addinivalue_line(
        "markers", "e2e: End-to-end tests"
    )
    config.addinivalue_line(
        "markers", "slow: Slow-running tests"
    )
EOF
```

- [ ] **Step 4: Create tests/__init__.py**

```bash
touch tests/__init__.py
```

- [ ] **Step 5: Commit mock infrastructure**

```bash
git add tests/fixtures/mocks.py tests/fixtures/conftest.py tests/__init__.py
git commit -m "test: add mock infrastructure and test fixtures"
```

---

## Task 12: Add Basic Unit Tests

**Files:**
- Create: `tests/unit/test_config/test_settings.py`
- Create: `tests/unit/test_ingestion/test_deduplicator.py`
- Create: `tests/unit/test_reward/test_calculator.py`

- [ ] **Step 1: Create test directories**

```bash
mkdir -p tests/unit/test_config tests/unit/test_ingestion tests/unit/test_reward
```

- [ ] **Step 2: Write config settings test**

```bash
cat > tests/unit/test_config/test_settings.py << 'EOF'
"""Tests for configuration settings."""

import os
import pytest
from agent.config.settings import Settings


@pytest.mark.unit
class TestSettings:
    """Test Settings configuration loading."""

    def test_default_settings(self, mock_env_vars):
        """Test settings load with default values."""
        settings = Settings()
        assert settings.MODELS_DIR is not None
        assert settings.DATA_DIR is not None

    def test_ollama_settings(self, mock_env_vars):
        """Test Ollama backend settings."""
        os.environ["OLLAMA_BASE_URL"] = "http://test-ollama:11434"
        os.environ["OLLAMA_MODEL"] = "test-model"

        settings = Settings()
        assert settings.OLLAMA_BASE_URL == "http://test-ollama:11434"
        assert settings.OLLAMA_MODEL == "test-model"

    def test_sandbox_limits(self, mock_env_vars):
        """Test sandbox resource limit settings."""
        os.environ["SANDBOX_CPU_LIMIT"] = "4"
        os.environ["SANDBOX_MEMORY_LIMIT"] = "4g"
        os.environ["SANDBOX_TIMEOUT_SECONDS"] = "120"

        settings = Settings()
        assert settings.SANDBOX_CPU_LIMIT == 4
        assert settings.SANDBOX_MEMORY_LIMIT == "4g"
        assert settings.SANDBOX_TIMEOUT_SECONDS == 120

    def test_domain_focus(self, mock_env_vars):
        """Test domain focus configuration."""
        os.environ["DOMAIN_FOCUS"] = "database-optimization"

        settings = Settings()
        assert settings.DOMAIN_FOCUS == "database-optimization"

    def test_finetune_triggers(self, mock_env_vars):
        """Test fine-tuning trigger thresholds."""
        os.environ["FINETUNE_LESSON_THRESHOLD"] = "100"
        os.environ["FINETUNE_TIME_THRESHOLD_DAYS"] = "14"

        settings = Settings()
        assert settings.FINETUNE_LESSON_THRESHOLD == 100
        assert settings.FINETUNE_TIME_THRESHOLD_DAYS == 14
EOF
```

- [ ] **Step 3: Write deduplicator test**

```bash
cat > tests/unit/test_ingestion/test_deduplicator.py << 'EOF'
"""Tests for ingestion deduplicator."""

import pytest
from agent.ingestion.deduplicator import Deduplicator
import hashlib


@pytest.mark.unit
class TestDeduplicator:
    """Test deduplication of ingested items."""

    @pytest.fixture
    def deduplicator(self, temp_db_path):
        """Provide deduplicator instance with test database."""
        return Deduplicator(db_path=temp_db_path)

    def test_generate_content_hash(self, deduplicator):
        """Test content hash generation."""
        content = "Test content for hashing"
        hash_value = deduplicator._generate_hash(content)

        # Verify it's a valid SHA-256 hex string
        assert len(hash_value) == 64
        assert all(c in "0123456789abcdef" for c in hash_value)

    def test_hash_consistency(self, deduplicator):
        """Test same content produces same hash."""
        content = "Consistent content"
        hash1 = deduplicator._generate_hash(content)
        hash2 = deduplicator._generate_hash(content)

        assert hash1 == hash2

    def test_hash_uniqueness(self, deduplicator):
        """Test different content produces different hashes."""
        hash1 = deduplicator._generate_hash("Content 1")
        hash2 = deduplicator._generate_hash("Content 2")

        assert hash1 != hash2

    def test_is_seen_false_for_new_item(self, deduplicator):
        """Test unseen item returns False."""
        content = {"id": "new-item", "title": "New Item"}
        is_seen = deduplicator.is_seen(content)

        assert is_seen is False

    def test_mark_seen_and_check(self, deduplicator):
        """Test marking item as seen and checking."""
        content = {"id": "test-item", "title": "Test Item"}

        # First check should be False
        assert deduplicator.is_seen(content) is False

        # Mark as seen
        deduplicator.mark_seen(content)

        # Next check should be True
        assert deduplicator.is_seen(content) is True

    def test_mark_seen_batch(self, deduplicator):
        """Test marking multiple items as seen."""
        items = [
            {"id": f"item-{i}", "title": f"Item {i}"}
            for i in range(10)
        ]

        deduplicator.mark_seen_batch(items)

        for item in items:
            assert deduplicator.is_seen(item) is True
EOF
```

- [ ] **Step 4: Write reward calculator test**

```bash
cat > tests/unit/test_reward/test_calculator.py << 'EOF'
"""Tests for reward calculator."""

import pytest
from agent.reward.calculator import RewardCalculator


@pytest.mark.unit
class TestRewardCalculator:
    """Test reward calculation for experiments."""

    @pytest.fixture
    def calculator(self):
        """Provide reward calculator instance."""
        return RewardCalculator()

    def test_positive_reward_for_improvement(self, calculator):
        """Test positive reward for improved performance."""
        baseline = {"ops_per_sec": 1000.0}
        new_metric = {"ops_per_sec": 1500.0}

        reward = calculator.calculate_reward(new_metric, baseline)

        assert reward > 0
        assert reward == pytest.approx(0.5, rel=0.01)  # (1500-1000)/1000 = 0.5

    def test_negative_reward_for_regression(self, calculator):
        """Test negative reward for degraded performance."""
        baseline = {"ops_per_sec": 1000.0}
        new_metric = {"ops_per_sec": 800.0}

        reward = calculator.calculate_reward(new_metric, baseline)

        assert reward < 0
        assert reward == pytest.approx(-0.2, rel=0.01)  # (800-1000)/1000 = -0.2

    def test_zero_reward_for_no_change(self, calculator):
        """Test zero reward for identical performance."""
        baseline = {"ops_per_sec": 1000.0}
        new_metric = {"ops_per_sec": 1000.0}

        reward = calculator.calculate_reward(new_metric, baseline)

        assert reward == 0

    def test_reward_clamping_positive(self, calculator):
        """Test reward is clamped at +1 for large improvements."""
        baseline = {"ops_per_sec": 100.0}
        new_metric = {"ops_per_sec": 1000.0}  # 10x improvement

        reward = calculator.calculate_reward(new_metric, baseline)

        assert reward <= 1.0

    def test_reward_clamping_negative(self, calculator):
        """Test reward is clamped at -1 for large regressions."""
        baseline = {"ops_per_sec": 1000.0}
        new_metric = {"ops_per_sec": 10.0}  # 99% degradation

        reward = calculator.calculate_reward(new_metric, baseline)

        assert reward >= -1.0

    def test_latency_reward(self, calculator):
        """Test reward calculation for latency metrics (lower is better)."""
        baseline = {"latency_p50": 0.01}
        new_metric = {"latency_p50": 0.005}  # 2x improvement

        reward = calculator.calculate_reward_latency(new_metric, baseline)

        assert reward > 0

    def test_combined_reward(self, calculator):
        """Test combined reward from throughput and latency."""
        baseline = {
            "ops_per_sec": 1000.0,
            "latency_p50": 0.01
        }
        new_metric = {
            "ops_per_sec": 1200.0,
            "latency_p50": 0.008
        }

        reward = calculator.calculate_combined_reward(new_metric, baseline)

        assert 0 < reward <= 1.0
EOF
```

- [ ] **Step 5: Commit basic unit tests**

```bash
git add tests/unit/test_config/test_settings.py tests/unit/test_ingestion/test_deduplicator.py tests/unit/test_reward/test_calculator.py
git commit -m "test: add basic unit tests for config, ingestion, and reward modules"
```

---

## Task 13: Create GitHub PR and Issue Templates

**Files:**
- Create: `.github/PULL_REQUEST_TEMPLATE.md`
- Create: `.github/ISSUE_TEMPLATE/bug_report.md`
- Create: `.github/ISSUE_TEMPLATE/feature_request.md`

- [ ] **Step 1: Create .github/ISSUE_TEMPLATE directory**

```bash
mkdir -p .github/ISSUE_TEMPLATE
```

- [ ] **Step 2: Write PR template**

```bash
cat > .github/PULL_REQUEST_TEMPLATE.md << 'EOF'
## Description
<!-- Brief description of changes -->

## Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to change)
- [ ] Documentation update

## Testing
- [ ] Tests added/updated
- [ ] All tests pass locally
- [ ] Coverage meets requirements (80% minimum)

## Checklist
- [ ] Code follows style guidelines (Ruff)
- [ ] Self-review completed
- [ ] Documentation updated (if applicable)
- [ ] CHANGELOG.md updated (for user-facing changes)
- [ ] No merge conflicts

## Related Issues
Fixes #
Related to #
EOF
```

- [ ] **Step 3: Write bug report template**

```bash
cat > .github/ISSUE_TEMPLATE/bug_report.md << 'EOF'
---
name: Bug report
about: Report a problem with the agent
title: '[BUG] '
labels: bug
assignees: ''
---

## Bug Description
<!-- Clear and concise description of the bug -->

## Reproduction Steps
<!-- Steps to reproduce the behavior -->
1.
2.
3.

## Expected Behavior
<!-- What you expected to happen -->

## Actual Behavior
<!-- What actually happened -->

## Environment
- Python version:
- Ollama version:
- Docker version:
- OS:
- Agent version:

## Logs
<!-- Relevant error messages or logs -->
```

## Additional Context
<!-- Any other relevant information, screenshots, etc. -->
EOF
```

- [ ] **Step 4: Write feature request template**

```bash
cat > .github/ISSUE_TEMPLATE/feature_request.md << 'EOF'
---
name: Feature request
about: Suggest an idea for the agent
title: '[FEATURE] '
labels: enhancement
assignees: ''
---

## Feature Description
<!-- Clear and concise description of the feature -->

## Use Case
<!-- Describe the use case this feature would enable -->

## Proposed Solution
<!-- Describe the solution you'd like -->

## Alternatives Considered
<!-- Describe alternative solutions or features you've considered -->

## Additional Context
<!-- Any other relevant information, examples, or mockups -->
EOF
```

- [ ] **Step 5: Commit GitHub templates**

```bash
git add .github/PULL_REQUEST_TEMPLATE.md .github/ISSUE_TEMPLATE/
git commit -m "docs: add GitHub PR and issue templates"
```

---

## Task 14: Final Verification and Tagging

**Files:**
- Modify: `README.md` (add badges and links)
- Create: Git tag v0.1.0

- [ ] **Step 1: Add badges to README.md**

```bash
# Add badges at top of README.md after first line
cat > /tmp/readme_badges.md << 'EOF'

[![CI](https://github.com/your-org/perpetual-scholar-agent/actions/workflows/ci.yml/badge.svg)](https://github.com/your-org/perpetual-scholar-agent/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/your-org/perpetual-scholar-agent/branch/main/graph/badge.svg)](https://codecov.io/gh/your-org/perpetual-scholar-agent)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: Ruff](https://img.shields.io/badge/code%20style-Ruff-000000.svg)](https://docs.astral.sh/ruff/)
EOF

# Insert badges after first line
head -1 README.md > /tmp/new_readme.md
cat /tmp/readme_badges.md >> /tmp/new_readme.md
tail -n +2 README.md >> /tmp/new_readme.md
mv /tmp/new_readme.md README.md
```

- [ ] **Step 2: Update README with new documentation links**

Add to README.md in appropriate section:

```markdown
## Documentation

- [Deployment Guide](docs/DEPLOYMENT.md) — Production deployment instructions
- [Testing Guide](docs/TESTING.md) — Testing conventions and guidelines
- [Contributing](CONTRIBUTING.md) — Development setup and contribution guidelines
- [Changelog](CHANGELOG.md) — Version history and changes
- [Security Policy](SECURITY.md) — Vulnerability reporting
- [Code of Conduct](CODE_OF_CONDUCT.md) — Community guidelines
```

- [ ] **Step 3: Verify all files exist**

```bash
# Check all required files exist
ls -la LICENSE CODE_OF_CONDUCT.md CONTRIBUTING.md SECURITY.md CHANGELOG.md
ls -la .github/workflows/ci.yml .pre-commit-config.yaml
ls -la docs/DEPLOYMENT.md docs/TESTING.md
ls -la tests/fixtures/mocks.py tests/fixtures/conftest.py
```

Expected: All files listed

- [ ] **Step 4: Run tests to ensure everything works**

```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Run Ruff checks
ruff check .
ruff format --check .

# Run tests
pytest --cov=agent
```

Expected: All checks pass, coverage ≥80%

- [ ] **Step 5: Commit README updates**

```bash
git add README.md
git commit -m "docs: add badges and documentation links to README"
```

- [ ] **Step 6: Create git tag for v0.1.0**

```bash
git tag -a v0.1.0 -m "Release v0.1.0: Initial production-ready release"
git push origin main --tags  # When remote is configured
```

Expected: Tag created successfully

---

## Task 15: Final Verification Checklist

- [ ] **Step 1: Verify all 9+ files created**

```bash
echo "=== Checking required files ==="
test -f LICENSE && echo "✓ LICENSE" || echo "✗ LICENSE missing"
test -f CODE_OF_CONDUCT.md && echo "✓ CODE_OF_CONDUCT.md" || echo "✗ CODE_OF_CONDUCT.md missing"
test -f CONTRIBUTING.md && echo "✓ CONTRIBUTING.md" || echo "✗ CONTRIBUTING.md missing"
test -f SECURITY.md && echo "✓ SECURITY.md" || echo "✗ SECURITY.md missing"
test -f CHANGELOG.md && echo "✓ CHANGELOG.md" || echo "✗ CHANGELOG.md missing"
test -f .github/workflows/ci.yml && echo "✓ .github/workflows/ci.yml" || echo "✗ CI workflow missing"
test -f .pre-commit-config.yaml && echo "✓ .pre-commit-config.yaml" || echo "✗ Pre-commit config missing"
test -f docs/DEPLOYMENT.md && echo "✓ docs/DEPLOYMENT.md" || echo "✗ DEPLOYMENT.md missing"
test -f docs/TESTING.md && echo "✓ docs/TESTING.md" || echo "✗ TESTING.md missing"
echo "=== Additional files ==="
test -f .github/PULL_REQUEST_TEMPLATE.md && echo "✓ PR template" || echo "✗ PR template missing"
test -f .github/ISSUE_TEMPLATE/bug_report.md && echo "✓ Bug template" || echo "✗ Bug template missing"
test -f .github/ISSUE_TEMPLATE/feature_request.md && echo "✓ Feature template" || echo "✗ Feature template missing"
test -f requirements-dev.txt && echo "✓ requirements-dev.txt" || echo "✗ requirements-dev.txt missing"
test -f tests/fixtures/mocks.py && echo "✓ Mock fixtures" || echo "✗ Mock fixtures missing"
test -f tests/fixtures/conftest.py && echo "✓ Test fixtures" || echo "✗ Test fixtures missing"
```

- [ ] **Step 2: Verify git status**

```bash
git status
git log --oneline -10
```

Expected: Clean working tree, all commits present

- [ ] **Step 3: Count lines of code**

```bash
echo "=== Project Statistics ==="
find agent -name "*.py" -type f | xargs wc -l | tail -1
find tests -name "*.py" -type f | xargs wc -l | tail -1 2>/dev/null || echo "0 tests"
```

- [ ] **Step 4: Display summary**

```bash
echo "=== Production Readiness Summary ==="
echo "✓ All required files created"
echo "✓ Git repository initialized"
echo "✓ MIT License added"
echo "✓ CI/CD pipeline configured (GitHub Actions)"
echo "✓ Pre-commit hooks configured (Ruff)"
echo "✓ Documentation complete (Contributing, Security, Deployment, Testing)"
echo "✓ GitHub templates added (PR, Issues)"
echo "✓ Mock infrastructure for testing"
echo "✓ Basic unit tests added"
echo "✓ v0.1.0 tag created"
echo ""
echo "Next steps:"
echo "1. Push repository to GitHub: git remote add origin <url> && git push -u origin main"
echo "2. Update organization URLs in templates (your-org, security email)"
echo "3. Enable GitHub Actions on repository"
echo "4. Enable Dependabot for dependency updates"
echo "5. Configure codecov.io for coverage reporting"
echo "6. Update README badges with correct repository URLs"
```

---

## Success Criteria

After completing all tasks, the project will have:

✅ **Legal & Community**
- MIT License for open-source distribution
- Contributor Covenant Code of Conduct for community guidelines
- Security policy for vulnerability reporting

✅ **Developer Experience**
- Comprehensive contributing guide
- Testing documentation with conventions
- Pre-commit hooks for code quality (Ruff)
- CI/CD pipeline for automated testing

✅ **Documentation**
- Production deployment guide (Docker Compose, systemd)
- Testing strategy and coverage goals
- Changelog with v0.1.0 release notes
- Updated README with badges and links

✅ **Infrastructure**
- GitHub Actions CI/CD (lint, test, security)
- GitHub templates for PRs and issues
- Mock infrastructure for fast testing
- Basic unit tests with mocked dependencies

✅ **Git Repository**
- Initialized git repository
- Clean commit history
- v0.1.0 release tag

**The project is now ready for:**
1. Pushing to GitHub
2. Enabling CI/CD
3. Accepting contributions
4. Tagging and releasing v0.1.0

**Note:** All model execution (LLM calls, RL training, LoRA fine-tuning) is mocked. Real model training will be enabled in production deployment.
