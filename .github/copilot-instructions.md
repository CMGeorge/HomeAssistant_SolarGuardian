# GitHub Copilot Instructions for SolarGuardian Home Assistant Integration

## Project Overview

This is a Home Assistant custom integration for Epever Solar inverters using the SolarGuardian API V2.3. The integration enables real-time monitoring of solar inverters, batteries, and power systems through the cloud-based SolarGuardian platform.

**Target Platform**: Home Assistant 2025.9.x  
**Python Version**: Only versions provided by Home Assistant 2025.9.x (Python 3.12+)  
**API Version**: SolarGuardian API V2.3  
**API Documentation**: See `/solarguardian_api.txt` (converted from PDF)

## Critical Development Rules

### 1. Security & Secrets Management

**NEVER** include or expose sensitive data in:
- Code files
- Log messages
- Commit messages
- Documentation
- Test files (except from `.env`)

**Sensitive Data Includes**:
- `appKey` / `APP_KEY` / API Keys
- `appSecret` / `APP_SECRET` / API Secrets
- Access tokens
- User credentials
- Device serial numbers (when identifiable)

**Correct Practices**:
```python
# ❌ WRONG - Don't log secrets
_LOGGER.debug(f"Using app_key: {app_key}")

# ✅ CORRECT - Mask secrets
_LOGGER.debug(f"Using app_key: {app_key[:8]}..." if len(app_key) > 8 else "***")

# ✅ CORRECT - Use environment variables for tests
import os
from dotenv import load_dotenv
load_dotenv()
app_key = os.getenv("APP_KEY")
```

### 2. Testing Strategy

**All tests use REAL API - NO MOCKS**

- Tests are located in `/tests` directory only
- Test credentials stored in `/tests/.env` file
- No mock data for API testing (integration may create mock data for fallback only)
- Real API calls to verify actual functionality

**Test Structure**:
```
tests/
├── .env                    # API credentials (git-ignored)
├── unit/                   # Unit tests
│   ├── test_api.py        # API client tests
│   ├── test_config_flow.py
│   └── test_sensor.py
└── integration/            # Integration tests
    ├── test_coordinator.py
    └── test_existing_integration.py
```

**Test Files That Should NOT Exist in Root**:
- Any `test_*.py` files in root
- Any `run_*_tests.py` files in root
- Move them to `/tests` directory

### 3. API Integration Guidelines

#### API Rate Limits (MUST RESPECT)
- **Authentication**: 10 calls per minute (6 seconds between calls)
- **Data Endpoints**: 30 calls per minute (2 seconds between calls)
- Implementation: Use `_rate_limit_auth()` and `_rate_limit_data()` in API client

#### API Domains
- **China**: `openapi.epsolarpv.com`
- **International**: `glapi.mysolarguardian.com`

#### Key API Endpoints

1. **Authentication** (POST)
   ```
   /epCloud/user/getAuthToken
   Body: {"appKey": "...", "appSecret": "..."}
   Returns: {"status": 0, "data": {"X-Access-Token": "..."}}
   Token expires in 2 hours
   ```

2. **Power Stations** (POST)
   ```
   /epCloud/vn/openApi/getPowerStationListPage
   Headers: {"X-Access-Token": "...", "Content-Type": "application/json"}
   Body: {"pageNo": 1, "pageSize": 100}
   ```

3. **Devices/Equipment** (POST)
   ```
   /epCloud/vn/openApi/getEquipmentList
   Body: {"powerStationId": 123, "pageNo": 1, "pageSize": 100}
   ```

4. **Device Parameters** (POST)
   ```
   /epCloud/vn/openApi/getEquipment
   Body: {"id": 456}
   Returns device configuration and parameter structure
   ```

5. **Latest Data** (POST) - **Special Port Configuration**
   ```
   https://{domain}:7002/history/lastDatapoint
   
   Method 1 - By Data Identifiers:
   Body: {"id": device_id, "dataIdentifiers": ["OutputPower", "InputVoltage"]}
   
   Method 2 - By Data Points:
   Body: {"devDatapoints": [{"dataPointId": 123, "deviceNo": "..."}]}
   
   IMPORTANT: Both methods MUST use port 7002, not standard HTTPS port
   ```

#### API Response Structure
```python
# Success response
{
    "status": 0,  # 0 = success, non-zero = error
    "data": {...},
    "info": "ok"
}

# Error codes to handle
# 200 - Success
# 500 - Internal server error
# 5002 - No parameters found
# 5004 - Insufficient permissions
# 5017 - Parameter error
# 5106 - Incomplete parameters
# 5126 - Too frequent requests (rate limit)
# 5144 - Defense mechanism triggered
# 5148 - Wrong content-type
```

#### Handling Latest Data Endpoint Issues

The latest data endpoint often returns 404 errors on some API servers:

```python
# ✅ CORRECT - Handle 404 gracefully
try:
    latest_data = await self.api.get_latest_data_by_datapoints(dev_datapoints)
except SolarGuardianAPIError as err:
    if "404" in str(err):
        # API doesn't support latest data - disable and retry later
        self._latest_data_failures += 1
        if self._latest_data_failures >= self._max_latest_data_failures:
            self._latest_data_disabled = True
            _LOGGER.warning("Latest data endpoint not available, disabling")
    else:
        # Real error - log and continue
        _LOGGER.warning("Failed to get latest data: %s", err)
```

### 4. Home Assistant Integration Standards

#### Platform Requirements
- **Home Assistant**: 2025.9.0+
- **Dependencies**: `aiohttp>=3.8.0` only
- **Config Flow**: Required (no YAML configuration)
- **IoT Class**: `cloud_polling`
- **Update Interval**: 15 seconds (default) - configurable 15-300 seconds
- **Rate Limits**: Respects API limits (10 auth/min, 30 data/min)

#### Entity Naming Convention
```python
# Device Name + Sensor Type
f"{device['equipmentName']} {sensor_config['name']}"
# Example: "Solar Inverter 1 Output Power"

# Unique ID: Device ID + Data Identifier
f"{device['id']}_{variable['dataIdentifier']}"
# Example: "12345_OutputPower"
```

#### Sensor Configuration
```python
SENSOR_TYPES = {
    "OutputPower": {
        "name": "Output Power",
        "unit": UnitOfPower.WATT,
        "device_class": SensorDeviceClass.POWER,
        "state_class": SensorStateClass.MEASUREMENT,
        "icon": "mdi:solar-power",
    },
    # ... more sensor types
}
```

#### Data Coordinator Pattern
```python
class SolarGuardianDataUpdateCoordinator(DataUpdateCoordinator):
    """Manage fetching data from API."""
    
    async def _async_update_data(self):
        """Fetch data from API."""
        # 1. Authenticate (uses cached token if valid)
        await self.api.authenticate()
        
        # 2. Get power stations
        stations = await self.api.get_power_stations()
        
        # 3. For each station, get devices
        for station in stations["data"]["list"]:
            devices = await self.api.get_devices(station["id"])
            
            # 4. For each device, get parameters and latest data
            for device in devices["data"]["list"]:
                params = await self.api.get_device_parameters(device["id"])
                latest = await self.api.get_latest_data(...)
```

### 5. Error Handling Best Practices

#### Graceful Degradation
```python
# ✅ CORRECT - Continue on partial failures
try:
    device_data = await self.api.get_device_parameters(device_id)
except Exception as err:
    error_msg = f"Failed to get data for device {device_name}: {err}"
    _LOGGER.warning(error_msg)
    data["update_summary"]["errors"].append(error_msg)
    continue  # Continue with other devices
```

#### Rate Limit Handling
```python
# ✅ CORRECT - Back off on rate limit errors
if data.get("status") == 5126:  # Too frequent requests
    _LOGGER.warning("Rate limit exceeded, backing off")
    await asyncio.sleep(5)
    # Retry or raise error
```

#### Token Expiration
```python
# ✅ CORRECT - Auto-refresh expired tokens
if self._token and self._token_expires and datetime.now() < self._token_expires:
    return True  # Use cached token
# Otherwise, authenticate again
```

### 6. Logging Standards

#### Log Levels
```python
# Debug - Detailed technical information
_LOGGER.debug("Processing device: %s (ID: %s)", device_name, device_id)

# Info - Normal operation milestones
_LOGGER.info("Found %d power stations", len(stations_list))

# Warning - Recoverable issues
_LOGGER.warning("Failed to get latest data for device %s", device_name)

# Error - Serious problems
_LOGGER.error("Authentication failed: %s", err)
```

#### Sensitive Data Masking
```python
# ✅ CORRECT
_LOGGER.debug("App Key: %s...", api.app_key[:8] if len(api.app_key) > 8 else "***")

# ❌ WRONG
_LOGGER.debug(f"App Key: {api.app_key}")
```

### 7. Code Organization

#### File Structure
```
custom_components/solarguardian/
├── __init__.py              # Setup, coordinator, services
├── api.py                   # API client class
├── binary_sensor.py         # Binary sensor platform
├── config_flow.py           # Configuration UI
├── const.py                 # Constants and configuration
├── manifest.json            # Integration metadata
├── sensor.py                # Sensor platform
├── services.yaml            # Service definitions
├── strings.json             # UI strings
└── translations/            # Localization files
    ├── en.json
    ├── de.json
    ├── hu.json
    └── ro.json
```

#### Import Order
```python
"""Module docstring."""
from __future__ import annotations

# Standard library
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Any

# Third-party
import aiohttp
import voluptuous as vol

# Home Assistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

# Local
from .api import SolarGuardianAPI, SolarGuardianAPIError
from .const import DOMAIN, CONF_APP_KEY
```

### 8. Testing with Real API

#### Create `.env` File
```bash
# tests/.env
APP_KEY=your_actual_app_key_here
APP_SECRET=your_actual_app_secret_here
DOMAIN=glapi.mysolarguardian.com  # or openapi.epsolarpv.com
```

#### Test Template
```python
"""Test with real API."""
import os
import unittest
from dotenv import load_dotenv

# Load credentials
load_dotenv()

class TestRealAPI(unittest.IsolatedAsyncioTestCase):
    """Test against real SolarGuardian API."""
    
    def setUp(self):
        """Set up test credentials."""
        self.app_key = os.getenv("APP_KEY")
        self.app_secret = os.getenv("APP_SECRET")
        self.domain = os.getenv("DOMAIN", "glapi.mysolarguardian.com")
        
        if not self.app_key or not self.app_secret:
            self.skipTest("API credentials not provided in .env")
    
    async def test_authentication(self):
        """Test real authentication."""
        from solarguardian.api import SolarGuardianAPI
        
        api = SolarGuardianAPI(self.domain, self.app_key, self.app_secret)
        try:
            result = await api.authenticate()
            self.assertTrue(result)
            self.assertIsNotNone(api._token)
        finally:
            await api.close()
```

### 9. Common Sensor Types and Units

Based on SolarGuardian API V2.3:

```python
# Power (W)
OutputPower, InputPower, loadpower, pvpower, battpower

# Voltage (V)
BatteryVoltage, PVVoltage, LoadVoltage, battvolt, pvvolt, loadvolt

# Current (A)
BatteryCurrent, PVCurrent, LoadCurrent, battcurr, pvcurr, loadcurr

# Temperature (°C)
BatteryTemperature, DeviceTemperature, batttemp, devtemp

# Energy (kWh)
GeneratedEnergyToday, GeneratedEnergyTotal, ConsumedEnergyToday, ConsumedEnergyTotal

# Battery (%)
BatterySOC, batterysoc

# Battery Capacity (Ah)
BatteryCapacity, battcap
```

### 10. Development Workflow

1. **Before Making Changes**
   - Read API documentation in `/solarguardian_api.txt`
   - Check existing implementations in `/custom_components/solarguardian/`
   - Review troubleshooting guide in `/TROUBLESHOOTING.md`

2. **When Adding Features**
   - Update API client (`api.py`) if new endpoints needed
   - Update constants (`const.py`) for new configuration
   - Update coordinator (`__init__.py`) for data flow changes
   - Update sensors (`sensor.py`) for new entity types
   - Add tests in `/tests` directory

3. **When Fixing Bugs**
   - Check logs for error messages
   - Review related API documentation
   - Test with real API credentials
   - Update error handling if needed
   - Add regression test

4. **Before Committing**
   - ✅ Verify no secrets in code
   - ✅ Verify no secrets in commit message
   - ✅ Run tests with real API
   - ✅ Check logs for sensitive data exposure
   - ✅ Update documentation if needed

### 11. Diagnostic Services

The integration provides built-in diagnostic services:

```python
# Test API connectivity
solarguardian.test_connection
# Parameters: verbose (boolean, optional)

# Get integration diagnostics  
solarguardian.get_diagnostics
# No parameters

# Reset latest data fetching
solarguardian.reset_latest_data
# No parameters - use when latest data gets disabled
```

## Quick Reference Card

### API Call Example
```python
# Always use rate limiting and error handling
await self._rate_limit_data()
try:
    response = await self._make_authenticated_request(endpoint, payload)
    # Process response
except SolarGuardianAPIError as err:
    if "404" in str(err):
        # Handle missing endpoint
    elif "5126" in str(err):
        # Handle rate limit
    else:
        # Log error
```

### Sensor Value Processing
```python
# API returns scaled values - apply decimal formatting
value = float(data_point.get("value", 0))
decimal = variable.get("decimal", "0")
if decimal and decimal.isdigit():
    value = value / (10 ** int(decimal))
return value
```

### Error Message Template
```python
_LOGGER.error(
    "Failed to %s for %s: %s",
    operation,  # e.g., "get devices"
    identifier,  # e.g., "station Test Station"
    err  # exception message
)
```

## File Cleanup Tasks

### Files to Move from Root to /tests:
- `/test_integration.py` → `/tests/integration/`
- `/run_basic_tests.py` → `/tests/`
- `/run_minimal_tests.py` → `/tests/`
- `/run_real_api_tests.py` → `/tests/`
- `/run_standalone_tests.py` → `/tests/`
- `/run_tests.py` → `/tests/`

### Create in /tests if missing:
- `/tests/.env` (git-ignored, template in `/tests/.env.example`)
- `/tests/.gitignore` (to ignore `.env`)

## Common Patterns to Use

### 1. API Client Method
```python
async def get_something(self, param: int) -> dict:
    """Get something from API."""
    payload = {"id": param}
    return await self._make_authenticated_request(ENDPOINT_SOMETHING, payload)
```

### 2. Coordinator Update
```python
async def _async_update_data(self):
    """Update data via API."""
    try:
        # Authenticate
        await self.api.authenticate()
        
        # Get data with error handling
        data = {}
        try:
            result = await self.api.get_something()
            data["something"] = result
        except Exception as err:
            _LOGGER.warning("Failed to get something: %s", err)
            data["errors"].append(str(err))
        
        return data
    except Exception as err:
        raise UpdateFailed(f"Error communicating with API: {err}") from err
```

### 3. Sensor Entity
```python
@property
def native_value(self) -> float | None:
    """Return sensor value."""
    # Get data from coordinator
    data = self.coordinator.data.get("device_data", {}).get(self._device_id, {})
    
    # Find parameter value
    for item in data.get("data", {}).get("list", []):
        if item.get("dataIdentifier") == self._data_identifier:
            return self._format_value(item.get("value"))
    
    return None
```

## Remember

1. **Security First**: Never commit secrets
2. **Real API Testing**: No mocks, test with real API
3. **Rate Limits**: Always respect API rate limits
4. **Error Handling**: Graceful degradation, continue on partial failures
5. **Logging**: Mask sensitive data, use appropriate log levels
6. **Documentation**: Keep API docs reference handy
7. **Home Assistant 2025.9.x**: Only use compatible Python features

## When in Doubt

1. Check `/solarguardian_api.txt` for API documentation
2. Check `/TROUBLESHOOTING.md` for common issues
3. Check existing implementation in `/custom_components/solarguardian/`
4. Test with real API using credentials from `/tests/.env`
5. Review Home Assistant coordinator and entity patterns

---

**Last Updated**: 2025-10-01
**API Version**: SolarGuardian API V2.3
**Home Assistant**: 2025.9.x
**Python**: 3.12+
