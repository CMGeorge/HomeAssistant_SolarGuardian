"""Support for SolarGuardian sensors."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.helpers.entity import EntityCategory
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfEnergy,
    UnitOfPower,
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import SolarGuardianDataUpdateCoordinator
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

# Sensors that should be marked as diagnostic (technical/debug info)
DIAGNOSTIC_SENSORS = [
    "SerialNumber", "DeviceSerialNumber", "GatewayID", "GatewaySN",
    "FirmwareVersion", "HardwareVersion", "ProtocolVersion",
    "RegisterAddress", "ModbusAddress", "DeviceAddress",
    "CommunicationStatus", "SignalStrength", "DataQuality",
]

# Mapping of parameter identifiers to sensor configurations
# Based on the actual SolarGuardian API parameter names
SENSOR_TYPES = {
    # Power sensors
    "OutputPower": {
        "name": "Output Power",
        "unit": UnitOfPower.WATT,
        "device_class": SensorDeviceClass.POWER,
        "state_class": SensorStateClass.MEASUREMENT,
        "icon": "mdi:solar-power",
    },
    "InputPower": {
        "name": "Input Power",
        "unit": UnitOfPower.WATT,
        "device_class": SensorDeviceClass.POWER,
        "state_class": SensorStateClass.MEASUREMENT,
        "icon": "mdi:solar-power",
    },
    "loadpower": {
        "name": "Load Power",
        "unit": UnitOfPower.WATT,
        "device_class": SensorDeviceClass.POWER,
        "state_class": SensorStateClass.MEASUREMENT,
        "icon": "mdi:home-lightning-bolt",
    },
    # Voltage sensors
    "BatteryVoltage": {
        "name": "Battery Voltage",
        "unit": UnitOfElectricPotential.VOLT,
        "device_class": SensorDeviceClass.VOLTAGE,
        "state_class": SensorStateClass.MEASUREMENT,
        "icon": "mdi:battery",
    },
    "battvolt": {
        "name": "Battery Voltage",
        "unit": UnitOfElectricPotential.VOLT,
        "device_class": SensorDeviceClass.VOLTAGE,
        "state_class": SensorStateClass.MEASUREMENT,
        "icon": "mdi:battery",
    },
    "PVVoltage": {
        "name": "PV Voltage",
        "unit": UnitOfElectricPotential.VOLT,
        "device_class": SensorDeviceClass.VOLTAGE,
        "state_class": SensorStateClass.MEASUREMENT,
        "icon": "mdi:solar-panel",
    },
    "pvvolt": {
        "name": "PV Voltage",
        "unit": UnitOfElectricPotential.VOLT,
        "device_class": SensorDeviceClass.VOLTAGE,
        "state_class": SensorStateClass.MEASUREMENT,
        "icon": "mdi:solar-panel",
    },
    "LoadVoltage": {
        "name": "Load Voltage",
        "unit": UnitOfElectricPotential.VOLT,
        "device_class": SensorDeviceClass.VOLTAGE,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "loadvolt": {
        "name": "Load Voltage",
        "unit": UnitOfElectricPotential.VOLT,
        "device_class": SensorDeviceClass.VOLTAGE,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    "crtrattedbatvolt": {
        "name": "Current Rated Battery Voltage",
        "unit": UnitOfElectricPotential.VOLT,
        "device_class": SensorDeviceClass.VOLTAGE,
        "state_class": SensorStateClass.MEASUREMENT,
        "icon": "mdi:battery",
    },
    "VLEVELFilter": {
        "name": "Battery Rated Voltage",
        "unit": UnitOfElectricPotential.VOLT,
        "device_class": SensorDeviceClass.VOLTAGE,
        "state_class": SensorStateClass.MEASUREMENT,
        "icon": "mdi:battery",
    },
    # Current sensors
    "BatteryCurrent": {
        "name": "Battery Current",
        "unit": UnitOfElectricCurrent.AMPERE,
        "device_class": SensorDeviceClass.CURRENT,
        "state_class": SensorStateClass.MEASUREMENT,
        "icon": "mdi:current-dc",
    },
    "battcurr": {
        "name": "Battery Current",
        "unit": UnitOfElectricCurrent.AMPERE,
        "device_class": SensorDeviceClass.CURRENT,
        "state_class": SensorStateClass.MEASUREMENT,
        "icon": "mdi:current-dc",
    },
    "PVCurrent": {
        "name": "PV Current",
        "unit": UnitOfElectricCurrent.AMPERE,
        "device_class": SensorDeviceClass.CURRENT,
        "state_class": SensorStateClass.MEASUREMENT,
        "icon": "mdi:current-dc",
    },
    "pvcurr": {
        "name": "PV Current",
        "unit": UnitOfElectricCurrent.AMPERE,
        "device_class": SensorDeviceClass.CURRENT,
        "state_class": SensorStateClass.MEASUREMENT,
        "icon": "mdi:current-dc",
    },
    "LoadCurrent": {
        "name": "Load Current",
        "unit": UnitOfElectricCurrent.AMPERE,
        "device_class": SensorDeviceClass.CURRENT,
        "state_class": SensorStateClass.MEASUREMENT,
        "icon": "mdi:current-dc",
    },
    "loadcurr": {
        "name": "Load Current",
        "unit": UnitOfElectricCurrent.AMPERE,
        "device_class": SensorDeviceClass.CURRENT,
        "state_class": SensorStateClass.MEASUREMENT,
        "icon": "mdi:current-dc",
    },
    # Device Information Sensors (Text)
    "_device_serial": {
        "name": "Serial Number",
        "icon": "mdi:identifier",
        "device_class": None,
        "state_class": None,
    },
    "_device_gateway": {
        "name": "Gateway ID",
        "icon": "mdi:router-wireless",
        "device_class": None,
        "state_class": None,
    },
    "_device_gateway_name": {
        "name": "Gateway Name",
        "icon": "mdi:router-wireless",
        "device_class": None,
        "state_class": None,
    },
    "_device_product": {
        "name": "Product Name",
        "icon": "mdi:information",
        "device_class": None,
        "state_class": None,
    },
    "_device_location": {
        "name": "Location",
        "icon": "mdi:map-marker",
        "device_class": None,
        "state_class": None,
    },
    "_device_status_text": {
        "name": "Status",
        "icon": "mdi:information",
        "device_class": None,
        "state_class": None,
    },
    # Temperature sensors
    "BatteryTemperature": {
        "name": "Battery Temperature",
        "unit": UnitOfTemperature.CELSIUS,
        "device_class": SensorDeviceClass.TEMPERATURE,
        "state_class": SensorStateClass.MEASUREMENT,
        "icon": "mdi:thermometer",
    },
    "batttemp": {
        "name": "Battery Temperature",
        "unit": UnitOfTemperature.CELSIUS,
        "device_class": SensorDeviceClass.TEMPERATURE,
        "state_class": SensorStateClass.MEASUREMENT,
        "icon": "mdi:thermometer",
    },
    "DeviceTemperature": {
        "name": "Device Temperature",
        "unit": UnitOfTemperature.CELSIUS,
        "device_class": SensorDeviceClass.TEMPERATURE,
        "state_class": SensorStateClass.MEASUREMENT,
        "icon": "mdi:thermometer",
    },
    "devtemp": {
        "name": "Device Temperature",
        "unit": UnitOfTemperature.CELSIUS,
        "device_class": SensorDeviceClass.TEMPERATURE,
        "state_class": SensorStateClass.MEASUREMENT,
        "icon": "mdi:thermometer",
    },
    # Energy sensors
    "GeneratedEnergyToday": {
        "name": "Generated Energy Today",
        "unit": UnitOfEnergy.KILO_WATT_HOUR,
        "device_class": SensorDeviceClass.ENERGY,
        "state_class": SensorStateClass.TOTAL_INCREASING,
        "icon": "mdi:solar-power",
    },
    "genenergytoday": {
        "name": "Generated Energy Today",
        "unit": UnitOfEnergy.KILO_WATT_HOUR,
        "device_class": SensorDeviceClass.ENERGY,
        "state_class": SensorStateClass.TOTAL_INCREASING,
        "icon": "mdi:solar-power",
    },
    "GeneratedEnergyTotal": {
        "name": "Generated Energy Total",
        "unit": UnitOfEnergy.KILO_WATT_HOUR,
        "device_class": SensorDeviceClass.ENERGY,
        "state_class": SensorStateClass.TOTAL_INCREASING,
        "icon": "mdi:solar-power",
    },
    "genergytotal": {
        "name": "Generated Energy Total",
        "unit": UnitOfEnergy.KILO_WATT_HOUR,
        "device_class": SensorDeviceClass.ENERGY,
        "state_class": SensorStateClass.TOTAL_INCREASING,
        "icon": "mdi:solar-power",
    },
    "ConsumedEnergyToday": {
        "name": "Consumed Energy Today",
        "unit": UnitOfEnergy.KILO_WATT_HOUR,
        "device_class": SensorDeviceClass.ENERGY,
        "state_class": SensorStateClass.TOTAL_INCREASING,
        "icon": "mdi:home-lightning-bolt",
    },
    "consumeenergytoday": {
        "name": "Consumed Energy Today",
        "unit": UnitOfEnergy.KILO_WATT_HOUR,
        "device_class": SensorDeviceClass.ENERGY,
        "state_class": SensorStateClass.TOTAL_INCREASING,
        "icon": "mdi:home-lightning-bolt",
    },
    "ConsumedEnergyTotal": {
        "name": "Consumed Energy Total",
        "unit": UnitOfEnergy.KILO_WATT_HOUR,
        "device_class": SensorDeviceClass.ENERGY,
        "state_class": SensorStateClass.TOTAL_INCREASING,
        "icon": "mdi:home-lightning-bolt",
    },
    "consumeenergytotal": {
        "name": "Consumed Energy Total",
        "unit": UnitOfEnergy.KILO_WATT_HOUR,
        "device_class": SensorDeviceClass.ENERGY,
        "state_class": SensorStateClass.TOTAL_INCREASING,
        "icon": "mdi:home-lightning-bolt",
    },
    # Battery sensors
    "BatterySOC": {
        "name": "Battery State of Charge",
        "unit": "%",
        "device_class": SensorDeviceClass.BATTERY,
        "state_class": SensorStateClass.MEASUREMENT,
        "icon": "mdi:battery",
    },
    "batterysoc": {
        "name": "Battery State of Charge",
        "unit": "%",
        "device_class": SensorDeviceClass.BATTERY,
        "state_class": SensorStateClass.MEASUREMENT,
        "icon": "mdi:battery",
    },
    "BatteryCapacity": {
        "name": "Battery Capacity",
        "unit": "Ah",
        "state_class": SensorStateClass.MEASUREMENT,
        "icon": "mdi:battery-high",
    },
    "battcap": {
        "name": "Battery Capacity",
        "unit": "Ah",
        "state_class": SensorStateClass.MEASUREMENT,
        "icon": "mdi:battery-high",
    },
    # Additional sensors that might be available
    "pvpower": {
        "name": "PV Power",
        "unit": UnitOfPower.WATT,
        "device_class": SensorDeviceClass.POWER,
        "state_class": SensorStateClass.MEASUREMENT,
        "icon": "mdi:solar-power",
    },
    "battpower": {
        "name": "Battery Power",
        "unit": UnitOfPower.WATT,
        "device_class": SensorDeviceClass.POWER,
        "state_class": SensorStateClass.MEASUREMENT,
        "icon": "mdi:battery",
    },
}


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up SolarGuardian sensors based on a config entry."""
    coordinator: SolarGuardianDataUpdateCoordinator = hass.data[DOMAIN][
        config_entry.entry_id
    ]["coordinator"]

    entities = []

    # Check if we have data
    if not coordinator.data:
        _LOGGER.warning("No initial data available for sensor setup")
        # Set up a listener to create sensors when data becomes available
        async def _async_data_updated():
            if coordinator.data and coordinator.data.get("devices"):
                _LOGGER.info("Data now available, setting up sensors")
                await _setup_sensors_from_data(coordinator, async_add_entities)
        
        # Listen for data updates
        coordinator.async_add_listener(_async_data_updated)
        return

    # Set up sensors immediately if data is available
    await _setup_sensors_from_data(coordinator, async_add_entities)


async def _setup_sensors_from_data(
    coordinator: SolarGuardianDataUpdateCoordinator,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up sensors from coordinator data."""
    entities = []
    
    # Check for connection status information
    data_status = coordinator.data.get("status", "unknown")
    _LOGGER.info("Setting up sensors with data status: %s", data_status)
    
    if data_status == "no_stations":
        _LOGGER.warning("No power stations available - sensors cannot be created")
        return
    
    # Log summary information
    summary = coordinator.data.get("update_summary", {})
    if summary:
        _LOGGER.info(
            "Data summary: %d stations, %d devices, %d sensors", 
            summary.get("stations", 0), 
            summary.get("devices", 0), 
            summary.get("sensors", 0)
        )

    # Create sensors for each device
    for station_id, devices in coordinator.data.get("devices", {}).items():
        station_devices = devices.get("data", {}).get("list", [])
        _LOGGER.debug("Processing %d devices from station %s", len(station_devices), station_id)
        
        for device in station_devices:
            device_id = device["id"]
            device_name = device.get("equipmentName", f"Device {device_id}")
            device_data = coordinator.data.get("device_data", {}).get(device_id, {})

            if not device_data:
                _LOGGER.warning("No parameter data available for device %s", device_name)
                continue

            # Initialize device sensor counter
            device_sensors = 0

            # Add device information sensors (Serial, Gateway, Location, etc.)
            # These are text sensors showing device metadata
            device_info_sensors = [
                ("_device_serial", device.get("equipmentNo", "Unknown")),
                ("_device_gateway", device.get("gatewayId", "Unknown")),
                ("_device_gateway_name", device.get("gatewayName", "Unknown")),
                ("_device_product", device.get("productName", device.get("productNameE", "Unknown"))),
                ("_device_location", device.get("address", "Unknown")),
                ("_device_status_text", "Online" if device.get("status") == 1 else "Offline"),
            ]
            
            for sensor_id, sensor_value in device_info_sensors:
                if sensor_id in SENSOR_TYPES and sensor_value != "Unknown":
                    entities.append(
                        SolarGuardianDeviceInfoSensor(
                            coordinator,
                            device,
                            sensor_id,
                            SENSOR_TYPES[sensor_id],
                            sensor_value,
                        )
                    )
                    device_sensors += 1

            # Create sensors for each parameter group
            for group in device_data.get("data", {}).get("variableGroupList", []):
                group_name = group.get("variableGroupNameE", group.get("variableGroupNameC", "Unknown"))
                for variable in group.get("variableList", []):
                    data_identifier = variable.get("dataIdentifier")
                    if not data_identifier:
                        continue
                    
                    # Skip configuration parameters (mode="1")
                    # These are device settings that are not provided by the latest_data endpoint
                    # mode="0" = real-time sensor (has values)
                    # mode="1" = configuration parameter (no values from API)
                    variable_mode = variable.get("mode", "0")
                    if variable_mode == "1":
                        _LOGGER.debug(
                            "Skipping configuration parameter: %s (mode=1, not readable via API)",
                            variable.get("variableNameE", data_identifier)
                        )
                        continue
                        
                    if data_identifier in SENSOR_TYPES:
                        entities.append(
                            SolarGuardianSensor(
                                coordinator,
                                device,
                                variable,
                                SENSOR_TYPES[data_identifier],
                            )
                        )
                        device_sensors += 1
                    else:
                        # Create generic sensor for unknown parameters
                        _LOGGER.debug(
                            "Creating generic sensor for unknown parameter: %s in group %s", 
                            data_identifier, group_name
                        )
                        entities.append(
                            SolarGuardianSensor(
                                coordinator,
                                device,
                                variable,
                                {
                                    "name": variable.get("variableNameE", variable.get("variableNameC", data_identifier)),
                                    "unit": variable.get("unit"),
                                    "icon": "mdi:gauge",
                                },
                            )
                        )
                        device_sensors += 1
            
            _LOGGER.info("Created %d sensors for device %s", device_sensors, device_name)

    _LOGGER.info("Total sensors created: %d", len(entities))
    if entities:
        async_add_entities(entities)


class SolarGuardianSensor(CoordinatorEntity, SensorEntity):
    """Representation of a SolarGuardian sensor."""

    def __init__(
        self,
        coordinator: SolarGuardianDataUpdateCoordinator,
        device: dict[str, Any],
        variable: dict[str, Any],
        sensor_config: dict[str, Any],
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        
        self._device = device
        self._variable = variable
        self._sensor_config = sensor_config
        self._attr_name = f"{device['equipmentName']} {sensor_config['name']}"
        self._attr_unique_id = f"{device['id']}_{variable['dataIdentifier']}"
        
        # Check if this is an enum sensor (has translationChild)
        has_translation = bool(variable.get("translationChild"))
        
        # Set sensor attributes
        # For enum sensors (text values), don't set device_class, state_class, or unit
        # This tells Home Assistant to treat them as text sensors
        if not has_translation:
            self._attr_native_unit_of_measurement = sensor_config.get("unit")
            self._attr_device_class = sensor_config.get("device_class")
            self._attr_state_class = sensor_config.get("state_class")
        
        self._attr_icon = sensor_config.get("icon")
        
        # Device info
        self._attr_device_info = {
            "identifiers": {(DOMAIN, str(device["id"]))},
            "name": device["equipmentName"],
            "manufacturer": "Epever",
            "model": device.get("productName", "Solar Inverter"),
            "sw_version": device.get("version"),
        }

    def _translate_value(self, value: float, translation_child: list) -> str | None:
        """Translate numeric value to text using translationChild mappings.
        
        Args:
            value: Numeric value from sensor (e.g., 0, 1, 2)
            translation_child: List of translation mappings from API
            
        Returns:
            Translated text value (e.g., "Not Charging") or None if no match
        """
        # Convert value to string for comparison (API uses string values in translations)
        value_str = str(int(value))  # Convert 0.0 to "0", 1.0 to "1", etc.
        
        for translation in translation_child:
            if translation.get("value") == value_str:
                # Use English result if available, fallback to Chinese
                return translation.get("resultE") or translation.get("result")
        
        # No translation found
        return None

    @property
    def native_value(self) -> str | float | None:
        """Return the native value of the sensor."""
        device_id = self._device["id"]
        device_name = self._device.get("equipmentName", "Unknown")
        device_data = self.coordinator.data.get("device_data", {}).get(device_id, {})
        
        if not device_data:
            _LOGGER.debug("No device data available for %s (ID: %s)", device_name, device_id)
            return None

        data_identifier = self._variable["dataIdentifier"]
        data_point_id = self._variable.get("dataPointId")
        
        # First try to get value from latest data
        # NOTE: latest_data response uses dataPointId, not dataIdentifier!
        latest_data = device_data.get("latest_data", {})
        if latest_data.get("data", {}).get("list") and data_point_id:
            for data_point in latest_data["data"]["list"]:
                if data_point.get("dataPointId") == data_point_id:
                    try:
                        # NOTE: latest_data values are ALREADY formatted with decimals applied
                        # The API returns "50.00" not "5000", so we use the value as-is
                        value = float(data_point.get("value", 0))
                        
                        # Check if this parameter has translation mappings (enum values)
                        translation_child = self._variable.get("translationChild", [])
                        if translation_child:
                            # Value needs to be translated (e.g., 0 -> "Not Charging")
                            translated_value = self._translate_value(value, translation_child)
                            if translated_value is not None:
                                _LOGGER.debug(
                                    "Sensor %s (%s) got translated value from latest_data: %s -> %s",
                                    self.name, data_identifier, value, translated_value
                                )
                                if hasattr(self, '_last_valid_value'):
                                    self._last_valid_value = translated_value
                                if hasattr(self, '_value_source'):
                                    self._value_source = "latest_data (translated)"
                                return translated_value
                        
                        _LOGGER.debug(
                            "Sensor %s (%s) got value from latest_data: %s",
                            self.name, data_identifier, value
                        )
                        if hasattr(self, '_last_valid_value'):
                            self._last_valid_value = value
                        if hasattr(self, '_value_source'):
                            self._value_source = "latest_data"
                        return value
                    except (ValueError, TypeError) as err:
                        _LOGGER.warning(
                            "Failed to convert value for %s: %s (error: %s)",
                            data_identifier, data_point.get("value"), err
                        )
                        return data_point.get("value")
        else:
            _LOGGER.debug(
                "No latest_data available for %s - latest_data status: %s",
                device_name,
                "present but empty" if "latest_data" in device_data else "not present"
            )

        # Fallback to checking variable configuration data
        for group in device_data.get("data", {}).get("variableGroupList", []):
            for variable in group.get("variableList", []):
                if variable.get("dataIdentifier") == data_identifier:
                    # Try multiple value fields
                    for value_field in ["currentValue", "value", "defaultValue"]:
                        if value_field in variable:
                            try:
                                value = float(variable[value_field])
                                # Apply decimal formatting if specified
                                decimal = variable.get("decimal", "0")
                                if decimal and decimal.isdigit():
                                    value = value / (10 ** int(decimal))
                                _LOGGER.debug(
                                    "Sensor %s (%s) got value from variable.%s: %s",
                                    self.name, data_identifier, value_field, value
                                )
                                if hasattr(self, '_last_valid_value'):
                                    self._last_valid_value = value
                                if hasattr(self, '_value_source'):
                                    self._value_source = f"variable.{value_field}"
                                return value
                            except (ValueError, TypeError):
                                # Try returning as-is if not numeric
                                return variable[value_field]
        
        # Log when we can't find any value
        # Check if attribute exists (backward compatibility with existing sensors)
        if hasattr(self, '_last_valid_value') and self._last_valid_value is not None:
            # Return last known value if we have one
            _LOGGER.debug(
                "No current value for sensor %s (%s) in device %s - using last known value: %s",
                self.name, data_identifier, device_name, self._last_valid_value
            )
            if hasattr(self, '_value_source'):
                self._value_source = "last_known (stale)"
            return self._last_valid_value
        
        _LOGGER.debug(
            "No value found for sensor %s (%s) in device %s - parameter not in latest_data",
            self.name, data_identifier, device_name
        )
        if hasattr(self, '_value_source'):
            self._value_source = "none"
        return None

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        # If coordinator has never successfully updated, entity is unavailable
        if not self.coordinator.last_update_success and not self.coordinator.data:
            return False
            
        # If we have data, check if our specific device data is available
        if self.coordinator.data:
            device_id = self._device["id"]
            device_data = self.coordinator.data.get("device_data", {}).get(device_id, {})
            # Entity is available if we have device data, even if latest update failed
            return bool(device_data)
        
        # Fallback to coordinator success status
        return self.coordinator.last_update_success

    @property
    def entity_category(self) -> EntityCategory | None:
        """Return the entity category if this is a diagnostic sensor."""
        data_identifier = self._variable.get("dataIdentifier", "")
        # Check if this sensor should be marked as diagnostic
        if any(diag in data_identifier for diag in DIAGNOSTIC_SENSORS):
            return EntityCategory.DIAGNOSTIC
        return None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional state attributes."""
        attrs = {
            "data_identifier": self._variable.get("dataIdentifier"),
            "variable_name": self._variable.get("variableName"),
            "data_source": getattr(self, '_value_source', None) or "none",
        }
        
        # Add parameter info for diagnostic purposes
        if self._variable.get("dataPointId"):
            attrs["data_point_id"] = self._variable["dataPointId"]
        if self._variable.get("unit"):
            attrs["api_unit"] = self._variable["unit"]
        
        # Show if parameter has real-time data available
        device_id = self._device["id"]
        device_data = self.coordinator.data.get("device_data", {}).get(device_id, {})
        latest_data = device_data.get("latest_data", {})
        if latest_data.get("data", {}).get("list"):
            has_latest = any(
                dp.get("dataIdentifier") == self._variable.get("dataIdentifier")
                for dp in latest_data["data"]["list"]
            )
            attrs["has_latest_data"] = has_latest
            if not has_latest:
                attrs["info"] = "Parameter not included in real-time updates"
        
        return attrs

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self.async_write_ha_state()


class SolarGuardianDeviceInfoSensor(CoordinatorEntity, SensorEntity):
    """Representation of a SolarGuardian device information sensor (text)."""

    def __init__(
        self,
        coordinator: SolarGuardianDataUpdateCoordinator,
        device: dict[str, Any],
        sensor_id: str,
        sensor_config: dict[str, Any],
        value: str,
    ) -> None:
        """Initialize the device info sensor."""
        super().__init__(coordinator)
        
        self._device = device
        self._sensor_id = sensor_id
        self._sensor_config = sensor_config
        self._value = value
        self._attr_name = f"{device['equipmentName']} {sensor_config['name']}"
        self._attr_unique_id = f"{device['id']}{sensor_id}"
        
        # Set sensor attributes (text sensors have no unit/device_class)
        self._attr_icon = sensor_config.get("icon")
        
        # Device info
        self._attr_device_info = {
            "identifiers": {(DOMAIN, str(device["id"]))},
            "name": device["equipmentName"],
            "manufacturer": "Epever",
            "model": device.get("productName", "Solar Inverter"),
            "sw_version": device.get("version"),
        }

    @property
    def native_value(self) -> str:
        """Return the value of the sensor."""
        # Update value from coordinator if device status changed
        device_id = self._device["id"]
        devices_data = self.coordinator.data.get("devices", {})
        
        for station_id, devices in devices_data.items():
            for device in devices.get("data", {}).get("list", []):
                if device["id"] == device_id:
                    # Update dynamic values
                    if self._sensor_id == "_device_status_text":
                        return "Online" if device.get("status") == 1 else "Offline"
                    # For static values, return stored value
                    break
        
        return self._value

    @property
    def entity_category(self) -> EntityCategory | None:
        """Return entity category - device info sensors are diagnostic."""
        return EntityCategory.DIAGNOSTIC