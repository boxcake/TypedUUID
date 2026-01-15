# Contributing to TypedUUID

Thank you for your interest in contributing to TypedUUID! This guide will help you get started.

## Development Setup

### Prerequisites

- Python 3.10 or higher
- Git

### Setting Up Your Environment

1. **Fork and clone the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/TypedUUID.git
   cd TypedUUID
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install development dependencies**
   ```bash
   pip install -e ".[all,dev]"
   ```

4. **Verify the setup**
   ```bash
   pytest
   ```

## Development Workflow

### Branching Strategy

- `main` - Stable release branch
- `dev` - Integration branch for testing
- `feature/*` - Feature branches

**Workflow:**
```
feature/your-feature → dev → main
```

### Creating a Feature Branch

```bash
git checkout dev
git pull origin dev
git checkout -b feature/your-feature-name
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=typed_uuid --cov-report=term

# Run specific test file
pytest tests/test_core.py

# Run specific test
pytest tests/test_core.py::TestTypedUUIDInstantiation::test_create_with_no_args
```

### Code Style

We use [ruff](https://github.com/astral-sh/ruff) for linting:

```bash
# Check for issues
ruff check typed_uuid/

# Auto-fix issues
ruff check --fix typed_uuid/
```

### Type Hints

All public functions should include type hints. The codebase uses standard Python typing.

## Submitting Changes

### Pull Request Process

1. **Ensure tests pass locally**
   ```bash
   pytest
   ruff check typed_uuid/
   ```

2. **Update documentation** if needed (README.md, docstrings)

3. **Update CHANGELOG.md** with your changes under `[Unreleased]`

4. **Create a pull request** targeting `dev` branch
   - Use a clear, descriptive title
   - Reference any related issues
   - Describe what changes you made and why

### Commit Messages

Write clear, concise commit messages:

```
Add feature X for Y functionality

- Detailed point about the change
- Another detail if needed
```

**Good examples:**
- `Add UUID7 support with timestamp extraction`
- `Fix thread safety issue in class registry`
- `Update README with short encoding examples`

**Avoid:**
- `Fix bug`
- `Update code`
- `WIP`

## Adding New Features

### Adapters

To add a new framework adapter:

1. Create `typed_uuid/adapters/your_framework.py`
2. Follow the pattern in existing adapters (sqlalchemy.py, pydantic.py)
3. Add the adapter to `create_typed_uuid_class()` in core.py
4. Add optional dependency to pyproject.toml
5. Add tests in `tests/test_adapters.py`
6. Update README.md with usage examples

### Core Features

For changes to core functionality:

1. Update `typed_uuid/core.py`
2. Add comprehensive tests
3. Update docstrings and type hints
4. Update README.md if it affects the public API

## Testing Guidelines

- Aim for high test coverage on new code
- Include both positive and negative test cases
- Test edge cases (empty strings, None values, etc.)
- For adapters, tests should skip gracefully if the framework isn't installed

Example test structure:
```python
class TestYourFeature:
    """Tests for your feature."""

    def test_basic_functionality(self):
        """Test the happy path."""
        ...

    def test_edge_case(self):
        """Test edge case handling."""
        ...

    def test_error_handling(self):
        """Test that errors are raised appropriately."""
        with pytest.raises(ExpectedError):
            ...
```

## Questions?

- Open an issue for bugs or feature requests
- Start a discussion for questions or ideas

Thank you for contributing!
