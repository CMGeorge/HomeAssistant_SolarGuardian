"""Unit tests for SolarGuardian sensors."""

import os

# Add custom components to path
import sys
import unittest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(current_dir, "../../custom_components"))

from solarguardian.const import (
    DEVICE_CLASS_CURRENT,
    DEVICE_CLASS_POWER,
    DEVICE_CLASS_VOLTAGE,
    DOMAIN,
    MOCK_DEVICE,
    MOCK_POWER_STATION,
    MOCK_VARIABLE_GROUPS,
    UNIT_AMPERE,
    UNIT_VOLT,
    UNIT_WATT,
)

# Mock homeassistant dependencies
try:
    from homeassistant.components.sensor import SensorEntity
    from homeassistant.const import STATE_UNAVAILABLE
    from homeassistant.helpers.entity import Entity
    from homeassistant.helpers.update_coordinator import CoordinatorEntity
except ImportError:
    # Create mock classes if homeassistant is not available
    class Entity:
        def __init__(self):
            self._attr_name = None
            self._attr_unique_id = None
            self._attr_device_info = None
            self._attr_available = True
            self._attr_state = None
            self._attr_native_value = None
            self._attr_native_unit_of_measurement = None
            self._attr_device_class = None
            self._attr_extra_state_attributes = {}

    class CoordinatorEntity(Entity):
        def __init__(self, coordinator):
            super().__init__()
            self.coordinator = coordinator

    class SensorEntity(Entity):
        pass

    STATE_UNAVAILABLE = "unavailable"

try:
    from solarguardian.sensor import SolarGuardianSensor, async_setup_entry
except ImportError:
    # If the sensor module imports fail, we'll skip these tests
    async_setup_entry = None
    SolarGuardianSensor = None


class TestSolarGuardianSensor(unittest.TestCase):
    """Test cases for SolarGuardian sensor entity."""

    def setUp(self):
        """Set up test fixtures."""
        if SolarGuardianSensor is None:
            self.skipTest("SolarGuardian sensor module not available")

        # Mock coordinator
        self.mock_coordinator = MagicMock()
        # Mock coordinator with proper data structure for sensor
        self.mock_coordinator.data = {
            "power_stations": {"status": 0, "data": {"list": [MOCK_POWER_STATION]}},
            "devices": {
                MOCK_POWER_STATION["id"]: {"status": 0, "data": {"list": [MOCK_DEVICE]}}
            },
            "device_data": {
                MOCK_DEVICE["id"]: {
                    "status": 0,
                    "data": {"variableGroupList": MOCK_VARIABLE_GROUPS},
                    "latest_data": {
                        "data": {
                            "list": [
                                {"dataIdentifier": "OutputPower", "value": "1500"},
                                {"dataIdentifier": "OutputVoltage", "value": "240.5"},
                                {"dataIdentifier": "OutputCurrent", "value": "6.25"},
                            ]
                        }
                    },
                }
            },
        }

        # Create sensor for OutputPower
        self.power_variable = MOCK_VARIABLE_GROUPS[0]["variableList"][0]  # OutputPower
        self.sensor_config = {
            "name": "Output Power",
            "unit": "W",
            "device_class": DEVICE_CLASS_POWER,
            "icon": "mdi:solar-power",
        }
        self.sensor = SolarGuardianSensor(
            coordinator=self.mock_coordinator,
            device=MOCK_DEVICE,
            variable=self.power_variable,
            sensor_config=self.sensor_config,
        )

    def test_sensor_initialization(self):
        """Test sensor initialization."""
        self.assertEqual(self.sensor.coordinator, self.mock_coordinator)
        self.assertIsNotNone(self.sensor._attr_unique_id)
        self.assertIn("OutputPower", self.sensor._attr_unique_id)
        self.assertEqual(self.sensor._attr_name, "Test Solar Inverter Output Power")
        self.assertEqual(self.sensor._attr_native_unit_of_measurement, "W")

    def test_sensor_unique_id(self):
        """Test sensor unique ID generation."""
        expected_id = f"{MOCK_DEVICE['id']}_OutputPower"
        self.assertEqual(self.sensor._attr_unique_id, expected_id)

    def test_sensor_device_info(self):
        """Test sensor device info."""
        device_info = self.sensor._attr_device_info
        self.assertIsNotNone(device_info)
        self.assertEqual(device_info["identifiers"], {(DOMAIN, str(MOCK_DEVICE["id"]))})
        self.assertEqual(device_info["name"], MOCK_DEVICE["equipmentName"])
        self.assertEqual(device_info["manufacturer"], "SolarGuardian")

    def test_sensor_device_class_power(self):
        """Test power sensor device class."""
        # OutputPower should have power device class
        self.assertEqual(self.sensor._attr_device_class, DEVICE_CLASS_POWER)

    def test_sensor_device_class_voltage(self):
        """Test voltage sensor device class."""
        voltage_variable = MOCK_VARIABLE_GROUPS[1]["variableList"][0]  # OutputVoltage
        voltage_config = {
            "name": "Output Voltage",
            "unit": "V",
            "device_class": DEVICE_CLASS_VOLTAGE,
            "icon": "mdi:flash",
        }
        voltage_sensor = SolarGuardianSensor(
            coordinator=self.mock_coordinator,
            device=MOCK_DEVICE,
            variable=voltage_variable,
            sensor_config=voltage_config,
        )
        self.assertEqual(voltage_sensor._attr_device_class, DEVICE_CLASS_VOLTAGE)

    def test_sensor_device_class_current(self):
        """Test current sensor device class."""
        current_variable = MOCK_VARIABLE_GROUPS[2]["variableList"][0]  # OutputCurrent
        current_config = {
            "name": "Output Current",
            "unit": "A",
            "device_class": DEVICE_CLASS_CURRENT,
            "icon": "mdi:current-dc",
        }
        current_sensor = SolarGuardianSensor(
            coordinator=self.mock_coordinator,
            device=MOCK_DEVICE,
            variable=current_variable,
            sensor_config=current_config,
        )
        self.assertEqual(current_sensor._attr_device_class, DEVICE_CLASS_CURRENT)

    def test_sensor_native_value_available(self):
        """Test sensor native value when data is available."""
        value = self.sensor.native_value
        self.assertEqual(value, 1500.0)

    def test_sensor_native_value_unavailable(self):
        """Test sensor native value when data is unavailable."""
        # Mock coordinator with no latest data
        self.mock_coordinator.data = {"device_data": {MOCK_DEVICE["id"]: {}}}

        value = self.sensor.native_value
        self.assertIsNone(value)

    def test_sensor_available_with_data(self):
        """Test sensor availability when data is present."""
        self.assertTrue(self.sensor.available)

    def test_sensor_unavailable_no_data(self):
        """Test sensor unavailability when no data is present."""
        # Mock coordinator with no data
        self.mock_coordinator.data = {}

        self.assertFalse(self.sensor.available)

    def test_sensor_unavailable_no_coordinator_data(self):
        """Test sensor unavailability when coordinator has no data."""
        self.mock_coordinator.data = None

        self.assertFalse(self.sensor.available)

    def test_sensor_extra_state_attributes(self):
        """Test sensor extra state attributes."""
        attributes = self.sensor.extra_state_attributes

        self.assertIsInstance(attributes, dict)
        self.assertIn("data_identifier", attributes)
        self.assertEqual(attributes["data_identifier"], "OutputPower")
        self.assertIn("device_id", attributes)
        self.assertEqual(attributes["device_id"], MOCK_DEVICE["id"])
        self.assertIn("station_name", attributes)
        self.assertEqual(
            attributes["station_name"], MOCK_POWER_STATION["powerStationName"]
        )

    def test_sensor_extra_attributes_with_timestamp(self):
        """Test sensor extra attributes include timestamp when available."""
        attributes = self.sensor.extra_state_attributes

        self.assertIn("last_updated", attributes)
        # The timestamp should be from our mock data
        self.assertIsNotNone(attributes["last_updated"])

    def test_sensor_name_generation(self):
        """Test sensor name generation for different variables."""
        # Test English name
        expected_name = (
            f"{MOCK_DEVICE['equipmentName']} {self.power_variable['variableNameE']}"
        )
        self.assertEqual(self.sensor._attr_name, expected_name)

    def test_sensor_name_fallback_chinese(self):
        """Test sensor name fallback to Chinese when English not available."""
        # Create variable with only Chinese name
        chinese_variable = {
            "dataIdentifier": "TestParam",
            "variableNameC": "测试参数",
            "unit": "W",
            "decimal": "0",
        }
        chinese_config = {"name": "测试参数", "unit": "W", "icon": "mdi:gauge"}

        chinese_sensor = SolarGuardianSensor(
            coordinator=self.mock_coordinator,
            device=MOCK_DEVICE,
            variable=chinese_variable,
            sensor_config=chinese_config,
        )

        expected_name = f"{MOCK_DEVICE['equipmentName']} 测试参数"
        self.assertEqual(chinese_sensor._attr_name, expected_name)

    def test_sensor_decimal_handling(self):
        """Test sensor handles decimal places correctly."""
        # Create variable with 2 decimal places
        decimal_variable = {
            "dataIdentifier": "TestDecimal",
            "variableNameE": "Test Decimal",
            "unit": "V",
            "decimal": "2",
        }
        decimal_config = {"name": "Test Decimal", "unit": "V", "icon": "mdi:gauge"}

        # Mock data with decimal value
        self.mock_coordinator.data["device_data"][MOCK_DEVICE["id"]]["latest_data"] = {
            "data": {"list": [{"dataIdentifier": "TestDecimal", "value": "123.456"}]}
        }

        decimal_sensor = SolarGuardianSensor(
            coordinator=self.mock_coordinator,
            device=MOCK_DEVICE,
            variable=decimal_variable,
            sensor_config=decimal_config,
        )

        # Should round to 2 decimal places
        self.assertEqual(decimal_sensor.native_value, 123.46)

    def test_sensor_zero_decimal(self):
        """Test sensor handles zero decimal places correctly."""
        value = self.sensor.native_value
        self.assertEqual(value, 1500.0)  # Should be integer value as float

    def test_sensor_invalid_value_handling(self):
        """Test sensor handles invalid values gracefully."""
        # Mock data with invalid value
        self.mock_coordinator.data["latest_data"][MOCK_DEVICE["id"]]["OutputPower"] = {
            "value": "invalid",
            "timestamp": datetime.now().isoformat(),
        }

        value = self.sensor.native_value
        self.assertIsNone(value)

    def test_sensor_string_value_conversion(self):
        """Test sensor converts string values to numbers."""
        # Mock data with string value
        self.mock_coordinator.data["latest_data"][MOCK_DEVICE["id"]]["OutputPower"] = {
            "value": "1500.75",
            "timestamp": datetime.now().isoformat(),
        }

        value = self.sensor.native_value
        self.assertEqual(value, 1500.0)  # Should round to 0 decimal places


class TestSensorSetup(unittest.IsolatedAsyncioTestCase):
    """Test cases for sensor setup function."""

    async def test_async_setup_entry_skip(self):
        """Test async_setup_entry function when import fails."""
        if async_setup_entry is None:
            self.skipTest("async_setup_entry function not available")

        # Mock homeassistant objects
        mock_hass = MagicMock()
        mock_entry = MagicMock()
        mock_async_add_entities = AsyncMock()

        # Mock coordinator with no data
        mock_coordinator = MagicMock()
        mock_coordinator.data = None
        mock_hass.data = {
            DOMAIN: {mock_entry.entry_id: {"coordinator": mock_coordinator}}
        }

        result = await async_setup_entry(mock_hass, mock_entry, mock_async_add_entities)

        # Should return True even with no data
        self.assertTrue(result)
        mock_async_add_entities.assert_called_once_with([])


class TestSensorConstants(unittest.TestCase):
    """Test cases for sensor-related constants."""

    def test_device_classes(self):
        """Test device class constants."""
        self.assertEqual(DEVICE_CLASS_POWER, "power")
        self.assertEqual(DEVICE_CLASS_VOLTAGE, "voltage")
        self.assertEqual(DEVICE_CLASS_CURRENT, "current")

    def test_units(self):
        """Test unit constants."""
        self.assertEqual(UNIT_WATT, "W")
        self.assertEqual(UNIT_VOLT, "V")
        self.assertEqual(UNIT_AMPERE, "A")

    def test_mock_data_structure(self):
        """Test mock data has correct structure."""
        self.assertIsInstance(MOCK_POWER_STATION, dict)
        self.assertIn("id", MOCK_POWER_STATION)
        self.assertIn("powerStationName", MOCK_POWER_STATION)

        self.assertIsInstance(MOCK_DEVICE, dict)
        self.assertIn("id", MOCK_DEVICE)
        self.assertIn("equipmentName", MOCK_DEVICE)

        self.assertIsInstance(MOCK_VARIABLE_GROUPS, list)
        self.assertGreater(len(MOCK_VARIABLE_GROUPS), 0)

        for group in MOCK_VARIABLE_GROUPS:
            self.assertIn("variableList", group)
            self.assertIsInstance(group["variableList"], list)

            for variable in group["variableList"]:
                self.assertIn("dataIdentifier", variable)
                self.assertIn("unit", variable)


if __name__ == "__main__":
    unittest.main()
