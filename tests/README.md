# SolarGuardian Home Assistant Integration

A comprehensive Home Assistant integration for Epever Solar inverters using the SolarGuardian API V2.3.

## Features

- Real-time monitoring of solar inverter parameters
- Power production tracking (voltage, current, power output)
- Battery monitoring (voltage, capacity, temperature)
- Device status and alarm monitoring
- Gateway and device management
- Historical data access
- Compatible with Home Assistant 2025.9.x

## Installation

### Via HACS (Recommended)

1. Add this repository to HACS as a custom repository
2. Install "SolarGuardian" integration
3. Restart Home Assistant
4. Go to Settings > Devices & Services
5. Click "Add Integration" and search for "SolarGuardian"

### Manual Installation

1. Copy the `custom_components/solarguardian` folder to your Home Assistant's `custom_components` directory
2. Restart Home Assistant
3. Add the integration via the UI

## Configuration

1. Obtain API credentials from your SolarGuardian web portal:
   - Login to your SolarGuardian account
   - Go to System Management > Personal Information Management > Open API
   - Apply for API credentials (appKey and appSecret)

2. Configure the integration:
   - Domain: Use `openapi.epsolarpv.com` for Mainland China or `glapi.mysolarguardian.com` for International
   - Enter your appKey and appSecret
   - Select update interval (default: 30 seconds)

## Supported Entities

### Sensors
- Power output (W)
- AC/DC voltage (V)
- AC/DC current (A)
- Battery voltage and capacity
- Temperature sensors
- Energy production counters
- Efficiency metrics

### Binary Sensors
- Device online status
- Alarm states
- System health indicators

## API Rate Limits

The integration respects SolarGuardian API rate limits:
- 30 API calls per minute for data requests
- 10 calls per minute for authentication
- Automatic retry with exponential backoff

## Support

- GitHub Issues: Report bugs and feature requests
- Home Assistant Community: Discuss usage and troubleshooting

## License

MIT License - see LICENSE file for details