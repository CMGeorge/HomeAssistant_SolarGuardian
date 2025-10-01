#!/usr/bin/env python3
"""
Enhanced test script for SolarGuardian API with detailed data display.
This script performs REAL API calls (not mocked) and shows actual values retrieved.

Usage:
    # Option 1: Use .env file (recommended)
    # Create tests/.env with:
    #   APP_KEY=your_app_key
    #   APP_SECRET=your_app_secret
    #   DOMAIN=glapi.mysolarguardian.com
    
    # Option 2: Set environment variables
    export APP_KEY=your_app_key
    export APP_SECRET=your_app_secret
    export DOMAIN=glapi.mysolarguardian.com
    
    # Run the script from tests directory
    cd tests
    python run_real_api_tests.py
"""

import asyncio
import json
import logging
import os
import sys
from typing import Optional
from datetime import datetime
from pathlib import Path

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    # Load .env from tests directory
    env_path = Path(__file__).parent / '.env'
    if env_path.exists():
        load_dotenv(env_path)
        print(f"✅ Loaded credentials from {env_path}")
    else:
        print(f"⚠️  No .env file found at {env_path}")
except ImportError:
    print("⚠️  python-dotenv not installed, will use environment variables only")

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Import API modules using wrapper to avoid Home Assistant dependencies
from test_api_wrapper import load_api_modules

api_module, const_module = load_api_modules()
SolarGuardianAPI = api_module.SolarGuardianAPI
SolarGuardianAPIError = api_module.SolarGuardianAPIError
DOMAIN_CHINA = const_module.DOMAIN_CHINA
DOMAIN_INTERNATIONAL = const_module.DOMAIN_INTERNATIONAL


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
                
                # Collect all data identifiers and datapoints
                all_data_identifiers = []
                all_dev_datapoints = []
                
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
                        data_point_id = var.get("dataPointId")
                        device_no = var.get("deviceNo")
                        
                        print(f"\n      Parameter {var_idx}: {var_name}")
                        print(f"         Data Identifier: {data_id}")
                        print(f"         Data Point ID: {data_point_id}")
                        print(f"         Device No: {device_no}")
                        print(f"         Unit: {unit}")
                        print(f"         Decimals: {decimal}")
                        
                        # Show all variable fields
                        for key, value in var.items():
                            if key not in ['variableNameE', 'variableNameC', 'dataIdentifier', 'unit', 'decimal', 'dataPointId', 'deviceNo']:
                                print(f"         {key}: {value}")
                        
                        if data_id:
                            all_data_identifiers.append({
                                'id': data_id,
                                'name': var_name,
                                'unit': unit,
                                'decimal': decimal
                            })
                        
                        # Collect datapoints for the correct API method
                        if data_point_id and device_no:
                            all_dev_datapoints.append({
                                'dataPointId': data_point_id,
                                'deviceNo': device_no,
                                'name': var_name,
                                'unit': unit,
                                'decimal': decimal
                            })
                
                # ==================================================
                # STEP 5: Get Latest Data for Parameters (Using Correct Method)
                # ==================================================
                if all_dev_datapoints:
                    # Use the CORRECT API method with dataPointId and deviceNo
                    # Get latest data for up to 15 parameters at a time
                    batch_size = 15
                    
                    for batch_idx in range(0, len(all_dev_datapoints), batch_size):
                        batch = all_dev_datapoints[batch_idx:batch_idx + batch_size]
                        dev_datapoints_batch = [{'dataPointId': dp['dataPointId'], 'deviceNo': dp['deviceNo']} for dp in batch]
                        
                        print_section(f"STEP 5.{station_idx}.{device_idx}.{batch_idx//batch_size + 1}: Fetching Latest Data (Batch {batch_idx//batch_size + 1})")
                        print(f"Making API call: get_latest_data_by_datapoints with {len(dev_datapoints_batch)} datapoints...")
                        print(f"First datapoint: dataPointId={batch[0]['dataPointId']}, deviceNo={batch[0]['deviceNo']}")
                        
                        try:
                            latest_response = await api.get_latest_data_by_datapoints(dev_datapoints_batch)
                            
                            print("\n📊 RAW API RESPONSE:")
                            print_json_pretty(latest_response)
                            
                            latest_list = latest_response.get("data", {}).get("list", [])
                            
                            print(f"\n📈 SUMMARY:")
                            print(f"   - API Status: {latest_response.get('status')}")
                            print(f"   - Data Points Retrieved: {len(latest_list)}")
                            
                            print(f"\n💡 ACTUAL SENSOR VALUES (Real-time from API):")
                            
                            for data_point in latest_list:
                                # The response may have dataPointId or dataIdentifier
                                data_point_id = data_point.get("dataPointId")
                                identifier = data_point.get("dataIdentifier", "Unknown")
                                value = data_point.get("value", "N/A")
                                
                                # Find parameter info by dataPointId or dataIdentifier
                                param_info = None
                                if data_point_id:
                                    param_info = next((p for p in batch if p.get('dataPointId') == data_point_id), None)
                                if not param_info and identifier:
                                    param_info = next((p for p in batch if p.get('name') == identifier), None)
                                
                                if param_info:
                                    param_name = param_info['name']
                                    unit = param_info['unit']
                                    decimal_places = int(param_info.get('decimal', '0'))
                                    
                                    # Format value with proper decimals
                                    try:
                                        formatted_value = f"{float(value):.{decimal_places}f}"
                                    except:
                                        formatted_value = value
                                    
                                    print(f"\n   📊 {param_name}")
                                    print(f"      Identifier: {identifier}")
                                    print(f"      DataPointId: {data_point_id}")
                                    print(f"      Value: {formatted_value} {unit}")
                                    
                                    # Show all data point fields
                                    for key, val in data_point.items():
                                        if key not in ['dataIdentifier', 'value', 'dataPointId']:
                                            print(f"      {key}: {val}")
                                else:
                                    print(f"\n   📊 DataPointId: {data_point_id}, Identifier: {identifier}")
                                    print(f"      Value: {value}")
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
    # Try environment variables (including from .env file)
    domain = os.getenv("DOMAIN") or os.getenv("SOLARGUARDIAN_DOMAIN")
    app_key = os.getenv("APP_KEY") or os.getenv("SOLARGUARDIAN_APP_KEY") or os.getenv("APPKEY")
    app_secret = os.getenv("APP_SECRET") or os.getenv("SOLARGUARDIAN_APP_SECRET") or os.getenv("APPSECRET")
    
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
        print("Option 1: Create tests/.env file (RECOMMENDED):")
        print("   APP_KEY=your_actual_app_key")
        print("   APP_SECRET=your_actual_app_secret")
        print("   DOMAIN=glapi.mysolarguardian.com\n")
        print("Option 2: Set environment variables:")
        print("   export APP_KEY=your_actual_app_key")
        print("   export APP_SECRET=your_actual_app_secret")
        print("   export DOMAIN=glapi.mysolarguardian.com\n")
        print("Option 3: Create test_config.json file:")
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
