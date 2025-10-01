#!/usr/bin/env python3
"""Test translation of enum sensor values with real API data."""

import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv

# Load credentials
env_path = Path(__file__).parent / '.env'
load_dotenv(env_path)

# Import API
from test_api_wrapper import load_api_modules
api_module, const_module = load_api_modules()
SolarGuardianAPI = api_module.SolarGuardianAPI

async def test_translations():
    """Test that enum sensors get translated correctly."""
    
    domain = os.getenv("DOMAIN", "openapi.epsolarpv.com")
    app_key = os.getenv("APP_KEY")
    app_secret = os.getenv("APP_SECRET")
    
    print("=" * 80)
    print("  Testing Enum Sensor Translations")
    print("=" * 80)
    print()
    
    api = SolarGuardianAPI(domain, app_key, app_secret)
    
    try:
        # Authenticate
        await api.authenticate()
        print("✅ Authenticated")
        
        # Get station
        stations = await api.get_power_stations()
        station = stations["data"]["list"][0]
        print(f"✅ Got station: {station['powerStationName']}")
        
        # Get device
        devices = await api.get_devices(station["id"])
        device = devices["data"]["list"][0]
        print(f"✅ Got device: {device['equipmentName']}")
        
        # Get device parameters
        params = await api.get_device_parameters(device["id"])
        variable_groups = params["data"]["variableGroupList"]
        print(f"✅ Got {len(variable_groups)} parameter groups")
        print()
        
        # Find all sensors with translationChild
        enum_sensors = []
        for group in variable_groups:
            for variable in group["variableList"]:
                if variable.get("translationChild"):
                    enum_sensors.append(variable)
        
        print(f"📊 Found {len(enum_sensors)} sensors with enum translations:")
        print()
        
        # Build datapoints list for latest_data
        dev_datapoints = []
        for var in enum_sensors:
            if var.get("dataPointId") and var.get("deviceNo"):
                dev_datapoints.append({
                    "dataPointId": var["dataPointId"],
                    "deviceNo": var["deviceNo"],
                })
        
        # Get latest data
        if dev_datapoints:
            latest_data = await api.get_latest_data_by_datapoints(dev_datapoints)
            latest_values = {dp["dataPointId"]: dp["value"] for dp in latest_data.get("data", {}).get("list", [])}
            print(f"✅ Got latest data for {len(latest_values)} enum sensors")
            print()
        else:
            latest_values = {}
        
        # Test translation logic
        def translate_value(value, translations):
            """Translate numeric value to text."""
            value_str = str(int(float(value)))
            for t in translations:
                if t.get('value') == value_str:
                    return t.get('resultE') or t.get('result')
            return None
        
        # Display each enum sensor with translation
        print("=" * 80)
        print("  Enum Sensor Values and Translations")
        print("=" * 80)
        print()
        
        for var in enum_sensors:
            name = var.get("variableNameE") or var.get("variableNameC")
            data_id = var.get("dataIdentifier")
            data_point_id = var.get("dataPointId")
            unit = var.get("unit", "")
            
            # Get latest value if available
            raw_value = latest_values.get(data_point_id)
            
            print(f"📊 {name}")
            print(f"   Identifier: {data_id}")
            print(f"   DataPointId: {data_point_id}")
            
            if raw_value is not None:
                print(f"   Raw Value: {raw_value}")
                
                # Translate
                translated = translate_value(raw_value, var["translationChild"])
                if translated:
                    print(f"   ✅ Translated: {translated}")
                else:
                    print(f"   ⚠️  No translation for value: {raw_value}")
            else:
                print(f"   ⚠️  No latest data available")
            
            # Show available translations
            print(f"   Available translations:")
            for t in var["translationChild"][:5]:  # Show first 5
                value = t.get("value")
                result = t.get("resultE") or t.get("result")
                print(f"      {value} → {result}")
            if len(var["translationChild"]) > 5:
                print(f"      ... and {len(var['translationChild']) - 5} more")
            
            print()
        
        print("=" * 80)
        print("✅ Translation test complete!")
        print("=" * 80)
        
    finally:
        await api.close()

if __name__ == "__main__":
    asyncio.run(test_translations())
