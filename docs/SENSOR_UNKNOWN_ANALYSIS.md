# Sensor "Unknown" Value Analysis

## Problem Report

Most sensors showing "Unknown" except:

- ✅ Alarm (working)
- ✅ Gateway ID (working)
- ✅ Serial (working)
- ✅ Status (working)
- ✅ Product Name (working)
- ✅ Location (working)

**Working sensors** = Device Info Sensors (text values from device metadata)
**Not working** = Parameter Sensors (numeric values from API data)

## Root Cause Analysis

### Issue 1: Latest Data Endpoint May Be Disabled

The coordinator can disable the latest data endpoint after 5 failures:

```python
if self._latest_data_failures >= self._max_latest_data_failures:
    self._latest_data_disabled = True
```

**Check logs for:**

```
Latest data endpoint consistently failing (5 failures), disabling
```

### Issue 2: Sensor Value Lookup Logic

Current `native_value` property in `SolarGuardianSensor`:

```python
def native_value(self) -> str | float | None:
    # 1. Try latest_data first
    latest_data = device_data.get("latest_data", {})
    if latest_data.get("data", {}).get("list"):
        # Search for matching dataIdentifier
        return value

    # 2. Fallback to variable configuration
    for group in device_data.get("data", {}).get("variableGroupList", []):
        for variable in group.get("variableList", []):
            if "currentValue" in variable:  # ❌ This might not exist!
                return value

    return None  # ❌ Returns None = "Unknown" in Home Assistant
```

**Problem:** The fallback assumes `currentValue` exists in the variable configuration, but the API might not provide this field.

### Issue 3: Missing Debug Information

We don't know which step is failing:

- Is latest_data empty?
- Is the dataIdentifier not matching?
- Is variableGroupList empty?
- Is currentValue missing?

## Solution Steps

### Step 1: Check Home Assistant Logs

Look for these messages:

```
📡 Latest Data Enabled: False
Latest data disabled after X failures
```

If you see this, run the service:

```yaml
service: solarguardian.reset_latest_data
```

### Step 2: Enable Debug Logging

Add to Home Assistant `configuration.yaml`:

```yaml
logger:
  default: info
  logs:
    custom_components.solarguardian: debug
```

Restart Home Assistant and check logs for:

- "Retrieved X latest values for device Y"
- "No dataPointId/deviceNo found"
- "Device X has Y parameters"

### Step 3: Enhanced Sensor Value Logic

We need to add:

1. Better debug logging to see what data is available
2. Store raw variable data as fallback
3. Show diagnostic information about data availability

### Step 4: Add Entity Categories

Home Assistant supports organizing entities:

- **Diagnostic entities**: Technical info (shown in separate section)
- **Config entities**: Settings
- **Standard entities**: Main sensors

We should mark these as diagnostic:

- Device Serial → `DIAGNOSTIC`
- Gateway ID → `DIAGNOSTIC`
- Device status indicators → `DIAGNOSTIC`
- Technical parameters (register addresses, etc.) → `DIAGNOSTIC`

Keep as standard:

- Battery Voltage, SOC, Current
- PV Voltage, Current, Power
- AC Output Power
- Energy counters
- Temperature

## API Control Capabilities Discovery

### Control Command Support ✅

The SolarGuardian API **DOES support control commands**!

**API Endpoint:** `POST {commandServerAddr}/v1.0/datapoint/{deviceId}`

**Process:**

1. Get auth token (already implemented)
2. Call `/epCloud/vn/ucloudSdk/getCommandAddress` to get control server URL
3. Send control command with:
   - `slaveName`: Device name
   - `dataPointId`: Parameter ID to control
   - `value`: New value to set

**Example - Set Battery Capacity:**

```json
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

### Writable Parameters

From API documentation, parameters have `rwmode` field:

- `0`: Read-only
- `1`: Read/write ✅ (can be controlled)
- `2`: Write-only

Common controllable parameters:

- **Load Switch Control** (ON/OFF)
- **Battery Capacity** (Ah setting)
- **Charging parameters**
- **System settings**

### Control Entity Types for Home Assistant

Future implementation should use:

1. **`switch.py`** platform:
   - Load Switch (ON/OFF)
   - System enable/disable switches

2. **`number.py`** platform:
   - Battery Capacity (Ah)
   - Voltage thresholds
   - Charging limits

3. **`select.py`** platform:
   - Operating modes (if available)
   - System presets

### Rate Limit for Controls

**Important:** Control commands have their own rate limit:

- Max 10 commands per second per user
- Exceeding limit returns error code `10001`

## Recommended Changes

### Priority 1: Fix Unknown Values (IMMEDIATE)

1. Add comprehensive debug logging to sensor.py
2. Check if latest_data is disabled and provide clear user guidance
3. Store initial parameter values from device configuration
4. Add "Last Updated" timestamp to sensors

### Priority 2: Add Entity Categories (HIGH)

Organize sensors for better UX:

```python
@property
def entity_category(self) -> EntityCategory | None:
    """Return entity category."""
    if self._data_identifier in [
        "DeviceSerialNumber", "GatewayID", "FirmwareVersion",
        "HardwareVersion", "RegisterAddress"
    ]:
        return EntityCategory.DIAGNOSTIC
    return None  # Standard entity
```

### Priority 3: Add Diagnostic Sensor (HIGH)

Create a special diagnostic sensor showing:

- Latest data enabled/disabled status
- Number of successful/failed updates
- Last update timestamp
- API call statistics

### Priority 4: Implement Controls (MEDIUM)

Add control platforms:

1. Implement command address fetching
2. Add switch platform for Load Control
3. Add number platform for settable values
4. Respect rate limits (10 commands/second max)

## Immediate Testing Commands

### Check Latest Data Status

```yaml
service: solarguardian.get_diagnostics
```

Should show:

- `latest_data_disabled`: true/false
- `latest_data_failures`: count
- Current data structure

### Reset Latest Data

If disabled:

```yaml
service: solarguardian.reset_latest_data
```

### Check Raw Coordinator Data

In Home Assistant Developer Tools → Template:

```jinja2
{{ state_attr('sensor.your_device_battery_voltage', 'device_id') }}
```

Then check the coordinator data for that device.

## Next Steps

1. **Enable debug logging** in Home Assistant
2. **Check logs** for latest_data status and error messages
3. **Run reset_latest_data service** if latest data is disabled
4. **Share logs** with device_data structure so we can see what's available
5. **Implement entity categories** to organize sensors better
6. **Plan control implementation** for switches and adjustable parameters

---

**Date:** October 1, 2025
**Status:** Analysis complete, solutions identified
**Priority:** High - affects core functionality
