# BUG FIX: Enum Sensors Showing Numeric Values Instead of Text

**Date**: October 1, 2025  
**Severity**: MEDIUM - Status/enum sensors showing "0.0" instead of descriptive text  
**Status**: ✅ FIXED

## Problem

Status and enum sensors were displaying numeric values (0.0, 1.0, 2.0) instead of their translated text values:

| Sensor | Showing | Should Show |
|--------|---------|-------------|
| PV Charging Status | 0.0 | Not Charging |
| Utility Charging Status | 0.0 | Not Charging |
| Battery Voltage Alarm | 0.0 | Normal |
| Battery Temperature Alarm | 0.0 | Normal |
| Output Load Status | 0.0 | Light Load |
| Load Short Circuit Alarm | 0.0 | NO |
| Charging Mode | 2.0 | Utility and Solar |
| Output Mode | 1.0 | Utility first |
| Day/Night Flag | 1.0 | Night |

## Root Cause

The API provides enum translation mappings in the device parameters via the `translationChild` array, but the sensor code was not using them.

### API Structure

**Device Parameters Response** (getEquipment):
```json
{
  "dataIdentifier": "BAT_STA1",
  "dataPointId": 105646627,
  "variableNameE": "PV Charging Status",
  "translationChild": [
    {
      "value": "0",
      "resultE": "Not Charging",
      "result": "未充电"
    },
    {
      "value": "1",
      "resultE": "Float Charging",
      "result": "浮充充电"
    },
    {
      "value": "2",
      "resultE": "Boost Charging",
      "result": "提升充电"
    }
  ]
}
```

**Latest Data Response**:
```json
{
  "dataPointId": 105646627,
  "value": "0"  ← Needs translation to "Not Charging"
}
```

## Fix Applied

Added translation support to sensor value retrieval:

### 1. Added `_translate_value` Method
```python
def _translate_value(self, value: float, translation_child: list) -> str | None:
    """Translate numeric value to text using translationChild mappings."""
    value_str = str(int(value))  # Convert 0.0 to "0"
    
    for translation in translation_child:
        if translation.get("value") == value_str:
            # Use English result if available, fallback to Chinese
            return translation.get("resultE") or translation.get("result")
    
    return None
```

### 2. Updated `native_value` Property
```python
# Check if this parameter has translation mappings
translation_child = self._variable.get("translationChild", [])
if translation_child:
    translated_value = self._translate_value(value, translation_child)
    if translated_value is not None:
        return translated_value

# Fallback to numeric value if no translation
return value
```

## Enum Sensors with Translations

Total: **22 sensors** have enum translations

### Real-Time Status Sensors (16)
1. **PV Charging Status**: Not Charging, Float Charging, Boost Charging, Equalize Charging
2. **Utility Charging Status**: Not Charging, Float Charging, Boost Charging, Equalize Charging
3. **Battery Voltage Alarm**: Normal, Overvoltage, Undervoltage, BMS Protected, etc.
4. **Battery Temperature Alarm**: Normal, Over High Temperature
5. **Output Load Status**: Light Load, Moderate, Rated, Overload
6. **Load Short Circuit Alarm**: NO, Short Circuit
7. **Output Voltage Status**: Normal, Voltage Abnormal
8. **PV Input Voltage Status**: Normal, Not Connected, Overvoltage, Voltage Error
9. **Bus Over Voltage**: NO, Over Voltage
10. **Bus Under Voltage**: NO, Under Voltage
11. **Device Fault**: NO, Device Overheating
12. **INV Bypass Status**: Not Bypass, Bypass
13. **Battery Detection**: Connected, Undetected
14. **Charging Mode**: Solar First, Utility and Solar, Solar Only
15. **Output Mode**: Inverter first, Utility first
16. **Day/Night Flag**: Day, Night

### Configuration Sensors (6 - no real-time data)
17. **Battery Type**: User, SLA, GEL, FLD, LFP4S, etc.
18. **Li-ion Battery Protect**: Enable, Disable
19. **LCD Backlight Timeout**: 30s, 60s, On solid
20. **Temperature Unit**: ℉, ℃
21. **Buzzer Alarm Switch**: ON, OFF
22. **Li-ion Battery BMS**: Disable, Enable

## Testing

Verified with real API test script:

```bash
cd tests
python test_translations.py
```

**Results**:
- ✅ 22 enum sensors identified
- ✅ 16 with real-time data showing translated values
- ✅ All translations working correctly
- ✅ Fallback to numeric value if no translation found

### Sample Output:
```
📊 PV Charging Status
   Raw Value: 0
   ✅ Translated: Not Charging

📊 Charging Mode
   Raw Value: 2
   ✅ Translated: Utility and Solar

📊 Output Load Status
   Raw Value: 0
   ✅ Translated: Light Load
```

## Impact

**Before Fix**:
- ❌ 22 enum sensors showing numeric values (0.0, 1.0, 2.0)
- ❌ Users seeing meaningless numbers
- ❌ Hard to understand system status

**After Fix**:
- ✅ 22 enum sensors showing descriptive text
- ✅ Clear status indicators (Not Charging, Normal, Light Load, etc.)
- ✅ Easy to understand at a glance
- ✅ Proper use of API translation data

## Files Changed

- `custom_components/solarguardian/sensor.py`
  - Lines 493-512: Added `_translate_value()` method
  - Lines 530-545: Added translation logic in `native_value` property
  - Translations use English (resultE) when available, fallback to Chinese (result)

- `tests/test_translations.py`
  - New test script to verify enum translations with real API

## Key Insights

1. **API Provides Rich Metadata**: The `translationChild` array contains all enum mappings
2. **Bilingual Support**: API provides both Chinese and English translations
3. **Numeric Storage**: Values stored as numeric but meant to be displayed as text
4. **Fallback Safety**: If translation not found, displays numeric value

## Deployment

Same as previous fixes:

1. Update Integration from HACS
2. Restart Home Assistant  
3. Verify status sensors now show text instead of numbers

---

**Commit**: `feat: Add enum translation support for status sensors`  
**Issue**: Status sensors showing "0.0" instead of "Not Charging", "Normal", etc.  
**Tested**: test_translations.py with real API - 22 enum sensors verified  
**Related**: Part of sensor value fix series (after dataPointId and decimal fixes)
