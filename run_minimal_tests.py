#!/usr/bin/env python3
"""Minimal test runner that works without HomeAssistant dependencies."""
import sys
import unittest
import os
from pathlib import Path

def run_simple_api_test():
    """Run a simple API test that doesn't depend on HomeAssistant."""
    print("🧪 Testing SolarGuardian API Client...")
    
    # Add custom components to path
    current_dir = Path(__file__).parent
    sys.path.insert(0, str(current_dir / 'custom_components'))
    
    try:
        # Try to import and test basic API functionality
        from solarguardian.api import SolarGuardianAPI, SolarGuardianAPIError
        
        print("✅ API classes imported successfully")
        
        # Test basic initialization
        api = SolarGuardianAPI(
            domain="test.domain.com",
            app_key="test_key", 
            app_secret="test_secret"
        )
        
        print("✅ API client initialized successfully")
        print(f"   - Domain: {api.domain}")
        print(f"   - Base URL: {api._base_url}")
        print(f"   - App Key: {api.app_key[:8]}...")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def run_constants_test():
    """Test constants without HomeAssistant dependencies."""
    print("\n📊 Testing Constants...")
    
    try:
        from solarguardian.const import (
            DOMAIN, DOMAIN_CHINA, DOMAIN_INTERNATIONAL,
            DEFAULT_UPDATE_INTERVAL, DEFAULT_TIMEOUT,
            ENDPOINT_AUTH, ENDPOINT_POWER_STATIONS
        )
        
        print("✅ Constants imported successfully")
        print(f"   - Domain: {DOMAIN}")
        print(f"   - International API: {DOMAIN_INTERNATIONAL}")
        print(f"   - China API: {DOMAIN_CHINA}")
        print(f"   - Update interval: {DEFAULT_UPDATE_INTERVAL}s")
        print(f"   - Timeout: {DEFAULT_TIMEOUT}s")
        
        # Basic validation
        assert isinstance(DOMAIN, str)
        assert isinstance(DEFAULT_UPDATE_INTERVAL, int)
        assert DOMAIN_INTERNATIONAL != DOMAIN_CHINA
        assert DEFAULT_UPDATE_INTERVAL > 0
        
        print("✅ Constants validation passed")
        return True
        
    except ImportError as e:
        print(f"❌ Constants import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Constants test failed: {e}")
        return False

def run_mock_data_test():
    """Test mock data structure."""
    print("\n🗂️  Testing Mock Data...")
    
    try:
        from solarguardian.const import (
            MOCK_POWER_STATION, MOCK_DEVICE, MOCK_VARIABLE_GROUPS
        )
        
        print("✅ Mock data imported successfully")
        
        # Test power station structure
        assert isinstance(MOCK_POWER_STATION, dict)
        assert "id" in MOCK_POWER_STATION
        assert "powerStationName" in MOCK_POWER_STATION
        print(f"   - Mock station: {MOCK_POWER_STATION['powerStationName']}")
        
        # Test device structure
        assert isinstance(MOCK_DEVICE, dict)
        assert "id" in MOCK_DEVICE
        assert "equipmentName" in MOCK_DEVICE
        print(f"   - Mock device: {MOCK_DEVICE['equipmentName']}")
        
        # Test variable groups
        assert isinstance(MOCK_VARIABLE_GROUPS, list)
        assert len(MOCK_VARIABLE_GROUPS) > 0
        
        param_count = 0
        for group in MOCK_VARIABLE_GROUPS:
            assert "variableList" in group
            param_count += len(group["variableList"])
        
        print(f"   - Mock parameters: {param_count} total")
        
        print("✅ Mock data validation passed")
        return True
        
    except ImportError as e:
        print(f"❌ Mock data import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Mock data test failed: {e}")
        return False

def run_integration_script_test():
    """Test the existing integration script."""
    print("\n🔧 Testing Integration Script...")
    
    try:
        # Test importing the integration script functions
        from test_integration import load_test_credentials, create_test_config
        
        print("✅ Integration script functions imported")
        
        # Test credential loading (should return None without credentials)
        credentials = load_test_credentials()
        if credentials is None:
            print("✅ Credential loading works (no credentials found)")
        else:
            print(f"✅ Found credentials for domain: {credentials[0]}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Integration script import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Integration script test failed: {e}")
        return False

def main():
    """Run minimal tests."""
    print("🚀 SolarGuardian Minimal Test Suite")
    print("=" * 40)
    
    tests = [
        ("API Client", run_simple_api_test),
        ("Constants", run_constants_test), 
        ("Mock Data", run_mock_data_test),
        ("Integration Script", run_integration_script_test)
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
    
    print("\n" + "=" * 40)
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("✅ All minimal tests passed!")
        return 0
    else:
        print("❌ Some tests failed!")
        return 1

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)