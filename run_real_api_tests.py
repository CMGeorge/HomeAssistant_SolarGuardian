#!/usr/bin/env python3
"""
Enhanced test script for SolarGuardian API with detailed data display.
This script performs REAL API calls (not mocked) and shows actual values retrieved.

Usage:
    # Set environment variables
    export SOLARGUARDIAN_DOMAIN=glapi.mysolarguardian.com
    export SOLARGUARDIAN_APP_KEY=your_app_key
    export SOLARGUARDIAN_APP_SECRET=your_app_secret
    
    # Run the script
    python run_real_api_tests.py
"""

import asyncio
import json
import logging
import os
import sys
from typing import Optional
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Add custom components to path
sys.path.insert(0, 'custom_components')

from solarguardian.api import SolarGuardianAPI, SolarGuardianAPIError
from solarguardian.const import DOMAIN_CHINA, DOMAIN_INTERNATIONAL


def print_separator(char='=', length=100):
    """Print a separator line."""
    print(char * length)


def print_section(title):
    """Print a section header."""
    print(f"\n{'=' * 100}")
    print(f"  {title}")
    print('=' * 100)


def print_json_pretty(data, indent=2, max_depth=None):
    """Pretty print JSON data."""
    print(json.dumps(data, indent=indent, ensure_ascii=False))


async def test_real_api_with_details(domain: str, app_key: str, app_secret: str):
    """Test API connection with REAL calls and display ALL retrieved data."""
    
    print_section(f"🚀 REAL API TEST - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"\n📡 Connecting to: {domain}")
    print(f"🔑 Using App Key: {app_key[:10]}..." if len(app_key) > 10 else f"🔑 Using App Key: {app_key}")
    print(f"\n⚠️  NOTE: This script makes REAL API calls to your SolarGuardian account")
    print(f"         All data shown below is retrieved from the actual API (not mocked)\n")
    
    api = SolarGuardianAPI(domain, app_key, app_secret)
    
    try:
        # ==================================================
        # STEP 1: Authentication
        # ==================================================
        print_section("STEP 1: Authentication")
        print("Making authentication API call...")
        
        success = await api.authenticate()
        
        if success:
            print("\n✅ Authentication SUCCESSFUL")
            print(f"   Access Token: {api._token[:20]}..." if api._token else "   No token")
            print(f"   Token Expires: {api._token_expires}")
        else:
            print("\n❌ Authentication FAILED")
            return
        
        # ==================================================
        # STEP 2: Get Power Stations
        # ==================================================
        print_section("STEP 2: Fetching Power Stations")
        print("Making API call: get_power_stations()...")
        
        stations_response = await api.get_power_stations()
        
        print("\n📊 RAW API RESPONSE:")
        print_json_pretty(stations_response)
        
        stations_list = stations_response.get("data", {}).get("list", [])
        total_stations = stations_response.get("data", {}).get("total", 0)
        
        print(f"\n📈 SUMMARY:")
        print(f"   - API Status: {stations_response.get('status')}")
        print(f"   - Total Stations: {total_stations}")
        print(f"   - Stations Retrieved: {len(stations_list)}")
        
        if not stations_list:
            print("\n⚠️  No power stations found in your account.")
            return
        
        # Process each station
        for station_idx, station in enumerate(stations_list, 1):
            print_section(f"STATION {station_idx}/{len(stations_list)}: {station.get('powerStationName', 'Unknown')}")
            
            # Show all station fields
            print("\n📋 ALL STATION FIELDS:")
            for key, value in station.items():
                print(f"   {key}: {value}")
            
            station_id = station["id"]
            station_name = station.get("powerStationName", "Unknown")
            
            # ==================================================
            # STEP 3: Get Devices for Station
            # ==================================================
            print_section(f"STEP 3.{station_idx}: Fetching Devices for Station '{station_name}'")
            print(f"Making API call: get_devices({station_id})...")
            
            devices_response = await api.get_devices(station_id, page_no=1, page_size=20)
            
            print("\n📊 RAW API RESPONSE:")
            print_json_pretty(devices_response)
            
            devices_list = devices_response.get("data", {}).get("list", [])
            total_devices = devices_response.get("data", {}).get("total", 0)
            
            print(f"\n📈 SUMMARY:")
            print(f"   - API Status: {devices_response.get('status')}")
            print(f"   - Total Devices: {total_devices}")
            print(f"   - Devices Retrieved: {len(devices_list)}")
            
            # Process each device
            for device_idx, device in enumerate(devices_list, 1):
                print_section(f"DEVICE {device_idx}/{len(devices_list)}: {device.get('equipmentName', 'Unknown')}")
                
                # Show all device fields
                print("\n📋 ALL DEVICE FIELDS:")
                for key, value in device.items():
                    print(f"   {key}: {value}")
                
                device_id = device["id"]
                device_name = device.get("equipmentName", "Unknown")
                
                # ==================================================
                # STEP 4: Get Device Parameters
                # ==================================================
                print_section(f"STEP 4.{station_idx}.{device_idx}: Fetching Parameters for Device '{device_name}'")
                print(f"Making API call: get_device_parameters({device_id})...")
                
                params_response = await api.get_device_parameters(device_id)
                
                print("\n📊 RAW API RESPONSE:")
                print_json_pretty(params_response)
                
                variable_groups = params_response.get("data", {}).get("variableGroupList", [])
                
                print(f"\n📈 SUMMARY:")
                print(f"   - API Status: {params_response.get('status')}")
                print(f"   - Parameter Groups: {len(variable_groups)}")
                
                # Collect all data identifiers
                all_data_identifiers = []
                
                # Display each parameter group
                for group_idx, group in enumerate(variable_groups, 1):
                    group_name_e = group.get("variableGroupNameE", "")
                    group_name_c = group.get("variableGroupNameC", "")
                    group_name = group_name_e or group_name_c or f"Group {group_idx}"
                    
                    variables = group.get("variableList", [])
                    
                    print(f"\n   📦 GROUP {group_idx}: {group_name}")
                    print(f"      Parameters: {len(variables)}")
                    
                    for var_idx, var in enumerate(variables, 1):
                        var_name_e = var.get("variableNameE", "")
                        var_name_c = var.get("variableNameC", "")
                        var_name = var_name_e or var_name_c or "Unknown"
                        data_id = var.get("dataIdentifier", "")
                        unit = var.get("unit", "")
                        decimal = var.get("decimal", "0")
                        
                        print(f"\n      Parameter {var_idx}: {var_name}")
                        print(f"         Data Identifier: {data_id}")
                        print(f"         Unit: {unit}")
                        print(f"         Decimals: {decimal}")
                        
                        # Show all variable fields
                        for key, value in var.items():
                            if key not in ['variableNameE', 'variableNameC', 'dataIdentifier', 'unit', 'decimal']:
                                print(f"         {key}: {value}")
                        
                        if data_id:
                            all_data_identifiers.append({
                                'id': data_id,
                                'name': var_name,
                                'unit': unit,
                                'decimal': decimal
                            })
                
                # ==================================================
                # STEP 5: Get Latest Data for Parameters
                # ==================================================
                if all_data_identifiers:
                    # Get latest data for up to 15 parameters at a time
                    batch_size = 15
                    
                    for batch_idx in range(0, len(all_data_identifiers), batch_size):
                        batch = all_data_identifiers[batch_idx:batch_idx + batch_size]
                        batch_ids = [item['id'] for item in batch]
                        
                        print_section(f"STEP 5.{station_idx}.{device_idx}.{batch_idx//batch_size + 1}: Fetching Latest Data (Batch {batch_idx//batch_size + 1})")
                        print(f"Making API call: get_latest_data({device_id}, {len(batch_ids)} parameters)...")
                        print(f"Parameters: {', '.join(batch_ids[:5])}{'...' if len(batch_ids) > 5 else ''}")
                        
                        try:
                            latest_response = await api.get_latest_data(device_id, batch_ids)
                            
                            print("\n📊 RAW API RESPONSE:")
                            print_json_pretty(latest_response)
                            
                            latest_list = latest_response.get("data", {}).get("list", [])
                            
                            print(f"\n📈 SUMMARY:")
                            print(f"   - API Status: {latest_response.get('status')}")
                            print(f"   - Data Points Retrieved: {len(latest_list)}")
                            
                            print(f"\n💡 ACTUAL SENSOR VALUES (Real-time from API):")
                            
                            for data_point in latest_list:
                                identifier = data_point.get("dataIdentifier", "Unknown")
                                value = data_point.get("value", "N/A")
                                
                                # Find parameter info
                                param_info = next((p for p in batch if p['id'] == identifier), None)
                                if param_info:
                                    param_name = param_info['name']
                                    unit = param_info['unit']
                                    decimal_places = int(param_info['decimal'])
                                    
                                    # Format value with proper decimals
                                    try:
                                        formatted_value = f"{float(value):.{decimal_places}f}"
                                    except:
                                        formatted_value = value
                                    
                                    print(f"\n   📊 {param_name}")
                                    print(f"      Identifier: {identifier}")
                                    print(f"      Value: {formatted_value} {unit}")
                                    
                                    # Show all data point fields
                                    for key, val in data_point.items():
                                        if key not in ['dataIdentifier', 'value']:
                                            print(f"      {key}: {val}")
                                else:
                                    print(f"\n   📊 {identifier}: {value}")
                                    for key, val in data_point.items():
                                        if key not in ['dataIdentifier', 'value']:
                                            print(f"      {key}: {val}")
                                
                        except Exception as e:
                            print(f"\n⚠️  Failed to get latest data: {e}")
                            print("   (This endpoint may require different configuration)")
                
                # Only process first device to avoid overwhelming output
                if device_idx >= 1 and len(devices_list) > 1:
                    print(f"\n   ... {len(devices_list) - 1} more devices available (not shown to limit output)")
                    break
            
            # Only process first station to avoid overwhelming output
            if station_idx >= 1 and len(stations_list) > 1:
                print(f"\n   ... {len(stations_list) - 1} more stations available (not shown to limit output)")
                break
        
        print_section("✅ REAL API TEST COMPLETED SUCCESSFULLY")
        print("\n📊 Test Summary:")
        print(f"   - All API calls were REAL (not mocked)")
        print(f"   - Retrieved data from live SolarGuardian account")
        print(f"   - Stations tested: {min(1, len(stations_list))}")
        print(f"   - Devices tested: {min(1, len(devices_list)) if stations_list and devices_list else 0}")
        print(f"   - Sensor values shown are real-time from the API")
        
    except SolarGuardianAPIError as e:
        print_section("❌ SolarGuardian API Error")
        print(f"\nError: {e}")
        print("\nThis is a REAL API error from the SolarGuardian service")
    except Exception as e:
        print_section("❌ Unexpected Error")
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await api.close()


def load_test_credentials() -> Optional[tuple]:
    """Load test credentials from environment or config file."""
    # Try environment variables first
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


async def main():
    """Main test function."""
    print("=" * 100)
    print("  🚀 SolarGuardian REAL API Test (No Mocking)")
    print("=" * 100)
    print("\n⚠️  IMPORTANT: This script makes REAL API calls to your SolarGuardian account")
    print("   All data displayed is retrieved from the actual API endpoints")
    print("   This is NOT using mock data\n")
    
    # Load credentials
    credentials = load_test_credentials()
    
    if not credentials or not all(credentials):
        print("❌ No test credentials found\n")
        print("To run REAL API tests, you need to provide your actual SolarGuardian credentials:\n")
        print("Option 1: Set environment variables:")
        print("   export SOLARGUARDIAN_DOMAIN=glapi.mysolarguardian.com")
        print("   export SOLARGUARDIAN_APP_KEY=your_actual_app_key")
        print("   export SOLARGUARDIAN_APP_SECRET=your_actual_app_secret\n")
        print("Option 2: Create test_config.json file:")
        print("   {")
        print('     "domain": "glapi.mysolarguardian.com",')
        print('     "app_key": "your_actual_app_key",')
        print('     "app_secret": "your_actual_app_secret"')
        print("   }\n")
        print("Note: You need real credentials from your SolarGuardian account")
        print("      to see actual sensor values and API responses.\n")
        return
    
    domain, app_key, app_secret = credentials
    
    await test_real_api_with_details(domain, app_key, app_secret)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n🛑 Test interrupted by user")
    except Exception as e:
        print(f"\n\n💥 Test failed with error: {e}")
        import traceback
        traceback.print_exc()
