"""SolarGuardian API client."""
from __future__ import annotations

import asyncio
import json
import logging
from datetime import datetime, timedelta

import aiohttp
from aiohttp import ClientTimeout

from .const import (
    DEFAULT_TIMEOUT,
    ENDPOINT_AUTH,
    ENDPOINT_DEVICE_PARAMETERS,
    ENDPOINT_DEVICES,
    ENDPOINT_LATEST_DATA,
    ENDPOINT_POWER_STATIONS,
    LATEST_DATA_PORT,
)

_LOGGER = logging.getLogger(__name__)


class SolarGuardianAPIError(Exception):
    """Exception raised for API errors."""


class SolarGuardianAPI:
    """SolarGuardian API client."""

    def __init__(self, domain: str, app_key: str, app_secret: str) -> None:
        """Initialize the API client."""
        self.domain = domain
        self.app_key = app_key
        self.app_secret = app_secret
        self._base_url = f"https://{domain}"
        self._session: aiohttp.ClientSession | None = None
        self._token: str | None = None
        self._token_expires: datetime | None = None
        self._rate_limit_lock = asyncio.Lock()
        self._last_auth_call = datetime.min
        self._last_data_call = datetime.min

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get aiohttp session."""
        if self._session is None:
            self._session = aiohttp.ClientSession(
                timeout=ClientTimeout(total=DEFAULT_TIMEOUT)
            )
        return self._session

    async def close(self) -> None:
        """Close the session."""
        if self._session:
            await self._session.close()
            self._session = None

    async def _rate_limit_auth(self) -> None:
        """Apply rate limiting for auth calls (10 per minute)."""
        async with self._rate_limit_lock:
            now = datetime.now()
            time_since_last = (now - self._last_auth_call).total_seconds()
            if time_since_last < 6:  # 10 calls per minute = 6 seconds between calls
                wait_time = 6 - time_since_last
                _LOGGER.debug("Rate limiting auth call, waiting %.2f seconds", wait_time)
                await asyncio.sleep(wait_time)
            self._last_auth_call = datetime.now()

    async def _rate_limit_data(self) -> None:
        """Apply rate limiting for data calls (30 per minute)."""
        async with self._rate_limit_lock:
            now = datetime.now()
            time_since_last = (now - self._last_data_call).total_seconds()
            if time_since_last < 2:  # 30 calls per minute = 2 seconds between calls
                wait_time = 2 - time_since_last
                _LOGGER.debug("Rate limiting data call, waiting %.2f seconds", wait_time)
                await asyncio.sleep(wait_time)
            self._last_data_call = datetime.now()

    async def authenticate(self) -> bool:
        """Authenticate with the API."""
        if self._token and self._token_expires and datetime.now() < self._token_expires:
            _LOGGER.debug("Using cached authentication token")
            return True

        await self._rate_limit_auth()

        session = await self._get_session()
        url = f"{self._base_url}{ENDPOINT_AUTH}"

        payload = {
            "appKey": self.app_key,
            "appSecret": self.app_secret,
        }

        headers = {
            "Content-Type": "application/json",
        }

        _LOGGER.debug("Attempting authentication with domain: %s", self.domain)

        try:
            async with session.post(url, json=payload, headers=headers) as response:
                response_text = await response.text()
                _LOGGER.debug("Auth response status: %s", response.status)

                if response.status != 200:
                    _LOGGER.error("Authentication failed - HTTP %s: %s", response.status, response_text[:200])
                    raise SolarGuardianAPIError(f"Authentication failed: HTTP {response.status}")

                try:
                    data = json.loads(response_text)
                except json.JSONDecodeError as json_err:
                    _LOGGER.error("Invalid JSON response from auth endpoint: %s", response_text[:200])
                    raise SolarGuardianAPIError(f"Invalid JSON response: {json_err}") from json_err

                if data.get("status") != 0:
                    error_info = data.get('info', 'Unknown error')
                    _LOGGER.error("Authentication API error - status: %s, info: %s", data.get("status"), error_info)
                    raise SolarGuardianAPIError(f"Authentication error: {error_info}")

                if "data" not in data or "X-Access-Token" not in data["data"]:
                    _LOGGER.error("Missing token in auth response: %s", data)
                    raise SolarGuardianAPIError("Authentication response missing access token")

                self._token = data["data"]["X-Access-Token"]
                # Token expires in 2 hours
                self._token_expires = datetime.now() + timedelta(hours=2)

                _LOGGER.info("Successfully authenticated with SolarGuardian API")
                return True

        except aiohttp.ClientError as err:
            _LOGGER.error("Network error during authentication: %s", err)
            # Check for specific connection errors
            if "Cannot connect to host" in str(err):
                raise SolarGuardianAPIError(f"Cannot connect to {self.domain}. Please check your domain setting and network connectivity.") from err
            elif "SSL" in str(err):
                raise SolarGuardianAPIError(f"SSL connection error to {self.domain}. Please verify the domain supports HTTPS.") from err
            elif "timeout" in str(err).lower():
                raise SolarGuardianAPIError(f"Connection timeout to {self.domain}. Please check your network connection.") from err
            else:
                raise SolarGuardianAPIError(f"Network error during authentication: {err}") from err

    async def _make_authenticated_request(self, endpoint: str, payload: dict = None) -> dict:
        """Make an authenticated request to the API."""
        await self.authenticate()
        await self._rate_limit_data()

        session = await self._get_session()
        url = f"{self._base_url}{endpoint}"

        headers = {
            "Content-Type": "application/json",
            "X-Access-Token": self._token,
        }

        try:
            async with session.post(url, json=payload or {}, headers=headers) as response:
                if response.status != 200:
                    raise SolarGuardianAPIError(f"API request failed: {response.status}")

                data = await response.json()

                if data.get("status") != 0:
                    error_msg = data.get("info", "Unknown error")
                    if data.get("status") == 5126:  # Too frequent requests
                        _LOGGER.error("API rate limit exceeded! The integration is making too many requests.")
                        _LOGGER.error("Please increase the update interval in integration options (recommended: 30+ seconds for multiple devices).")
                        await asyncio.sleep(10)  # Back off longer
                    raise SolarGuardianAPIError(f"API error: {error_msg}")

                return data

        except aiohttp.ClientError as err:
            raise SolarGuardianAPIError(f"Network error: {err}") from err
        except json.JSONDecodeError as err:
            raise SolarGuardianAPIError(f"Invalid JSON response: {err}") from err

    async def get_power_stations(self, page_no: int = 1, page_size: int = 100) -> dict:
        """Get list of power stations."""
        payload = {
            "pageNo": page_no,
            "pageSize": page_size,
        }

        return await self._make_authenticated_request(ENDPOINT_POWER_STATIONS, payload)

    async def get_devices(self, power_station_id: int, page_no: int = 1, page_size: int = 100) -> dict:
        """Get list of devices for a power station."""
        payload = {
            "powerStationId": power_station_id,
            "pageNo": page_no,
            "pageSize": page_size,
        }

        return await self._make_authenticated_request(ENDPOINT_DEVICES, payload)

    async def get_gateways(self, power_station_id: int, page_no: int = 1, page_size: int = 100) -> dict:
        """Get list of gateways for a power station."""
        payload = {
            "powerStationId": power_station_id,
            "pageNo": page_no,
            "pageSize": page_size,
        }

        return await self._make_authenticated_request("/epCloud/vn/openApi/getGatewayListPage", payload)

    async def get_device_parameters(self, device_id: int) -> dict:
        """Get all parameters for a device."""
        payload = {
            "id": device_id,
        }

        return await self._make_authenticated_request(ENDPOINT_DEVICE_PARAMETERS, payload)

    async def get_latest_data(self, device_id: int, data_identifiers: list[str]) -> dict:
        """Get latest data for specific parameters.

        Note: This endpoint uses port 7002 as specified in the API documentation.
        """
        if not data_identifiers:
            raise SolarGuardianAPIError("No data identifiers provided")

        # Use the correct endpoint with port 7002 as specified in API docs
        await self.authenticate()
        await self._rate_limit_data()

        session = await self._get_session()

        # Parse domain to get host without protocol
        domain_parts = self.domain.replace("https://", "").replace("http://", "")
        latest_data_url = f"https://{domain_parts}:{LATEST_DATA_PORT}{ENDPOINT_LATEST_DATA}"

        headers = {
            "Content-Type": "application/json",
            "X-Access-Token": self._token,
        }

        payload = {
            "id": device_id,
            "dataIdentifiers": data_identifiers,
        }

        _LOGGER.debug("Making latest data request to %s for device %d with %d identifiers", latest_data_url, device_id, len(data_identifiers))

        try:
            async with session.post(latest_data_url, json=payload, headers=headers) as response:
                if response.status != 200:
                    if response.status == 404:
                        _LOGGER.debug("Latest data endpoint not available (404 error)")
                        raise SolarGuardianAPIError(f"Latest data endpoint not available: HTTP {response.status}")
                    raise SolarGuardianAPIError(f"Latest data API request failed: {response.status}")

                data = await response.json()

                if data.get("status") != 0:
                    error_msg = data.get("info", "Unknown error")
                    if data.get("status") == 5126:  # Too frequent requests
                        _LOGGER.error("API rate limit exceeded during latest data request!")
                        _LOGGER.error("Please increase the update interval in integration options (recommended: 30+ seconds for multiple devices).")
                        await asyncio.sleep(10)  # Back off longer
                    raise SolarGuardianAPIError(f"Latest data API error: {error_msg}")

                return data

        except aiohttp.ClientError as err:
            raise SolarGuardianAPIError(f"Network error during latest data request: {err}") from err
        except json.JSONDecodeError as err:
            raise SolarGuardianAPIError(f"Invalid JSON response from latest data endpoint: {err}") from err

    async def get_latest_data_by_datapoints(self, dev_datapoints: list[dict]) -> dict:
        """Get latest data using the correct API endpoint with dataPointId and deviceNo.

        Args:
            dev_datapoints: List of dicts with 'dataPointId' and 'deviceNo' keys

        Returns:
            API response with latest data
        """
        if not dev_datapoints:
            raise SolarGuardianAPIError("No data points provided")

        # Use the correct endpoint with port 7002 as specified in API docs
        await self.authenticate()
        await self._rate_limit_data()

        session = await self._get_session()

        # Parse domain to get host without protocol
        domain_parts = self.domain.replace("https://", "").replace("http://", "")
        latest_data_url = f"https://{domain_parts}:{LATEST_DATA_PORT}{ENDPOINT_LATEST_DATA}"

        headers = {
            "Content-Type": "application/json",
            "X-Access-Token": self._token,
        }

        payload = {
            "devDatapoints": dev_datapoints
        }

        _LOGGER.debug("Making latest data request to %s with %d data points", latest_data_url, len(dev_datapoints))

        try:
            async with session.post(latest_data_url, json=payload, headers=headers) as response:
                if response.status != 200:
                    raise SolarGuardianAPIError(f"Latest data API request failed: {response.status}")

                data = await response.json()

                if data.get("status") != 0:
                    error_msg = data.get("info", "Unknown error")
                    if data.get("status") == 5126:  # Too frequent requests
                        _LOGGER.error("API rate limit exceeded during latest data request!")
                        _LOGGER.error("Please increase the update interval in integration options (recommended: 30+ seconds for multiple devices).")
                        await asyncio.sleep(10)  # Back off longer
                    raise SolarGuardianAPIError(f"Latest data API error: {error_msg}")

                return data

        except aiohttp.ClientError as err:
            raise SolarGuardianAPIError(f"Network error during latest data request: {err}") from err
        except json.JSONDecodeError as err:
            raise SolarGuardianAPIError(f"Invalid JSON response from latest data endpoint: {err}") from err
