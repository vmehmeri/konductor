# Contributing to Konductor

Thank you for your interest in contributing to Konductor! This document provides guidelines and information for contributors.

## 📋 Table of Contents

- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Code Style and Quality](#code-style-and-quality)
- [Testing](#testing)
- [Submitting Changes](#submitting-changes)
- [Project Structure](#project-structure)
- [Adding New Providers](#adding-new-providers)
- [Documentation](#documentation)

## 🚀 Getting Started

### Prerequisites

- Python 3.12 or higher
- [uv](https://docs.astral.sh/uv/) (Python package manager)
- Git

### Fork and Clone

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/your-username/konductor.git
   cd konductor
   ```

## 🛠️ Development Setup

### Install Dependencies

```bash
# Install all development dependencies
uv sync --extra dev

# Or install only test dependencies
uv sync --extra test
```

### Environment Variables

For Google ADK development:
```bash
export GOOGLE_API_KEY=<your-api-key>
```

### Verify Setup

```bash
# Run tests to verify everything works
uv run pytest

# Generate code from an example
uv run python -m konductor.cli generate examples/simple_agent_stack.yaml
```

## 🎨 Code Style and Quality

Konductor follows code quality standards using black, pylint, isort, and mypy.

### Before Committing

**Always run these commands before committing:**

```bash
# Format code
uv run black .

# Sort imports
uv run isort .

# Lint code
uv run pylint konductor/

# Type check
uv run mypy konductor/

# Run tests
uv run pytest
```

### All-in-One Quality Check

```bash
# Run all quality checks at once
uv run black --check . && uv run isort --check-only . && uv run pylint konductor/ && uv run mypy konductor/ && uv run pytest
```

### Code Style Guidelines

1. **Formatting**: Code is formatted with `black` (line length: 100)
2. **Import Sorting**: Imports are sorted with `isort` (black-compatible profile)
3. **Linting**: Code must pass `pylint` checks
4. **Type Hints**: All functions should have type hints (checked with `mypy`)
5. **Docstrings**: All public functions, classes, and modules should have docstrings

### Naming Conventions

- **Python**: Follow PEP 8 naming conventions
- **Agent Names**: Use underscores, not hyphens (ADK requirement: `my_agent` not `my-agent`)
- **Files**: Use snake_case for Python files
- **Classes**: Use PascalCase
- **Functions/Variables**: Use snake_case

## 🧪 Testing

Konductor has a test suite with multiple test categories.

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=konductor

# Run specific test categories
uv run pytest -m unit          # Unit tests only
uv run pytest -m integration   # Integration tests only
uv run pytest -m "not slow"    # Skip slow tests

# Run tests for specific components
uv run pytest tests/core/              # Core functionality
uv run pytest tests/providers/         # Provider tests
uv run pytest tests/test_cli.py        # CLI tests
```

### Test Categories

- **Unit Tests** (`tests/core/`, `tests/providers/`): Test individual components
- **Integration Tests** (`tests/test_integration.py`): Test end-to-end workflows
- **CLI Tests** (`tests/test_cli.py`): Test command-line interface

### Writing Tests

1. **Location**: Place tests in the appropriate directory under `tests/`
2. **Naming**: Test files should start with `test_`
3. **Structure**: Use classes to group related tests
4. **Fixtures**: Use `tests/fixtures/` for reusable test data
5. **Mocking**: Mock external dependencies and file operations

### Test Guidelines

```python
# Good test structure
class TestMyComponent:
    """Test the MyComponent class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.component = MyComponent()
    
    def test_specific_behavior(self):
        """Test a specific behavior with clear assertions."""
        result = self.component.do_something()
        assert result.status == "success"
        assert len(result.items) == 2
```

## 📝 Submitting Changes

### Workflow

1. **Create a branch** for your feature/fix:
   ```bash
   git checkout -b feature/my-feature
   ```

2. **Make your changes** following the guidelines above

3. **Run quality checks**:
   ```bash
   uv run black . && uv run isort . && uv run pylint konductor/ && uv run mypy konductor/ && uv run pytest
   ```

4. **Commit your changes** with a clear message:
   ```bash
   git commit -m "feat: add support for new agent type"
   ```

5. **Push to your fork**:
   ```bash
   git push origin feature/my-feature
   ```

6. **Create a Pull Request** on GitHub

### Commit Message Format

Follow conventional commit format:

- `feat:` New features
- `fix:` Bug fixes
- `docs:` Documentation changes
- `style:` Code style changes (formatting, etc.)
- `refactor:` Code refactoring
- `test:` Adding or updating tests
- `chore:` Maintenance tasks

### Pull Request Guidelines

1. **Title**: Clear, descriptive title
2. **Description**: Explain what changes you made and why
3. **Tests**: Include tests for new functionality
4. **Documentation**: Update documentation if needed
5. **Quality**: Ensure all quality checks pass

## 🏗️ Project Structure

Understanding the codebase structure:

```
konductor/
├── konductor/                      # Main package
│   ├── core/                      # Provider-agnostic components
│   │   ├── models.py             # Resource models (Pydantic)
│   │   ├── parser.py             # Manifest parser
│   │   └── generator.py          # Generation orchestrator
│   ├── providers/                 # Framework-specific implementations
│   │   ├── base.py               # Provider interface
│   │   └── google_adk/           # Google ADK provider
│   │       ├── generator.py      # ADK code generator
│   │       ├── models.py         # ADK-specific models
│   │       └── templates/        # Jinja2 templates
│   └── cli.py                    # Command-line interface
├── tests/                         # Test suite
│   ├── core/                     # Core component tests
│   ├── providers/                # Provider tests
│   └── fixtures/                 # Test data
├── examples/                      # Example manifests
└── tools/                        # Example tool implementations
```

### Key Concepts

- **Providers**: Framework-specific implementations (Google ADK, future: LangChain, etc.)
- **Resources**: YAML manifest components (Tools, Models, Agents)
- **Templates**: Jinja2 templates for code generation
- **Registry**: Dynamic provider registration system

## 🔌 Adding New Providers

To add support for a new AI framework:

1. **Create provider directory**:
   ```
   konductor/providers/my_framework/
   ├── __init__.py
   ├── generator.py      # Inherit from CodeGenerator
   ├── models.py        # Framework-specific models (optional)
   └── templates/       # Jinja2 templates
   ```

2. **Implement CodeGenerator**:
   ```python
   from ..base import CodeGenerator
   
   class MyFrameworkGenerator(CodeGenerator):
       def generate_code(self, manifest, output_dir, **kwargs):
           # Implementation
           pass
       
       def get_required_dependencies(self):
           return ["my-framework>=1.0.0"]
       
       def validate_manifest_for_provider(self, manifest):
           # Framework-specific validation
           return []
   ```

3. **Register the provider**:
   ```python
   # In konductor/__init__.py
   from .providers.my_framework.generator import MyFrameworkGenerator
   provider_registry.register("my_framework", MyFrameworkGenerator())
   ```

4. **Add tests**:
   ```
   tests/providers/my_framework/
   └── test_generator.py
   ```

## 📚 Documentation

### Types of Documentation

1. **Code Documentation**: Docstrings in code
2. **API Documentation**: In docstrings and type hints
3. **User Documentation**: README.md and examples
4. **Developer Documentation**: This file and CLAUDE.md

### Documentation Standards

- **Docstrings**: Use Google-style docstrings
- **Type Hints**: All public functions should have type hints
- **Examples**: Include usage examples in docstrings
- **CLAUDE.md**: Update for significant architecture changes

### Example Documentation

```python
def parse_manifest(self, file_path: str) -> ParsedManifest:
    """Parse a YAML manifest file into structured resources.
    
    Args:
        file_path: Path to the YAML manifest file to parse
        
    Returns:
        ParsedManifest containing all parsed resources
        
    Raises:
        FileNotFoundError: If the manifest file doesn't exist
        ValidationError: If the manifest contains invalid resources
        
    Example:
        >>> parser = ManifestParser()
        >>> manifest = parser.parse_manifest("my_agents.yaml")
        >>> print(f"Found {len(manifest.llm_agents)} agents")
    """
```

## 🤝 Community Guidelines

### Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and grow
- Assume good intentions

### Getting Help

- **Issues**: Create GitHub issues for bugs or feature requests
- **Discussions**: Use GitHub Discussions for questions
- **Documentation**: Check README.md and CLAUDE.md first

### Review Process

All contributions go through code review:

1. **Automated checks**: CI runs quality checks and tests
2. **Manual review**: Maintainers review code and design
3. **Feedback**: Address review comments
4. **Approval**: Once approved, changes are merged

## 🔄 Development Workflow Tips

### Pre-commit Hook (Recommended)

Set up automatic quality checks:

```bash
echo '#!/bin/bash
uv run black --check . && uv run isort --check-only . && uv run pylint konductor/' > .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

### VS Code Setup

Recommended extensions:
- Python
- Pylint
- Black Formatter
- isort

Settings:
```json
{
    "python.formatting.provider": "black",
    "python.linting.pylintEnabled": true,
    "python.linting.enabled": true
}
```

### Development Commands Reference

```bash
# Setup
uv sync --extra dev

# Quality checks
uv run black .                           # Format code
uv run isort .                          # Sort imports  
uv run pylint konductor/                # Lint code
uv run mypy konductor/                  # Type check

# Testing
uv run pytest                           # Run all tests
uv run pytest --cov=konductor          # Run with coverage
uv run pytest -k "test_name"           # Run specific test

# CLI testing
uv run python -m konductor.cli generate examples/simple_agent_stack.yaml
uv run python -m konductor.cli list-providers
```

Thank you for contributing to Konductor! 🎉