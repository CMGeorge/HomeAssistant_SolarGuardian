# SolarGuardian Installation Guide

## Prerequisites

1. **Home Assistant 2025.9.0 or later**
2. **SolarGuardian API Credentials**
   - Login to your SolarGuardian web portal
   - For China: https://hncloud.epsolarpv.com/
   - For International: https://gl.mysolarguardian.com/
   - Navigate to: System Management → Personal Information Management → Open API
   - Apply for API credentials (you'll receive `appKey` and `appSecret`)

## Installation Methods

### Method 1: HACS (Recommended)

1. **Add Custom Repository**
   - Open HACS in Home Assistant
   - Go to Integrations
   - Click the three dots menu (⋮) → Custom repositories
   - Add repository URL: `https://github.com/CMGeorge/HomeAssistant_SolarGuardina`
   - Category: Integration
   - Click Add

2. **Install Integration**
   - Search for "SolarGuardian" in HACS
   - Click Install
   - Restart Home Assistant

3. **Configure Integration**
   - Go to Settings → Devices & Services
   - Click "Add Integration"
   - Search for "SolarGuardian"
   - Follow the configuration steps

### Method 2: Manual Installation

1. **Download Files**

   ```bash
   cd /config
   git clone https://github.com/CMGeorge/HomeAssistant_SolarGuardina.git
   ```

2. **Copy Integration**

   ```bash
   cp -r HomeAssistant_SolarGuardina/custom_components/solarguardian /config/custom_components/
   ```

3. **Restart Home Assistant**

4. **Configure Integration**
   - Go to Settings → Devices & Services
   - Click "Add Integration"
   - Search for "SolarGuardian"

## Configuration

### Basic Setup

1. **Domain Selection**
   - Choose your SolarGuardian domain:
     - China: `openapi.epsolarpv.com`
     - International: `glapi.mysolarguardian.com`

2. **API Credentials**
   - Enter your `App Key`
   - Enter your `App Secret`

3. **Verification**
   - The integration will test your credentials
   - If successful, devices will be automatically discovered

### Advanced Configuration

The integration automatically discovers all available:

- Power stations
- Gateways
- Devices (solar inverters, charge controllers, etc.)
- Parameters (power, voltage, current, temperature, etc.)

## Post-Installation

### Verify Installation

1. **Check Devices**
   - Go to Settings → Devices & Services → SolarGuardian
   - You should see your power stations and devices

2. **Check Entities**
   - Go to Settings → Entities
   - Filter by `solarguardian`
   - Verify sensors are showing data

### Integration with Energy Dashboard

1. **Add Solar Source**

   ```yaml
   energy:
     sources:
       - type: solar
         stat_energy_from: sensor.your_device_generated_energy_today
   ```

2. **Add Battery Storage** (if applicable)
   ```yaml
   energy:
     sources:
       - type: battery
         stat_energy_from: sensor.your_device_battery_energy_from
         stat_energy_to: sensor.your_device_battery_energy_to
   ```

## Troubleshooting

### Common Issues

1. **Authentication Failed**
   - Verify your App Key and App Secret
   - Check that your account has API access enabled
   - Ensure you're using the correct domain

2. **No Devices Found**
   - Verify devices are online in the SolarGuardian web portal
   - Check that your account has proper permissions
   - Wait a few minutes and reload the integration

3. **Sensors Not Updating**
   - Check Home Assistant logs for errors
   - Verify network connectivity
   - API rate limits: 30 calls/minute (integration handles this automatically)

### Log Analysis

Enable debug logging:

```yaml
logger:
  default: info
  logs:
    custom_components.solarguardian: debug
```

### API Rate Limits

The integration automatically handles rate limiting:

- Authentication: 10 calls per minute
- Data requests: 30 calls per minute
- Default update interval: 30 seconds (configurable)

## Performance Optimization

### Reduce Update Frequency

If you have many devices or want to reduce API calls:

1. Go to Settings → Devices & Services → SolarGuardian
2. Click Configure
3. Increase update interval (e.g., 60 seconds)

### Selective Monitoring

The integration creates sensors for all available parameters. You can disable unused sensors:

1. Go to Settings → Entities
2. Filter by `solarguardian`
3. Disable entities you don't need

## Support

- **GitHub Issues**: https://github.com/CMGeorge/HomeAssistant_SolarGuardina/issues
- **Home Assistant Community**: Search for "SolarGuardian"
- **Documentation**: Check README.md for additional details
