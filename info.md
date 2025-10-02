# SolarGuardian Integration for Home Assistant

Monitor your Epever Solar inverters through the SolarGuardian cloud API!

## Features

✅ **Real-time Monitoring**

- Solar power output (W, kW)
- Battery voltage, current, capacity (%)
- AC/DC voltage and current
- Temperature sensors
- Energy production (daily, total)

✅ **Device Status**

- Online/offline status
- Alarm monitoring
- Equipment health indicators
- Bitmask status register (for advanced users)

✅ **Multiple Devices**

- Supports multiple power stations
- Multiple devices per station
- Automatic device discovery

✅ **Cloud API**

- No local network access needed
- Works from anywhere
- API rate limiting respected
- Automatic token refresh

## Installation

1. Click the "**Download**" button in HACS
2. Restart Home Assistant
3. Go to **Settings → Devices & Services**
4. Click "**+ Add Integration**"
5. Search for "**SolarGuardian**"
6. Enter your API credentials

## Configuration

You'll need API credentials from your SolarGuardian account:

1. Login to your SolarGuardian web portal
2. Go to **System Management → Personal Information Management → Open API**
3. Apply for API credentials (appKey and appSecret)
4. Choose your API domain:
   - `openapi.epsolarpv.com` - Mainland China
   - `glapi.mysolarguardian.com` - International

## Sensors Created

The integration automatically creates sensors for:

- **Power**: Output Power, Input Power, Load Power
- **Voltage**: Battery, PV, Load, AC Output
- **Current**: Battery, PV, Load
- **Temperature**: Battery, Device
- **Energy**: Generated (today/total), Consumed (today/total)
- **Status**: Battery SOC, Charging Status, Device Status
- **And many more...**

All sensors show proper units (W, V, A, °C, kWh, %) and include:

- ✅ Device class (for proper icons)
- ✅ State class (for statistics/energy dashboard)
- ✅ Proper translations (English, German, Hungarian, Romanian)

## Rate Limits

The integration respects API rate limits:

- **Authentication**: 10 calls/minute
- **Data requests**: 30 calls/minute
- Automatic retry with backoff on errors

## Support

- **Issues**: [GitHub Issues](https://github.com/CMGeorge/HomeAssistant_SolarGuardian/issues)
- **Documentation**: [GitHub Repository](https://github.com/CMGeorge/HomeAssistant_SolarGuardian)
- **Troubleshooting**: [Troubleshooting Guide](https://github.com/CMGeorge/HomeAssistant_SolarGuardian/blob/master/TROUBLESHOOTING.md)

## System Requirements

- Home Assistant 2025.9.0 or higher
- SolarGuardian API credentials
- Internet connection

## Notes

- **Update Interval**: Default 15 seconds, configurable 15-300 seconds
- **API Version**: SolarGuardian API V2.3
- **IoT Class**: Cloud Polling
- **Platforms**: Sensor, Binary Sensor

Perfect for monitoring your off-grid or grid-tied solar system! 🌞🔋
