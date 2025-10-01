# Quick Fix: Unknown Sensor Values - October 1, 2025

## Your Report

**Working Sensors (Device Info):**
- ✅ Alarm
- ✅ Gateway ID
- ✅ Serial
- ✅ Status
- ✅ Product Name
- ✅ Location

**Not Working (Parameter Sensors):**
- ❌ All numeric sensors showing "Unknown"
- Battery Voltage, PV Power, SOC, etc.

## What I've Done (Commit 7eb3322)

### 1. Enhanced Sensor Debugging
Added comprehensive logging to see exactly why sensors are showing "Unknown":

```python
# Now logs:
- "No device data available for {device}" 
- "No latest_data available for {device}"
- "Sensor {name} got value from latest_data: {value}"
- "Sensor {name} got value from variable.{field}: {value}"
- "No value found for sensor {name} - check if latest_data is enabled"
```

### 2. Better Value Fallback
Sensors now try multiple value sources:
1. `latest_data` (real-time API data)
2. `variable.currentValue` (from device config)
3. `variable.value` (alternative field)
4. `variable.defaultValue` (fallback)

### 3. Entity Categories
All sensors now properly organized:

**Diagnostic Section** (technical info):
- Device Serial
- Gateway ID
- Product Name
- Location
- Status
- Any technical parameters

**Main Sensors** (measurements):
- Battery Voltage/Current/SOC
- PV Voltage/Current/Power
- AC Output
- Energy counters
- Temperature

### 4. Control API Documentation
Discovered and documented control capabilities:
- ✅ API supports writable parameters
- ✅ Switches (Load ON/OFF)
- ✅ Numbers (Battery capacity, voltage thresholds)
- ✅ Rate limit: 10 commands/second
- 📋 Full implementation guide created

## What You Need to Do NOW

### Step 1: Update Integration from HACS

1. Open HACS in Home Assistant
2. Go to Integrations
3. Find "SolarGuardian"
4. Click "Redownload" or "Update"
5. Should pull commit `7eb3322`
6. **Restart Home Assistant** (full restart required)

### Step 2: Enable Debug Logging

Add to `configuration.yaml`:

```yaml
logger:
  default: info
  logs:
    custom_components.solarguardian: debug
```

Restart Home Assistant again.

### Step 3: Check Latest Data Status

Run this service:

```yaml
service: solarguardian.get_diagnostics
```

Look for:
```json
{
  "latest_data_disabled": false,  // Should be false
  "latest_data_failures": 0,      // Should be 0
}
```

**If `latest_data_disabled` is `true`**, run:

```yaml
service: solarguardian.reset_latest_data
```

Wait 30 seconds for next update cycle.

### Step 4: Check Logs

Go to Settings → System → Logs, search for "solarguardian"

**Look for these messages:**

**Good signs:**
```
Retrieved X latest values for device Y
Sensor Battery Voltage (BatteryVoltage) got value from latest_data: 25.6
Setting up sensors with data status: success
```

**Problem signs:**
```
Latest data endpoint consistently failing (5 failures), disabling
No latest_data available for UP HI - not present
No value found for sensor Battery Voltage (BatteryVoltage)
```

### Step 5: Share Logs

Copy any error messages or the full diagnostic output and share them so I can:
- See if latest_data is working
- See what data structure we're actually receiving
- Identify why values aren't being found

## Common Issues & Solutions

### Issue 1: Latest Data Disabled

**Symptom:** All sensors show "Unknown"

**Log message:**
```
Latest data endpoint consistently failing (5 failures), disabling
```

**Solution:**
```yaml
service: solarguardian.reset_latest_data
```

### Issue 2: Wrong API Port

**Symptom:** 404 errors for latest data

**Log message:**
```
Latest data API request failed: 404
```

**Solution:** Already fixed in code - uses port 7002 automatically

### Issue 3: Data Structure Mismatch

**Symptom:** Sensors created but show "Unknown"

**Log message:**
```
No value found for sensor {name} - check if latest_data is enabled
```

**Solution:** Need to see your actual device data structure - run diagnostics service

## Expected Behavior After Fix

### Home Assistant UI

**Device Card should show TWO sections:**

1. **Main Sensors** (top):
   - Battery Voltage: 25.6 V
   - Battery SOC: 99%
   - PV Power: 69.62 W
   - AC Output Power: 100 W
   - Temperature: 25°C

2. **Diagnostic** (collapsed section at bottom):
   - Serial: 0000000001742059729951
   - Gateway ID: 06150296093XY22X-00831
   - Product Name: UP HI
   - Location: Strada Huszár, Ciumani
   - Status: Online

### Logs

Every 15 seconds (your update interval):
```
Update complete: 1 stations, 1 devices, 95 sensors, 0 errors
Retrieved 89 latest values for device UP HI
Sensor Battery Voltage got value from latest_data: 25.6
Sensor PV Power got value from latest_data: 69.62
```

## Control Features (Future)

**YES**, controls are available! 🎉

The API documentation shows:
- **Switches**: Load control (ON/OFF)
- **Numbers**: Battery capacity, voltage thresholds
- **Rate limit**: 10 commands/second

Implementation guide created in `CONTROL_IMPLEMENTATION_GUIDE.md`.

**Next steps for controls:**
1. First fix sensor values (priority)
2. Identify which parameters are writable (`rwmode=1`)
3. Implement switch platform for Load control
4. Implement number platform for adjustable settings
5. Add safety confirmations for critical parameters

## Diagnostic vs. Standard Entities

**Why separate them?**

Home Assistant best practices:
- **Diagnostic** = Technical/configuration info (shown in collapsed section)
- **Standard** = Operational measurements (shown prominently)

**Benefits:**
- Cleaner main view (only important sensors)
- Technical details available when needed
- Follows Home Assistant conventions
- Better mobile app experience

**You can always see diagnostic entities:**
- Click on device card
- Expand "Diagnostic" section at bottom
- All info still available, just organized

## Summary

✅ **Committed (7eb3322):**
- Enhanced logging to diagnose "Unknown" values
- Better fallback logic for sensor values
- Entity categories for organization
- Control API fully documented

⏳ **Your Action Required:**
1. Update integration from HACS
2. Restart Home Assistant  
3. Enable debug logging
4. Run diagnostics service
5. Share logs/output

🎯 **Goal:**
- All numeric sensors showing real values
- Better organized UI (diagnostic vs. standard)
- Path forward for control features

📊 **Timeline:**
- Immediate: Update & check logs
- Short-term: Fix sensor values
- Medium-term: Implement controls

---

**Commit:** 7eb3322  
**Status:** Awaiting user update and diagnostics  
**Next:** Analyze logs to identify root cause of "Unknown" values
