# Device Status Sensor - Technical Documentation

**Date**: October 1, 2025  
**Sensor**: `sensor.{device_name}_device_status`  
**Type**: Numeric bitmask status register  
**User System**: Off-grid solar installation

## Overview

The **Device Status** sensor displays a numeric value representing the inverter's operational state as a bitmask. Each bit in the binary representation indicates a specific condition or mode.

## Current Behavior

- **Sensor Type**: Numeric (no enum translations)
- **Value Format**: Decimal number (e.g., 5249.00)
- **Update Frequency**: Real-time (mode="0")
- **API Field**: `dataIdentifier: "equipmentStatus"`

## Off-Grid System Analysis

### User's System Configuration
- **Type**: Off-grid (no utility/grid connection)
- **Typical Status**: 5249
- **Binary**: `0b1010010000001`
- **Hex**: `0x1481`

### Active Bits (Status 5249)

| Bit | Decimal | Likely Meaning | Status |
|-----|---------|----------------|--------|
| 0 | 1 | System Running | ✓ Active |
| 7 | 128 | Battery Mode / Off-Grid Operation | ✓ Active |
| 10 | 1024 | Solar Charging / Battery Active | ✓ Active |
| 12 | 4096 | Inverter Output Active | ✓ Active |

**Interpretation**: Normal off-grid operation
- System is operational
- Running in battery/solar mode (no grid)
- PV charging or battery supplying power
- Inverter converting DC to AC for loads

## Understanding Status Changes

### What Different Values Might Mean

Since this is a **bitmask**, the value changes as operating conditions change:

**Example Scenarios**:

```python
# Daytime - Solar charging, loads active
5249 = bits 0,7,10,12 (Running, Battery mode, Charging, Output)

# Night - Battery only, loads active  
4225 = bits 0,7,12 (Running, Battery mode, Output)
# (bit 10 off = no solar input)

# Sleep mode - No loads
129 = bits 0,7 (Running, Battery mode only)
# (bits 10,12 off = no charging, no output)

# Fault condition
161 = bits 0,5,7 (Running, Fault flag, Battery mode)
# (bit 5 might indicate fault)
```

## Monitoring Recommendations

### 1. Track Status Changes

Monitor when the value changes to understand operating patterns:

```yaml
# automation.yaml
- alias: "Log Inverter Status Changes"
  trigger:
    - platform: state
      entity_id: sensor.solar_inverter_device_status
  action:
    - service: logbook.log
      data:
        name: "Inverter Status"
        message: >
          Status changed from {{ trigger.from_state.state }} to {{ trigger.to_state.state }}
          (Binary: {{ '%016b' | format(trigger.to_state.state | int) }})
```

### 2. Create Binary Sensors for Key Bits

Extract individual bits for easier monitoring:

```yaml
# configuration.yaml
template:
  - binary_sensor:
      - name: "Solar Inverter Running"
        state: "{{ states('sensor.solar_inverter_device_status') | int | bitwise_and(1) > 0 }}"
        device_class: power
        
      - name: "Solar Inverter Battery Mode"
        state: "{{ states('sensor.solar_inverter_device_status') | int | bitwise_and(128) > 0 }}"
        device_class: battery
        
      - name: "Solar Inverter Charging Active"
        state: "{{ states('sensor.solar_inverter_device_status') | int | bitwise_and(1024) > 0 }}"
        device_class: battery_charging
        
      - name: "Solar Inverter Output Active"
        state: "{{ states('sensor.solar_inverter_device_status') | int | bitwise_and(4096) > 0 }}"
        device_class: power
```

### 3. Alert on Unexpected Changes

```yaml
- alias: "Inverter Status Fault Alert"
  trigger:
    - platform: numeric_state
      entity_id: sensor.solar_inverter_device_status
      # Alert if value changes significantly from normal
      above: 6000  # Or below 4000
  action:
    - service: notify.mobile_app
      data:
        title: "Inverter Status Change"
        message: "Unusual status value: {{ states('sensor.solar_inverter_device_status') }}"
```

## Off-Grid Specific Notes

### Normal Operating Range

For off-grid systems, typical status values might be:

| Scenario | Typical Range | Description |
|----------|---------------|-------------|
| Day + Loads | 5000-5500 | Solar charging, output active |
| Day + No loads | 1000-1500 | Solar charging only |
| Night + Loads | 4000-4500 | Battery discharge, output active |
| Night + No loads | 100-200 | Standby mode |
| Fault | Variable | Unusual bit patterns |

### Correlation with Other Sensors

Monitor Device Status alongside:

```yaml
# Example dashboard card
type: entities
entities:
  - entity: sensor.solar_inverter_device_status
    name: Status Register
  - entity: sensor.solar_inverter_pv_charging_status
    name: PV Charging
  - entity: sensor.solar_inverter_output_load_status
    name: Load Status
  - entity: sensor.solar_inverter_battery_soc
    name: Battery SOC
  - entity: sensor.solar_inverter_pv_power
    name: Solar Power
  - entity: sensor.solar_inverter_output_power
    name: Load Power
```

## Bit Analysis Tools

### Decode Current Status

Use this template to decode the status value:

```yaml
# template sensor for human-readable status
template:
  - sensor:
      - name: "Solar Inverter Status Decoded"
        state: >
          {% set status = states('sensor.solar_inverter_device_status') | int %}
          {% set bits = [] %}
          {% if status | bitwise_and(1) > 0 %}{% set bits = bits + ['Running'] %}{% endif %}
          {% if status | bitwise_and(128) > 0 %}{% set bits = bits + ['Battery Mode'] %}{% endif %}
          {% if status | bitwise_and(1024) > 0 %}{% set bits = bits + ['Charging'] %}{% endif %}
          {% if status | bitwise_and(4096) > 0 %}{% set bits = bits + ['Output Active'] %}{% endif %}
          {{ bits | join(', ') if bits | length > 0 else 'Unknown' }}
```

### History Tracking

Track status values over time to identify patterns:

```yaml
# Lovelace history card
type: history-graph
entities:
  - entity: sensor.solar_inverter_device_status
hours_to_show: 24
```

## Future Enhancement Ideas

### If Official Documentation Becomes Available

1. **Add translationChild mappings** to API
2. **Create binary_sensor platform** for individual bits
3. **Add human-readable state names** to main sensor
4. **Document all bit meanings** officially

### User Can Help By

1. **Recording status values** during different conditions:
   - Full sun, charging, loads on
   - Night, battery only, loads on
   - No loads, standby
   - Fault conditions (if they occur)

2. **Correlating with events**:
   - When does status = 5249?
   - When does it change?
   - What causes specific values?

3. **Sharing patterns** for documentation:
   - Your observations help other users
   - Build knowledge base for off-grid setups

## Troubleshooting

### Status Value Never Changes
- Normal if operating conditions are stable
- Check other sensors to verify system is active

### Unexpected Status Values
- Note the value
- Check other sensors for clues
- Look for error messages in logs
- May indicate fault condition

### Status Shows 0 or None
- Communication issue with device
- Check other sensors also showing Unknown
- Integration may need restart

## Technical Details

### API Response Format
```json
{
  "dataPointId": 105646595,
  "dataPointName": "设备状态点",
  "value": "5249.00",
  "deviceNo": "...",
  "time": 1759334139387
}
```

### Sensor Configuration
```python
# In sensor.py
{
    "name": "Device Status",
    "unit": None,  # No unit for status register
    "device_class": None,  # Generic numeric sensor
    "state_class": None,  # Not a measurement
    "icon": "mdi:chip"
}
```

### Value Processing
- Raw API value: "5249.00"
- Displayed as: 5249.00 (or 5249)
- No decimal division applied for status registers
- No enum translation (translationChild empty)

## Related Sensors

**Other Status Indicators**:
- `sensor.{device}_pv_charging_status` - Solar charging state (enum)
- `sensor.{device}_utility_charging_status` - Grid charging state (enum)
- `sensor.{device}_output_load_status` - Load condition (enum)
- `sensor.{device}_device_fault` - Fault indicator (enum)
- `sensor.{device}_battery_voltage_alarm` - Battery alerts (enum)
- `sensor.{device}_battery_temperature_alarm` - Temperature alerts (enum)

These provide more specific status information with human-readable values.

## Contributing

If you discover patterns in your Device Status values:

1. **Document the pattern**: Status value → Operating condition
2. **Share your findings**: Open GitHub issue or discussion
3. **Help others**: Your off-grid experience is valuable!

Example contribution:
```
Status 5249: Normal day operation (solar + loads)
Status 4225: Normal night operation (battery + loads)
Status 129: Standby mode (no loads)
```

---

**Status**: ✅ Sensor working correctly (shows numeric bitmask)  
**User System**: Off-grid solar installation  
**Typical Value**: 5249 (normal operation)  
**Enhancement**: Awaiting bit definitions for full decoding
