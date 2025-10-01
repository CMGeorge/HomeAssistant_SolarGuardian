# SolarGuardian Integration Tests

This directory contains all tests for the SolarGuardian Home Assistant integration.

## Testing Philosophy

**IMPORTANT**: This integration uses **REAL API testing** - no mocks or simulated API responses.

### Why Real API Testing?

1. **Accuracy**: Ensures integration works with actual API behavior
2. **API Changes**: Detects when the SolarGuardian API changes
3. **Real-world Validation**: Tests against actual data structures and responses
4. **Reliability**: Catches issues that mocks might miss

## Setup

### 1. Install Dependencies

```bash
pip install -r ../requirements.txt
pip install pytest pytest-asyncio python-dotenv
```

### 2. Configure API Credentials

1. Copy the `.env.example` file to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and fill in your actual SolarGuardian API credentials:
   ```bash
   APP_KEY=your_actual_app_key_here
   APP_SECRET=your_actual_app_secret_here
   DOMAIN=glapi.mysolarguardian.com  # or openapi.epsolarpv.com for China
   ```

3. Get your API credentials from SolarGuardian web portal:
   - Login to your account
   - Go to: System Management > Personal Information Management > Open API
   - Apply for API credentials (appKey and appSecret)

**CRITICAL**: The `.env` file is in `.gitignore` - NEVER commit it with real credentials!

## Test Structure

```
tests/
├── .env.example           # Template for credentials
├── .env                   # Your credentials (git-ignored)
├── .gitignore            # Ignore credentials and cache
├── pytest.ini            # Pytest configuration
├── README.md             # This file
├── unit/                 # Unit tests
│   ├── test_api.py       # API client unit tests
│   ├── test_config_flow.py
│   ├── test_sensor.py
│   └── test_constants.py
└── integration/          # Integration tests
    ├── test_coordinator.py
    └── test_existing_integration.py
```

## Running Tests

### Run All Tests
```bash
cd tests
pytest
```

### Run Specific Test Categories
```bash
# Unit tests only
pytest unit/

# Integration tests only
pytest integration/

# Specific test file
pytest unit/test_api.py

# Specific test function
pytest unit/test_api.py::TestSolarGuardianAPI::test_authenticate
```

### Run with Verbose Output
```bash
pytest -v
```

### Run with Coverage
```bash
pytest --cov=custom_components.solarguardian --cov-report=html
```

## Test Categories

### Unit Tests (`unit/`)

Test individual components in isolation:
- **`test_api.py`**: API client methods, authentication, rate limiting
- **`test_config_flow.py`**: Configuration flow and options
- **`test_sensor.py`**: Sensor entities and value processing
- **`test_constants.py`**: Constants and configuration values

### Integration Tests (`integration/`)

Test complete workflows with real API:
- **`test_coordinator.py`**: Data coordinator update cycles
- **`test_existing_integration.py`**: Full integration setup and operation

## Writing New Tests

### Example: Real API Test

```python
"""Test with real SolarGuardian API."""
import os
import unittest
from dotenv import load_dotenv

# Load credentials from .env
load_dotenv()

class TestRealAPI(unittest.IsolatedAsyncioTestCase):
    """Test against real SolarGuardian API."""
    
    def setUp(self):
        """Set up test credentials."""
        self.app_key = os.getenv("APP_KEY")
        self.app_secret = os.getenv("APP_SECRET")
        self.domain = os.getenv("DOMAIN", "glapi.mysolarguardian.com")
        
        # Skip test if credentials not provided
        if not self.app_key or not self.app_secret:
            self.skipTest("API credentials not provided in .env")
    
    async def test_authentication(self):
        """Test real authentication."""
        # Add custom_components to path
        import sys
        sys.path.insert(0, '../../custom_components')
        
        from solarguardian.api import SolarGuardianAPI
        
        api = SolarGuardianAPI(self.domain, self.app_key, self.app_secret)
        try:
            result = await api.authenticate()
            self.assertTrue(result)
            self.assertIsNotNone(api._token)
        finally:
            await api.close()
```

### Security Guidelines for Tests

**DO**:
- ✅ Load credentials from `.env` file
- ✅ Skip tests if credentials not provided
- ✅ Mask credentials in log output
- ✅ Use environment variables

**DON'T**:
- ❌ Hard-code credentials in test files
- ❌ Commit `.env` file with real credentials
- ❌ Print full credentials in logs or output
- ❌ Use mock credentials that look real

## Troubleshooting

### Tests Fail with "API credentials not provided"

**Solution**: Create and configure your `.env` file (see Setup above).

### Tests Fail with Connection Errors

**Solutions**:
1. Check your internet connection
2. Verify the DOMAIN in `.env` is correct:
   - International: `glapi.mysolarguardian.com`
   - China: `openapi.epsolarpv.com`
3. Test API connectivity manually:
   ```bash
   curl -I https://glapi.mysolarguardian.com
   ```

### Tests Fail with Authentication Errors

**Solutions**:
1. Verify your APP_KEY and APP_SECRET are correct
2. Check if your API credentials are still active
3. Ensure no extra spaces in `.env` file
4. Try generating new API credentials in SolarGuardian portal

### Rate Limit Errors

**Solution**: The integration includes rate limiting. If you still hit limits:
1. Wait 1-2 minutes between test runs
2. Don't run multiple test tools simultaneously
3. Check if other applications are using the same API key

## API Rate Limits

The SolarGuardian API has these limits:
- **Authentication**: 10 calls per minute (6 seconds between calls)
- **Data Endpoints**: 30 calls per minute (2 seconds between calls)

Our tests respect these limits automatically through the API client's rate limiting.

## Best Practices

1. **Run Tests Regularly**: Test against real API to catch changes
2. **Check API Status**: If many tests fail, check SolarGuardian API status
3. **Update Credentials**: Refresh API credentials if they expire
4. **Report Issues**: If API behavior changes, report to integration maintainer
5. **Clean Test Data**: Tests should not modify production data

## CI/CD Considerations

For continuous integration:
1. Store API credentials as CI secrets
2. Set appropriate timeout limits (API calls can be slow)
3. Run tests on schedule (not every commit) to respect rate limits
4. Consider using dedicated test API account if available

## Additional Resources

- **API Documentation**: `/solarguardian_api.txt` in repository root
- **Troubleshooting**: `/TROUBLESHOOTING.md` in repository root
- **Integration Code**: `/custom_components/solarguardian/`
- **Copilot Instructions**: `/.github/copilot-instructions.md`

## Support

If you encounter issues with tests:
1. Check this README for troubleshooting steps
2. Review logs for error details
3. Verify API credentials are valid
4. Check network connectivity to API servers
5. Report persistent issues on GitHub with:
   - Test output (with credentials masked)
   - Error messages
   - API domain being used
   - Home Assistant version

---

**Remember**: These tests use REAL API calls. Always use valid credentials and respect rate limits!