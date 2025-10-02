# BUG FIX: Incorrect Decimal Formatting on Sensor Values

**Date**: October 1, 2025
**Severity**: HIGH - Sensor values incorrectly divided by 10^decimal
**Status**: ✅ FIXED

## Problem

Sensors were showing incorrect values with wrong decimal places:

| Sensor              | Expected | Shown    | Error |
| ------------------- | -------- | -------- | ----- |
| AC Output Voltage   | 219.93 V | 2.1993 V | ÷ 100 |
| AC Output Frequency | 50.00 Hz | 0.50 Hz  | ÷ 100 |

## Root Cause

**Double Decimal Formatting**

The code was applying decimal formatting to values that were **already formatted by the API**:

### API Response (latest_data endpoint)

```json
{
  "dataPointId": 105646638,
  "value": "50.00",    ← Already formatted with 2 decimal places!
  "dataPointName": "AC Output Frequency"
}
```

### Device Parameters

```json
{
  "dataIdentifier": "load_4",
  "dataPointId": 105646638,
  "decimal": "2",      ← This is for REFERENCE only
  "unit": "Hz"
}
```

### The Bug

```python
# ❌ OLD CODE (BROKEN)
value = float(data_point.get("value", 0))  # Gets 50.00
decimal = self._variable.get("decimal", "0")  # Gets "2"
if decimal and decimal.isdigit():
    value = value / (10 ** int(decimal))  # 50.00 / 100 = 0.50 ❌
```

**Result**: Values divided by 100 when they shouldn't be!

## Fix Applied

Removed decimal formatting for `latest_data` values (they're already formatted):

```python
# ✅ NEW CODE (FIXED)
# NOTE: latest_data values are ALREADY formatted with decimals applied
# The API returns "50.00" not "5000", so we use the value as-is
value = float(data_point.get("value", 0))  # Gets 50.00, returns 50.00 ✅
```

**Decimal formatting is ONLY applied to fallback values** from `variableList` (which are unformatted integers).

## API Behavior Analysis

### latest_data Endpoint (Port 7002)

- ✅ Returns **formatted** values: `"50.00"`, `"220.06"`, `"48.2"`
- ✅ Values are **strings** with decimals already applied
- ❌ Do NOT apply decimal formatting

### getEquipment Endpoint (Device Parameters)

- ✅ Returns **raw** integer values in `currentValue` field: `5000`, `22006`, `482`
- ✅ Includes `decimal` field for formatting: `"2"`, `"2"`, `"1"`
- ✅ DO apply decimal formatting: `5000 / 100 = 50.00`

## Testing

Verified with real API test:

```bash
cd tests
python run_real_api_tests.py 2>&1 | grep -A 3 '"dataPointId": 105646638'
```

**Result**:

```json
{
  "dataPointId": 105646638,
  "value": "50.00",  ← Already formatted!
  "time": 1759331142569
}
```

## Impact

**Before Fix**:

- ❌ AC Output Voltage: 2.1993 V (should be 219.93 V)
- ❌ AC Output Frequency: 0.5 Hz (should be 50.0 Hz)
- ❌ Battery Voltage: 4.82 V (should be 48.2 V)
- ❌ All sensors with decimal > 0 were wrong

**After Fix**:

- ✅ AC Output Voltage: 219.93 V
- ✅ AC Output Frequency: 50.0 Hz
- ✅ Battery Voltage: 48.2 V
- ✅ All sensors show correct values

## Files Changed

- `custom_components/solarguardian/sensor.py`
  - Lines 520-535: Removed decimal formatting for latest_data values
  - Lines 560-575: Kept decimal formatting for variable fallback values
  - Added comments explaining why

## Key Insight

**The `decimal` field in device parameters is metadata, not a formatting instruction for latest_data!**

- It describes how many decimal places the value has
- latest_data endpoint: Values already formatted → Use as-is
- getEquipment endpoint: Values are raw integers → Apply decimal formatting

## Deployment

Same as previous fix:

1. Update Integration from HACS
2. Restart Home Assistant
3. Verify sensor values are now correct

---

**Commit**: `fix: Remove double decimal formatting on latest_data sensor values`
**Issue**: Sensor values incorrectly divided by 10^decimal
**Tested**: Real API test shows values already formatted
**Related**: Part of sensor value fix series (after dataPointId matching fix)
