# How to Get SolarGuardian API Credentials

This guide explains how to obtain your `App Key` and `App Secret` for the SolarGuardian API.

---

## Prerequisites

- An active Epever solar system
- The SolarGuardian mobile app installed on your device
- An active account in the SolarGuardian app

---

## Method 1: Request from Epever Support (Recommended)

### Step 1: Contact Epever Support

Send an email to Epever's official support requesting API credentials:

**Email Address**: 
- International: `support@epever.com` or `service@epever.com`
- China: Check the official Epever website for local support contacts

**Email Template**:

```
Subject: Request for SolarGuardian API Credentials

Dear Epever Support Team,

I am using the SolarGuardian platform to monitor my Epever solar system and would like to integrate it with Home Assistant for home automation purposes.

Please provide me with the following API credentials for my account:
- App Key (appKey)
- App Secret (appSecret)

My SolarGuardian account details:
- Username/Email: [Your email/username]
- Phone Number: [If registered with phone]
- Power Station Name: [Your power station name]

I will use these credentials responsibly and only for personal use with my own equipment.

Thank you for your assistance.

Best regards,
[Your Name]
```

### Step 2: Wait for Response

Epever support will verify your account and provide:
- **App Key**: A unique identifier (e.g., `abc123def456`)
- **App Secret**: A secret token (e.g., `xyz789uvw012`)

**Response Time**: Usually 1-3 business days

### Step 3: Store Credentials Securely

⚠️ **IMPORTANT**: Keep your credentials secure!
- Never share them publicly
- Never commit them to git repositories
- Store them in Home Assistant's configuration UI only

---

## Method 2: Extract from SolarGuardian Mobile App (Advanced)

⚠️ **Warning**: This method requires technical knowledge and may violate app terms of service. Use at your own risk.

### Android Method

1. **Install ADB (Android Debug Bridge)**
   ```bash
   # On Ubuntu/Debian
   sudo apt install android-tools-adb
   
   # On macOS
   brew install android-platform-tools
   ```

2. **Enable USB Debugging on your Android device**
   - Go to Settings → About Phone
   - Tap "Build Number" 7 times to enable Developer Mode
   - Go to Settings → Developer Options
   - Enable "USB Debugging"

3. **Connect device and authorize**
   ```bash
   adb devices
   ```

4. **Extract app data** (requires root or backup permissions)
   ```bash
   # Pull app data
   adb backup -f solarguardian.ab com.epever.solarguardian
   
   # Convert to tar (use abe tool)
   java -jar abe.jar unpack solarguardian.ab solarguardian.tar
   
   # Extract and search for credentials
   tar -xf solarguardian.tar
   grep -r "appKey\|appSecret" .
   ```

### iOS Method

1. **Jailbreak Required** (not recommended)
   - iOS encrypts app data making extraction very difficult
   - Jailbreaking may void warranty and pose security risks

2. **Network Traffic Monitoring** (easier, no jailbreak)
   - Use a proxy tool like Charles Proxy or mitmproxy
   - Configure your phone to use the proxy
   - Open SolarGuardian app and log in
   - Monitor HTTPS traffic to `*.epsolarpv.com` or `*.mysolarguardian.com`
   - Look for API calls containing `appKey` and `appSecret` in headers or body

---

## Method 3: Network Traffic Capture (Technical)

This method captures API credentials by monitoring network traffic from the mobile app.

### Tools Needed

- **mitmproxy** (free, open-source): https://mitmproxy.org/
- Or **Charles Proxy** (paid): https://www.charlesproxy.com/

### Steps Using mitmproxy

1. **Install mitmproxy**
   ```bash
   # macOS
   brew install mitmproxy
   
   # Linux
   pip install mitmproxy
   
   # Windows
   # Download from https://mitmproxy.org/
   ```

2. **Start mitmproxy**
   ```bash
   mitmproxy
   ```
   
   This will start a proxy on `http://localhost:8080`

3. **Configure your phone to use the proxy**
   - Connect phone to same WiFi network as computer
   - Find your computer's IP address (e.g., `192.168.1.100`)
   - On phone, go to WiFi settings → Modify Network
   - Set Proxy to Manual
   - Proxy hostname: Your computer's IP
   - Proxy port: `8080`

4. **Install mitmproxy certificate on phone**
   - Open browser on phone and visit `mitm.it`
   - Install certificate for your device OS
   - Trust the certificate (Settings → Security on Android)

5. **Capture API traffic**
   - Open SolarGuardian app on phone
   - Log in (if not already logged in)
   - Navigate through the app
   - In mitmproxy, filter for requests to:
     - `openapi.epsolarpv.com`
     - `glapi.mysolarguardian.com`
   
6. **Find credentials**
   Look for POST requests to `/epCloud/user/getAuthToken`
   
   The request body will contain:
   ```json
   {
     "appKey": "your_app_key_here",
     "appSecret": "your_app_secret_here"
   }
   ```

7. **Copy credentials**
   - Copy the `appKey` and `appSecret` values
   - Store them securely

8. **Clean up**
   - Remove proxy settings from phone
   - Optionally remove mitmproxy certificate from phone

---

## Method 4: Developer Account Registration (Future)

⚠️ **Status**: Not currently available

Epever may offer a developer portal in the future where users can register and generate API credentials. Check:
- https://www.epever.com/
- https://www.mysolarguardian.com/

---

## Choosing Your API Domain

When you obtain your credentials, you'll also need to know which API domain to use:

### China Domain
- **Domain**: `openapi.epsolarpv.com`
- **Use if**: Your account was registered in China or you use the Chinese version of the app

### International Domain
- **Domain**: `glapi.mysolarguardian.com`
- **Use if**: Your account was registered outside China or you use the international app

**How to determine**:
1. Open the SolarGuardian mobile app
2. Check the app version or region settings
3. If unsure, try the international domain first

---

## Configuring in Home Assistant

Once you have your credentials:

1. **Go to Home Assistant**
   - Settings → Devices & Services

2. **Add Integration**
   - Click "+ ADD INTEGRATION"
   - Search for "SolarGuardian"
   - Click on it

3. **Enter Credentials**
   - **Domain**: Select `China` or `International`
   - **App Key**: Paste your App Key
   - **App Secret**: Paste your App Secret
   - **Update Interval**: Leave default (15 seconds) or adjust

4. **Submit**
   - The integration will test the connection
   - If successful, your devices will appear

---

## Troubleshooting

### Authentication Failed

**Problem**: "Authentication failed: Invalid credentials"

**Solutions**:
- Double-check App Key and App Secret for typos
- Verify you're using the correct domain (China vs International)
- Ensure credentials haven't expired
- Contact Epever support to verify credentials are active

### Rate Limit Exceeded

**Problem**: "Rate limit exceeded"

**Solutions**:
- Increase update interval (Settings → Integration → Configure)
- Wait a few minutes before retrying
- Check if you're running multiple instances with same credentials

### Wrong Domain

**Problem**: Connection timeout or 404 errors

**Solutions**:
- Try switching between China and International domains
- Check your internet connection
- Verify domain is accessible: `ping openapi.epsolarpv.com`

---

## Security Best Practices

### ✅ DO

- ✅ Store credentials only in Home Assistant configuration
- ✅ Use HTTPS/SSL for Home Assistant access
- ✅ Enable authentication for Home Assistant
- ✅ Keep credentials private and secure
- ✅ Use unique credentials for each Home Assistant instance
- ✅ Regularly update Home Assistant and the integration

### ❌ DON'T

- ❌ Share credentials with others
- ❌ Post credentials in public forums or GitHub
- ❌ Store credentials in plain text files
- ❌ Use credentials from unofficial sources
- ❌ Share your Home Assistant instance publicly without authentication
- ❌ Commit credentials to version control

---

## Frequently Asked Questions

### Q: Are API credentials free?

**A**: Yes, if you own an Epever solar system and have a SolarGuardian account, API access should be provided free of charge by Epever support.

### Q: Do credentials expire?

**A**: API credentials may expire after a certain period (e.g., 1-2 years). Contact Epever support for renewal.

### Q: Can I use the same credentials on multiple Home Assistant instances?

**A**: Technically yes, but it may cause rate limiting issues. It's better to request separate credentials for each instance.

### Q: Are there API rate limits?

**A**: Yes:
- **Authentication**: 10 calls per minute
- **Data endpoints**: 30 calls per minute
- The integration respects these limits automatically

### Q: Is this legal and within terms of service?

**A**: Using officially provided API credentials from Epever support is legal. Extracting credentials from the app may violate terms of service. Always use the official method (Method 1) when possible.

### Q: What if Epever refuses to provide credentials?

**A**: Try explaining your use case for home automation. If they still refuse, consider:
- Using the official mobile app only
- Waiting for official API documentation
- Contacting Epever sales/business development

---

## Support

If you have issues obtaining API credentials:

1. **Epever Official Support**
   - Email: support@epever.com
   - Website: https://www.epever.com/

2. **Home Assistant Community**
   - Community Forum: https://community.home-assistant.io/
   - Search for "SolarGuardian" or "Epever"

3. **Integration Issues**
   - GitHub: https://github.com/CMGeorge/HomeAssistant_SolarGuardian/issues

---

## Legal Notice

This documentation is provided for informational purposes only. Users are responsible for:
- Complying with Epever's terms of service
- Complying with local laws and regulations
- Securing their API credentials
- Using credentials ethically and responsibly

The integration developers are not affiliated with Epever and cannot provide official API credentials.

---

**Last Updated**: October 2, 2025  
**Integration Version**: 1.0.0
