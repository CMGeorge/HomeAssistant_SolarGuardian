# SolarGuardian API Rate Limit Analysis

## API Rate Limits (from Documentation)

**Per the SolarGuardian API V2.3 documentation:**

1. **Authentication Endpoint**: Maximum 10 calls per minute (minimum 6 seconds between calls)
2. **Data Endpoints**: Maximum 30 calls per minute (minimum 2 seconds between calls)

## Current Implementation Status

### ✅ Rate Limiting Implementation (CORRECT)

The API client (`api.py`) **correctly implements** rate limiting:

```python
async def _rate_limit_auth(self) -> None:
    """Apply rate limiting for auth calls (10 per minute)."""
    async with self._rate_limit_lock:
        now = datetime.now()
        time_since_last = (now - self._last_auth_call).total_seconds()
        if time_since_last < 6:  # 10 calls per minute = 6 seconds between calls
            wait_time = 6 - time_since_last
            _LOGGER.debug("Rate limiting auth call, waiting %.2f seconds", wait_time)
            await asyncio.sleep(wait_time)
        self._last_auth_call = datetime.now()

async def _rate_limit_data(self) -> None:
    """Apply rate limiting for data calls (30 per minute)."""
    async with self._rate_limit_lock:
        now = datetime.now()
        time_since_last = (now - self._last_data_call).total_seconds()
        if time_since_last < 2:  # 30 calls per minute = 2 seconds between calls
            wait_time = 2 - time_since_last
            _LOGGER.debug("Rate limiting data call, waiting %.2f seconds", wait_time)
            await asyncio.sleep(wait_time)
        self._last_data_call = datetime.now()
```

**Key Features:**
- Uses asyncio.Lock to prevent concurrent calls
- Tracks last call time for each endpoint type
- Automatically sleeps if calls are too frequent
- Debug logging shows when rate limiting is applied

## API Calls Per Update Cycle

### Current Pattern (1 Station, 1 Device)

Per coordinator update cycle (`_async_update_data`):

1. **authenticate()** - 1 call (auth endpoint)
   - Uses cached token if still valid (2-hour expiry)
   - Only makes actual API call if token expired
   
2. **get_power_stations()** - 1 call (data endpoint)
   - Retrieves list of power stations
   
3. **get_devices(station_id)** - 1 call per station (data endpoint)
   - For 1 station: 1 call
   
4. **get_device_parameters(device_id)** - 1 call per device (data endpoint)
   - For 1 device: 1 call
   
5. **get_latest_data_by_datapoints()** - 1 call per device (data endpoint)
   - For 1 device: 1 call

**Total calls per cycle (1 station, 1 device):**
- Auth calls: 0-1 (only when token expires, ~every 2 hours)
- Data calls: 4 (stations + devices + parameters + latest data)

### Scaled Pattern (Multiple Stations/Devices)

For N stations with M devices each:

- **Auth calls**: 0-1 (cached token)
- **Data calls**: 1 + N + (N × M) + (N × M)
  - 1 for get_power_stations
  - N for get_devices (one per station)
  - N × M for get_device_parameters (one per device)
  - N × M for get_latest_data_by_datapoints (one per device)

**Example: 2 stations, 3 devices each:**
- Data calls per cycle: 1 + 2 + 6 + 6 = **15 calls**

## Update Interval Configuration

### Current Settings

- **Default**: 10 seconds
- **User Configurable**: 5-300 seconds
- **Minimum Safe**: 15 seconds (recommended)

### Rate Limit Compliance Analysis

#### With 10-Second Interval (Default)

**Scenario: 1 station, 1 device**
- Calls per cycle: 4 data calls
- Cycles per minute: 6 updates
- Total calls per minute: **24 data calls**
- **Status**: ✅ SAFE (under 30/minute limit)

**Scenario: 2 stations, 3 devices each**
- Calls per cycle: 15 data calls
- Cycles per minute: 6 updates
- Total calls per minute: **90 data calls**
- **Status**: ⚠️ **EXCEEDS LIMIT** (over 30/minute limit)

#### With 5-Second Interval (Minimum Allowed)

**Scenario: 1 station, 1 device**
- Calls per cycle: 4 data calls
- Cycles per minute: 12 updates
- Total calls per minute: **48 data calls**
- **Status**: ⚠️ **EXCEEDS LIMIT** (over 30/minute limit)

#### With 15-Second Interval (Recommended)

**Scenario: 1 station, 1 device**
- Calls per cycle: 4 data calls
- Cycles per minute: 4 updates
- Total calls per minute: **16 data calls**
- **Status**: ✅ SAFE (well under limit)

**Scenario: 2 stations, 3 devices each**
- Calls per cycle: 15 data calls
- Cycles per minute: 4 updates
- Total calls per minute: **60 data calls**
- **Status**: ⚠️ **EXCEEDS LIMIT** (over 30/minute limit)

#### With 30-Second Interval

**Scenario: 2 stations, 3 devices each**
- Calls per cycle: 15 data calls
- Cycles per minute: 2 updates
- Total calls per minute: **30 data calls**
- **Status**: ✅ SAFE (exactly at limit)

## ⚠️ IDENTIFIED ISSUES

### Issue 1: Internal Rate Limiting Not Sufficient for All Scenarios

**Problem**: While the API client correctly enforces 2-second delays between **individual** data calls, it does not prevent exceeding the **30 calls per minute** limit when:
- Multiple stations/devices exist
- Update interval is too short
- Coordinator makes many rapid calls within a single update cycle

**Example Failure Scenario:**
- 1 station, 1 device, 10-second interval = 4 calls per cycle
- With rate limiting: Call 1 at 0s, Call 2 at 2s, Call 3 at 4s, Call 4 at 6s
- Next cycle at 10s: Call 5 at 10s, Call 6 at 12s...
- After 60s: 24 calls ✅ SAFE

But with 2 stations, 3 devices each:
- 15 calls per cycle with 2-second spacing = 30 seconds to complete one cycle
- If update interval is 10 seconds, coordinator tries to start next cycle while previous is still running
- This can queue up calls and potentially exceed limits

### Issue 2: Minimum Update Interval Too Aggressive

**Problem**: Current minimum of 5 seconds allows users to configure intervals that **will definitely exceed** rate limits.

**Example:**
- 1 station, 1 device (4 calls/cycle)
- 5-second interval = 12 cycles/minute = 48 calls/minute
- **Exceeds 30/minute limit by 60%**

### Issue 3: No Warning for Complex Configurations

**Problem**: Users with multiple stations/devices are not warned that they may need longer intervals.

## 🔧 RECOMMENDED FIXES

### Fix 1: Increase Minimum Update Interval

Change minimum from 5 seconds to **15 seconds**:

```python
# config_flow.py
vol.Required(
    CONF_UPDATE_INTERVAL,
    default=DEFAULT_UPDATE_INTERVAL,
): vol.All(vol.Coerce(int), vol.Range(min=15, max=300)),  # Changed from min=5
```

**Rationale:**
- 15-second minimum ensures safe operation with 1 station, 1 device
- Provides buffer for rate limiting delays
- Still allows near-real-time updates

### Fix 2: Add Dynamic Interval Calculation

Add warning in coordinator if configuration may exceed limits:

```python
def _calculate_safe_interval(self, num_stations: int, num_devices: int) -> int:
    """Calculate safe update interval based on number of stations/devices."""
    # Calls per cycle: 1 + N + (N*M) + (N*M) where N=stations, M=avg devices
    # Simplified: 1 + N + 2NM
    total_devices = num_devices
    calls_per_cycle = 1 + num_stations + (2 * total_devices)
    
    # Need to stay under 30 calls/minute
    # cycles_per_minute = 30 / calls_per_cycle
    # interval = 60 / cycles_per_minute = 60 * calls_per_cycle / 30
    safe_interval = (60 * calls_per_cycle) / 30
    
    # Add 20% buffer
    safe_interval = safe_interval * 1.2
    
    return max(15, int(safe_interval))

async def _async_update_data(self):
    """Update data via library."""
    # After discovering stations/devices, check interval
    if hasattr(self, '_interval_warned'):
        return
    
    num_stations = len(stations_list)
    num_devices = sum(len(data["devices"][sid].get("data", {}).get("list", [])) 
                     for sid in data["devices"])
    
    safe_interval = self._calculate_safe_interval(num_stations, num_devices)
    current_interval = self.update_interval.total_seconds()
    
    if current_interval < safe_interval:
        _LOGGER.warning(
            "Update interval (%ds) may exceed API rate limits with %d stations and %d devices. "
            "Recommended minimum: %ds. You can adjust this in integration options.",
            current_interval, num_stations, num_devices, safe_interval
        )
        self._interval_warned = True
```

### Fix 3: Add Rate Limit Error Handling

Enhance error handling to detect rate limit errors:

```python
# In api.py, _make_authenticated_request()
if data.get("status") == 5126:  # Too frequent requests
    _LOGGER.error("API rate limit exceeded! The integration is making too many requests.")
    _LOGGER.error("Please increase the update interval in integration options.")
    await asyncio.sleep(10)  # Back off longer
    raise SolarGuardianAPIError("Rate limit exceeded - please increase update interval")
```

### Fix 4: Add Documentation to Options Flow

```python
# In config_flow.py OptionsFlowHandler
data_schema = vol.Schema({
    vol.Required(CONF_UPDATE_INTERVAL, default=current_interval): vol.All(
        vol.Coerce(int), 
        vol.Range(min=15, max=300)
    ),
})

# Update strings.json
"data_description": {
    "update_interval": "Update interval in seconds (15-300). Lower values provide more frequent updates but increase API usage. Recommended: 15s for single device, 30s+ for multiple devices to avoid rate limiting."
}
```

## 📊 SAFE CONFIGURATION GUIDELINES

### Single Station, Single Device
- **Minimum**: 15 seconds ✅
- **Recommended**: 15-20 seconds
- **API Usage**: ~16-20 calls/minute

### Single Station, 2-3 Devices
- **Minimum**: 20 seconds
- **Recommended**: 30 seconds ✅
- **API Usage**: ~20-30 calls/minute

### Multiple Stations (2+) or 4+ Devices
- **Minimum**: 30 seconds
- **Recommended**: 60 seconds ✅
- **API Usage**: ~15-30 calls/minute

### Large Installation (3+ stations, 6+ devices)
- **Minimum**: 60 seconds
- **Recommended**: 120 seconds
- **API Usage**: ~15-20 calls/minute

## 🎯 ACTION ITEMS

### Priority 1: CRITICAL (Prevent Rate Limit Violations)
- [ ] Increase minimum update interval from 5s to 15s
- [ ] Add rate limit detection in error handling
- [ ] Update documentation to warn about rate limits

### Priority 2: HIGH (User Experience)
- [ ] Add dynamic interval calculation with warnings
- [ ] Enhance options flow description
- [ ] Add configuration examples to README

### Priority 3: MEDIUM (Long-term Improvements)
- [ ] Add auto-adjustment of interval if rate limit detected
- [ ] Add dashboard showing API usage statistics
- [ ] Implement caching for less-frequently-changing data (device parameters)

## 📝 SUMMARY

**Current Status:**
- ✅ Rate limiting **IS** implemented in API client
- ✅ Individual calls are spaced correctly (2s for data, 6s for auth)
- ⚠️ **ISSUE**: Minimum interval (5s) allows rate limit violations
- ⚠️ **ISSUE**: No warnings for users with multiple devices

**Immediate Risk:**
- Users with default 10s interval and 2+ devices may hit rate limits
- Users who set 5s interval will definitely hit rate limits

**Recommended Action:**
1. **Immediately**: Increase minimum interval to 15 seconds
2. **Soon**: Add warning when configuration may exceed limits
3. **Future**: Implement auto-adjustment based on actual usage

---
**Last Updated**: October 1, 2025
**Status**: Requires fixes to prevent rate limit violations
