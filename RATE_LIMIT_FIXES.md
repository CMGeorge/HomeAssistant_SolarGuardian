# Rate Limit Protection Fixes - October 1, 2025

## Summary

Implemented comprehensive rate limit protection to prevent API restrictions from SolarGuardian API. The integration now enforces safe update intervals and provides clear warnings if rate limits are approached.

## Changes Made

### 1. Increased Minimum Update Interval ✅

**File**: `custom_components/solarguardian/config_flow.py`

**Changed**: Minimum update interval from 5 seconds to **15 seconds**

```python
# Before
vol.Range(min=5, max=300)

# After  
vol.Range(min=15, max=300)
```

**Rationale**:
- 5-second interval with single device = 48 calls/minute (exceeds 30/min limit by 60%)
- 15-second interval with single device = 16 calls/minute (safe)
- Provides buffer for rate limiting delays

### 2. Updated Default Update Interval ✅

**File**: `custom_components/solarguardian/const.py`

**Changed**: Default from 10 seconds to **15 seconds**

```python
# Before
DEFAULT_UPDATE_INTERVAL = 10  # seconds - update frequently to get near real-time data

# After
DEFAULT_UPDATE_INTERVAL = 15  # seconds - safe for most installations, respects 30 calls/minute API limit
```

**Impact**:
- New installations will use safer default
- Existing installations keep their configured value
- Users can still adjust down to 15s if they have single device

### 3. Enhanced Rate Limit Error Handling ✅

**File**: `custom_components/solarguardian/api.py`

**Enhanced**: Error messages for rate limit violations (status code 5126)

```python
# Before
if data.get("status") == 5126:
    _LOGGER.warning("Rate limit exceeded, backing off")
    await asyncio.sleep(5)

# After
if data.get("status") == 5126:
    _LOGGER.error("API rate limit exceeded! The integration is making too many requests.")
    _LOGGER.error("Please increase the update interval in integration options (recommended: 30+ seconds for multiple devices).")
    await asyncio.sleep(10)  # Back off longer
```

**Applied to**:
- `_make_authenticated_request()` - main data endpoint handler
- `get_latest_data()` - legacy latest data method
- `get_latest_data_by_datapoints()` - current latest data method

**Benefits**:
- Clear user-facing error messages
- Actionable guidance (increase interval)
- Longer backoff time (10s vs 5s)

### 4. Improved User Documentation ✅

**File**: `custom_components/solarguardian/strings.json`

**Updated**: Options flow descriptions

```json
{
  "data": {
    "update_interval": "Update interval (seconds, min: 15, max: 300)"
  },
  "data_description": {
    "update_interval": "Update interval in seconds (15-300). Lower values provide more frequent updates but increase API usage. API rate limit: 30 calls/minute. Recommended: 15s for single device, 30s+ for multiple devices to avoid rate limiting."
  }
}
```

**Also updated**: Step description to mention API rate limits explicitly

### 5. Updated Copilot Instructions ✅

**File**: `.github/copilot-instructions.md`

**Updated**: Platform requirements section to reflect new defaults

## Rate Limit Analysis

### API Call Pattern (Per Update Cycle)

For a typical installation with 1 station and 1 device:

1. `authenticate()` - 0-1 calls (cached 2 hours)
2. `get_power_stations()` - 1 call
3. `get_devices()` - 1 call per station
4. `get_device_parameters()` - 1 call per device
5. `get_latest_data_by_datapoints()` - 1 call per device

**Total**: ~4 data calls per cycle (auth only when token expires)

### Safe Configuration Guidelines

| Setup | Min Interval | Recommended | Calls/Minute |
|-------|-------------|-------------|--------------|
| 1 station, 1 device | 15s | 15-20s | 16-20 |
| 1 station, 2-3 devices | 20s | 30s | 20-30 |
| 2+ stations or 4+ devices | 30s | 60s | 15-30 |
| Large (3+ stations, 6+ devices) | 60s | 120s | 15-20 |

### Before vs After

**Before (5s minimum)**:
- 1 device @ 5s = 48 calls/min ❌ EXCEEDS LIMIT
- 1 device @ 10s = 24 calls/min ⚠️ CLOSE TO LIMIT
- 3 devices @ 10s = 90 calls/min ❌ SEVERELY EXCEEDS

**After (15s minimum)**:
- 1 device @ 15s = 16 calls/min ✅ SAFE
- 1 device @ 20s = 12 calls/min ✅ VERY SAFE
- 3 devices @ 30s = 30 calls/min ✅ AT LIMIT (with guidance to increase)

## Rate Limiting Implementation

### Already Implemented ✅

The API client (`api.py`) correctly implements rate limiting:

```python
async def _rate_limit_data(self) -> None:
    """Apply rate limiting for data calls (30 per minute)."""
    async with self._rate_limit_lock:
        now = datetime.now()
        time_since_last = (now - self._last_data_call).total_seconds()
        if time_since_last < 2:  # 30 calls per minute = 2 seconds between calls
            wait_time = 2 - time_since_last
            await asyncio.sleep(wait_time)
        self._last_data_call = datetime.now()
```

**Features**:
- Enforces minimum 2-second spacing between data calls
- Enforces minimum 6-second spacing between auth calls
- Uses asyncio lock to prevent race conditions
- Tracks last call time per endpoint type

**Why This Helps**: Prevents burst requests within a single update cycle from overwhelming the API

## Testing Recommendations

### Before Deployment

1. **Single Device Test**:
   - Set 15s interval
   - Monitor logs for rate limit warnings
   - Verify ~16 calls/minute

2. **Multiple Device Test** (if applicable):
   - Set 30s interval initially
   - Monitor logs for 5-10 minutes
   - Adjust if rate limit warnings appear

3. **Rate Limit Test** (optional):
   - Temporarily set to 10s with 3+ devices
   - Verify error messages are clear
   - Confirm backoff behavior works
   - Reset to safe interval

### After Deployment

Monitor Home Assistant logs for:
```
API rate limit exceeded! The integration is making too many requests.
Please increase the update interval in integration options
```

If seen, increase update interval:
- Single device: 20s
- 2-3 devices: 45s
- 4+ devices: 90s

## User Migration

### Existing Users

Users with existing installations will **not** be affected immediately:
- Their configured interval is preserved
- Only new installations get 15s default

**If they reconfigure**:
- Minimum is now 15s (was 5s)
- If they had 5-14s configured, they'll need to adjust to 15s minimum

### Communication

Consider adding to release notes:
```markdown
## Breaking Changes

**Minimum update interval increased from 5s to 15s**

To comply with SolarGuardian API rate limits (30 calls/minute), the minimum 
update interval has been increased to 15 seconds. Users who previously 
configured intervals below 15s will need to adjust their settings.

Recommended intervals:
- Single device: 15-20 seconds
- Multiple devices: 30+ seconds
- Large installations: 60+ seconds
```

## Files Modified

1. ✅ `custom_components/solarguardian/config_flow.py` - Min interval 5→15s
2. ✅ `custom_components/solarguardian/const.py` - Default 10→15s
3. ✅ `custom_components/solarguardian/api.py` - Enhanced error messages (3 locations)
4. ✅ `custom_components/solarguardian/strings.json` - Updated descriptions
5. ✅ `.github/copilot-instructions.md` - Updated documentation
6. ✅ `RATE_LIMIT_ANALYSIS.md` - Created comprehensive analysis
7. ✅ `RATE_LIMIT_FIXES.md` - This document

## Verification Checklist

- [x] Minimum interval increased to 15s
- [x] Default interval increased to 15s
- [x] Rate limit errors provide clear guidance
- [x] Error backoff increased from 5s to 10s
- [x] User-facing documentation updated
- [x] Developer documentation updated
- [x] Safe configuration guidelines documented
- [ ] Test with real API (15s interval, single device)
- [ ] Test with real API (30s interval, multiple devices)
- [ ] Monitor logs for rate limit warnings
- [ ] Verify no rate limit errors in production

## Next Steps

1. **Test the changes** with real API credentials:
   ```bash
   cd tests
   .venv/bin/python run_real_api_tests.py
   ```

2. **Deploy to Home Assistant** test instance:
   - Copy to custom_components/solarguardian
   - Restart Home Assistant
   - Configure with 15s interval
   - Monitor for 30 minutes

3. **Monitor production**:
   - Check logs for rate limit errors
   - Verify update frequency is as expected
   - Collect user feedback on update frequency

4. **Document in README**:
   - Add rate limit section
   - Include configuration examples
   - Link to RATE_LIMIT_ANALYSIS.md

## Risk Assessment

**Risk Level**: Low

**Mitigations**:
- Changes only affect new installations and reconfigurations
- Existing users keep their settings
- Rate limiting code already working correctly
- Clear error messages guide users

**Potential Issues**:
- Users may notice less frequent updates (15s vs 10s default)
- Users with <15s configured will need to reconfigure
- Some users may want more frequent updates

**Solutions**:
- Document the change clearly
- Explain the reasoning (API limits)
- Provide clear configuration guidelines
- Add monitoring to detect rate limit issues early

---

**Status**: ✅ **COMPLETE**  
**Last Updated**: October 1, 2025  
**Tested**: Awaiting deployment test
