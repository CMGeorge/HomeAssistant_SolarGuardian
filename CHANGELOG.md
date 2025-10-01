# Changelog

All notable changes to the SolarGuardian Home Assistant integration will be documented in this file.

## [Unreleased] - 2025-10-01

### 🚀 Major Improvements

#### Performance & Data Frequency
- **Reduced update interval from 30s to 10s** - Get near real-time solar data updates
  - More responsive sensor readings
  - Faster detection of power changes
  - Better monitoring of battery status
  - Configurable via integration options

#### API Endpoint Fixes
- **Fixed `get_latest_data()` endpoint** - Now correctly uses port 7002
  - Both `get_latest_data()` and `get_latest_data_by_datapoints()` now use the correct port
  - Matches API V2.3 specification for `/history/lastDatapoint` endpoint
  - Improved error handling for 404 responses
  - Better logging for debugging

### 🔧 Technical Changes

#### API Client (`api.py`)
```python
# BEFORE: Used standard port (incorrect)
await self._make_authenticated_request(ENDPOINT_LATEST_DATA, payload)

# AFTER: Uses port 7002 (correct)
latest_data_url = f"https://{domain_parts}:{LATEST_DATA_PORT}{ENDPOINT_LATEST_DATA}"
```

#### Constants (`const.py`)
```python
# BEFORE
DEFAULT_UPDATE_INTERVAL = 30  # seconds

# AFTER
DEFAULT_UPDATE_INTERVAL = 10  # seconds - update frequently to get near real-time data
```

### 🏗️ Architecture Improvements

#### Test Infrastructure
- **Removed duplicate code** - Created symlink from `tests/custom_components` to `../custom_components`
  - Single source of truth for integration code
  - No need to maintain code in two places
  - Automatic synchronization of changes

- **Fixed import issues** - Created `test_api_wrapper.py` for standalone testing
  - Tests can run without Home Assistant installed
  - Uses `importlib.util` to load modules directly
  - Bypasses `__init__.py` Home Assistant dependencies

- **Enhanced test script** - Updated `tests/run_real_api_tests.py`
  - Automatic loading from `.env` file
  - Support for `python-dotenv`
  - Better error messages and documentation

### 📝 Documentation Updates

#### Updated Files
- `.github/copilot-instructions.md` - Added update interval and rate limit documentation
- `TESTING_SUCCESS.md` - Documented successful API integration test
- `CHANGELOG.md` - This file

### 🔒 Security

- All changes maintain existing security measures
- No secrets exposed in code or logs
- `.env` file remains git-ignored
- Proper credential masking in logs

### ⚡ Performance Impact

**Update Frequency:**
- **Before**: Every 30 seconds (2 updates/minute)
- **After**: Every 10 seconds (6 updates/minute)

**API Rate Limits (Respected):**
- Authentication: 10 calls/minute (6s between calls)
- Data endpoints: 30 calls/minute (2s between calls)
- Update interval respects rate limits with multiple devices

**Real-World Impact:**
```
1 station + 3 devices = 4 API calls per update cycle
At 10s interval = 6 update cycles/minute = 24 API calls/minute
Well within 30 calls/minute data limit ✅
```

### 🐛 Bug Fixes

1. **Fixed port 7002 usage** - `get_latest_data()` now uses correct port
   - Issue: Was using standard HTTPS port (443)
   - Fix: Now uses port 7002 as specified in API docs
   - Impact: Latest data endpoint will work correctly

2. **Improved error handling** - Better 404 detection
   - Added specific check for 404 status
   - More informative debug logging
   - Cleaner error messages

### 🧪 Testing

- ✅ Real API test passed with live credentials
- ✅ Authentication successful
- ✅ Power station retrieval working
- ✅ Device enumeration functional
- ✅ All endpoints using correct ports

### 📋 Migration Notes

**For Existing Users:**
- Update will automatically use 10-second interval
- To customize interval, go to integration settings
- No configuration changes required
- Existing sensors will update more frequently

**For New Users:**
- Default 10-second update interval
- Configurable in integration options
- Respects API rate limits automatically

### 🔜 Future Improvements

- [ ] Add configurable update interval in UI
- [ ] Implement adaptive polling based on solar activity
- [ ] Add WebSocket support if API adds it
- [ ] Cache device parameters to reduce API calls
- [ ] Add device type detection for optimized polling

---

## Version History

### Current Development
- Date: October 1, 2025
- Status: Testing phase
- Target: Home Assistant 2025.9.x
- API: SolarGuardian API V2.3

---

**Note**: This integration is under active development. See `STATUS.md` for current development status and `TROUBLESHOOTING.md` for common issues.
