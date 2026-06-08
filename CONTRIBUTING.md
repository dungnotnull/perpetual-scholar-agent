# Contributing to Perpetual Scholar Agent

Thank you for your interest in contributing to Perpetual Scholar Agent! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Documentation](#documentation)
- [Submitting Changes](#submitting-changes)
- [Community Guidelines](#community-guidelines)

## Code of Conduct

By participating in this project, you agree to abide by our [Code of Conduct](CODE_OF_CONDUCT.md).

## Getting Started

### Prerequisites

- Docker and Docker Compose
- Python 3.10+
- Ollama (for local SLM)
- Git

### Initial Setup

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/your-username/perpetual-scholar-agent.git
   cd perpetual-scholar-agent
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

## Development Workflow

### Branch Naming Convention

- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation changes
- `refactor/` - Code refactoring
- `test/` - Test additions or modifications

### Development Process

1. Create a new branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes following our coding standards

3. Write tests for new functionality

4. Ensure all tests pass:
   ```bash
   pytest tests/
   ```

5. Format code:
   ```bash
   black .
   isort .
   ```

6. Commit changes with clear messages

7. Push to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

8. Create a Pull Request

## Coding Standards

### Python Code Style

- Follow PEP 8 guidelines
- Use type hints for function signatures
- Write docstrings for all public functions and classes
- Keep functions focused and under 50 lines when possible
- Use descriptive variable names

### Example Code Style

```python
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

def process_papers(papers: List[Dict]) -> List[Dict]:
    """
    Process and filter academic papers based on relevance criteria.
    
    Args:
        papers: List of paper dictionaries with metadata
        
    Returns:
        Filtered list of relevant papers
    """
    relevant_papers = [
        paper for paper in papers
        if is_relevant(paper)
    ]
    logger.info(f"Filtered {len(relevant_papers)} relevant papers")
    return relevant_papers
```

### Documentation Standards

- All public APIs must have docstrings
- Docstrings should follow Google style
- Include examples for complex functions
- Update README.md for user-facing changes

## Testing Guidelines

### Test Structure

```
tests/
├── unit/           # Unit tests
├── integration/    # Integration tests
├── e2e/           # End-to-end tests
└── fixtures/      # Test data and fixtures
```

### Writing Tests

- Write tests before implementing features (TDD)
- Aim for >80% code coverage
- Use pytest fixtures for common test data
- Mock external dependencies (APIs, databases)

### Example Test

```python
import pytest
from agent.paper_processor import process_papers

def test_process_papers_filters_correctly():
    papers = [
        {"title": "Relevant Paper", "year": 2024},
        {"title": "Old Paper", "year": 2010}
    ]
    result = process_papers(papers)
    assert len(result) == 1
    assert result[0]["title"] == "Relevant Paper"
```

## Documentation

### Required Documentation

- README.md - Project overview and setup
- API documentation - For all public APIs
- CONTRIBUTING.md - This file
- CHANGELOG.md - Record of notable changes

### Documentation Updates

When contributing, ensure you:
- Update relevant documentation
- Add docstrings to new functions
- Include examples for complex features
- Update CHANGELOG.md for user-facing changes

## Submitting Changes

### Pull Request Guidelines

1. **Title**: Use clear, descriptive titles (e.g., "feat: Add arXiv paper crawler")
2. **Description**: Include:
   - Summary of changes
   - Motivation for the change
   - Testing performed
   - Screenshots (if applicable)
3. **Related Issues**: Link to related issues

### Pull Request Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
Description of testing performed

## Checklist
- [ ] Tests pass locally
- [ ] Documentation updated
- [ ] No breaking changes (or documented)
- [ ] Code follows style guidelines
```

### Review Process

1. Automated checks must pass
2. At least one maintainer approval required
3. Address review feedback promptly
4. Keep PRs focused and small

## Community Guidelines

### Communication Channels

- **Issues**: Bug reports and feature requests
- **Discussions**: General questions and ideas
- **PRs**: Code contributions

### Getting Help

- Check existing issues and discussions
- Read documentation thoroughly
- Ask questions in Discussions
- Be patient and respectful

### Recognition

Contributors are recognized in:
- CONTRIBUTORS.md file
- Release notes for significant contributions
- Project documentation for major features

## Area Stewardship

The project is divided into several key areas:

- **Knowledge Ingestion**: Paper crawlers, data processing
- **Reasoning Engine**: SLM integration, prompt engineering
- **Sandbox**: Docker execution, resource management
- **Reward Engine**: Benchmarking, metrics
- **RL Loop**: Training, policy optimization
- **Self-Improvement**: LoRA fine-tuning, lesson storage

You can specialize in one area or contribute across multiple areas.

## License

By contributing, you agree that your contributions will be licensed under the same license as the project (MIT License).

## Questions?

Feel free to open a discussion or contact maintainers directly. We're happy to help new contributors get started!

Thank you for contributing to Perpetual Scholar Agent!
