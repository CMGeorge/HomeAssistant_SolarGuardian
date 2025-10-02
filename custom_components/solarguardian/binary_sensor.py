"""Support for SolarGuardian binary sensors."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import SolarGuardianDataUpdateCoordinator
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up SolarGuardian binary sensors based on a config entry."""
    coordinator: SolarGuardianDataUpdateCoordinator = hass.data[DOMAIN][
        config_entry.entry_id
    ]["coordinator"]

    entities = []

    # Wait for initial data
    if not coordinator.data:
        return

    # Create binary sensors for each device
    for _station_id, devices in coordinator.data.get("devices", {}).items():
        for device in devices.get("data", {}).get("list", []):
            # Device online status
            entities.append(
                SolarGuardianDeviceStatusSensor(coordinator, device, "online")
            )

            # Device alarm status
            entities.append(
                SolarGuardianDeviceStatusSensor(coordinator, device, "alarm")
            )

    async_add_entities(entities)


class SolarGuardianDeviceStatusSensor(CoordinatorEntity, BinarySensorEntity):
    """Representation of a SolarGuardian device status binary sensor."""

    def __init__(
        self,
        coordinator: SolarGuardianDataUpdateCoordinator,
        device: dict[str, Any],
        sensor_type: str,
    ) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator)

        self._device = device
        self._sensor_type = sensor_type

        if sensor_type == "online":
            self._attr_name = f"{device['equipmentName']} Online"
            self._attr_device_class = BinarySensorDeviceClass.CONNECTIVITY
            self._attr_icon = "mdi:wifi"
        elif sensor_type == "alarm":
            self._attr_name = f"{device['equipmentName']} Alarm"
            self._attr_device_class = BinarySensorDeviceClass.PROBLEM
            self._attr_icon = "mdi:alert"

        self._attr_unique_id = f"{device['id']}_{sensor_type}"

        # Device info
        self._attr_device_info = {
            "identifiers": {(DOMAIN, str(device["id"]))},
            "name": device["equipmentName"],
            "manufacturer": "Epever",
            "model": device.get("productName", "Solar Inverter"),
            "sw_version": device.get("version"),
        }

    @property
    def is_on(self) -> bool | None:
        """Return true if the binary sensor is on."""
        device_id = self._device["id"]

        # Look for device status in the current data
        for _station_id, devices in self.coordinator.data.get("devices", {}).items():
            for device in devices.get("data", {}).get("list", []):
                if device["id"] == device_id:
                    if self._sensor_type == "online":
                        # Check online status (1 = online, 0 = offline)
                        return device.get("onlineStatus") == 1
                    elif self._sensor_type == "alarm":
                        # Check alarm status (1 = alarm, 0 = normal)
                        return device.get("datapointAlarm", 0) == 1

        return None

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.coordinator.last_update_success

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self.async_write_ha_state()
