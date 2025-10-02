# CRITICAL BUG FIX: Sensors Showing "Unknown"

**Date**: October 1, 2025
**Severity**: CRITICAL - All sensors show "Unknown" despite API returning 43 values
**Status**: ✅ FIXED

## Problem

All sensors in Home Assistant showed "Unknown" values, despite logs showing:

```
Retrieved 43 latest values for device Makkaizsolt_1742059709718
```

## Root Cause

**Field Mismatch in API Response Structure**

The sensor code was matching on `dataIdentifier`, but the latest_data API endpoint returns `dataPointId`.

### Device Parameters Response (getEquipment)

```json
{
  "dataIdentifier": "AC_3",        ← String identifier (e.g., "OutputPower")
  "dataPointId": 105646605,        ← Integer ID linking to latest_data
  "variableNameE": "Output Power",
  "unit": "W"
}
```

### Latest Data Response (lastDatapoint)

```json
{
  "dataPointId": 105646605,        ← ONLY has dataPointId (NOT dataIdentifier!)
  "value": "1250.5",
  "deviceNo": "06150296093XY22X-00831",
  "dataPointName": "Output Power"
}
```

**The Bug**: Code tried to match using `data_point.get("dataIdentifier")`, which doesn't exist in the latest_data response!

```python
# ❌ OLD CODE (BROKEN)
for data_point in latest_data["data"]["list"]:
    if data_point.get("dataIdentifier") == data_identifier:  # Always fails!
        return value
```

## Fix Applied

Changed sensor matching logic to use `dataPointId` instead of `dataIdentifier`:

```python
# ✅ NEW CODE (FIXED)
data_point_id = self._variable.get("dataPointId")

for data_point in latest_data["data"]["list"]:
    if data_point.get("dataPointId") == data_point_id:  # Matches correctly!
        return value
```

## Testing

Verified using real API test (`tests/run_real_api_tests.py`):

```bash
cd tests
python run_real_api_tests.py
```

**Results**:

- API returns `dataPointId` in latest_data response ✅
- Device parameters contain both `dataPointId` and `dataIdentifier` ✅
- Matching on `dataPointId` correctly retrieves values ✅

## Impact

**Before Fix**:

- ❌ All 79 sensors showed "Unknown"
- ❌ 43 real-time values retrieved but not displayed
- ❌ Only 6 device info text sensors worked

**After Fix**:

- ✅ 43 sensors show real-time values
- ✅ 36 static/configuration sensors show "Unknown" (expected - no real-time data)
- ✅ 6 device info sensors work correctly

## Files Changed

- `custom_components/solarguardian/sensor.py`
  - Line ~516: Added `data_point_id = self._variable.get("dataPointId")`
  - Line ~521: Changed matching from `dataIdentifier` to `dataPointId`
  - Removed debug logging that was added during diagnosis

## Deployment

1. **Update Integration**:

   ```
   HACS → Integrations → SolarGuardian → Redownload
   ```

2. **Restart Home Assistant**:

   ```
   Settings → System → Restart Home Assistant
   ```

3. **Verification**:
   - Check logs: `Settings → System → Logs`
   - Should see: "Update complete: 1 stations, 1 devices, 79 sensors, 0 errors"
   - Sensors should now show values (43 real-time + 6 device info)

## API Documentation Reference

See `/solarguardian_api.txt`:

- Section 3.3 (Response parameters) - No `dataIdentifier` field listed
- Section 3.5 (Response example) - Shows `dataPointId` but no `dataIdentifier`
- Section 1.3.3 (Device parameters) - Shows both `dataPointId` and `dataIdentifier`

## Prevention

Future API integrations should:

1. ✅ Test with real API calls, not just mocks
2. ✅ Verify field names in API documentation
3. ✅ Use the existing `run_real_api_tests.py` before committing
4. ✅ Check that retrieved data count matches displayed sensor count

---

**Commit**: `fix: Match sensors on dataPointId instead of dataIdentifier for latest_data`
**Issue**: #CRITICAL - All sensors showing "Unknown"
**Tested**: Real API test confirmed fix works correctly
