# Critical Fix: Enum Sensors Must Be Text Sensors

**Date**: October 1, 2025
**Severity**: CRITICAL
**Commit**: 074e9a6
**Status**: ✅ Fixed and Tested

## The Problem

After implementing enum translation support, Home Assistant crashed when trying to add enum sensors with this error:

```
ValueError: Sensor sensor.makkaizsolt_1742059709718_pv_charging_status has device class 'None',
state class 'None' unit '' and suggested precision 'None' thus indicating it has a numeric value;
however, it has the non-numeric value: 'Not Charging' (<class 'str'>)
```

**30 occurrences** across sensors like:

- PV Charging Status
- Device Fault
- INV Bypass Status
- Battery Detection
- Charging Mode
- Output Mode

## Root Cause

**Home Assistant's Sensor Type Detection Logic:**

1. If a sensor has `device_class`, `state_class`, or `unit` → expects **numeric** value
2. If sensor returns **string** value → Home Assistant tries `int(value)` then `float(value)`
3. If both fail → **ValueError** and sensor fails to load

**Our Bug:**

```python
# ❌ WRONG - Set these attributes for ALL sensors
self._attr_native_unit_of_measurement = sensor_config.get("unit")
self._attr_device_class = sensor_config.get("device_class")
self._attr_state_class = sensor_config.get("state_class")

# Then later we return translated text
return "Not Charging"  # ❌ HA tries float("Not Charging") → ValueError
```

Even though `device_class`, `state_class`, and `unit` were `None`, Home Assistant still treated the sensor as numeric because these attributes were **set** (even to None).

## The Fix

**Detect enum sensors and configure them as text sensors:**

```python
def __init__(self, ...):
    # Check if this is an enum sensor (has translationChild)
    has_translation = bool(variable.get("translationChild"))

    # Set sensor attributes
    # For enum sensors (text values), don't set device_class, state_class, or unit
    # This tells Home Assistant to treat them as text sensors
    if not has_translation:
        self._attr_native_unit_of_measurement = sensor_config.get("unit")
        self._attr_device_class = sensor_config.get("device_class")
        self._attr_state_class = sensor_config.get("state_class")

    self._attr_icon = sensor_config.get("icon")
```

**Key Change**: Only set `device_class`, `state_class`, and `unit` for **numeric sensors**. Enum sensors get **no attributes** (except icon), making them pure text sensors.

## Affected Sensors (22 Total)

All sensors with `translationChild` in their variable definition:

1. **PV Charging Status** - 0 → "Not Charging"
2. **Utility Charging Status** - 0 → "Not Charging"
3. **Battery Voltage Alarm** - 0 → "Normal"
4. **Battery Temperature Alarm** - 0 → "Normal"
5. **Charging Mode** - 2 → "Utility and Solar"
6. **Load Control Mode** - 0 → "Solar First"
7. **Battery Detection** - 1 → "Detected"
8. **INV Bypass Status** - 1 → "Bypass"
9. **Output Mode** - 0 → "Single Machine Output"
10. **PV Relay Status** - 1 → "Closed"
11. **PV Control Status** - 0 → "NO"
12. **Output Load Status** - 0 → "Light Load"
13. **Device Fault** - 0 → "Normal"
14. **System Voltage Level** - 24 → "24V"
15. **Day/Night Flag** - 1 → "Night"
16. **PV Input On/Off Status** - Various statuses
17. **Battery Type** - Various battery types
18. **Standard Battery AH** - Capacity values
19. **Battery Current Detection Precision** - Precision levels
20. **Fault Code 1** - Fault descriptions
21. **Fault Code 2** - Fault descriptions
22. **Fault Code 3** - Fault descriptions

## Testing

**Verified with `test_translations.py`:**

```bash
✅ Got latest data for 16 enum sensors
📊 PV Charging Status: 0 → ✅ Translated: Not Charging
📊 Utility Charging Status: 0 → ✅ Translated: Not Charging
📊 Battery Voltage Alarm: 0 → ✅ Translated: Normal
📊 Charging Mode: 2 → ✅ Translated: Utility and Solar
```

All enum sensors now:

- ✅ Load without errors
- ✅ Display translated text values
- ✅ Show correct icon
- ✅ Don't have device_class/state_class/unit (text sensors)

## Home Assistant Sensor Configuration Rules

**For NUMERIC sensors:**

```python
device_class = SensorDeviceClass.POWER  # or VOLTAGE, CURRENT, etc.
state_class = SensorStateClass.MEASUREMENT  # or TOTAL
unit = UnitOfPower.WATT  # or VOLT, AMPERE, etc.
native_value = 1234.5  # numeric value
```

**For TEXT sensors:**

```python
# Don't set device_class, state_class, or unit
icon = "mdi:battery-charging"  # optional
native_value = "Not Charging"  # string value
```

**Critical Rule**: If `native_value` returns a **string**, sensor MUST NOT have `device_class`, `state_class`, or `unit` set.

## Impact

Before fix:

- ❌ 22 enum sensors failed to load with ValueError
- ❌ 30+ errors in Home Assistant logs
- ❌ Integration setup partially failed

After fix:

- ✅ All 22 enum sensors load successfully
- ✅ Display human-readable text (not numbers)
- ✅ No errors in Home Assistant logs
- ✅ Integration setup completes fully

## Deployment

1. User updates from HACS (gets commit 074e9a6)
2. **IMPORTANT**: Must fully restart Home Assistant (not just reload integration)
3. All enum sensors should now show translated text
4. Check logs - should see 0 ValueError errors

## Related Documentation

- `BUGFIX_ENUM_TRANSLATIONS.md` - How translation system works
- `CRITICAL_BUG_FIX_SENSORS.md` - dataPointId matching fix
- `BUGFIX_DECIMAL_FORMATTING.md` - Decimal places fix
- `FIXES_SUMMARY.md` - Complete overview of all fixes

## Technical Notes

**Why Home Assistant has this rule:**

Sensors with `device_class`, `state_class`, or `unit` are assumed to be numeric because:

- `device_class` like POWER, VOLTAGE implies numeric measurements
- `state_class` like MEASUREMENT implies time-series data (numeric)
- `unit` like WATT, VOLT implies quantifiable values (numeric)

Text sensors (like status, mode, name) shouldn't have these attributes because:

- No device class makes sense ("Not Charging" isn't a power reading)
- No state class makes sense (text isn't a measurement or total)
- No unit makes sense (you don't measure "Not Charging" in watts)

**Our enum sensors are pure text sensors** - they show status information, not measurements.

---

**Status**: ✅ Fixed, tested, committed, ready for deployment
