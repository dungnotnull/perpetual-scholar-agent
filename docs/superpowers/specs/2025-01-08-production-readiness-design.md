# Production Readiness & Open Source Design

**Project:** perpetual-scholar-agent
**Date:** 2025-01-08
**Status:** Approved

## Overview

This design adds production-ready infrastructure and open-source requirements to the perpetual-scholar-agent project. All code will be complete with mocked/stubbed model execution to save resources. Real model training and execution will be enabled later in production.

## Goal

Transform the project from a feature-complete codebase to a production-ready open-source project with:
- Proper licensing and legal framework
- CI/CD pipeline with automated testing
- Code quality enforcement via pre-commit hooks
- Comprehensive documentation for contributors and operators
- 100% code coverage with mocked model execution

## Constraints

**IMPORTANT:** All model execution (LLM calls, RL training, LoRA fine-tuning) will be mocked/stubbed. No real model training, pulling, or running during this phase.

## Files to Create

### 1. LICENSE (MIT License)

Permissive open-source license allowing any use, modification, and distribution.

### 2. CODE_OF_CONDUCT.md

Contributor Covenant v2.1 — industry-standard code of conduct covering scope, responsibilities, enforcement, and attribution.

### 3. CONTRIBUTING.md

Developer onboarding and contribution guidelines:
- Quick start for contributors
- Development workflow (branch, commit, PR, review)
- Code style guide (Ruff configuration)
- Testing requirements and coverage goals
- PR template guidelines

### 4. SECURITY.md

Vulnerability reporting and security policy:
- Private disclosure process (security@ email)
- Supported versions policy
- Update and disclosure timeline

### 5. CHANGELOG.md

Version history following Keep a Changelog format with sections: Added, Changed, Deprecated, Removed, Fixed, Security.

### 6. .github/workflows/ci.yml

GitHub Actions CI/CD pipeline:

**Triggers:**
- Push to main branch
- Pull requests to any branch
- Manual workflow dispatch

**Jobs:**
1. **lint** — Ruff format and lint check
2. **test** — pytest with coverage reporting (80% minimum)
3. **security** — Safety scan for known vulnerabilities

**Matrix:** Python 3.11, 3.12

### 7. .pre-commit-config.yaml

Pre-commit hooks for code quality:
- Ruff (format + lint) on all Python files
- End-of-file fixer
- Trailing whitespace fixer
- Check for large files (>500KB)

### 8. docs/DEPLOYMENT.md

Production deployment guide:
- Prerequisites (Docker, Ollama, Python 3.11+)
- Environment configuration (.env setup)
- Deployment options (Docker Compose, systemd)
- Production checklist (TLS, monitoring, backups)
- Troubleshooting guide

### 9. docs/TESTING.md

Testing strategy and conventions:
- Test organization (unit, integration, e2e)
- Coverage requirements (80% minimum, 90% goal)
- How to run tests locally
- Test writing guidelines
- Mocking strategy for model execution

## Technical Decisions

### License: MIT
- Most permissive and widely understood
- Minimal restrictions maximize adoption
- Suitable for both commercial and academic use

### CI/CD: GitHub Actions
- Industry standard for open-source projects
- Excellent GitHub integration
- Free for public repositories
- Vast ecosystem of actions

### Code Quality: Ruff
- Modern, all-in-one tool (replaces flake8, black, isort)
- Extremely fast (10-100x faster than traditional tools)
- Active development and wide adoption

### Code of Conduct: Contributor Covenant v2.1
- Industry standard, widely recognized
- Clear moderation guidelines
- Signals inclusive community

### Changelog: Keep a Changelog format
- Human-readable and machine-parseable
- Industry standard format
- Can be automated later if desired

## Implementation Priority

1. **High Priority (Blocking):**
   - LICENSE — Cannot open source without license
   - .github/workflows/ci.yml — Cannot merge PRs without CI
   - .pre-commit-config.yaml — Code quality enforcement

2. **Medium Priority (Important):**
   - CONTRIBUTING.md — Essential for contributors
   - docs/TESTING.md — Essential for code quality
   - CHANGELOG.md — Essential for release tracking

3. **Standard Priority (Best Practices):**
   - SECURITY.md — Security best practice
   - CODE_OF_CONDUCT.md — Community best practice
   - docs/DEPLOYMENT.md — Operations documentation

## Mocking Strategy

To save resources, all model-dependent operations will be mocked:

**LLM Backends (Ollama, Claude, OpenAI):**
- Mock generate() to return predetermined responses
- Mock embeddings to return deterministic vectors
- Mock health checks to always return healthy

**RL Training:**
- Mock PPO training to skip actual training
- Return dummy policy checkpoints
- Mock reward calculations

**LoRA Fine-tuning:**
- Mock trainer.train() to skip actual training
- Return dummy adapter files
- Mock Ollama reload calls

**Sandbox Execution:**
- Mock Docker container creation
- Return predetermined benchmark results
- Skip actual code execution

## Testing Strategy

### Unit Tests
- Test individual functions and classes
- Mock all external dependencies (Docker, LLMs, databases)
- Fast execution (<1 second per test)

### Integration Tests
- Test component interactions
- Use in-memory SQLite
- Mock Docker and LLM calls
- Slower but still fast (<5 seconds per test)

### E2E Tests
- Test full pipeline with mocked components
- Verify data flow through all stages
- Mock external services

### Coverage Goals
- Minimum: 80% line coverage
- Goal: 90% line coverage
- Critical paths: 100% coverage

## Success Criteria

1. All 9 files created and committed
2. CI/CD pipeline passes on first run
3. Pre-commit hooks installed and passing
4. Test coverage ≥80%
5. All tests pass with mocked model execution
6. Documentation complete and accurate
7. Project can be tagged as v0.1.0

## Related Files

- PROJECT-DEVELOPMENT-PHASE-TRACKING.md — Phase completion status
- README.md — Project overview and quickstart
- CLAUDE.md — Development guidelines
