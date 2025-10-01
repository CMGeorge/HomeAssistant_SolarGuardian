# Control Capabilities Implementation Guide

## Overview

The SolarGuardian API V2.3 **DOES support control commands** for writable parameters. This guide documents how to implement control entities (switches, numbers, selects) in Home Assistant.

## API Control Documentation

### Endpoint: Command Issuing

**Step 1:** Get Command Server Address

```
POST https://{Domain}/epCloud/vn/ucloudSdk/getCommandAddress
Headers:
  X-Access-Token: {token}
  Content-Type: application/json

Response:
{
  "status": 0,
  "data": {
    "commandServerAddr": "https://xxx.xxx.xxx:xxx"
  }
}
```

**Step 2:** Send Control Command

```
POST {commandServerAddr}/v1.0/datapoint/{gatewayId}
Headers:
  X-Access-Token: {token}
  Content-Type: application/json
Body:
{
  "setDataPoint": [
    {
      "slaveName": "TRACER-AN",
      "dataPointId": "101443681",
      "value": "190"
    }
  ]
}
```

### Rate Limits

**CRITICAL:** Control commands have strict rate limits:
- **Max 10 commands per second per user**
- Exceeding limit returns error code `10001` (Frequency out of limit)
- Must implement request throttling

### Error Codes

| HTTP Code | Error Code | Description |
|-----------|------------|-------------|
| 404 | - | Page not found |
| 500 | 500 | Internal server error |
| 429 | 10001 | Frequency out of limit |
| 401 | 10003 | Authorization failed |
| 413 | 10004 | Content too large |
| 400 | 10005 | Parameter format error |

## Identifying Controllable Parameters

Parameters have a `rwmode` field that indicates read/write capability:

- `0`: **Read-only** (cannot be controlled)
- `1`: **Read/write** ✅ (can be controlled via API)
- `2`: **Write-only** (rare, write-only access)

Example parameter structure:
```json
{
  "dataIdentifier": "BatteryCapacity",
  "dataPointId": 101443681,
  "deviceNo": "2023021512345678900001",
  "rwmode": 1,  // ✅ Read/write - can be controlled!
  "variableName": "Battery Capacity",
  "unit": "Ah",
  "minValue": "10",
  "maxValue": "1000"
}
```

## Common Controllable Parameters

Based on Epever/SolarGuardian systems, these are typically writable:

### Load Control
- **Load Switch Control** - ON/OFF switch for AC output
- **Load Test Mode** - Enable/disable test mode

### Battery Settings
- **Battery Capacity** (Ah) - System battery capacity setting
- **Battery Type** - Lead-acid, Lithium, etc.
- **Battery Over Voltage** - Protection threshold
- **Battery Under Voltage** - Protection threshold
- **Battery Float Voltage** - Float charging voltage
- **Battery Boost Voltage** - Boost charging voltage

### Charging Parameters
- **Charging Limit Voltage** - Maximum charging voltage
- **Discharging Limit Voltage** - Minimum discharging voltage
- **Charging Current Limit** - Maximum charge current
- **Load Current Limit** - Maximum load current

### System Settings
- **Time Settings** - System clock
- **LCD Backlight** - Display brightness
- **Buzzer** - Enable/disable audible alerts

## Implementation Plan

### Phase 1: API Client Enhancement

Add to `api.py`:

```python
async def get_command_server_address(self) -> str:
    """Get the command server address for issuing control commands."""
    await self._rate_limit_auth()  # Control uses auth rate limit
    
    endpoint = "/epCloud/vn/ucloudSdk/getCommandAddress"
    response = await self._make_authenticated_request(endpoint, {})
    
    return response.get("data", {}).get("commandServerAddr")

async def send_control_command(
    self,
    gateway_id: str,
    slave_name: str,
    data_point_id: str,
    value: str
) -> dict:
    """Send a control command to a device.
    
    Args:
        gateway_id: Gateway serial number
        slave_name: Device name
        data_point_id: Parameter ID to control
        value: New value to set
        
    Returns:
        Response data from API
        
    Raises:
        SolarGuardianAPIError: If command fails
    """
    # Get command server if not cached
    if not hasattr(self, '_command_server'):
        self._command_server = await self.get_command_server_address()
    
    # Rate limit: max 10 commands/second
    await self._rate_limit_control()
    
    url = f"{self._command_server}/v1.0/datapoint/{gateway_id}"
    
    payload = {
        "setDataPoint": [
            {
                "slaveName": slave_name,
                "dataPointId": data_point_id,
                "value": value
            }
        ]
    }
    
    return await self._make_authenticated_request(url, payload)

async def _rate_limit_control(self):
    """Rate limit for control commands (10/second)."""
    if not hasattr(self, '_last_control_call'):
        self._last_control_call = datetime.now()
        return
    
    elapsed = (datetime.now() - self._last_control_call).total_seconds()
    if elapsed < 0.1:  # 10 per second = 0.1s between calls
        await asyncio.sleep(0.1 - elapsed)
    
    self._last_control_call = datetime.now()
```

### Phase 2: Switch Platform

Create `custom_components/solarguardian/switch.py`:

```python
"""Support for SolarGuardian switches."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import SolarGuardianDataUpdateCoordinator
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

SWITCH_TYPES = {
    "LoadSwitchControl": {
        "name": "Load Switch",
        "icon": "mdi:power-plug",
        "on_value": "1",
        "off_value": "0",
    },
}

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up SolarGuardian switches."""
    coordinator: SolarGuardianDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    
    switches = []
    
    # Find writable switch-type parameters
    for device_id, device_data in coordinator.data.get("device_data", {}).items():
        device = None
        # Find device info
        for station_id, devices in coordinator.data.get("devices", {}).items():
            for dev in devices.get("data", {}).get("list", []):
                if dev["id"] == device_id:
                    device = dev
                    break
        
        if not device:
            continue
        
        # Find writable switch parameters
        for group in device_data.get("data", {}).get("variableGroupList", []):
            for variable in group.get("variableList", []):
                rwmode = variable.get("rwmode", "0")
                data_identifier = variable.get("dataIdentifier")
                
                # Check if writable and is a switch type
                if rwmode in ["1", "2"] and data_identifier in SWITCH_TYPES:
                    switches.append(
                        SolarGuardianSwitch(
                            coordinator,
                            device,
                            variable,
                            SWITCH_TYPES[data_identifier]
                        )
                    )
    
    async_add_entities(switches)

class SolarGuardianSwitch(CoordinatorEntity, SwitchEntity):
    """Representation of a SolarGuardian switch."""
    
    def __init__(self, coordinator, device, variable, switch_config):
        """Initialize the switch."""
        super().__init__(coordinator)
        self._device = device
        self._variable = variable
        self._config = switch_config
        self._attr_name = f"{device['equipmentName']} {switch_config['name']}"
        self._attr_unique_id = f"{device['id']}_{variable['dataIdentifier']}"
        self._attr_icon = switch_config["icon"]
    
    @property
    def is_on(self) -> bool:
        """Return true if switch is on."""
        device_id = self._device["id"]
        device_data = self.coordinator.data.get("device_data", {}).get(device_id, {})
        
        # Get current value
        data_identifier = self._variable["dataIdentifier"]
        latest_data = device_data.get("latest_data", {})
        
        for data_point in latest_data.get("data", {}).get("list", []):
            if data_point.get("dataIdentifier") == data_identifier:
                value = str(data_point.get("value", "0"))
                return value == self._config["on_value"]
        
        return False
    
    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the switch on."""
        await self._set_value(self._config["on_value"])
    
    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the switch off."""
        await self._set_value(self._config["off_value"])
    
    async def _set_value(self, value: str) -> None:
        """Set the switch value."""
        try:
            await self.coordinator.api.send_control_command(
                gateway_id=self._variable["deviceNo"],
                slave_name=self._device["equipmentName"],
                data_point_id=str(self._variable["dataPointId"]),
                value=value
            )
            # Request immediate update
            await self.coordinator.async_request_refresh()
        except Exception as err:
            _LOGGER.error("Failed to set %s: %s", self.name, err)
```

### Phase 3: Number Platform

Create `custom_components/solarguardian/number.py`:

```python
"""Support for SolarGuardian number entities."""
from __future__ import annotations

import logging

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfElectricCurrent, UnitOfElectricPotential
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import SolarGuardianDataUpdateCoordinator
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

NUMBER_TYPES = {
    "BatteryCapacity": {
        "name": "Battery Capacity",
        "unit": "Ah",
        "icon": "mdi:battery",
        "mode": NumberMode.BOX,
    },
    "BatteryOverVoltage": {
        "name": "Battery Over Voltage Protection",
        "unit": UnitOfElectricPotential.VOLT,
        "icon": "mdi:lightning-bolt",
        "mode": NumberMode.BOX,
    },
}

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up SolarGuardian number entities."""
    coordinator: SolarGuardianDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    
    numbers = []
    
    # Find writable number-type parameters
    for device_id, device_data in coordinator.data.get("device_data", {}).items():
        device = None
        for station_id, devices in coordinator.data.get("devices", {}).items():
            for dev in devices.get("data", {}).get("list", []):
                if dev["id"] == device_id:
                    device = dev
                    break
        
        if not device:
            continue
        
        for group in device_data.get("data", {}).get("variableGroupList", []):
            for variable in group.get("variableList", []):
                rwmode = variable.get("rwmode", "0")
                data_identifier = variable.get("dataIdentifier")
                
                if rwmode in ["1", "2"] and data_identifier in NUMBER_TYPES:
                    numbers.append(
                        SolarGuardianNumber(
                            coordinator,
                            device,
                            variable,
                            NUMBER_TYPES[data_identifier]
                        )
                    )
    
    async_add_entities(numbers)

class SolarGuardianNumber(CoordinatorEntity, NumberEntity):
    """Representation of a SolarGuardian number entity."""
    
    def __init__(self, coordinator, device, variable, number_config):
        """Initialize the number entity."""
        super().__init__(coordinator)
        self._device = device
        self._variable = variable
        self._config = number_config
        
        # Get min/max from variable
        self._attr_native_min_value = float(variable.get("minValue", 0))
        self._attr_native_max_value = float(variable.get("maxValue", 1000))
        self._attr_native_step = 1.0  # Adjust based on variable precision
        
        self._attr_name = f"{device['equipmentName']} {number_config['name']}"
        self._attr_unique_id = f"{device['id']}_{variable['dataIdentifier']}"
        self._attr_native_unit_of_measurement = number_config.get("unit")
        self._attr_icon = number_config["icon"]
        self._attr_mode = number_config["mode"]
    
    @property
    def native_value(self) -> float | None:
        """Return the current value."""
        device_id = self._device["id"]
        device_data = self.coordinator.data.get("device_data", {}).get(device_id, {})
        
        data_identifier = self._variable["dataIdentifier"]
        latest_data = device_data.get("latest_data", {})
        
        for data_point in latest_data.get("data", {}).get("list", []):
            if data_point.get("dataIdentifier") == data_identifier:
                try:
                    return float(data_point.get("value", 0))
                except (ValueError, TypeError):
                    return None
        
        return None
    
    async def async_set_native_value(self, value: float) -> None:
        """Set new value."""
        try:
            await self.coordinator.api.send_control_command(
                gateway_id=self._variable["deviceNo"],
                slave_name=self._device["equipmentName"],
                data_point_id=str(self._variable["dataPointId"]),
                value=str(int(value))
            )
            await self.coordinator.async_request_refresh()
        except Exception as err:
            _LOGGER.error("Failed to set %s to %s: %s", self.name, value, err)
```

### Phase 4: Update manifest.json

Add new platforms:

```json
{
  "domain": "solarguardian",
  "name": "SolarGuardian",
  "codeowners": ["@CMGeorge"],
  "config_flow": true,
  "dependencies": [],
  "documentation": "https://github.com/CMGeorge/HomeAssistant_SolarGuardian",
  "iot_class": "cloud_polling",
  "issue_tracker": "https://github.com/CMGeorge/HomeAssistant_SolarGuardian/issues",
  "requirements": ["aiohttp>=3.8.0"],
  "version": "1.1.0",
  "integration_type": "device",
  "platforms": ["sensor", "binary_sensor", "switch", "number"]
}
```

### Phase 5: Update __init__.py

Add new platforms to PLATFORMS constant:

```python
PLATFORMS = [Platform.SENSOR, Platform.BINARY_SENSOR, Platform.SWITCH, Platform.NUMBER]
```

## Testing Plan

### Step 1: Identify Writable Parameters

Run this service to see all parameters with their `rwmode`:

```yaml
service: solarguardian.get_diagnostics
```

Look for parameters where `rwmode` == `1` or `2`.

### Step 2: Test Control Commands Manually

Use the test service (to be added):

```yaml
service: solarguardian.test_control_command
data:
  device_id: 12345
  data_point_id: "101443681"
  value: "190"
```

### Step 3: Implement Switches First

Start with simple ON/OFF switches like "Load Switch Control" as they're easier to test and debug.

### Step 4: Add Numbers

Once switches work, add number entities for adjustable values like battery capacity.

## Safety Considerations

### 1. User Confirmation

Add confirmation dialogs for critical controls:
- Battery voltage thresholds
- System mode changes
- Load switching

### 2. Value Validation

Always validate values before sending:
- Check against `minValue` and `maxValue` from API
- Ensure correct data type
- Apply proper decimal formatting

### 3. Error Handling

Implement robust error handling:
- Catch API errors gracefully
- Show clear error messages to users
- Don't leave system in undefined state

### 4. Rate Limiting

**CRITICAL:** Implement proper rate limiting:
- Max 10 commands per second
- Add queue for multiple commands
- Show user feedback when throttled

## Future Enhancements

### 1. Bulk Operations

Allow setting multiple parameters at once:
```yaml
service: solarguardian.set_parameters
data:
  device_id: 12345
  parameters:
    - data_point_id: "101443681"
      value: "190"
    - data_point_id: "101443682"
      value: "24"
```

### 2. Presets/Scenes

Create scenes for common configurations:
- "Night Mode" - Adjust charging parameters
- "Economy Mode" - Limit load output
- "Max Charge" - Optimize for charging

### 3. Automations

Enable Home Assistant automations:
- Turn off load during peak hours
- Adjust charging based on weather forecast
- Alert on threshold violations

### 4. Historical Controls

Log all control commands for audit trail:
- Who changed what
- When it was changed
- Previous and new values

## Documentation for Users

Add to README.md:

```markdown
## Controls

The integration provides control entities for writable parameters:

### Switches
- **Load Switch**: Turn AC output on/off

### Numbers
- **Battery Capacity**: Set system battery capacity (Ah)
- **Battery Protection**: Adjust voltage thresholds

### Safety

⚠️ **WARNING**: Changing parameters can affect system operation and battery health. 
Only modify settings if you understand their impact.

### Rate Limits

- Maximum 10 control commands per second
- Commands are automatically queued to prevent API throttling
```

## Status

- **Current:** Read-only sensors implemented ✅
- **Next:** Identify writable parameters from your device
- **Phase 1:** API client control methods
- **Phase 2:** Switch platform for ON/OFF controls
- **Phase 3:** Number platform for adjustable values
- **Phase 4:** Testing and validation
- **Phase 5:** Documentation and user guides

---

**Date:** October 1, 2025  
**API Version:** SolarGuardian API V2.3  
**Status:** Design complete, ready for implementation  
**Priority:** Medium - Enhancement (not critical for basic functionality)
