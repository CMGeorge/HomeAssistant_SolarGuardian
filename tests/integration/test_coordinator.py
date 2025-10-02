"""Integration tests for SolarGuardian data coordinator."""

import os

# Add custom components to path
import sys
import unittest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(current_dir, "../../custom_components"))

from solarguardian.api import SolarGuardianAPI, SolarGuardianAPIError
from solarguardian.const import MOCK_DEVICE, MOCK_POWER_STATION, MOCK_VARIABLE_GROUPS

# Mock homeassistant dependencies
try:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.update_coordinator import UpdateFailed
except ImportError:
    # Create mock classes if homeassistant is not available
    class HomeAssistant:
        pass

    class UpdateFailed(Exception):
        pass


try:
    from solarguardian import SolarGuardianDataUpdateCoordinator
except ImportError:
    SolarGuardianDataUpdateCoordinator = None


class TestSolarGuardianDataUpdateCoordinator(unittest.IsolatedAsyncioTestCase):
    """Test cases for SolarGuardian data update coordinator."""

    def setUp(self):
        """Set up test fixtures."""
        if SolarGuardianDataUpdateCoordinator is None:
            self.skipTest("SolarGuardianDataUpdateCoordinator not available")

        self.hass = MagicMock(spec=HomeAssistant)
        self.mock_api = AsyncMock(spec=SolarGuardianAPI)
        self.coordinator = SolarGuardianDataUpdateCoordinator(
            hass=self.hass, api=self.mock_api, update_interval=30
        )

    async def test_coordinator_initialization(self):
        """Test coordinator initialization."""
        self.assertEqual(self.coordinator.api, self.mock_api)
        self.assertEqual(self.coordinator.update_interval.total_seconds(), 30)
        self.assertFalse(self.coordinator.test_mode)

    async def test_coordinator_test_mode(self):
        """Test coordinator in test mode."""
        test_coordinator = SolarGuardianDataUpdateCoordinator(
            hass=self.hass, api=self.mock_api, update_interval=30, test_mode=True
        )

        self.assertTrue(test_coordinator.test_mode)

    async def test_update_data_success(self):
        """Test successful data update."""
        # Mock API responses
        self.mock_api.authenticate.return_value = True
        self.mock_api.get_power_stations.return_value = {
            "status": 0,
            "data": {"list": [MOCK_POWER_STATION], "total": 1},
        }
        self.mock_api.get_devices.return_value = {
            "status": 0,
            "data": {"list": [MOCK_DEVICE], "total": 1},
        }
        self.mock_api.get_device_parameters.return_value = {
            "status": 0,
            "data": {"variableGroupList": MOCK_VARIABLE_GROUPS},
        }
        self.mock_api.get_latest_data.return_value = {
            "status": 0,
            "data": {
                "list": [
                    {"dataIdentifier": "OutputPower", "value": "1500"},
                    {"dataIdentifier": "OutputVoltage", "value": "240.5"},
                ]
            },
        }

        # Trigger update
        data = await self.coordinator._async_update_data()

        # Verify data structure
        self.assertIsInstance(data, dict)
        self.assertIn("power_stations", data)
        self.assertIn("devices", data)
        self.assertIn("device_data", data)
        self.assertIn("latest_data", data)
        self.assertIn("status", data)
        self.assertIn("last_update", data)

        # Verify API calls were made
        self.mock_api.authenticate.assert_called_once()
        self.mock_api.get_power_stations.assert_called_once()
        self.mock_api.get_devices.assert_called()
        self.mock_api.get_device_parameters.assert_called()

    async def test_update_data_authentication_failure(self):
        """Test data update with authentication failure."""
        self.mock_api.authenticate.side_effect = SolarGuardianAPIError("Auth failed")

        with self.assertRaises(UpdateFailed):
            await self.coordinator._async_update_data()

    async def test_update_data_api_error(self):
        """Test data update with API error."""
        self.mock_api.authenticate.return_value = True
        self.mock_api.get_power_stations.side_effect = SolarGuardianAPIError(
            "API Error"
        )

        with self.assertRaises(UpdateFailed):
            await self.coordinator._async_update_data()

    async def test_update_data_network_error(self):
        """Test data update with network error."""
        self.mock_api.authenticate.return_value = True
        self.mock_api.get_power_stations.side_effect = Exception("Network error")

        with self.assertRaises(UpdateFailed):
            await self.coordinator._async_update_data()

    async def test_update_data_mock_mode_activation(self):
        """Test mock mode activation after failures."""
        # Mock consecutive failures
        self.mock_api.authenticate.side_effect = [
            SolarGuardianAPIError("Fail 1"),
            SolarGuardianAPIError("Fail 2"),
            SolarGuardianAPIError("Fail 3"),
        ]

        # First three failures should raise UpdateFailed
        for _ in range(3):
            with self.assertRaises(UpdateFailed):
                await self.coordinator._async_update_data()

        # Fourth call might activate mock mode (depending on implementation)
        # This test would need to be adapted based on actual mock mode logic

    async def test_update_data_empty_stations(self):
        """Test data update with no power stations."""
        self.mock_api.authenticate.return_value = True
        self.mock_api.get_power_stations.return_value = {
            "status": 0,
            "data": {"list": [], "total": 0},
        }

        data = await self.coordinator._async_update_data()

        self.assertIn("power_stations", data)
        self.assertEqual(len(data["power_stations"]["data"]["list"]), 0)

    async def test_update_data_device_processing(self):
        """Test device data processing."""
        self.mock_api.authenticate.return_value = True
        self.mock_api.get_power_stations.return_value = {
            "status": 0,
            "data": {"list": [MOCK_POWER_STATION], "total": 1},
        }
        self.mock_api.get_devices.return_value = {
            "status": 0,
            "data": {"list": [MOCK_DEVICE], "total": 1},
        }
        self.mock_api.get_device_parameters.return_value = {
            "status": 0,
            "data": {"variableGroupList": MOCK_VARIABLE_GROUPS},
        }

        data = await self.coordinator._async_update_data()

        # Verify device data structure
        station_id = MOCK_POWER_STATION["id"]
        device_id = MOCK_DEVICE["id"]

        self.assertIn(station_id, data["devices"])
        self.assertIn(device_id, data["device_data"])

        device_data = data["device_data"][device_id]["data"]
        self.assertIn("variableGroupList", device_data)
        self.assertEqual(
            len(device_data["variableGroupList"]), len(MOCK_VARIABLE_GROUPS)
        )

    async def test_update_data_latest_data_processing(self):
        """Test latest data processing."""
        self.mock_api.authenticate.return_value = True
        self.mock_api.get_power_stations.return_value = {
            "status": 0,
            "data": {"list": [MOCK_POWER_STATION], "total": 1},
        }
        self.mock_api.get_devices.return_value = {
            "status": 0,
            "data": {"list": [MOCK_DEVICE], "total": 1},
        }
        self.mock_api.get_device_parameters.return_value = {
            "status": 0,
            "data": {"variableGroupList": MOCK_VARIABLE_GROUPS},
        }

        # Mock latest data response
        self.mock_api.get_latest_data.return_value = {
            "status": 0,
            "data": {
                "list": [
                    {"dataIdentifier": "OutputPower", "value": "1500"},
                    {"dataIdentifier": "OutputVoltage", "value": "240.5"},
                    {"dataIdentifier": "OutputCurrent", "value": "6.25"},
                ]
            },
        }

        data = await self.coordinator._async_update_data()

        # Verify latest data structure
        device_id = MOCK_DEVICE["id"]
        self.assertIn(device_id, data["latest_data"])

        latest_data = data["latest_data"][device_id]
        self.assertIn("OutputPower", latest_data)
        self.assertIn("OutputVoltage", latest_data)
        self.assertIn("OutputCurrent", latest_data)

        # Verify data values
        self.assertEqual(latest_data["OutputPower"]["value"], "1500")
        self.assertEqual(latest_data["OutputVoltage"]["value"], "240.5")

    async def test_update_data_partial_failure(self):
        """Test handling of partial API failures."""
        self.mock_api.authenticate.return_value = True
        self.mock_api.get_power_stations.return_value = {
            "status": 0,
            "data": {"list": [MOCK_POWER_STATION], "total": 1},
        }
        self.mock_api.get_devices.return_value = {
            "status": 0,
            "data": {"list": [MOCK_DEVICE], "total": 1},
        }
        self.mock_api.get_device_parameters.return_value = {
            "status": 0,
            "data": {"variableGroupList": MOCK_VARIABLE_GROUPS},
        }

        # Latest data fails
        self.mock_api.get_latest_data.side_effect = SolarGuardianAPIError(
            "Latest data failed"
        )

        data = await self.coordinator._async_update_data()

        # Should still have basic data even if latest data fails
        self.assertIn("power_stations", data)
        self.assertIn("devices", data)
        self.assertIn("device_data", data)

        # Latest data might be empty or have error information
        self.assertIn("latest_data", data)

    async def test_coordinator_data_freshness(self):
        """Test data freshness tracking."""
        self.mock_api.authenticate.return_value = True
        self.mock_api.get_power_stations.return_value = {
            "status": 0,
            "data": {"list": [], "total": 0},
        }

        before_update = datetime.now()
        data = await self.coordinator._async_update_data()
        after_update = datetime.now()

        # Verify timestamp is recent
        self.assertIn("last_update", data)
        update_time = datetime.fromisoformat(data["last_update"])
        self.assertGreaterEqual(update_time, before_update)
        self.assertLessEqual(update_time, after_update)

    async def test_coordinator_error_tracking(self):
        """Test error tracking in update summary."""
        self.mock_api.authenticate.return_value = True
        self.mock_api.get_power_stations.return_value = {
            "status": 0,
            "data": {"list": [], "total": 0},
        }

        data = await self.coordinator._async_update_data()

        self.assertIn("update_summary", data)
        summary = data["update_summary"]
        self.assertIn("errors", summary)
        self.assertIsInstance(summary["errors"], list)

    async def test_coordinator_statistics(self):
        """Test statistics in update summary."""
        self.mock_api.authenticate.return_value = True
        self.mock_api.get_power_stations.return_value = {
            "status": 0,
            "data": {"list": [MOCK_POWER_STATION], "total": 1},
        }
        self.mock_api.get_devices.return_value = {
            "status": 0,
            "data": {"list": [MOCK_DEVICE], "total": 1},
        }

        data = await self.coordinator._async_update_data()

        self.assertIn("update_summary", data)
        summary = data["update_summary"]
        self.assertIn("stations", summary)
        self.assertIn("devices", summary)
        self.assertEqual(summary["stations"], 1)
        self.assertEqual(summary["devices"], 1)


class TestCoordinatorMockMode(unittest.TestCase):
    """Test cases for coordinator mock mode functionality."""

    def setUp(self):
        """Set up test fixtures."""
        if SolarGuardianDataUpdateCoordinator is None:
            self.skipTest("SolarGuardianDataUpdateCoordinator not available")

        self.hass = MagicMock(spec=HomeAssistant)
        self.mock_api = AsyncMock(spec=SolarGuardianAPI)
        self.coordinator = SolarGuardianDataUpdateCoordinator(
            hass=self.hass, api=self.mock_api
        )

    def test_create_mock_data_structure(self):
        """Test mock data creation."""
        mock_data = self.coordinator._create_mock_data()

        self.assertIsInstance(mock_data, dict)
        self.assertIn("power_stations", mock_data)
        self.assertIn("devices", mock_data)
        self.assertIn("device_data", mock_data)
        self.assertIn("status", mock_data)
        self.assertEqual(mock_data["status"], "mock_mode")

    def test_mock_data_stations(self):
        """Test mock data power stations."""
        mock_data = self.coordinator._create_mock_data()

        stations = mock_data["power_stations"]["data"]["list"]
        self.assertEqual(len(stations), 1)
        self.assertEqual(stations[0]["id"], MOCK_POWER_STATION["id"])
        self.assertEqual(
            stations[0]["powerStationName"], MOCK_POWER_STATION["powerStationName"]
        )

    def test_mock_data_devices(self):
        """Test mock data devices."""
        mock_data = self.coordinator._create_mock_data()

        station_id = MOCK_POWER_STATION["id"]
        self.assertIn(station_id, mock_data["devices"])

        devices = mock_data["devices"][station_id]["data"]["list"]
        self.assertEqual(len(devices), 1)
        self.assertEqual(devices[0]["id"], MOCK_DEVICE["id"])

    def test_mock_data_device_parameters(self):
        """Test mock data device parameters."""
        mock_data = self.coordinator._create_mock_data()

        device_id = MOCK_DEVICE["id"]
        self.assertIn(device_id, mock_data["device_data"])

        variable_groups = mock_data["device_data"][device_id]["data"][
            "variableGroupList"
        ]
        self.assertEqual(len(variable_groups), len(MOCK_VARIABLE_GROUPS))

        # Verify structure matches expected format
        for i, group in enumerate(variable_groups):
            self.assertEqual(
                group["variableGroupNameE"],
                MOCK_VARIABLE_GROUPS[i]["variableGroupNameE"],
            )
            self.assertEqual(
                len(group["variableList"]), len(MOCK_VARIABLE_GROUPS[i]["variableList"])
            )

    def test_mock_data_summary(self):
        """Test mock data update summary."""
        mock_data = self.coordinator._create_mock_data()

        self.assertIn("update_summary", mock_data)
        summary = mock_data["update_summary"]

        self.assertEqual(summary["stations"], 1)
        self.assertEqual(summary["devices"], 1)
        self.assertGreater(summary["sensors"], 0)
        self.assertIn("errors", summary)
        self.assertIn("Using mock data", summary["errors"][0])


if __name__ == "__main__":
    unittest.main()
