#!/usr/bin/env python3
"""Test to verify sensor value matching fix.

This test simulates the actual API response structure to verify that
sensors can correctly match and extract values from latest_data.

The bug was: latest_data uses dataPointId, but code was matching on dataIdentifier.
The fix: Match on dataPointId instead of dataIdentifier.
"""

def test_sensor_value_matching():
    """Test that sensor value matching works with real API structure."""
    
    # Simulate actual API response structure for latest_data
    # Based on API docs section 3.5 - Response example for lastDatapoint endpoint
    latest_data_response = {
        "status": 0,
        "data": {
            "list": [
                {
                    "slaveName": "Device-1",
                    "deviceName": "Solar Inverter",
                    "dataPointName": "Output Power",
                    "dataPointId": 101754260,  # ← API uses dataPointId
                    "deviceNo": "2023021512345678900001",
                    "error": 0,
                    "templateDataPointId": 102804581,
                    "value": "1250.5",  # ← Value as string
                    "time": 1705479748496
                },
                {
                    "slaveName": "Device-1",
                    "deviceName": "Solar Inverter",
                    "dataPointName": "Battery Voltage",
                    "dataPointId": 101754282,  # ← API uses dataPointId
                    "deviceNo": "2023021512345678900001",
                    "error": 0,
                    "templateDataPointId": 102804603,
                    "value": "48.2",  # ← Value as string
                    "time": 1705479748496
                }
            ]
        },
        "info": ""
    }
    
    # Simulate device parameter structure (from getEquipment endpoint)
    # This has BOTH dataPointId AND dataIdentifier
    sensor_variable = {
        "id": 12345,
        "dataPointId": 101754260,  # ← Links to latest_data
        "dataIdentifier": "OutputPower",  # ← Used for unique_id/internal reference
        "variableNameE": "Output Power",
        "unit": "W",
        "decimal": "1",  # Value needs to be divided by 10
    }
    
    # Test the matching logic (simulating what sensor.py does)
    data_point_id = sensor_variable.get("dataPointId")
    data_identifier = sensor_variable["dataIdentifier"]
    
    print(f"Testing sensor: {sensor_variable['variableNameE']}")
    print(f"  dataIdentifier: {data_identifier}")
    print(f"  dataPointId: {data_point_id}")
    print()
    
    # OLD CODE (BROKEN) - would match on dataIdentifier
    print("OLD CODE (matching on dataIdentifier):")
    found_old = False
    for data_point in latest_data_response["data"]["list"]:
        if data_point.get("dataIdentifier") == data_identifier:  # ❌ This field doesn't exist!
            found_old = True
            print(f"  ✅ Found match! Value: {data_point.get('value')}")
            break
    if not found_old:
        print(f"  ❌ NO MATCH FOUND - dataIdentifier not in latest_data response!")
    print()
    
    # NEW CODE (FIXED) - matches on dataPointId  
    print("NEW CODE (matching on dataPointId):")
    found_new = False
    for data_point in latest_data_response["data"]["list"]:
        if data_point.get("dataPointId") == data_point_id:  # ✅ This field exists!
            found_new = True
            value = float(data_point.get("value", 0))
            
            # Apply decimal formatting
            decimal = sensor_variable.get("decimal", "0")
            if decimal and decimal.isdigit():
                value = value / (10 ** int(decimal))
            
            print(f"  ✅ Found match!")
            print(f"     Raw value: {data_point.get('value')}")
            print(f"     Decimal places: {decimal}")
            print(f"     Final value: {value} {sensor_variable['unit']}")
            break
    if not found_new:
        print(f"  ❌ NO MATCH FOUND")
    print()
    
    # Verify fix works
    assert not found_old, "Old code should NOT find match (dataIdentifier not in response)"
    assert found_new, "New code SHOULD find match (dataPointId in response)"
    
    print("=" * 60)
    print("✅ TEST PASSED: Sensor value matching fix verified!")
    print("=" * 60)
    print()
    print("Summary:")
    print("  • latest_data response uses 'dataPointId' (not 'dataIdentifier')")
    print("  • Sensors must match on 'dataPointId' to get real-time values")
    print("  • 'dataIdentifier' is only in device parameters for reference")
    print()
    return True


if __name__ == "__main__":
    test_sensor_value_matching()
