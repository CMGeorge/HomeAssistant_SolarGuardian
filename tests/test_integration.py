#!/usr/bin/env python3
"""Test script for SolarGuardian API integration (for development purposes)."""

import asyncio
import json
import logging
import os
import sys
from typing import Optional

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Add custom components to path
sys.path.insert(0, 'custom_components')

from solarguardian.api import SolarGuardianAPI, SolarGuardianAPIError
from solarguardian.const import DOMAIN_CHINA, DOMAIN_INTERNATIONAL


async def test_api_connection(domain: str, app_key: str, app_secret: str):
    """Test API connection and data retrieval."""
    print(f"🔗 Testing connection to {domain}")
    
    api = SolarGuardianAPI(domain, app_key, app_secret)
    
    try:
        # Test authentication
        print("🔐 Testing authentication...")
        success = await api.authenticate()
        if success:
            print("✅ Authentication successful")
        else:
            print("❌ Authentication failed")
            return
        
        # Test power stations
        print("🏭 Getting power stations...")
        stations = await api.get_power_stations()
        stations_list = stations.get("data", {}).get("list", [])
        print(f"✅ Found {len(stations_list)} power stations")
        
        for station in stations_list[:1]:  # Test first station only
            station_id = station["id"]
            station_name = station["powerStationName"]
            print(f"   📍 Station: {station_name} (ID: {station_id})")
            
            # Test devices
            print("   🔌 Getting devices...")
            devices = await api.get_devices(station_id, page_no=1, page_size=10)
            
            devices_list = devices.get("data", {}).get("list", [])
            print(f"   ✅ Found {len(devices_list)} devices")
            
            for device in devices_list[:1]:  # Test first device only
                device_id = device["id"]
                device_name = device["equipmentName"]
                print(f"      🔧 Device: {device_name} (ID: {device_id})")
                
                # Test device parameters
                print("      📊 Getting device parameters...")
                device_data = await api.get_device_parameters(device_id)
                
                variable_groups = device_data.get("data", {}).get("variableGroupList", [])
                print(f"      ✅ Found {len(variable_groups)} parameter groups")
                
                # List some parameters
                param_count = 0
                data_identifiers = []
                
                for group in variable_groups:
                    group_name = group.get("variableGroupNameE", group.get("variableGroupNameC", "Unknown"))
                    variables = group.get("variableList", [])
                    print(f"         📋 Group: {group_name} ({len(variables)} parameters)")
                    
                    for variable in variables[:3]:  # Show first 3 parameters
                        param_name = variable.get("variableNameE", variable.get("variableNameC", "Unknown"))
                        data_id = variable.get("dataIdentifier", "")
                        unit = variable.get("unit", "")
                        param_count += 1
                        
                        if data_id:
                            data_identifiers.append(data_id)
                        
                        print(f"            • {param_name} ({data_id}) [{unit}]")
                
                print(f"      ✅ Total parameters found: {param_count}")
                
                # Test latest data if we have identifiers
                if data_identifiers[:5]:  # Test first 5 parameters
                    print("      🔄 Getting latest data...")
                    try:
                        latest = await api.get_latest_data(device_id, data_identifiers[:5])
                        latest_list = latest.get("data", {}).get("list", [])
                        print(f"      ✅ Retrieved {len(latest_list)} current values")
                        
                        for data_point in latest_list[:3]:  # Show first 3 values
                            identifier = data_point.get("dataIdentifier", "Unknown")
                            value = data_point.get("value", "N/A")
                            print(f"         📈 {identifier}: {value}")
                            
                    except Exception as latest_err:
                        print(f"      ⚠️  Latest data failed: {latest_err}")
        
        print("✅ API test completed successfully")
        
    except SolarGuardianAPIError as e:
        print(f"❌ SolarGuardian API Error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        raise
    finally:
        await api.close()


def load_test_credentials() -> Optional[tuple]:
    """Load test credentials from environment or config file."""
    # Try environment variables first (check both long and short forms)
    domain = os.getenv("SOLARGUARDIAN_DOMAIN")
    app_key = os.getenv("SOLARGUARDIAN_APP_KEY") or os.getenv("APPKEY")
    app_secret = os.getenv("SOLARGUARDIAN_APP_SECRET") or os.getenv("APPSECRET")
    
    if domain and app_key and app_secret:
        return (domain, app_key, app_secret)
    
    # Try config file
    config_file = "test_config.json"
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
            return (
                config.get("domain"),
                config.get("app_key"),
                config.get("app_secret")
            )
        except Exception as e:
            print(f"⚠️  Error reading config file: {e}")
    
    return None


def create_test_config():
    """Create a test configuration file template."""
    config = {
        "domain": DOMAIN_INTERNATIONAL,
        "app_key": "your_app_key_here",
        "app_secret": "your_app_secret_here"
    }
    
    with open("test_config.json", 'w') as f:
        json.dump(config, f, indent=2)
    
    print("📝 Created test_config.json template")
    print("   Please edit the file with your actual credentials")


async def main():
    """Main test function."""
    print("🚀 SolarGuardian Integration Test\n")
    
    # Load credentials
    credentials = load_test_credentials()
    
    if not credentials or not all(credentials):
        print("❌ No test credentials found")
        print("\nTo test the integration, you need to provide credentials:")
        print("Option 1: Set environment variables:")
        print("   export SOLARGUARDIAN_DOMAIN=glapi.mysolarguardian.com")
        print("   export SOLARGUARDIAN_APP_KEY=your_app_key")
        print("   export SOLARGUARDIAN_APP_SECRET=your_app_secret")
        print("   OR use shorter forms:")
        print("   export APPKEY=your_app_key")
        print("   export APPSECRET=your_app_secret")
        print("\nOption 2: Create test_config.json file")
        
        if input("Create test_config.json template? (y/n): ").lower() == 'y':
            create_test_config()
        
        return
    
    domain, app_key, app_secret = credentials
    print(f"🔧 Using domain: {domain}")
    print(f"🔧 Using app key: {app_key[:8]}...")
    
    await test_api_connection(domain, app_key, app_secret)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted by user")
    except Exception as e:
        print(f"\n💥 Test failed with error: {e}")
        import traceback
        traceback.print_exc()