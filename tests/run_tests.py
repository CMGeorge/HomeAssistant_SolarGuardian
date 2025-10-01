#!/usr/bin/env python3
"""Test runner for SolarGuardian integration tests."""
import sys
import unittest
import os
from pathlib import Path

# Add custom components to path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir / 'custom_components'))

def run_unit_tests():
    """Run unit tests."""
    print("🧪 Running Unit Tests...")
    loader = unittest.TestLoader()
    start_dir = 'tests/unit'
    suite = loader.discover(start_dir, pattern='test_*.py')
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()

def run_integration_tests():
    """Run integration tests."""
    print("🔗 Running Integration Tests...")
    loader = unittest.TestLoader()
    start_dir = 'tests/integration'
    suite = loader.discover(start_dir, pattern='test_*.py')
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()

def run_all_tests():
    """Run all tests."""
    print("🚀 Running All Tests...")
    loader = unittest.TestLoader()
    start_dir = 'tests'
    suite = loader.discover(start_dir, pattern='test_*.py')
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()

def main():
    """Main test runner."""
    if len(sys.argv) > 1:
        test_type = sys.argv[1].lower()
        if test_type == 'unit':
            success = run_unit_tests()
        elif test_type == 'integration':
            success = run_integration_tests()
        elif test_type == 'all':
            success = run_all_tests()
        else:
            print(f"❌ Unknown test type: {test_type}")
            print("Usage: python run_tests.py [unit|integration|all]")
            sys.exit(1)
    else:
        success = run_all_tests()
    
    if success:
        print("✅ All tests passed!")
        sys.exit(0)
    else:
        print("❌ Some tests failed!")
        sys.exit(1)

if __name__ == '__main__':
    main()