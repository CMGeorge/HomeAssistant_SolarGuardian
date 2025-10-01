"""The SolarGuardian integration."""
from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timedelta

import voluptuous as vol
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_DOMAIN, Platform
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import SolarGuardianAPI, SolarGuardianAPIError
from .const import DOMAIN, CONF_APP_KEY, CONF_APP_SECRET, CONF_DOMAIN, CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR, Platform.BINARY_SENSOR]

# Service schemas
SERVICE_TEST_CONNECTION = "test_connection"
SERVICE_GET_DIAGNOSTICS = "get_diagnostics"
SERVICE_RESET_LATEST_DATA = "reset_latest_data"

SERVICE_TEST_CONNECTION_SCHEMA = vol.Schema({
    vol.Optional("verbose", default=False): cv.boolean,
})


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up SolarGuardian from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    # Create API client
    api = SolarGuardianAPI(
        domain=entry.data[CONF_DOMAIN],
        app_key=entry.data[CONF_APP_KEY],
        app_secret=entry.data[CONF_APP_SECRET],
    )

    # Test authentication
    try:
        await api.authenticate()
        _LOGGER.info("Successfully authenticated with SolarGuardian API")
    except Exception as err:
        _LOGGER.error("Failed to authenticate with SolarGuardian API: %s", err)
        await api.close()
        return False

    # Create coordinator with custom update interval if specified
    update_interval = entry.options.get(CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL)
    coordinator = SolarGuardianDataUpdateCoordinator(hass, api, update_interval)

    # Fetch initial data
    try:
        await coordinator.async_config_entry_first_refresh()
    except Exception as err:
        _LOGGER.error("Failed to fetch initial data: %s", err)
        await api.close()
        return False

    hass.data[DOMAIN][entry.entry_id] = {
        "api": api,
        "coordinator": coordinator,
    }

    # Forward setup to platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    # Set up options update listener
    entry.async_on_unload(entry.add_update_listener(async_update_options))

    # Register services
    async def test_connection_service(call: ServiceCall) -> None:
        """Handle test connection service call."""
        verbose = call.data.get("verbose", False)
        await _test_connection_service(hass, entry.entry_id, verbose)

    async def get_diagnostics_service(call: ServiceCall) -> None:
        """Handle get diagnostics service call."""
        await _get_diagnostics_service(hass, entry.entry_id)
    
    async def reset_latest_data_service(call: ServiceCall) -> None:
        """Handle reset latest data service call."""
        await _reset_latest_data_service(hass, entry.entry_id)

    hass.services.async_register(
        DOMAIN, SERVICE_TEST_CONNECTION, test_connection_service, SERVICE_TEST_CONNECTION_SCHEMA
    )
    hass.services.async_register(
        DOMAIN, SERVICE_GET_DIAGNOSTICS, get_diagnostics_service
    )
    hass.services.async_register(
        DOMAIN, SERVICE_RESET_LATEST_DATA, reset_latest_data_service
    )

    return True


async def _test_connection_service(hass: HomeAssistant, entry_id: str, verbose: bool) -> None:
    """Test API connection and log results."""
    if entry_id not in hass.data[DOMAIN]:
        _LOGGER.error("SolarGuardian integration not found")
        return

    api: SolarGuardianAPI = hass.data[DOMAIN][entry_id]["api"]
    
    _LOGGER.info("🚀 Starting SolarGuardian API connection test")
    _LOGGER.info("🔧 Domain: %s", api.domain)
    _LOGGER.info("🔧 App Key: %s...", api.app_key[:8] if len(api.app_key) > 8 else "***")
    
    try:
        # Test authentication
        _LOGGER.info("🔐 Testing authentication...")
        auth_success = await api.authenticate()
        if auth_success:
            _LOGGER.info("✅ Authentication successful")
        else:
            _LOGGER.error("❌ Authentication failed")
            return

        # Test power stations
        _LOGGER.info("🏭 Testing power stations endpoint...")
        stations = await api.get_power_stations()
        stations_list = stations.get("data", {}).get("list", [])
        _LOGGER.info("✅ Found %d power stations", len(stations_list))

        if verbose and stations_list:
            for station in stations_list[:3]:  # Show first 3 stations
                station_name = station.get("powerStationName", "Unknown")
                station_id = station["id"]
                _LOGGER.info("   📍 Station: %s (ID: %s)", station_name, station_id)

        # Test devices for first station
        if stations_list:
            station = stations_list[0]
            station_id = station["id"]
            station_name = station.get("powerStationName", "Unknown")
            
            _LOGGER.info("🔧 Testing devices endpoint for station: %s", station_name)
            devices = await api.get_devices(station_id)
            devices_list = devices.get("data", {}).get("list", [])
            _LOGGER.info("✅ Found %d devices", len(devices_list))

            if verbose and devices_list:
                # Test device parameters for first device
                device = devices_list[0]
                device_id = device["id"]
                device_name = device.get("equipmentName", "Unknown")
                
                _LOGGER.info("📊 Testing device parameters for: %s", device_name)
                device_data = await api.get_device_parameters(device_id)
                variable_groups = device_data.get("data", {}).get("variableGroupList", [])
                _LOGGER.info("✅ Found %d parameter groups", len(variable_groups))

                # Count parameters
                total_params = sum(len(group.get("variableList", [])) for group in variable_groups)
                _LOGGER.info("📈 Total parameters: %d", total_params)

        _LOGGER.info("🎉 Connection test completed successfully")

    except SolarGuardianAPIError as e:
        _LOGGER.error("❌ SolarGuardian API Error: %s", e)
    except Exception as e:
        _LOGGER.error("❌ Unexpected error during connection test: %s", e)


async def _get_diagnostics_service(hass: HomeAssistant, entry_id: str) -> None:
    """Get and log diagnostic information."""
    if entry_id not in hass.data[DOMAIN]:
        _LOGGER.error("SolarGuardian integration not found")
        return

    coordinator: SolarGuardianDataUpdateCoordinator = hass.data[DOMAIN][entry_id]["coordinator"]
    api: SolarGuardianAPI = hass.data[DOMAIN][entry_id]["api"]

    _LOGGER.info("📋 SolarGuardian Integration Diagnostics")
    _LOGGER.info("🔧 API Domain: %s", api.domain)
    _LOGGER.info("🔧 App Key: %s...", api.app_key[:8] if len(api.app_key) > 8 else "***")
    _LOGGER.info("⏱️  Update Interval: %s seconds", coordinator.update_interval.total_seconds())
    _LOGGER.info("✅ Last Update Success: %s", coordinator.last_update_success)
    _LOGGER.info("🔄 Failed Updates: %d", coordinator._failed_updates)
    _LOGGER.info("📡 Latest Data Enabled: %s", not coordinator._latest_data_disabled)
    if coordinator._latest_data_disabled:
        _LOGGER.info("   Latest data disabled after %d failures", coordinator._latest_data_failures)
    
    if coordinator.data:
        summary = coordinator.data.get("update_summary", {})
        _LOGGER.info("📊 Data Summary:")
        _LOGGER.info("   Stations: %d", summary.get("stations", 0))
        _LOGGER.info("   Devices: %d", summary.get("devices", 0))
        _LOGGER.info("   Sensors: %d", summary.get("sensors", 0))
        _LOGGER.info("   Errors: %d", len(summary.get("errors", [])))
        
        if summary.get("errors"):
            _LOGGER.info("⚠️  Recent Errors:")
            for error in summary["errors"][:5]:  # Show first 5 errors
                _LOGGER.info("   • %s", error)
    else:
        _LOGGER.warning("❌ No data available from coordinator")


async def _reset_latest_data_service(hass: HomeAssistant, entry_id: str) -> None:
    """Reset latest data fetching status."""
    if entry_id not in hass.data[DOMAIN]:
        _LOGGER.error("SolarGuardian integration not found")
        return

    coordinator: SolarGuardianDataUpdateCoordinator = hass.data[DOMAIN][entry_id]["coordinator"]
    
    old_disabled = coordinator._latest_data_disabled
    old_failures = coordinator._latest_data_failures
    
    coordinator._latest_data_disabled = False
    coordinator._latest_data_failures = 0
    if hasattr(coordinator, '_successful_updates_since_disable'):
        coordinator._successful_updates_since_disable = 0
    
    _LOGGER.info("🔄 Latest data fetching reset - was disabled: %s, failures: %d", old_disabled, old_failures)
    _LOGGER.info("🔄 Latest data fetching is now enabled and will be tried on next update")


async def async_update_options(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Update options."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        # Close API client
        api = hass.data[DOMAIN][entry.entry_id]["api"]
        await api.close()
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


class SolarGuardianDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching SolarGuardian data from the API."""

    def __init__(self, hass: HomeAssistant, api: SolarGuardianAPI, update_interval: int = DEFAULT_UPDATE_INTERVAL, test_mode: bool = False) -> None:
        """Initialize."""
        self.api = api
        self.test_mode = test_mode
        self._failed_updates = 0
        self._max_failed_updates = 3
        self._latest_data_disabled = False  # Flag to disable latest data after repeated failures
        self._latest_data_failures = 0
        self._max_latest_data_failures = 5
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=update_interval),
        )

    def _create_mock_data(self) -> dict:
        """Create mock data for testing purposes."""
        from .const import MOCK_POWER_STATION, MOCK_DEVICE, MOCK_VARIABLE_GROUPS
        
        _LOGGER.info("Creating mock data for testing (API unavailable)")
        
        mock_data = {
            "power_stations": {
                "status": 0,
                "data": {
                    "list": [MOCK_POWER_STATION],
                    "total": 1
                }
            },
            "devices": {
                MOCK_POWER_STATION["id"]: {
                    "status": 0,
                    "data": {
                        "list": [MOCK_DEVICE],
                        "total": 1
                    }
                }
            },
            "device_data": {
                MOCK_DEVICE["id"]: {
                    "status": 0,
                    "data": {
                        "variableGroupList": MOCK_VARIABLE_GROUPS
                    }
                }
            },
            "status": "mock_mode",
            "message": "Using mock data - API unavailable",
            "last_update": datetime.now().isoformat(),
            "update_summary": {
                "stations": 1,
                "devices": 1,
                "sensors": sum(len(group["variableList"]) for group in MOCK_VARIABLE_GROUPS),
                "errors": ["Using mock data due to API connectivity issues"]
            }
        }
        
        return mock_data

    async def _async_update_data(self):
        """Update data via library."""
        try:
            _LOGGER.debug("Starting data update cycle")
            
            # Test authentication first
            try:
                auth_success = await self.api.authenticate()
                if not auth_success:
                    raise UpdateFailed("Authentication failed")
                _LOGGER.debug("Authentication successful")
            except Exception as auth_err:
                _LOGGER.error("Authentication failed: %s", auth_err)
                raise UpdateFailed(f"Authentication error: {auth_err}") from auth_err
            
            # Get power stations
            try:
                power_stations = await self.api.get_power_stations()
                _LOGGER.debug("Power stations response: %s", power_stations.get("status"))
            except Exception as ps_err:
                _LOGGER.error("Failed to get power stations: %s", ps_err)
                raise UpdateFailed(f"Power stations error: {ps_err}") from ps_err
            
            if not power_stations.get("data", {}).get("list"):
                _LOGGER.warning("No power stations found in response")
                return {"status": "no_stations", "message": "No power stations available"}
            
            stations_list = power_stations.get("data", {}).get("list", [])
            _LOGGER.info("Found %d power stations", len(stations_list))
            
            data = {
                "power_stations": power_stations,
                "devices": {},
                "device_data": {},
                "status": "success",
                "last_update": datetime.now().isoformat(),
                "update_summary": {
                    "stations": len(stations_list),
                    "devices": 0,
                    "sensors": 0,
                    "errors": []
                }
            }

            # Get devices for each power station
            for station in stations_list:
                station_id = station["id"]
                station_name = station.get("powerStationName", f"Station {station_id}")
                _LOGGER.debug("Processing station: %s (ID: %s)", station_name, station_id)
                
                try:
                    # Get devices using the proper API method
                    devices = await self.api.get_devices(station_id, page_no=1, page_size=100)
                    data["devices"][station_id] = devices
                    
                    devices_list = devices.get("data", {}).get("list", [])
                    data["update_summary"]["devices"] += len(devices_list)
                    _LOGGER.debug("Found %d devices for station %s", len(devices_list), station_name)

                    # Get device parameters for each device
                    for device in devices_list:
                        device_id = device["id"]
                        device_name = device.get("equipmentName", f"Device {device_id}")
                        _LOGGER.debug("Processing device: %s (ID: %s)", device_name, device_id)
                        
                        try:
                            device_data = await self.api.get_device_parameters(device_id)
                            data["device_data"][device_id] = device_data
                            
                            # Count parameters
                            param_count = 0
                            variable_groups = device_data.get("data", {}).get("variableGroupList", [])
                            for group in variable_groups:
                                param_count += len(group.get("variableList", []))
                            
                            data["update_summary"]["sensors"] += param_count
                            _LOGGER.debug("Device %s has %d parameters", device_name, param_count)
                            
                            # Get latest data for real-time values (only if device data was successful and not disabled)
                            if variable_groups and not self._latest_data_disabled:
                                dev_datapoints = []
                                for group in variable_groups:
                                    for variable in group.get("variableList", []):
                                        data_point_id = variable.get("dataPointId")
                                        device_no = variable.get("deviceNo")
                                        if data_point_id and device_no:
                                            dev_datapoints.append({
                                                "dataPointId": data_point_id,
                                                "deviceNo": device_no
                                            })
                                
                                if dev_datapoints:
                                    try:
                                        # Use the correct method with dataPointId and deviceNo
                                        _LOGGER.debug("Fetching latest data for device %s with %d datapoints", device_name, len(dev_datapoints))
                                        latest_data = await self.api.get_latest_data_by_datapoints(dev_datapoints)
                                        data["device_data"][device_id]["latest_data"] = latest_data
                                        latest_count = len(latest_data.get("data", {}).get("list", []))
                                        _LOGGER.debug("Retrieved %d latest values for device %s", latest_count, device_name)
                                        # Reset failure counter on success
                                        self._latest_data_failures = 0
                                    except SolarGuardianAPIError as latest_err:
                                        error_msg = f"Failed to get latest data for device {device_name}: {latest_err}"
                                        _LOGGER.warning(error_msg)
                                        
                                        # Track failures and disable if too many
                                        if "404" in str(latest_err) or "inner error" in str(latest_err).lower():
                                            self._latest_data_failures += 1
                                            if self._latest_data_failures >= self._max_latest_data_failures:
                                                self._latest_data_disabled = True
                                                _LOGGER.warning("Latest data endpoint consistently failing (%d failures), disabling", self._latest_data_failures)
                                        else:
                                            data["update_summary"]["errors"].append(error_msg)
                                    except Exception as latest_err:
                                        error_msg = f"Failed to get latest data for device {device_name}: {latest_err}"
                                        _LOGGER.warning(error_msg)
                                        data["update_summary"]["errors"].append(error_msg)
                                else:
                                    _LOGGER.debug("No dataPointId/deviceNo found for device %s, skipping latest data", device_name)
                            elif self._latest_data_disabled:
                                _LOGGER.debug("Latest data fetching disabled for device %s due to repeated failures", device_name)
                                        
                        except Exception as err:
                            error_msg = f"Failed to get data for device {device_name}: {err}"
                            _LOGGER.warning(error_msg)
                            data["update_summary"]["errors"].append(error_msg)
                            
                except Exception as station_err:
                    error_msg = f"Failed to get devices for station {station_name}: {station_err}"
                    _LOGGER.warning(error_msg)
                    data["update_summary"]["errors"].append(error_msg)
                    
                            # Reset failed counter on successful update
            self._failed_updates = 0
            
            # Periodically try to re-enable latest data if it was disabled
            if self._latest_data_disabled and summary["devices"] > 0:
                # Try to re-enable every 10 successful updates
                if hasattr(self, '_successful_updates_since_disable'):
                    self._successful_updates_since_disable += 1
                    if self._successful_updates_since_disable >= 10:
                        _LOGGER.info("Re-enabling latest data fetching after successful updates")
                        self._latest_data_disabled = False
                        self._latest_data_failures = 0
                        self._successful_updates_since_disable = 0
                else:
                    self._successful_updates_since_disable = 1
            
            # Log summary
            summary = data["update_summary"]
            _LOGGER.info(
                "Update complete: %d stations, %d devices, %d sensors, %d errors",
                summary["stations"], summary["devices"], summary["sensors"], len(summary["errors"])
            )
            
            if summary["errors"]:
                _LOGGER.warning("Errors during update: %s", "; ".join(summary["errors"][:3]))
            
            return data

        except Exception as err:
            self._failed_updates += 1
            
            # Log detailed error information
            _LOGGER.error("Data update failed (attempt %d/%d): %s", 
                         self._failed_updates, self._max_failed_updates, err)
            
            # If we've exceeded max failures and don't have any data, try mock mode
            if self._failed_updates >= self._max_failed_updates and not self.data:
                _LOGGER.warning("Max failures reached and no data available, switching to mock mode")
                try:
                    mock_data = self._create_mock_data()
                    _LOGGER.info("Mock data created successfully with %d sensors", 
                               mock_data["update_summary"]["sensors"])
                    return mock_data
                except Exception as mock_err:
                    _LOGGER.error("Failed to create mock data: %s", mock_err)
            
            # Increase update interval if we're having repeated failures
            if self._failed_updates >= self._max_failed_updates:
                old_interval = self.update_interval.total_seconds()
                self.update_interval = timedelta(seconds=300)  # 5 minutes
                _LOGGER.warning(
                    "Multiple update failures (%d), increasing interval from %ds to 5 minutes", 
                    self._failed_updates, old_interval
                )
            
            raise UpdateFailed(f"Error communicating with API: {err}") from err