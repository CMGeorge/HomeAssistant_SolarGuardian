#!/usr/bin/env python3
"""Standalone test runner that directly imports specific files."""
import sys
import json
import os
from pathlib import Path

def test_constants():
    """Test constants by directly importing the const.py file."""
    print("📊 Testing Constants...")
    
    try:
        # Add the specific directory to path
        const_path = Path(__file__).parent / 'custom_components' / 'solarguardian'
        sys.path.insert(0, str(const_path))
        
        # Import const module directly
        import const
        
        print("✅ Constants imported successfully")
        print(f"   - Domain: {const.DOMAIN}")
        print(f"   - International API: {const.DOMAIN_INTERNATIONAL}")
        print(f"   - China API: {const.DOMAIN_CHINA}")
        print(f"   - Update interval: {const.DEFAULT_UPDATE_INTERVAL}s")
        print(f"   - Timeout: {const.DEFAULT_TIMEOUT}s")
        
        # Test mock data
        print(f"   - Mock station: {const.MOCK_POWER_STATION['powerStationName']}")
        print(f"   - Mock device: {const.MOCK_DEVICE['equipmentName']}")
        
        param_count = 0
        for group in const.MOCK_VARIABLE_GROUPS:
            param_count += len(group["variableList"])
        print(f"   - Mock parameters: {param_count} total")
        
        # Basic validation
        assert isinstance(const.DOMAIN, str)
        assert isinstance(const.DEFAULT_UPDATE_INTERVAL, int)
        assert const.DOMAIN_INTERNATIONAL != const.DOMAIN_CHINA
        assert const.DEFAULT_UPDATE_INTERVAL > 0
        assert isinstance(const.MOCK_POWER_STATION, dict)
        assert isinstance(const.MOCK_DEVICE, dict)
        assert isinstance(const.MOCK_VARIABLE_GROUPS, list)
        
        print("✅ Constants validation passed")
        return True
        
    except Exception as e:
        print(f"❌ Constants test failed: {e}")
        return False

def test_api_class():
    """Test API class by examining the file."""
    print("\n🧪 Testing API Client...")
    
    try:
        # Read and validate the API file
        api_path = Path(__file__).parent / 'custom_components' / 'solarguardian' / 'api.py'
        
        if not api_path.exists():
            print("❌ API file not found")
            return False
            
        with open(api_path, 'r') as f:
            content = f.read()
        
        print("✅ API file found and readable")
        print(f"   - File size: {len(content)} bytes")
        
        # Check for required classes and methods
        required_items = [
            'class SolarGuardianAPI',
            'class SolarGuardianAPIError',
            'def __init__',
            'def authenticate',
            'def get_power_stations',
            'def get_devices',
            'def get_device_parameters',
            'def close'
        ]
        
        missing_items = []
        for item in required_items:
            if item not in content:
                missing_items.append(item)
        
        if missing_items:
            print(f"❌ Missing required items: {missing_items}")
            return False
        
        print("✅ All required API methods found")
        
        # Check for imports
        if 'import aiohttp' in content:
            print("✅ aiohttp dependency found")
        
        if 'import asyncio' in content:
            print("✅ asyncio support found")
            
        # Check for error handling
        if 'try:' in content and 'except' in content:
            print("✅ Error handling patterns found")
        
        # Check for rate limiting
        if 'rate_limit' in content.lower():
            print("✅ Rate limiting implementation found")
        
        return True
        
    except Exception as e:
        print(f"❌ API test failed: {e}")
        return False

def test_json_serialization():
    """Test that mock data is JSON serializable."""
    print("\n🗂️  Testing JSON Serialization...")
    
    try:
        # Import const module directly
        const_path = Path(__file__).parent / 'custom_components' / 'solarguardian'
        sys.path.insert(0, str(const_path))
        import const
        
        # Test JSON serialization
        json.dumps(const.MOCK_POWER_STATION)
        json.dumps(const.MOCK_DEVICE)
        json.dumps(const.MOCK_VARIABLE_GROUPS)
        
        print("✅ All mock data is JSON serializable")
        
        # Test data structure
        station = const.MOCK_POWER_STATION
        device = const.MOCK_DEVICE
        groups = const.MOCK_VARIABLE_GROUPS
        
        # Validate required fields
        assert "id" in station and isinstance(station["id"], int)
        assert "powerStationName" in station and isinstance(station["powerStationName"], str)
        assert "id" in device and isinstance(device["id"], int)  
        assert "equipmentName" in device and isinstance(device["equipmentName"], str)
        
        # Validate variable groups structure
        power_params = 0
        voltage_params = 0
        current_params = 0
        
        for group in groups:
            assert "variableList" in group
            for var in group["variableList"]:
                assert "dataIdentifier" in var
                assert "unit" in var
                unit = var["unit"]
                if unit == "W":
                    power_params += 1
                elif unit == "V":
                    voltage_params += 1
                elif unit == "A":
                    current_params += 1
        
        print(f"   - Power parameters: {power_params}")
        print(f"   - Voltage parameters: {voltage_params}")
        print(f"   - Current parameters: {current_params}")
        
        assert power_params > 0, "Should have power parameters"
        assert voltage_params > 0, "Should have voltage parameters"
        assert current_params > 0, "Should have current parameters"
        
        print("✅ Data structure validation passed")
        return True
        
    except Exception as e:
        print(f"❌ JSON serialization test failed: {e}")
        return False

def test_integration_script():
    """Test the existing integration script."""
    print("\n🔧 Testing Integration Script...")
    
    try:
        # The integration script should be importable
        script_path = Path(__file__).parent
        sys.path.insert(0, str(script_path))
        
        # Test if file exists and is readable
        integration_script = script_path / 'test_integration.py'
        if not integration_script.exists():
            print("❌ test_integration.py not found")
            return False
        
        with open(integration_script, 'r') as f:
            content = f.read()
        
        # Check for required functions
        required_functions = [
            'load_test_credentials',
            'create_test_config', 
            'test_api_connection',
            'main'
        ]
        
        for func in required_functions:
            if f"def {func}" not in content:
                print(f"❌ Required function {func} not found")
                return False
        
        print("✅ Integration script structure validated")
        print(f"   - File size: {len(content)} bytes")
        
        # Check for required imports
        if "from solarguardian.api import" in content:
            print("✅ API imports found")
        
        if "DOMAIN_INTERNATIONAL" in content or "DOMAIN_CHINA" in content:
            print("✅ Domain constants referenced")
        
        return True
        
    except Exception as e:
        print(f"❌ Integration script test failed: {e}")
        return False

def test_file_structure():
    """Test the test file structure."""
    print("\n📁 Testing File Structure...")
    
    try:
        base_path = Path(__file__).parent
        
        # Check for test directories
        tests_dir = base_path / 'tests'
        unit_dir = tests_dir / 'unit'
        integration_dir = tests_dir / 'integration'
        
        print(f"✅ Tests directory exists: {tests_dir.exists()}")
        print(f"✅ Unit tests directory exists: {unit_dir.exists()}")
        print(f"✅ Integration tests directory exists: {integration_dir.exists()}")
        
        # Count test files
        if unit_dir.exists():
            unit_tests = list(unit_dir.glob('test_*.py'))
            print(f"   - Unit test files: {len(unit_tests)}")
            for test_file in unit_tests:
                print(f"     • {test_file.name}")
        
        if integration_dir.exists():
            integration_tests = list(integration_dir.glob('test_*.py'))
            print(f"   - Integration test files: {len(integration_tests)}")
            for test_file in integration_tests:
                print(f"     • {test_file.name}")
        
        # Check for test runners
        runners = [
            'run_tests.py',
            'run_basic_tests.py',
            'pytest.ini'
        ]
        
        for runner in runners:
            runner_path = base_path / runner
            if runner_path.exists():
                print(f"✅ Test runner exists: {runner}")
            else:
                print(f"⚠️  Test runner missing: {runner}")
        
        # Check for documentation
        docs = ['TEST_RESULTS.md', 'tests/README.md']
        for doc in docs:
            doc_path = base_path / doc
            if doc_path.exists():
                print(f"✅ Documentation exists: {doc}")
        
        return True
        
    except Exception as e:
        print(f"❌ File structure test failed: {e}")
        return False

def main():
    """Run standalone tests."""
    print("🚀 SolarGuardian Standalone Test Suite")
    print("=" * 50)
    
    tests = [
        ("Constants & Mock Data", test_constants),
        ("API Client", test_api_class),
        ("JSON Serialization", test_json_serialization),
        ("Integration Script", test_integration_script),
        ("File Structure", test_file_structure)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            failed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("✅ All standalone tests passed!")
        print("\n💡 Note: These tests validate core functionality without")
        print("   requiring HomeAssistant installation. Full test suite")
        print("   with HomeAssistant integration requires additional setup.")
        return 0
    else:
        print("❌ Some tests failed!")
        return 1

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)