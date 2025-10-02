# Home Assistant Code Reload Instructions

## Issue

Home Assistant is still running the **old version** of the code, even though the fix has been committed and pushed.

## Why This Happens

Home Assistant caches Python modules in memory. Simply restarting the integration or reloading YAML is **not enough** to reload custom component code.

## Solution: Full Restart Required

### Option 1: Restart Home Assistant (Recommended)

1. **Go to Settings → System → Restart**
2. Click "Restart Home Assistant"
3. Wait for Home Assistant to fully restart (30-60 seconds)
4. Check logs again

### Option 2: Command Line Restart

If you have SSH access:

```bash
# For Home Assistant OS/Supervised
ha core restart

# For Home Assistant Container
docker restart homeassistant

# For Home Assistant Core (venv)
systemctl restart home-assistant@homeassistant
```

### Option 3: Reload Integration (Less Reliable)

**Note**: This may not always work for code changes.

1. Go to **Settings → Devices & Services**
2. Find "SolarGuardian" integration
3. Click the three dots menu → "Reload"
4. Wait 10 seconds
5. Check logs

## Verification Steps

After restart, verify the fix:

1. **Check the integration loads**:
   - Go to Settings → Devices & Services
   - Find SolarGuardian - should show "X entities" (not error)

2. **Check logs** (Settings → System → Logs):
   - Should see: "Setting up sensors with data status: success"
   - Should see: "Successfully set up X sensors for device Y"
   - Should **NOT** see: "UnboundLocalError"

3. **Check sensors are created**:
   - Go to Settings → Devices & Services → SolarGuardian
   - Click on your device
   - You should see device info sensors:
     - Device Serial
     - Gateway ID
     - Gateway Name
     - Product Name
     - Location
     - Status Text
   - Plus all your parameter sensors (Battery Voltage, PV Power, etc.)

## Expected Behavior After Fix

✅ Integration loads successfully
✅ All sensors created (device info + parameters)
✅ No errors in logs
✅ Sensors update every 15 seconds (or your configured interval)

## Troubleshooting

### If Error Persists After Restart

1. **Verify file was copied correctly**:

   ```bash
   # Check the file on Home Assistant
   cat /config/custom_components/solarguardian/sensor.py | grep -A 5 "device_sensors = 0"
   ```

   Should show:

   ```python
   # Initialize device sensor counter
   device_sensors = 0

   # Add device information sensors
   ```

2. **Check file permissions**:

   ```bash
   ls -la /config/custom_components/solarguardian/sensor.py
   ```

   Should be readable by Home Assistant user.

3. **Force clear Python cache**:

   ```bash
   # Remove Python cache files
   find /config/custom_components/solarguardian -name "*.pyc" -delete
   find /config/custom_components/solarguardian -name "__pycache__" -type d -exec rm -rf {} +

   # Then restart Home Assistant
   ha core restart
   ```

### If You Need to Manually Copy File

If you're updating via git pull or manual copy:

```bash
# On your development machine
cd /Users/cmgeorge/Dev/CMGeorge/HomeAssistant_SolarGuardian

# Copy to Home Assistant
scp custom_components/solarguardian/sensor.py \
    root@your-homeassistant-ip:/config/custom_components/solarguardian/

# Or via Samba/SMB share
# Navigate to \\your-homeassistant-ip\config\custom_components\solarguardian\
# Replace sensor.py with the new version

# Then restart Home Assistant
```

## Quick Verification Script

Run this on your development machine to verify the fix is in the file:

```bash
cd /Users/cmgeorge/Dev/CMGeorge/HomeAssistant_SolarGuardian
grep -n "device_sensors = 0" custom_components/solarguardian/sensor.py
```

Should show:

```
388:            # Initialize device sensor counter
389:            device_sensors = 0
```

If line 389 shows `device_sensors = 0`, the fix is correct in your local file.

## Summary

**The fix is correct in git**, but Home Assistant needs a **full restart** to load the new code.

**Action Required**:

1. Restart Home Assistant (full restart, not just reload)
2. Wait 30-60 seconds for restart to complete
3. Check logs for success

The error should disappear after the restart! ✅

---

**Last Updated**: October 1, 2025
**Fix Commit**: d9206a8
**Status**: Code fixed, restart required
