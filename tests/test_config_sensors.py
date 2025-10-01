"""Test configuration sensors - why are they Unknown?"""
import asyncio
import os
import sys
import aiohttp
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import API client directly
import importlib.util
spec = importlib.util.spec_from_file_location(
    "api",
    str(Path(__file__).parent.parent / "custom_components" / "solarguardian" / "api.py")
)
api_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(api_module)
SolarGuardianAPI = api_module.SolarGuardianAPI

async def test_config_sensors():
    """Check what data we get for configuration sensors."""
    
    domain = os.getenv("DOMAIN", "openapi.epsolarpv.com")
    app_key = os.getenv("APP_KEY")
    app_secret = os.getenv("APP_SECRET")
    
    if not app_key or not app_secret:
        print("❌ Missing APP_KEY or APP_SECRET in .env file")
        return
    
    print("=" * 80)
    print("  Testing Configuration Sensors")
    print("=" * 80)
    print()
    
    api = SolarGuardianAPI(domain, app_key, app_secret)
    
    try:
        # Authenticate
        if await api.authenticate():
            print("✅ Authenticated")
        else:
            print("❌ Authentication failed")
            return
        
        # Get power stations
        stations_data = await api.get_power_stations()
        if stations_data.get("status") != 0:
            print(f"❌ Failed to get stations: {stations_data}")
            return
        
        stations_list = stations_data.get("data", {}).get("list", [])
        if not stations_list:
            print("❌ No power stations found")
            return
        
        station = stations_list[0]
        print(f"✅ Got station: {station['stationName']}")
        
        # Get devices
        devices_data = await api.get_devices(station["id"])
        if devices_data.get("status") != 0:
            print(f"❌ Failed to get devices: {devices_data}")
            return
        
        devices_list = devices_data.get("data", {}).get("list", [])
        if not devices_list:
            print("❌ No devices found")
            return
        
        device = devices_list[0]
        print(f"✅ Got device: {device['equipmentName']}")
        
        # Get device parameters
        params_data = await api.get_device_parameters(device["id"])
        if params_data.get("status") != 0:
            print(f"❌ Failed to get parameters: {params_data}")
            return
        
        print(f"✅ Got device parameters")
        print()
        
        # Configuration sensors we're looking for
        config_sensors = [
            "Battery Type", "Bulk Charging Voltage", "Bulk Voltage Recovery Voltage",
            "Buzzer Alarm Switch", "Charging Limit Voltage", "Device Time",
            "Discharging Voltage Limit Voltage", "Equalize Charging Voltage",
            "Float Charging Voltage", "LCD Backlight Timeout", "Li-ion Battery BMS",
            "Li-ion Battery Protect", "Li-ion Battery Protocol Type",
            "Low Temperature Charging Limit", "Low Temperature Discharging Limit",
            "Low Voltage Disconnect Voltage", "Low Voltage Recovery Voltage",
            "Overvoltage Disconnect Voltage", "Overvoltage Recovery Voltage",
            "Temperature Compensation", "Temperature Unit", "Under voltage alarm",
            "Undervoltage Alarm Recovery Voltage"
        ]
        
        print("=" * 80)
        print("  Searching for Configuration Sensors")
        print("=" * 80)
        print()
        
        found_sensors = []
        
        # Search through all parameter groups
        for group in params_data.get("data", {}).get("variableGroupList", []):
            group_name = group.get("variableGroupNameE", group.get("variableGroupNameC", "Unknown"))
            
            for variable in group.get("variableList", []):
                var_name = variable.get("variableNameE", variable.get("variableNameC", "Unknown"))
                data_identifier = variable.get("dataIdentifier", "")
                
                # Check if this is one of our config sensors
                if any(config in var_name for config in config_sensors):
                    found_sensors.append({
                        "name": var_name,
                        "identifier": data_identifier,
                        "group": group_name,
                        "variable": variable
                    })
        
        print(f"📊 Found {len(found_sensors)} configuration sensors")
        print()
        
        # Get latest data to see if any of these have real-time values
        print("=" * 80)
        print("  Checking Latest Data Endpoint")
        print("=" * 80)
        print()
        
        # Build datapoint list for all config sensors
        dev_datapoints = []
        for sensor in found_sensors:
            data_point_id = sensor["variable"].get("dataPointId")
            if data_point_id:
                dev_datapoints.append({
                    "dataPointId": data_point_id,
                    "deviceNo": device.get("equipmentNo", "")
                })
        
        print(f"📋 Requesting latest data for {len(dev_datapoints)} sensors...")
        
        try:
            latest_data = await api.get_latest_data_by_datapoints(dev_datapoints)
            
            if latest_data.get("status") == 0:
                latest_list = latest_data.get("data", {}).get("list", [])
                print(f"✅ Got latest data: {len(latest_list)} values")
                
                # Map dataPointId to value
                latest_values = {
                    item.get("dataPointId"): item.get("value")
                    for item in latest_list
                }
            else:
                print(f"⚠️ Latest data request returned status: {latest_data.get('status')}")
                latest_values = {}
        except Exception as err:
            print(f"⚠️ Latest data endpoint failed: {err}")
            latest_values = {}
        
        print()
        print("=" * 80)
        print("  Configuration Sensor Details")
        print("=" * 80)
        print()
        
        # Show details for each sensor
        for sensor in found_sensors[:10]:  # Show first 10 as sample
            variable = sensor["variable"]
            data_point_id = variable.get("dataPointId")
            
            print(f"📊 {sensor['name']}")
            print(f"   Group: {sensor['group']}")
            print(f"   Identifier: {sensor['identifier']}")
            print(f"   DataPointId: {data_point_id}")
            
            # Check for values
            current_value = variable.get("currentValue")
            default_value = variable.get("defaultValue")
            value = variable.get("value")
            latest_value = latest_values.get(data_point_id) if data_point_id else None
            
            print(f"   currentValue: {current_value}")
            print(f"   defaultValue: {default_value}")
            print(f"   value: {value}")
            print(f"   latest_data value: {latest_value}")
            
            # Check translation
            translation_child = variable.get("translationChild", [])
            if translation_child:
                print(f"   Has translations: {len(translation_child)} mappings")
            
            print()
        
        if len(found_sensors) > 10:
            print(f"... and {len(found_sensors) - 10} more sensors")
            print()
        
        # Summary
        print("=" * 80)
        print("  Summary")
        print("=" * 80)
        print()
        
        sensors_with_current = sum(1 for s in found_sensors if s["variable"].get("currentValue") is not None)
        sensors_with_default = sum(1 for s in found_sensors if s["variable"].get("defaultValue") is not None)
        sensors_with_value = sum(1 for s in found_sensors if s["variable"].get("value") is not None)
        sensors_with_latest = sum(1 for s in found_sensors if latest_values.get(s["variable"].get("dataPointId")) is not None)
        
        print(f"Total config sensors: {len(found_sensors)}")
        print(f"With currentValue: {sensors_with_current}")
        print(f"With defaultValue: {sensors_with_default}")
        print(f"With value field: {sensors_with_value}")
        print(f"With latest_data: {sensors_with_latest}")
        
    finally:
        await api.close()

if __name__ == "__main__":
    asyncio.run(test_config_sensors())
