"""Unit tests for SolarGuardian API client."""

import json
import os

# Add custom components to path
import sys
import unittest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, patch

import aiohttp

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(current_dir, "../../custom_components"))

from solarguardian.api import SolarGuardianAPI, SolarGuardianAPIError
from solarguardian.const import DOMAIN_INTERNATIONAL, ENDPOINT_AUTH


class TestSolarGuardianAPI(unittest.IsolatedAsyncioTestCase):
    """Test cases for SolarGuardian API client."""

    def setUp(self):
        """Set up test fixtures."""
        self.domain = DOMAIN_INTERNATIONAL
        self.app_key = "test_app_key_12345678"
        self.app_secret = "test_app_secret_abcdefgh"
        self.api = SolarGuardianAPI(self.domain, self.app_key, self.app_secret)

    async def asyncTearDown(self):
        """Clean up after each test."""
        if self.api._session:
            await self.api.close()

    def test_init(self):
        """Test API client initialization."""
        self.assertEqual(self.api.domain, self.domain)
        self.assertEqual(self.api.app_key, self.app_key)
        self.assertEqual(self.api.app_secret, self.app_secret)
        self.assertEqual(self.api._base_url, f"https://{self.domain}")
        self.assertIsNone(self.api._session)
        self.assertIsNone(self.api._token)
        self.assertIsNone(self.api._token_expires)

    @patch("aiohttp.ClientSession.post")
    async def test_authenticate_success(self, mock_post):
        """Test successful authentication."""
        # Mock successful auth response
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.text.return_value = json.dumps(
            {
                "status": 0,
                "info": "success",
                "data": {"X-Access-Token": "test_token_xyz123"},
            }
        )
        mock_post.return_value.__aenter__.return_value = mock_response

        result = await self.api.authenticate()

        self.assertTrue(result)
        self.assertEqual(self.api._token, "test_token_xyz123")
        self.assertIsNotNone(self.api._token_expires)

        # Verify the request was made correctly
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        self.assertTrue(call_args[0][0].endswith(ENDPOINT_AUTH))

        expected_payload = {"appKey": self.app_key, "appSecret": self.app_secret}
        self.assertEqual(call_args[1]["json"], expected_payload)

    @patch("aiohttp.ClientSession.post")
    async def test_authenticate_invalid_credentials(self, mock_post):
        """Test authentication with invalid credentials."""
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.text.return_value = json.dumps(
            {"status": 1, "info": "Invalid credentials"}
        )
        mock_post.return_value.__aenter__.return_value = mock_response

        with self.assertRaises(SolarGuardianAPIError) as context:
            await self.api.authenticate()

        self.assertIn("Invalid credentials", str(context.exception))
        self.assertIsNone(self.api._token)

    @patch("aiohttp.ClientSession.post")
    async def test_authenticate_http_error(self, mock_post):
        """Test authentication with HTTP error."""
        mock_response = AsyncMock()
        mock_response.status = 401
        mock_response.text.return_value = "Unauthorized"
        mock_post.return_value.__aenter__.return_value = mock_response

        with self.assertRaises(SolarGuardianAPIError) as context:
            await self.api.authenticate()

        self.assertIn("Authentication failed: HTTP 401", str(context.exception))

    @patch("aiohttp.ClientSession.post")
    async def test_authenticate_network_error(self, mock_post):
        """Test authentication with network error."""
        mock_post.side_effect = aiohttp.ClientError("Cannot connect to host")

        with self.assertRaises(SolarGuardianAPIError) as context:
            await self.api.authenticate()

        self.assertIn("Cannot connect to", str(context.exception))

    @patch("aiohttp.ClientSession.post")
    async def test_authenticate_invalid_json(self, mock_post):
        """Test authentication with invalid JSON response."""
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.text.return_value = "Invalid JSON response"
        mock_post.return_value.__aenter__.return_value = mock_response

        with self.assertRaises(SolarGuardianAPIError) as context:
            await self.api.authenticate()

        self.assertIn("Invalid JSON response", str(context.exception))

    @patch("aiohttp.ClientSession.post")
    async def test_authenticate_missing_token(self, mock_post):
        """Test authentication with missing token in response."""
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.text.return_value = json.dumps(
            {"status": 0, "info": "success", "data": {}}  # Missing X-Access-Token
        )
        mock_post.return_value.__aenter__.return_value = mock_response

        with self.assertRaises(SolarGuardianAPIError) as context:
            await self.api.authenticate()

        self.assertIn("missing access token", str(context.exception))

    async def test_authenticate_cached_token(self):
        """Test authentication with cached valid token."""
        # Set up a cached token
        self.api._token = "cached_token"
        self.api._token_expires = datetime.now() + timedelta(hours=1)

        result = await self.api.authenticate()

        self.assertTrue(result)
        self.assertEqual(self.api._token, "cached_token")

    async def test_authenticate_expired_token(self):
        """Test authentication with expired cached token."""
        # Set up an expired token
        self.api._token = "expired_token"
        self.api._token_expires = datetime.now() - timedelta(hours=1)

        with patch("aiohttp.ClientSession.post") as mock_post:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.text.return_value = json.dumps(
                {
                    "status": 0,
                    "info": "success",
                    "data": {"X-Access-Token": "new_token_abc456"},
                }
            )
            mock_post.return_value.__aenter__.return_value = mock_response

            result = await self.api.authenticate()

            self.assertTrue(result)
            self.assertEqual(self.api._token, "new_token_abc456")
            mock_post.assert_called_once()

    @patch("aiohttp.ClientSession.post")
    async def test_get_power_stations_success(self, mock_post):
        """Test successful power stations retrieval."""
        # Mock authentication
        auth_response = AsyncMock()
        auth_response.status = 200
        auth_response.text.return_value = json.dumps(
            {"status": 0, "data": {"X-Access-Token": "test_token"}}
        )

        # Mock power stations response
        stations_response = AsyncMock()
        stations_response.status = 200
        stations_response.json.return_value = {
            "status": 0,
            "data": {
                "list": [
                    {"id": 123, "powerStationName": "Test Station", "capacity": 5000}
                ],
                "total": 1,
            },
        }

        mock_post.return_value.__aenter__.side_effect = [
            auth_response,
            stations_response,
        ]

        result = await self.api.get_power_stations()

        self.assertEqual(result["status"], 0)
        self.assertEqual(len(result["data"]["list"]), 1)
        self.assertEqual(result["data"]["list"][0]["powerStationName"], "Test Station")

    @patch("aiohttp.ClientSession.post")
    async def test_get_devices_success(self, mock_post):
        """Test successful devices retrieval."""
        station_id = 123

        # Mock authentication
        auth_response = AsyncMock()
        auth_response.status = 200
        auth_response.text.return_value = json.dumps(
            {"status": 0, "data": {"X-Access-Token": "test_token"}}
        )

        # Mock devices response
        devices_response = AsyncMock()
        devices_response.status = 200
        devices_response.json.return_value = {
            "status": 0,
            "data": {
                "list": [
                    {
                        "id": 456,
                        "equipmentName": "Test Inverter",
                        "productName": "Test Product",
                    }
                ],
                "total": 1,
            },
        }

        mock_post.return_value.__aenter__.side_effect = [
            auth_response,
            devices_response,
        ]

        result = await self.api.get_devices(station_id)

        self.assertEqual(result["status"], 0)
        self.assertEqual(len(result["data"]["list"]), 1)
        self.assertEqual(result["data"]["list"][0]["equipmentName"], "Test Inverter")

    @patch("aiohttp.ClientSession.post")
    async def test_get_device_parameters_success(self, mock_post):
        """Test successful device parameters retrieval."""
        device_id = 456

        # Mock authentication
        auth_response = AsyncMock()
        auth_response.status = 200
        auth_response.text.return_value = json.dumps(
            {"status": 0, "data": {"X-Access-Token": "test_token"}}
        )

        # Mock device parameters response
        params_response = AsyncMock()
        params_response.status = 200
        params_response.json.return_value = {
            "status": 0,
            "data": {
                "variableGroupList": [
                    {
                        "variableGroupNameE": "Power Parameters",
                        "variableList": [
                            {
                                "dataIdentifier": "OutputPower",
                                "variableNameE": "Output Power",
                                "unit": "W",
                            }
                        ],
                    }
                ]
            },
        }

        mock_post.return_value.__aenter__.side_effect = [auth_response, params_response]

        result = await self.api.get_device_parameters(device_id)

        self.assertEqual(result["status"], 0)
        self.assertEqual(len(result["data"]["variableGroupList"]), 1)
        variables = result["data"]["variableGroupList"][0]["variableList"]
        self.assertEqual(variables[0]["dataIdentifier"], "OutputPower")

    @patch("aiohttp.ClientSession.post")
    async def test_get_latest_data_success(self, mock_post):
        """Test successful latest data retrieval."""
        device_id = 456
        data_identifiers = ["OutputPower", "InputVoltage"]

        # Mock authentication
        auth_response = AsyncMock()
        auth_response.status = 200
        auth_response.text.return_value = json.dumps(
            {"status": 0, "data": {"X-Access-Token": "test_token"}}
        )

        # Mock latest data response
        data_response = AsyncMock()
        data_response.status = 200
        data_response.json.return_value = {
            "status": 0,
            "data": {
                "list": [
                    {"dataIdentifier": "OutputPower", "value": "1500"},
                    {"dataIdentifier": "InputVoltage", "value": "240.5"},
                ]
            },
        }

        mock_post.return_value.__aenter__.side_effect = [auth_response, data_response]

        result = await self.api.get_latest_data(device_id, data_identifiers)

        self.assertEqual(result["status"], 0)
        self.assertEqual(len(result["data"]["list"]), 2)
        self.assertEqual(result["data"]["list"][0]["value"], "1500")

    async def test_close(self):
        """Test session cleanup."""
        # Create a mock session
        mock_session = AsyncMock()
        self.api._session = mock_session

        await self.api.close()

        mock_session.close.assert_called_once()
        self.assertIsNone(self.api._session)

    async def test_close_no_session(self):
        """Test closing when no session exists."""
        self.assertIsNone(self.api._session)

        # Should not raise an exception
        await self.api.close()

    def test_rate_limiting_setup(self):
        """Test rate limiting initialization."""
        self.assertIsNotNone(self.api._rate_limit_lock)
        self.assertEqual(self.api._last_auth_call, datetime.min)
        self.assertEqual(self.api._last_data_call, datetime.min)


if __name__ == "__main__":
    unittest.main()
