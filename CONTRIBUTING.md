# Contributing to Amdusias Discord DJ Bot

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and grow

## Getting Started

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/yourusername/Amdusias-Discord-DJ-Bot.git
   cd Amdusias-Discord-DJ-Bot
   ```

3. Set up development environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # or venv\Scripts\activate on Windows
   pip install -r requirements.txt
   ```

4. Create a feature branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```

## Development Workflow

### Before You Code

1. Check existing issues to avoid duplicates
2. Open an issue to discuss major changes
3. Read [CLAUDE.md](CLAUDE.md) for best practices

### Writing Code

1. Follow PEP 8 style guide
2. Use type hints for all functions
3. Write docstrings for all public APIs
4. Keep functions small and focused
5. Use meaningful variable names

### Writing Tests

1. Write tests for all new functions
2. Maintain 80%+ code coverage
3. Use descriptive test names
4. Mock external dependencies
5. Test edge cases and error conditions

Example test:
```python
def test_get_env_var_required_exists(self) -> None:
    """Test getting required environment variable that exists."""
    with patch.dict(os.environ, {'TEST_VAR': 'test_value'}):
        result = ConfigLoader.get_env_var('TEST_VAR')
        assert result == 'test_value'
```

### Running Tests Locally

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_config.py

# Run specific test
pytest tests/test_config.py::TestConfigLoader::test_load_config_success
```

### Code Quality Checks

Before committing, run:

```bash
# Format code
black src tests

# Type check
mypy src

# Lint
flake8 src tests

# Run all checks together
black src tests && mypy src && flake8 src tests && pytest --cov=src
```

### Commit Messages

Use [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `test:` Adding or updating tests
- `refactor:` Code refactoring
- `style:` Code style changes
- `chore:` Maintenance tasks
- `perf:` Performance improvements

Examples:
```
feat: add support for multiple audio streams
fix: resolve connection timeout issue
docs: update installation instructions
test: add tests for stream reconnection
```

### Pull Request Process

1. Update documentation if needed
2. Add tests for new features
3. Ensure all tests pass
4. Update CHANGELOG.md if applicable
5. Push to your fork
6. Open a Pull Request with:
   - Clear title describing the change
   - Description of what changed and why
   - Reference to related issues
   - Screenshots for UI changes

### Pull Request Checklist

Before submitting, ensure:

- [ ] Code follows project style guidelines
- [ ] All tests pass locally
- [ ] New tests added for new features
- [ ] Code coverage is at least 80%
- [ ] Type hints added to all functions
- [ ] Docstrings added to all public functions
- [ ] No secrets or credentials in code
- [ ] Documentation updated if needed
- [ ] Commit messages follow conventions
- [ ] Code formatted with black
- [ ] No linting errors
- [ ] No type errors from mypy

## Project Structure

Understanding the codebase:

```
src/
├── config.py                  # Environment variable management
├── audio_device.py            # Audio device enumeration (WASAPI + DirectShow)
├── audio_sources.py           # Audio source implementations (WASAPI, Local, URL)
├── audio_source_factory.py    # Factory for creating audio sources
└── bot.py                     # Discord bot commands

tests/
├── test_config.py
├── test_audio_device.py
├── test_audio_sources.py
├── test_audio_source_factory.py
└── test_bot.py
```

## Testing Guidelines

### Unit Tests

- Test individual functions in isolation
- Mock all external dependencies
- Use fixtures for common setup
- One assertion per test (when possible)
- Test happy path and error cases

### Test Organization

```python
class TestClassName:
    """Tests for ClassName class."""

    @pytest.fixture
    def mock_dependency(self) -> MockType:
        """Create mock dependency."""
        return MockType()

    def test_method_name_scenario(self) -> None:
        """Test method_name with specific scenario."""
        # Arrange
        # Act
        # Assert
```

### Async Testing

For async functions:

```python
@pytest.mark.asyncio
async def test_async_function(self) -> None:
    """Test async function."""
    result = await async_function()
    assert result == expected
```

### Mocking

Use pytest-mock or unittest.mock:

```python
def test_with_mock(self) -> None:
    """Test with mocked dependency."""
    with patch('module.function') as mock_func:
        mock_func.return_value = 'mocked'
        result = function_under_test()
        assert result == 'expected'
        mock_func.assert_called_once()
```

## Documentation

### Code Documentation

All public functions need docstrings:

```python
def function_name(param1: str, param2: int) -> bool:
    """Short description of what the function does.

    Longer description if needed. Explain the purpose,
    not just what the code does.

    Args:
        param1: Description of param1.
        param2: Description of param2.

    Returns:
        Description of return value.

    Raises:
        ValueError: When param1 is invalid.
    """
```

### README Updates

Update README.md when:
- Adding new features
- Changing setup process
- Adding new dependencies
- Changing configuration

## Reporting Bugs

When reporting bugs, include:

1. Description of the bug
2. Steps to reproduce
3. Expected behavior
4. Actual behavior
5. Environment (OS, Python version)
6. Relevant logs or error messages
7. Screenshots if applicable

Use the bug report template when creating issues.

## Suggesting Features

When suggesting features:

1. Check if already requested
2. Describe the problem it solves
3. Describe the proposed solution
4. Consider alternatives
5. Explain impact on existing functionality

## Questions?

- Check existing issues and discussions
- Read [CLAUDE.md](CLAUDE.md) for technical details
- Read [README.md](README.md) for usage information
- Open an issue for questions

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Recognition

Contributors will be recognized in:
- README.md Contributors section
- Release notes for significant contributions

Thank you for contributing to Amdusias Discord DJ Bot!
