# Contributing to SolarGuardian Home Assistant Integration

Thank you for your interest in contributing! This document provides guidelines for contributing to this project.

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/HomeAssistant_SolarGuardian.git
   cd HomeAssistant_SolarGuardian
   ```
3. **Create a branch** for your feature or fix:
   ```bash
   git checkout -b feature/your-feature-name
   ```

## Development Setup

### Prerequisites

- Python 3.12 or higher
- Home Assistant 2025.9.0 or higher
- SolarGuardian API credentials (for testing)

### Install Development Dependencies

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
pip install pre-commit
pre-commit install
```

### Testing Setup

Create a `.env` file in the `tests/` directory:

```bash
APP_KEY=your_test_app_key
APP_SECRET=your_test_app_secret
DOMAIN=glapi.mysolarguardian.com  # or openapi.epsolarpv.com
```

**IMPORTANT**: Never commit the `.env` file! It's git-ignored for security.

## Code Standards

### Python Style

- Follow **PEP 8** style guidelines
- Use **Black** for code formatting (line length: 88)
- Use **isort** for import sorting
- Use **Ruff** for linting

Run formatters before committing:

```bash
black custom_components/solarguardian/
isort custom_components/solarguardian/
ruff check custom_components/solarguardian/ --fix
```

Or use pre-commit (automatically runs on commit):

```bash
pre-commit run --all-files
```

### Type Hints

- Use type hints for all function parameters and return values
- Use `from __future__ import annotations` at the top of files

### Docstrings

- Use Google-style docstrings
- Document all public functions and classes
- Include examples for complex functionality

Example:

```python
async def get_devices(self, station_id: int) -> dict:
    """Get all devices for a power station.

    Args:
        station_id: The ID of the power station.

    Returns:
        Dict containing device list and metadata.

    Raises:
        SolarGuardianAPIError: If API request fails.
    """
```

## Testing Requirements

### Test Categories

1. **Unit Tests** (`tests/unit/`): Test individual components
2. **Integration Tests** (`tests/integration/`): Test with real API

### Running Tests

**Unit Tests** (fast, no API required):

```bash
pytest tests/unit/ -v
```

**Integration Tests** (requires API credentials):

```bash
pytest tests/integration/ -v
```

**All Tests**:

```bash
pytest tests/ -v
```

**With Coverage**:

```bash
pytest tests/ -v --cov=custom_components/solarguardian --cov-report=html
```

### Testing Guidelines

- ✅ **Always test with real API** - No mocks for API testing
- ✅ Write tests for new features
- ✅ Update tests when changing existing code
- ✅ Test edge cases and error conditions
- ❌ Never mock the SolarGuardian API in tests

## Security Guidelines

### NEVER Commit Sensitive Data

- ❌ API keys (appKey, appSecret)
- ❌ Access tokens
- ❌ User credentials
- ❌ Device serial numbers (when identifiable)

### Log Safely

```python
# ❌ WRONG
_LOGGER.debug(f"Using API key: {api_key}")

# ✅ CORRECT
_LOGGER.debug(f"Using API key: {api_key[:8]}...")
```

### Use Environment Variables

```python
import os
from dotenv import load_dotenv

load_dotenv()
app_key = os.getenv("APP_KEY")
```

## Commit Message Guidelines

Follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- **feat**: New feature
- **fix**: Bug fix
- **docs**: Documentation changes
- **style**: Code style changes (formatting, etc.)
- **refactor**: Code refactoring
- **test**: Adding or updating tests
- **chore**: Maintenance tasks

### Examples

```
feat(sensor): Add battery temperature sensor

Added support for battery temperature monitoring using the
BatteryTemperature data identifier.

Closes #123
```

```
fix(api): Handle 404 errors from latest data endpoint

The latest data endpoint returns 404 on some API servers.
Added graceful fallback and error handling.

Fixes #456
```

## Pull Request Process

1. **Update documentation** if needed
2. **Add tests** for new functionality
3. **Run all tests** and ensure they pass
4. **Run formatters** (Black, isort, Ruff)
5. **Update CHANGELOG.md** with your changes
6. **Create Pull Request** with clear description

### PR Template

```markdown
## Description

Brief description of changes

## Type of Change

- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing

- [ ] Tested with real API
- [ ] Unit tests pass
- [ ] Integration tests pass

## Checklist

- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] Tests added/updated
```

## API Integration Guidelines

### Rate Limits

- **Authentication**: 10 calls/minute (6 seconds between calls)
- **Data Endpoints**: 30 calls/minute (2 seconds between calls)

### Error Handling

```python
try:
    result = await self.api.get_something()
except SolarGuardianAPIError as err:
    if "404" in str(err):
        # Handle missing endpoint
    elif "5126" in str(err):
        # Handle rate limit
    else:
        # Log error
        _LOGGER.error("API error: %s", err)
```

### API Documentation

Refer to `/solarguardian_api.txt` for endpoint details.

## Home Assistant Guidelines

- Follow [Home Assistant Development Guidelines](https://developers.home-assistant.io/)
- Use `DataUpdateCoordinator` for data fetching
- Implement proper config flow
- Add translations for all user-facing strings
- Test with Home Assistant 2025.9.x

## Documentation

- Update `README.md` for user-facing changes
- Update `INSTALLATION.md` for setup changes
- Create documentation files for major features
- Include code examples where helpful

## Community

- Be respectful and inclusive
- Help other contributors
- Share knowledge and discoveries
- Document API quirks and solutions

## Questions?

- Open a [GitHub Discussion](https://github.com/CMGeorge/HomeAssistant_SolarGuardian/discussions)
- Check existing [Issues](https://github.com/CMGeorge/HomeAssistant_SolarGuardian/issues)
- Review documentation in `/docs` directory

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing! 🌞🔋
