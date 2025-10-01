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

1. Obtain API credentials from your SolarGuardian web portal:
   - Login to your SolarGuardian account
   - Go to System Management > Personal Information Management > Open API
   - Apply for API credentials (appKey and appSecret)

2. Configure the integration:
   - Domain: Use `openapi.epsolarpv.com` for Mainland China or `glapi.mysolarguardian.com` for International
   - Enter your appKey and appSecret
   - Select update interval (default: 30 seconds)

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
- ☕ **[Buy me a coffee](https://www.buymeacoffee.com/yourusername)** (one-time donation)
- 💝 **[Sponsor on GitHub](https://github.com/sponsors/CMGeorge)** (monthly support)
- 🐛 **Report bugs** and suggest features
- 📖 **Improve documentation**
- 🔧 **Contribute code**

Your support helps maintain and improve this integration! 🙏

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