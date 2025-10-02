# SolarGuardian Home Assistant Integration

A comprehensive Home Assistant integration for Epever Solar inverters using the SolarGuardian API V2.3.

[![Validate](https://github.com/CMGeorge/HomeAssistant_SolarGuardian/actions/workflows/validate.yaml/badge.svg)](https://github.com/CMGeorge/HomeAssistant_SolarGuardian/actions/workflows/validate.yaml)
[![hassfest](https://github.com/CMGeorge/HomeAssistant_SolarGuardian/actions/workflows/hassfest.yaml/badge.svg)](https://github.com/CMGeorge/HomeAssistant_SolarGuardian/actions/workflows/hassfest.yaml)
[![HACS](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)
[![GitHub release](https://img.shields.io/github/release/CMGeorge/HomeAssistant_SolarGuardian.svg)](https://github.com/CMGeorge/HomeAssistant_SolarGuardian/releases)
[![License](https://img.shields.io/github/license/CMGeorge/HomeAssistant_SolarGuardian.svg)](LICENSE)

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=CMGeorge&repository=HomeAssistant_SolarGuardian&category=integration)

---

## Features

- Real-time monitoring of solar inverter parameters
- Power production tracking (voltage, current, power output)
- Battery monitoring (voltage, capacity, temperature)
- Device status and alarm monitoring
- Gateway and device management
- Historical data access
- Compatible with Home Assistant 2025.9.x

---

## Installation

### Via HACS (Recommended)

1. In Home Assistant, go to **HACS → Integrations → Custom Repositories**
2. Add this repository: `https://github.com/CMGeorge/HomeAssistant_SolarGuardian`
3. Choose category: **Integration**
4. Install "SolarGuardian" integration
5. Restart Home Assistant
6. Go to **Settings > Devices & Services**
7. Click "**Add Integration**" and search for "**SolarGuardian**"

### Manual Installation

1. Download the [latest release](https://github.com/CMGeorge/HomeAssistant_SolarGuardian/releases)
2. Copy the `custom_components/solarguardian` folder to your Home Assistant's `custom_components` directory
3. Restart Home Assistant
4. Add the integration via the UI

---

## Configuration

### Step 1: Obtain API Credentials

You need to obtain your `App Key` and `App Secret` from Epever:

**📖 [Complete Guide: How to Get API Credentials](docs/API_CREDENTIALS.md)**

**Quick Summary**:

1. **Recommended**: Email Epever support (`support@epever.com`) requesting API credentials
2. **Alternative**: Extract from mobile app using network monitoring (advanced)
3. Provide your SolarGuardian account details to verify ownership

See the [detailed guide](docs/API_CREDENTIALS.md) for step-by-step instructions including:

- Email templates for requesting credentials
- Network traffic capture methods
- Troubleshooting tips
- Security best practices

### Step 2: Configure Integration

1. Configure the integration in Home Assistant:
   - Go to **Settings > Devices & Services**
   - Click "**Add Integration**"
   - Search for "**SolarGuardian**"

2. Enter your credentials:
   - **Domain**:
     - `China` (openapi.epsolarpv.com) - for accounts registered in China
     - `International` (glapi.mysolarguardian.com) - for international accounts
   - **App Key**: Your API key from Epever
   - **App Secret**: Your API secret from Epever
   - **Update Interval**: 15-300 seconds (default: 15 seconds)

3. Click **Submit** - the integration will test the connection

---

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

---

## 💖 Support This Project

If you find this integration useful, consider supporting its development:

- ⭐ **Star this repository** on GitHub
- 💝 **[Sponsor on GitHub](https://github.com/sponsors/CMGeorge)** - Support ongoing development (no fees!)
- 🐛 **Report bugs** and suggest features
- 📖 **Improve documentation**
- 🔧 **Contribute code**

Your support helps maintain and improve this integration! 🙏

### Development

This integration was developed through collaboration between human expertise and AI assistance (GitHub Copilot). All code is reviewed, tested, and maintained to ensure quality and security.

## 🤝 Contributing

Contributions are welcome! Please read our [Contributing Guidelines](CONTRIBUTING.md) before submitting PRs.

---

## Support

- **GitHub Issues**: [Report bugs and feature requests](https://github.com/CMGeorge/HomeAssistant_SolarGuardian/issues)
- **Documentation**: Check our [Troubleshooting Guide](TROUBLESHOOTING.md)
- **Security**: See our [Security Policy](https://github.com/CMGeorge/HomeAssistant_SolarGuardian/security/policy)

---

## License

MIT License - see [LICENSE](LICENSE) file for details
