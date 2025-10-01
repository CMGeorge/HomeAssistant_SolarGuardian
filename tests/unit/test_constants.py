"""Unit tests for SolarGuardian constants."""
import unittest
import re

# Add custom components to path
import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(current_dir, '../../custom_components'))

from solarguardian.const import (
    DOMAIN,
    CONF_APP_KEY,
    CONF_APP_SECRET,
    CONF_DOMAIN,
    CONF_UPDATE_INTERVAL,
    CONF_TEST_MODE,
    DEFAULT_UPDATE_INTERVAL,
    DEFAULT_TIMEOUT,
    DOMAIN_CHINA,
    DOMAIN_INTERNATIONAL,
    DEVICE_CLASS_POWER,
    DEVICE_CLASS_VOLTAGE,
    DEVICE_CLASS_CURRENT,
    DEVICE_CLASS_ENERGY,
    DEVICE_CLASS_TEMPERATURE,
    DEVICE_CLASS_BATTERY,
    UNIT_WATT,
    UNIT_VOLT,
    UNIT_AMPERE,
    UNIT_KWH,
    UNIT_CELSIUS,
    UNIT_PERCENT,
    ENDPOINT_AUTH,
    ENDPOINT_POWER_STATIONS,
    ENDPOINT_DEVICES,
    ENDPOINT_DEVICE_PARAMETERS,
    ENDPOINT_DEVICE_HISTORY,
    ENDPOINT_LATEST_DATA,
    LATEST_DATA_PORT,
    RATE_LIMIT_AUTH,
    RATE_LIMIT_DATA
)


class TestDomainConstants(unittest.TestCase):
    """Test cases for domain-related constants."""

    def test_domain_name(self):
        """Test main domain constant."""
        self.assertEqual(DOMAIN, "solarguardian")
        self.assertIsInstance(DOMAIN, str)
        self.assertGreater(len(DOMAIN), 0)
        
        # Domain should be lowercase and contain no spaces
        self.assertEqual(DOMAIN, DOMAIN.lower())
        self.assertNotIn(" ", DOMAIN)

    def test_api_domains(self):
        """Test API domain constants."""
        domains = [DOMAIN_CHINA, DOMAIN_INTERNATIONAL]
        
        for domain in domains:
            self.assertIsInstance(domain, str)
            self.assertGreater(len(domain), 0)
            
            # Should look like a valid hostname
            self.assertIn(".", domain)
            self.assertNotIn(" ", domain)
            self.assertNotIn("http", domain)  # Should not include protocol
            
            # Should be valid domain format
            domain_pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*$'
            self.assertIsNotNone(re.match(domain_pattern, domain))

    def test_domain_differences(self):
        """Test that different domains are actually different."""
        self.assertNotEqual(DOMAIN_CHINA, DOMAIN_INTERNATIONAL)


class TestConfigurationConstants(unittest.TestCase):
    """Test cases for configuration constants."""

    def test_config_keys(self):
        """Test configuration key constants."""
        config_keys = [
            CONF_APP_KEY,
            CONF_APP_SECRET,
            CONF_DOMAIN,
            CONF_UPDATE_INTERVAL,
            CONF_TEST_MODE
        ]
        
        for key in config_keys:
            self.assertIsInstance(key, str)
            self.assertGreater(len(key), 0)
            self.assertNotIn(" ", key)  # Should use underscores, not spaces
        
        # Check specific expected values
        self.assertEqual(CONF_APP_KEY, "app_key")
        self.assertEqual(CONF_APP_SECRET, "app_secret")
        self.assertEqual(CONF_DOMAIN, "domain")
        self.assertEqual(CONF_UPDATE_INTERVAL, "update_interval")

    def test_config_keys_uniqueness(self):
        """Test that all config keys are unique."""
        config_keys = [
            CONF_APP_KEY,
            CONF_APP_SECRET,
            CONF_DOMAIN,
            CONF_UPDATE_INTERVAL,
            CONF_TEST_MODE
        ]
        
        self.assertEqual(len(config_keys), len(set(config_keys)))


class TestDefaultValues(unittest.TestCase):
    """Test cases for default value constants."""

    def test_default_update_interval(self):
        """Test default update interval."""
        self.assertIsInstance(DEFAULT_UPDATE_INTERVAL, int)
        self.assertGreater(DEFAULT_UPDATE_INTERVAL, 0)
        self.assertLessEqual(DEFAULT_UPDATE_INTERVAL, 300)  # Reasonable upper limit
        self.assertGreaterEqual(DEFAULT_UPDATE_INTERVAL, 10)  # Reasonable lower limit

    def test_default_timeout(self):
        """Test default timeout."""
        self.assertIsInstance(DEFAULT_TIMEOUT, int)
        self.assertGreater(DEFAULT_TIMEOUT, 0)
        self.assertLessEqual(DEFAULT_TIMEOUT, 120)  # Reasonable upper limit
        self.assertGreaterEqual(DEFAULT_TIMEOUT, 5)  # Reasonable lower limit

    def test_default_values_relationship(self):
        """Test relationship between default values."""
        # Timeout should be less than or equal to update interval to avoid overlapping requests
        self.assertLessEqual(DEFAULT_TIMEOUT, DEFAULT_UPDATE_INTERVAL)


class TestDeviceClassConstants(unittest.TestCase):
    """Test cases for device class constants."""

    def test_device_classes(self):
        """Test device class constants."""
        device_classes = [
            DEVICE_CLASS_POWER,
            DEVICE_CLASS_VOLTAGE,
            DEVICE_CLASS_CURRENT,
            DEVICE_CLASS_ENERGY,
            DEVICE_CLASS_TEMPERATURE,
            DEVICE_CLASS_BATTERY
        ]
        
        for device_class in device_classes:
            self.assertIsInstance(device_class, str)
            self.assertGreater(len(device_class), 0)
            self.assertNotIn(" ", device_class)
        
        # Check specific expected values
        self.assertEqual(DEVICE_CLASS_POWER, "power")
        self.assertEqual(DEVICE_CLASS_VOLTAGE, "voltage")
        self.assertEqual(DEVICE_CLASS_CURRENT, "current")

    def test_device_classes_uniqueness(self):
        """Test that all device classes are unique."""
        device_classes = [
            DEVICE_CLASS_POWER,
            DEVICE_CLASS_VOLTAGE,
            DEVICE_CLASS_CURRENT,
            DEVICE_CLASS_ENERGY,
            DEVICE_CLASS_TEMPERATURE,
            DEVICE_CLASS_BATTERY
        ]
        
        self.assertEqual(len(device_classes), len(set(device_classes)))


class TestUnitConstants(unittest.TestCase):
    """Test cases for unit constants."""

    def test_units(self):
        """Test unit constants."""
        units = [
            UNIT_WATT,
            UNIT_VOLT,
            UNIT_AMPERE,
            UNIT_KWH,
            UNIT_CELSIUS,
            UNIT_PERCENT
        ]
        
        for unit in units:
            self.assertIsInstance(unit, str)
            self.assertGreater(len(unit), 0)
        
        # Check specific expected values
        self.assertEqual(UNIT_WATT, "W")
        self.assertEqual(UNIT_VOLT, "V")
        self.assertEqual(UNIT_AMPERE, "A")
        self.assertEqual(UNIT_KWH, "kWh")
        self.assertEqual(UNIT_CELSIUS, "°C")
        self.assertEqual(UNIT_PERCENT, "%")

    def test_unit_format(self):
        """Test unit format correctness."""
        # Temperature unit should have degree symbol
        self.assertIn("°", UNIT_CELSIUS)
        
        # Percent should be single character
        self.assertEqual(len(UNIT_PERCENT), 1)
        
        # Basic electrical units should be single letters
        basic_units = [UNIT_WATT, UNIT_VOLT, UNIT_AMPERE]
        for unit in basic_units:
            self.assertEqual(len(unit), 1)
            self.assertTrue(unit.isupper())


class TestEndpointConstants(unittest.TestCase):
    """Test cases for API endpoint constants."""

    def test_endpoints(self):
        """Test API endpoint constants."""
        endpoints = [
            ENDPOINT_AUTH,
            ENDPOINT_POWER_STATIONS,
            ENDPOINT_DEVICES,
            ENDPOINT_DEVICE_PARAMETERS,
            ENDPOINT_DEVICE_HISTORY,
            ENDPOINT_LATEST_DATA
        ]
        
        for endpoint in endpoints:
            self.assertIsInstance(endpoint, str)
            self.assertGreater(len(endpoint), 0)
            
            # Should start with forward slash
            self.assertTrue(endpoint.startswith("/"))
            
            # Should not contain spaces
            self.assertNotIn(" ", endpoint)

    def test_endpoint_paths(self):
        """Test endpoint path structure."""
        # Most endpoints should be under /epCloud/
        epcloud_endpoints = [
            ENDPOINT_AUTH,
            ENDPOINT_POWER_STATIONS,
            ENDPOINT_DEVICES,
            ENDPOINT_DEVICE_PARAMETERS,
            ENDPOINT_DEVICE_HISTORY
        ]
        
        for endpoint in epcloud_endpoints:
            self.assertIn("/epCloud/", endpoint)

    def test_latest_data_port(self):
        """Test latest data port constant."""
        self.assertIsInstance(LATEST_DATA_PORT, int)
        self.assertGreater(LATEST_DATA_PORT, 1024)  # Should be non-privileged port
        self.assertLess(LATEST_DATA_PORT, 65536)  # Valid port range


class TestRateLimitingConstants(unittest.TestCase):
    """Test cases for rate limiting constants."""

    def test_rate_limits(self):
        """Test rate limiting constants."""
        rate_limits = [RATE_LIMIT_AUTH, RATE_LIMIT_DATA]
        
        for rate_limit in rate_limits:
            self.assertIsInstance(rate_limit, int)
            self.assertGreater(rate_limit, 0)
            self.assertLess(rate_limit, 1000)  # Reasonable upper limit

    def test_rate_limit_relationship(self):
        """Test relationship between rate limits."""
        # Auth rate limit should generally be lower than data rate limit
        # as authentication is less frequent
        self.assertLessEqual(RATE_LIMIT_AUTH, RATE_LIMIT_DATA)


class TestConstantTypeConsistency(unittest.TestCase):
    """Test cases for type consistency across constants."""

    def test_string_constants(self):
        """Test all string constants are actually strings."""
        string_constants = [
            DOMAIN,
            CONF_APP_KEY,
            CONF_APP_SECRET,
            CONF_DOMAIN,
            CONF_UPDATE_INTERVAL,
            CONF_TEST_MODE,
            DOMAIN_CHINA,
            DOMAIN_INTERNATIONAL,
            DEVICE_CLASS_POWER,
            DEVICE_CLASS_VOLTAGE,
            DEVICE_CLASS_CURRENT,
            UNIT_WATT,
            UNIT_VOLT,
            UNIT_AMPERE,
            ENDPOINT_AUTH,
            ENDPOINT_POWER_STATIONS
        ]
        
        for constant in string_constants:
            self.assertIsInstance(constant, str)

    def test_integer_constants(self):
        """Test all integer constants are actually integers."""
        integer_constants = [
            DEFAULT_UPDATE_INTERVAL,
            DEFAULT_TIMEOUT,
            LATEST_DATA_PORT,
            RATE_LIMIT_AUTH,
            RATE_LIMIT_DATA
        ]
        
        for constant in integer_constants:
            self.assertIsInstance(constant, int)

    def test_no_none_constants(self):
        """Test that no constants are None."""
        all_constants = [
            DOMAIN,
            CONF_APP_KEY,
            DEFAULT_UPDATE_INTERVAL,
            DOMAIN_CHINA,
            DEVICE_CLASS_POWER,
            UNIT_WATT,
            ENDPOINT_AUTH,
            RATE_LIMIT_AUTH
        ]
        
        for constant in all_constants:
            self.assertIsNotNone(constant)


if __name__ == '__main__':
    unittest.main()