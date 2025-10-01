#!/usr/bin/env python3
"""Basic test runner for core functionality."""
import sys
import unittest
import os
from pathlib import Path

# Add custom components to path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir / 'custom_components'))

def run_basic_api_tests():
    """Run basic API tests that should work."""
    print("🧪 Running Basic API Tests...")
    loader = unittest.TestLoader()
    
    # Load specific test classes that should work
    from tests.unit.test_api import TestSolarGuardianAPI
    from tests.unit.test_constants import TestDomainConstants, TestConfigurationConstants
    from tests.unit.test_mock_data import TestMockDataStructure
    
    suite = unittest.TestSuite()
    
    # Add API tests
    suite.addTest(loader.loadTestsFromTestCase(TestSolarGuardianAPI))
    
    # Add constants tests  
    suite.addTest(loader.loadTestsFromTestCase(TestDomainConstants))
    suite.addTest(loader.loadTestsFromTestCase(TestConfigurationConstants))
    
    # Add mock data tests
    suite.addTest(loader.loadTestsFromTestCase(TestMockDataStructure))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()

def main():
    """Main test runner."""
    success = run_basic_api_tests()
    
    if success:
        print("✅ Basic tests passed!")
        sys.exit(0)
    else:
        print("❌ Some basic tests failed!")
        sys.exit(1)

if __name__ == '__main__':
    main()