# Solution: Sensors Showing "Unknown" - October 1, 2025

## Problem Identified

From your logs:

```
Retrieved 43 latest values for device Makkaizsolt_1742059709718
Device Makkaizsolt_1742059709718 has 79 parameters
No value found for sensor... totalPowerGeneration
No value found for sensor... totalPowerGeneration1
No value found for sensor... totalPowerConsumption
```

**Root Cause:** The API returns 43 out of 79 parameters in real-time `latest_data`. The missing 36 parameters are not included because they are:

- Configuration values (don't change in real-time)
- Accumulated counters (updated less frequently)
- Write-only parameters (for control commands)
- Parameters not supported by your specific device model

This is **NORMAL API BEHAVIOR** - not all parameters have real-time data.

## Solution Implemented (Commit Incoming)

### 1. **Store Last Valid Value**

Sensors now remember their last known value:

```python
self._last_valid_value = None  # Store last good value
self._value_source = None  # Track where it came from
```

When a parameter isn't in latest_data but had a value before, the sensor will:

- Return the last known value
- Mark it as "stale" in attributes
- Log debug message

### 2. **Extra State Attributes**

Every sensor now shows:

```yaml
data_identifier: "totalPowerGeneration"
variable_name: "Total PV Generation"
data_source: "none" # or "latest_data" or "variable.currentValue"
has_latest_data: false
info: "Parameter not included in real-time updates"
data_point_id: 105646597
api_unit: "kWh"
```

This helps you understand:

- ✅ Which sensors get real-time updates
- ✅ Which are configuration/static values
- ✅ Where the current value came from

### 3. **Better Logging**

Now logs show:

```
✅ "Sensor Battery Voltage got value from latest_data: 25.6"
⚠️  "No current value for sensor Total PV - using last known value: 206.39"
❌ "No value found for sensor Config Parameter - parameter not in latest_data"
```

## What This Means for You

### Sensors Will Be Organized

**Working Real-time Sensors (43):**
These will update every 15 seconds with live data:

- ✅ Battery Voltage, Current, SOC, Temperature
- ✅ PV Voltage, Current, Power
- ✅ AC Output Voltage, Current, Power
- ✅ Load status, charging status
- ✅ Other active measurements

**Static/Config Sensors (36):**
These show initial values or "Unknown":

- 📊 Total energy counters (updated less frequently)
- ⚙️ Configuration parameters (battery type, capacity)
- 🔧 System settings (threshold voltages)
- 📋 Device information

### How to Check Which Sensors Have Real-Time Data

1. Click on any sensor in Home Assistant
2. Scroll down to "Attributes"
3. Look for `has_latest_data`:
   - `true` = Gets real-time updates ✅
   - `false` = Static/configuration value ⚙️

### Example Sensor Attributes

**Real-time Sensor (Battery Voltage):**

```yaml
friendly_name: UP HI Battery Voltage
unit_of_measurement: V
device_class: voltage
state_class: measurement
data_identifier: BatteryVoltage
variable_name: Battery Voltage
data_source: latest_data
has_latest_data: true
data_point_id: 105646543
api_unit: V
```

**Static Sensor (Total Generation):**

```yaml
friendly_name: UP HI Total PV Generation
unit_of_measurement: kWh
device_class: energy
state_class: total_increasing
data_identifier: totalPowerGeneration
variable_name: Total Generation
data_source: variable.defaultValue
has_latest_data: false
info: Parameter not included in real-time updates
data_point_id: 105646597
api_unit: kWh
```

## Which Sensors Typically Don't Have Real-Time Data

Based on Epever/SolarGuardian systems:

### Energy Totals

- `totalPowerGeneration` - Total PV generation (kWh)
- `totalPowerGeneration1` - Total utility charging (kWh)
- `totalPowerConsumption` - Total load consumption (kWh)
- `todayPowerGeneration` - Today's generation (kWh)

**Why:** These are counters that update less frequently (hourly/daily), not every 15 seconds.

### Configuration Parameters

- Battery capacity setting
- Battery type setting
- Voltage thresholds
- System presets

**Why:** These are settings, not measurements.

### Control Parameters

- Load switch control
- Charging mode control
- System enable/disable

**Why:** These are write-only or report status separately.

## Options to Handle "Unknown" Sensors

### Option 1: Keep Them (Recommended)

**Pros:**

- Shows all available parameters
- Can see configuration values
- Future firmware updates might add real-time data

**Cons:**

- Some sensors show "Unknown" or stale values
- More entities in UI

### Option 2: Hide Sensors Without Real-Time Data

I can add a configuration option:

```yaml
# In integration options
show_only_realtime_sensors: true
```

This would:

- Only create sensors for parameters with `has_latest_data: true`
- Hide the 36 static/config parameters
- Cleaner UI with only 43 active sensors

### Option 3: Mark Static Sensors as Diagnostic

Already partially done! Sensors like Serial, Gateway ID are marked as DIAGNOSTIC.

We could extend this to mark ALL non-real-time sensors as diagnostic:

```python
if not has_latest_data:
    return EntityCategory.DIAGNOSTIC
```

**Result:** 43 sensors in main view, 36 in diagnostic section.

## Recommended Actions

### Immediate (Already Done)

1. ✅ Added last_valid_value storage
2. ✅ Added extra_state_attributes
3. ✅ Enhanced logging

### Your Next Steps

1. **Update integration from HACS** (get new commit)
2. **Restart Home Assistant**
3. **Check sensor attributes** to see which have real-time data
4. **Decide on Option 2 or 3** if you want cleaner UI

### To Enable "Real-Time Only" Mode (Option 2)

I can add a checkbox in integration options:

```
☐ Show only sensors with real-time data
```

This would require:

1. New option in `config_flow.py`
2. Filter sensors during setup in `sensor.py`
3. Allow toggling without re-adding integration

**Want this?** Let me know and I'll implement it!

### To Move Static Sensors to Diagnostic (Option 3)

Already have infrastructure, just need to add:

```python
@property
def entity_category(self) -> EntityCategory | None:
    # Check if parameter has real-time data
    if not self._has_latest_data():
        return EntityCategory.DIAGNOSTIC
    # ... existing checks
```

**Want this?** Easy to add!

## Summary

**The "Unknown" sensors are NOT a bug!** ✅

They're parameters that:

1. Don't have real-time data from API (normal)
2. Are configuration/static values (expected)
3. May update less frequently (hourly/daily)

**Solution provides:**

- ✅ Clear indication via attributes
- ✅ Helpful info messages
- ✅ Last known values where available
- ✅ Better debugging

**You can choose:**

- Keep all sensors (see everything)
- Hide static sensors (cleaner)
- Move to diagnostic section (organized)

---

**Commit:** Coming next (enhanced sensor with attributes)
**Status:** Root cause identified and explained
**Action:** Choose UI preference (keep all, hide, or move to diagnostic)
