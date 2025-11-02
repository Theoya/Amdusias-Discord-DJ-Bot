# Development Best Practices - Amdusias Discord DJ Bot

This document outlines the coding standards, testing practices, and architectural principles for the Amdusias Discord DJ Bot project.

## Code Standards

### Python Style Guide

- Follow PEP 8 style guidelines
- Use type hints for all function signatures
- Maximum line length: 127 characters
- Use meaningful variable and function names
- Classes use PascalCase, functions/variables use snake_case

### Type Hints

All functions must include complete type hints:

```python
def function_name(param1: str, param2: int) -> bool:
    """Docstring describing the function."""
    return True
```

### Documentation

- Every module must have a module-level docstring
- Every class must have a class-level docstring
- Every public function/method must have a docstring following Google style:
  - Summary line
  - Args section (if applicable)
  - Returns section (if applicable)
  - Raises section (if applicable)

Example:
```python
def get_env_var(key: str, default: Optional[str] = None, required: bool = True) -> str:
    """Get environment variable with optional default.

    Args:
        key: Environment variable name.
        default: Default value if variable is not set.
        required: Whether the variable is required.

    Returns:
        Environment variable value.

    Raises:
        ValueError: If required variable is not set.
    """
    pass
```

## Testing Standards

### Test Coverage

- Minimum 80% code coverage required
- Every function must have at least one direct test
- Tests run automatically on every PR via GitHub Actions

### Test Structure

- Use pytest as the testing framework
- Tests located in `tests/` directory
- Test files named `test_*.py`
- Test classes named `Test*`
- Test functions named `test_*`

### Mockable Design

All classes must be designed for mockability:

1. **Use dependency injection**: Pass dependencies as constructor parameters
2. **Use protocols**: Define interfaces using `typing.Protocol` for easy mocking
3. **Avoid global state**: Keep state contained within class instances
4. **Separate concerns**: Each class should have a single, well-defined responsibility

Example:
```python
from typing import Protocol

class StreamReaderProtocol(Protocol):
    """Protocol for stream readers (for testing/mocking)."""

    async def read_stream(self, chunk_size: int) -> AsyncGenerator[bytes, None]:
        ...

class AudioSource:
    def __init__(self, stream_reader: StreamReaderProtocol) -> None:
        self._stream_reader = stream_reader
```

### Test Organization

Each test module should:
- Import only what's needed
- Use fixtures for common setup
- Group related tests in classes
- Test one behavior per test function
- Use descriptive test names that explain what's being tested

Example:
```python
class TestConfigLoader:
    """Tests for ConfigLoader class."""

    def test_get_env_var_required_exists(self) -> None:
        """Test getting required environment variable that exists."""
        # Test implementation
```

## Architecture Principles

### Separation of Concerns

- **Configuration** (`src/config.py`): All environment variable loading and validation
- **Audio Device Enumeration** (`src/audio_device.py`): Device detection and WASAPI loopback
- **Audio Sources** (`src/audio_sources.py`): Audio source implementations (WASAPI, Local, URL)
- **Audio Source Factory** (`src/audio_source_factory.py`): Factory for creating audio sources
- **Bot Logic** (`src/bot.py`): Discord bot commands and event handling
- **Entry Point** (`main.py`): Application startup and error handling

### Async/Await

- Use `async/await` for all I/O operations
- Network calls (HTTP, Discord) must be async
- Use `AsyncMock` for testing async functions
- Mark test functions with `@pytest.mark.asyncio`

### Error Handling

1. **Fail fast**: Validate configuration at startup
2. **Descriptive errors**: Include context in error messages
3. **Graceful degradation**: Handle network failures gracefully
4. **Logging**: Log all errors with appropriate levels

Example:
```python
try:
    await self._stream_reader.connect()
except Exception as e:
    logger.error(f"Failed to connect to stream: {e}")
    raise
```

### Dependency Management

- Pin exact versions in `requirements.txt`
- Keep dependencies minimal
- Group dependencies by purpose (core, testing, quality)

## Git Workflow

### Branches

- `main`: Production-ready code
- Feature branches: `feature/description`
- Bugfix branches: `bugfix/description`

### Pull Requests

All PRs must:
1. Pass all automated tests
2. Pass linting (flake8)
3. Pass type checking (mypy)
4. Pass code formatting check (black)
5. Maintain or improve code coverage

### Commit Messages

Follow conventional commits:
- `feat:` New feature
- `fix:` Bug fix
- `test:` Adding or updating tests
- `docs:` Documentation changes
- `refactor:` Code refactoring
- `chore:` Maintenance tasks

## Security

### Secrets Management

- Never commit secrets to the repository
- All sensitive data in `.env` file
- `.env` file is in `.gitignore`
- Provide `.env.example` with placeholder values
- Document all required environment variables

### Bot Token Security

- Use environment variables for Discord bot token
- Never log or print the bot token
- Rotate tokens if accidentally exposed

## Configuration

### Environment Variables

All configuration through environment variables:
- Required variables must be validated at startup
- Provide sensible defaults where possible
- Document all variables in `.env.example`

### Validation

Configuration validation happens at startup:
```python
config = ConfigLoader.load_config()  # Raises ValueError if invalid
```

## Logging

### Log Levels

- `DEBUG`: Detailed diagnostic information
- `INFO`: General informational messages
- `WARNING`: Warning messages for potentially harmful situations
- `ERROR`: Error messages for serious problems

### Log Format

Use consistent format with timestamp, logger name, level, and message:
```
%(asctime)s - %(name)s - %(levelname)s - %(message)s
```

## Performance Considerations

### Bandwidth Optimization

The bot streams audio to multiple users. Consider:
- Each listener receives a unicast stream from Discord's servers
- Your uplink bandwidth limits total listeners
- Use appropriate bitrate (128 kbps recommended)
- Formula: `Max listeners ≈ (uplink_Mbps × 1000) / (audio_kbps × 1.1)`

### Latency

- MP3 128 kbps: Universal compatibility, ~2-3 seconds latency
- Opus codec: Better quality per bit, modern browser compatible
- Use FFmpeg reconnection options for stream stability

## Development Setup

### Initial Setup

1. Clone the repository
2. Create virtual environment: `python -m venv venv`
3. Activate: `venv\Scripts\activate` (Windows) or `source venv/bin/activate` (Linux/Mac)
4. Install dependencies: `pip install -r requirements.txt`
5. Copy `.env.example` to `.env` and configure

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Run specific test file
pytest tests/test_config.py

# Run with verbose output
pytest -v
```

### Code Quality Checks

```bash
# Format code
black src tests

# Check formatting
black --check src tests

# Lint code
flake8 src tests

# Type check
mypy src
```

## Code Review Checklist

Before submitting a PR, ensure:

- [ ] All tests pass locally
- [ ] Code is formatted with black
- [ ] No linting errors from flake8
- [ ] No type errors from mypy
- [ ] All new functions have type hints
- [ ] All new functions have docstrings
- [ ] All new functions have unit tests
- [ ] Code coverage is at least 80%
- [ ] No secrets in code or commits
- [ ] `.env.example` updated if new config added

## Continuous Integration

GitHub Actions runs on every PR:
1. Tests on Python 3.10, 3.11, 3.12
2. Linting with flake8
3. Type checking with mypy
4. Code coverage reporting
5. Code formatting check with black

All checks must pass before merging.
