# Control Platform Implementation Guide

**Date**: October 1, 2025  
**Status**: 📋 Ready for Implementation  
**Priority**: HIGH - Adds missing functionality

## Executive Summary

**YES! We can implement controls!** 🎉

The configuration parameters showing "Unknown" are actually **writable parameters**. They're controls, not sensors!

### What the API Provides

✅ **Write/Control**: Command issuing endpoint (Section 6 of API docs)  
⚠️ **Read Current Values**: Not directly available (use optimistic mode)  
✅ **Parameter Definitions**: Already have (names, ranges, translations)

### API Command Endpoint

```http
POST {commandServerAddr}/v1.0/datapoint/{gatewayId}
Headers: X-Access-Token, Content-Type: application/json
Body: {"setDataPoint": [{"slaveName": "Device", "dataPointId": "123", "value": "1"}]}
Rate Limit: 10 commands/second
```

## Summary Answer

**Yes, the "Unknown" parameters are controls!**

- 44 writable configuration parameters
- 3 Home Assistant platforms: Number (voltages, currents, times), Select (modes), Switch (on/off)
- API fully supports writing values
- Need to implement optimistic mode (assume success since can't read back)

## Implementation Estimate

- **21 hours total** (API + 3 platforms + safety + testing + docs)
- Can start with simple controls (Load Switch, Buzzer) for quick testing
- Critical parameters (Battery Type, Voltages) need extra safety validation

## Questions for You

1. **Do you want controls implemented?** (Yes/No/Maybe)
2. **Priority level?** (Immediate/Soon/Eventually)  
3. **Willing to test with your device?** (Required for implementation)
4. **Which controls are most important to you?**

See full implementation details below ⬇️

---

## Controllable Parameters (44 total)

### Battery Settings (5 controls)
- Battery Type → **Select**: User/Lithium/Lead-acid
- Battery Capacity → **Number**: 50-1000 Ah  
- Battery Detection, BMS, Protocol → **Switch/Select**

### Charging Voltages (7 controls) ⚠️ CRITICAL  
- Bulk/Float/Equalize Voltages → **Number**: 48-64 V
- Charging Limit, Recovery → **Number**

### Protection Settings (5 controls) ⚠️ CRITICAL
- Low Voltage Disconnect/Recovery → **Number**: 40-52 V
- Undervoltage Alarms → **Number**

### Current Limits (3 controls)
- Charging/Discharging Currents → **Number**: 0-200 A

### Operating Modes (4 controls)
- Charging Mode → **Select**: Solar First/Utility First/etc.
- Output Mode, Load Control → **Select**

### Switches (6 controls)
- Load Switch, Buzzer, PV Control → **Switch**: On/Off

### Temperature (4 controls)
- Temp Compensation, Unit, Limits → **Number/Select**

### Timing/Misc (10 controls)  
- Charge Times, LCD Timeout, Device Time, etc.

## Implementation Plan

### Phase 1: API Client (2 hours)
```python
# api.py - Add methods
async def get_command_server_address() -> str
async def send_command(gateway_id, slave_name, datapoint_id, value) -> bool
```

### Phase 2: Number Platform (4 hours)
```python
# number.py - NEW FILE
class SolarGuardianNumber(CoordinatorEntity, NumberEntity):
    async def async_set_native_value(value):
        await coordinator.api.send_command(...)
```

### Phase 3: Select Platform (4 hours)
```python
# select.py - NEW FILE  
class SolarGuardianSelect(CoordinatorEntity, SelectEntity):
    async def async_select_option(option):
        value = translate_option_to_value(option)
        await coordinator.api.send_command(...)
```

### Phase 4: Switch Platform (2 hours)
```python
# switch.py - NEW FILE
class SolarGuardianSwitch(CoordinatorEntity, SwitchEntity):
    async def async_turn_on/off():
        await coordinator.api.send_command(...)
```

### Phase 5: Safety & Config (3 hours)
- Add "Enable Controls" option (default: OFF)
- Show safety warning when enabling
- Mark critical parameters with warnings
- Add validation for voltage/current ranges

### Phase 6: Testing & Docs (6 hours)
- Test API calls with real device
- Start with safe parameters (LCD, Buzzer)
- Test critical parameters carefully  
- Write user documentation

**Total**: 21 hours

## Safety Implementation

### Critical Parameters
```python
CRITICAL_PARAMETERS = {
    "VTYPE": "Battery Type - FIRE RISK",
    "BULKVOLT": "Bulk Voltage - BATTERY DAMAGE",
    "FLOATVOLT": "Float Voltage - BATTERY DAMAGE",
    # etc.
}
```

### Configuration Warning
```
⚠️ WARNING: Device controls allow changing inverter settings.

Incorrect settings can:
• Damage batteries (wrong voltages)
• Damage inverter (excess current)
• Void warranty
• Cause fires (wrong battery type)

Only enable if you understand your equipment!
```

### Entity Safety
- Mark critical entities with `EntityCategory.CONFIG`
- Show warning icon on critical controls
- Log all critical parameter changes
- Validate ranges before sending

## Testing Strategy

1. **API Testing** (safe, no device changes)
   ```python
   # Test getting command server address
   # Test command format (don't send yet)
   ```

2. **Safe Parameter Testing** (start here!)
   - LCD Backlight Timeout (can't break anything)
   - Buzzer Alarm (just sound)
   - Load Switch (easily reversible)

3. **Critical Parameter Testing** (careful!)
   - Battery Capacity (verify it works)
   - Temperature limits (not immediately dangerous)
   - Eventually: Voltages (with extreme caution)

## User Documentation

### Enable Controls
1. Configuration → Integrations → SolarGuardian → Configure
2. Enable "Device Controls"  
3. Read and accept warning
4. Restart Home Assistant

### Control Entities Appear
- **number.solar_inverter_bulk_voltage** (48.0-58.4 V)
- **select.solar_inverter_charging_mode** (Solar First/Utility First/etc.)
- **switch.solar_inverter_load_switch** (On/Off)

### Use Controls
```yaml
# Set charging voltage
service: number.set_value
data:
  entity_id: number.solar_inverter_bulk_voltage
  value: 56.4

# Change mode
service: select.select_option
data:
  entity_id: select.solar_inverter_charging_mode
  option: "Solar First"
```

## Optimistic Mode Explained

**Problem**: API can write values but doesn't provide easy way to read them back

**Solution**: Optimistic mode
- When user sets value, immediately update entity state
- Don't wait for confirmation from device
- If command fails, log error and restore previous state
- Mark entities with `assumed_state = True`

This is standard HA pattern for write-only controls!

---

## Next Steps

**Waiting for your decision:**

1. Should we implement controls? (Yes/No)
2. What's the priority? (High/Medium/Low)
3. Are you willing to test with your device?
4. Which controls do you want most?

If yes, I can start with Phase 1 (API client) right away!

