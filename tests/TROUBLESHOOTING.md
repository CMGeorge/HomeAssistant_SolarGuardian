# SolarGuardian Integration Troubleshooting Guide

This guide helps you diagnose and fix common issues with the SolarGuardian Home Assistant integration.

## Common Issues

### 1. All Sensors Show as "Unavailable"

This is the most common issue and can have several causes:

#### A. Network Connectivity Problems

**Symptoms:**
- All sensors show "unavailable"
- Logs show connection errors like "Cannot connect to host"
- Authentication failures

**Diagnosis:**
1. Check Home Assistant logs for SolarGuardian errors:
   ```
   Settings > System > Logs
   Search for: "solarguardian"
   ```

2. Test API connection using the diagnostic service:
   ```
   Developer Tools > Services
   Service: solarguardian.test_connection
   Check "verbose" for detailed output
   ```

**Solutions:**
1. **Verify API Domain**: Ensure you're using the correct domain:
   - Chinese servers: `openapi.epsolarpv.com`
   - International servers: `glapi.mysolarguardian.com`

2. **Check Network Access**: From Home Assistant host, test connectivity:
   ```bash
   # Test domain resolution
   nslookup openapi.epsolarpv.com
   nslookup glapi.mysolarguardian.com
   
   # Test HTTPS connectivity
   curl -I https://openapi.epsolarpv.com
   curl -I https://glapi.mysolarguardian.com
   ```

3. **Firewall/Proxy Issues**: Ensure Home Assistant can make outbound HTTPS connections to the API domain.

#### B. Authentication Problems

**Symptoms:**
- Logs show "Authentication failed" or "Authentication error"
- HTTP 401/403 errors

**Solutions:**
1. **Verify Credentials**: Double-check your App Key and App Secret in the integration configuration.

2. **Check API Key Validity**: Contact your solar system provider to ensure your API credentials are still active.

3. **Rate Limiting**: The integration implements rate limiting, but if you have multiple integrations or tools using the same API key, you might hit limits.

#### C. API Server Issues

**Symptoms:**
- Intermittent connectivity
- HTTP 5xx errors
- Timeouts

**Solutions:**
1. **Wait and Retry**: API servers sometimes have temporary issues.

2. **Check Integration Settings**: The integration will automatically increase update intervals when encountering repeated failures.

### 2. Some Sensors Work, Others Don't

**Symptoms:**
- Some devices show data, others are unavailable
- Partial sensor data

**Diagnosis:**
1. Check logs for device-specific errors
2. Use the diagnostics service to see which devices are failing

**Solutions:**
1. **Device Communication Issues**: Some devices might be offline or have communication problems with the monitoring system.

2. **Parameter Changes**: Solar system manufacturers sometimes change available parameters. The integration creates generic sensors for unknown parameters.

### 3. Mock/Test Mode

When the API is completely unavailable, the integration can create mock sensors for testing:

**When Mock Mode Activates:**
- After 3 consecutive API failures
- When no data is available at all
- Network connectivity issues prevent any API access

**Mock Mode Features:**
- Creates test sensors with realistic parameter names
- Provides sample device structure
- Helps verify integration setup without API access

## Diagnostic Tools

### 1. Test Connection Service

Use this service to test API connectivity:

```yaml
service: solarguardian.test_connection
data:
  verbose: true
```

This will test:
- Authentication
- Power station retrieval
- Device enumeration
- Parameter discovery

### 2. Get Diagnostics Service

Use this service to get integration status:

```yaml
service: solarguardian.get_diagnostics
```

This shows:
- Current configuration
- Update statistics
- Error counts
- Data summary

### 3. Log Analysis

Enable debug logging for detailed troubleshooting:

```yaml
# configuration.yaml
logger:
  default: info
  logs:
    custom_components.solarguardian: debug
```

Look for these log patterns:
- `Authentication successful` - API connection working
- `Found X power stations` - Data retrieval working
- `Created X sensors` - Sensor setup successful
- `Network error` - Connectivity issues
- `Authentication error` - Credential problems

## Configuration Examples

### Chinese Server Configuration
```yaml
Domain: openapi.epsolarpv.com
App Key: your_app_key_here
App Secret: your_app_secret_here
Update Interval: 30 seconds
```

### International Server Configuration
```yaml
Domain: glapi.mysolarguardian.com
App Key: your_app_key_here
App Secret: your_app_secret_here
Update Interval: 30 seconds
```

### 4. Latest Data Issues (404 Errors)

**Symptoms:**
- Logs show "Failed to get latest data for device: API request failed: 404"
- Sensors work but don't update with current values
- Error appears repeatedly in logs

**Explanation:**
The SolarGuardian API has two different endpoints for latest data:
1. `/epCloud/vn/openApi/getLastDataPoint` - Often returns 404 (doesn't exist)
2. `/history/lastDatapoint` - Correct endpoint per API documentation

**Solutions:**
1. **Automatic Handling**: The integration now automatically handles 404 errors and will:
   - Try the correct endpoint first
   - Fall back to the legacy endpoint
   - Disable latest data fetching if both fail repeatedly
   - Re-enable automatically after successful updates

2. **Manual Reset**: If latest data fetching gets disabled, you can re-enable it:
   ```yaml
   service: solarguardian.reset_latest_data
   ```

3. **Monitor Status**: Check the diagnostics service to see latest data status:
   ```yaml
   service: solarguardian.get_diagnostics
   ```

**Note**: Your sensors will still work without latest data - they just won't have real-time values.

## Advanced Troubleshooting

### 1. Manual API Testing

Create a simple test script to verify API access outside of Home Assistant:

```python
import aiohttp
import asyncio
import json

async def test_api():
    session = aiohttp.ClientSession()
    
    # Test authentication
    auth_url = "https://openapi.epsolarpv.com/epCloud/user/getAuthToken"
    auth_payload = {
        "appKey": "your_app_key",
        "appSecret": "your_app_secret"
    }
    
    try:
        async with session.post(auth_url, json=auth_payload) as response:
            print(f"Status: {response.status}")
            text = await response.text()
            print(f"Response: {text}")
    finally:
        await session.close()

asyncio.run(test_api())
```

### 2. Network Debugging

If you suspect network issues:

1. **Check DNS Resolution**:
   ```bash
   dig openapi.epsolarpv.com
   dig glapi.mysolarguardian.com
   ```

2. **Test SSL Certificate**:
   ```bash
   openssl s_client -connect openapi.epsolarpv.com:443
   ```

3. **Trace Network Path**:
   ```bash
   traceroute openapi.epsolarpv.com
   ```

## Getting Help

If you continue to experience issues:

1. **Enable Debug Logging**: Capture detailed logs showing the exact error
2. **Use Diagnostic Services**: Run the integration's built-in diagnostic services
3. **Check Network Connectivity**: Verify your Home Assistant instance can reach the API servers
4. **Verify Credentials**: Ensure your API key and secret are correct and active

## Integration Services

The integration provides several services for troubleshooting:

### 1. Test Connection Service
```yaml
service: solarguardian.test_connection
data:
  verbose: true  # Optional: show detailed connection test results
```

### 2. Get Diagnostics Service
```yaml
service: solarguardian.get_diagnostics
```
Shows:
- API configuration details
- Update statistics
- Latest data fetching status
- Error summaries

### 3. Reset Latest Data Service
```yaml
service: solarguardian.reset_latest_data
```
Use this if latest data fetching gets disabled due to repeated 404 errors.

Include this information when seeking help:
- Home Assistant version
- Integration version
- Complete error logs with debug enabled
- Results from diagnostic services
- Network configuration details
- API server being used (Chinese vs International)

## Mock Mode Details

When API connectivity fails completely, the integration can create mock sensors to help with testing and development:

**Mock Data Includes:**
- 1 test power station
- 1 test solar inverter device  
- 8 test sensors covering power, voltage, and current parameters
- Realistic parameter names and units

**Mock Mode Indicators:**
- Integration status shows "mock_mode"
- Logs indicate "Using mock data - API unavailable"
- Sensors have test values and may show as unavailable initially

This allows you to:
- Verify integration installation
- Test Home Assistant configuration
- Develop automations and dashboards
- Troubleshoot sensor setup issues

Mock mode automatically activates when:
- 3 consecutive API call failures occur
- No existing data is available
- Network connectivity prevents API access