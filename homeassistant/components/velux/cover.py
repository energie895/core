"""Support for Velux covers."""
from __future__ import annotations

from pyvlx import OpeningDevice, Position
from pyvlx.opening_device import Awning, Blind, GarageDoor, Gate, RollerShutter, Window

from homeassistant.components.cover import (
    ATTR_POSITION,
    ATTR_TILT_POSITION,
    CoverDeviceClass,
    CoverEntity,
    CoverEntityFeature,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

from . import DATA_VELUX, VeluxEntity

PARALLEL_UPDATES = 1


async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    async_add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up cover(s) for Velux platform."""
    entities = []
    for node in hass.data[DATA_VELUX].pyvlx.nodes:
        if isinstance(node, OpeningDevice):
            entities.append(VeluxCover(node))
    async_add_entities(entities)


class VeluxCover(VeluxEntity, CoverEntity):
    """Representation of a Velux cover."""

    @property
    def supported_features(self):
        """Flag supported features."""
        supported_features = (
            CoverEntityFeature.OPEN
            | CoverEntityFeature.CLOSE
            | CoverEntityFeature.SET_POSITION
            | CoverEntityFeature.STOP
        )
        if self.current_cover_tilt_position is not None:
            supported_features |= (
                CoverEntityFeature.OPEN_TILT
                | CoverEntityFeature.CLOSE_TILT
                | CoverEntityFeature.SET_TILT_POSITION
                | CoverEntityFeature.STOP_TILT
            )
        return supported_features

    @property
    def current_cover_position(self):
        """Return the current position of the cover."""
        return 100 - self.node.position.position_percent

    @property
    def current_cover_tilt_position(self):
        """Return the current position of the cover."""
        if isinstance(self.node, Blind):
            return 100 - self.node.orientation.position_percent
        return None

    @property
    def device_class(self):
        """Define this cover as either awning, blind, garage, gate, shutter or window."""
        if isinstance(self.node, Awning):
            return CoverDeviceClass.AWNING
        if isinstance(self.node, Blind):
            return CoverDeviceClass.BLIND
        if isinstance(self.node, GarageDoor):
            return CoverDeviceClass.GARAGE
        if isinstance(self.node, Gate):
            return CoverDeviceClass.GATE
        if isinstance(self.node, RollerShutter):
            return CoverDeviceClass.SHUTTER
        if isinstance(self.node, Window):
            return CoverDeviceClass.WINDOW
        return CoverDeviceClass.WINDOW

    @property
    def is_closed(self):
        """Return if the cover is closed."""
        return self.node.position.closed

    async def async_close_cover(self, **kwargs):
        """Close the cover."""
        await self.node.close(wait_for_completion=False)

    async def async_open_cover(self, **kwargs):
        """Open the cover."""
        await self.node.open(wait_for_completion=False)

    async def async_set_cover_position(self, **kwargs):
        """Move the cover to a specific position."""
        position_percent = 100 - kwargs[ATTR_POSITION]

        await self.node.set_position(
            Position(position_percent=position_percent), wait_for_completion=False
        )

    async def async_stop_cover(self, **kwargs):
        """Stop the cover."""
        await self.node.stop(wait_for_completion=False)

    async def async_close_cover_tilt(self, **kwargs):
        """Close cover tilt."""
        await self.node.close_orientation(wait_for_completion=False)

    async def async_open_cover_tilt(self, **kwargs):
        """Open cover tilt."""
        await self.node.open_orientation(wait_for_completion=False)

    async def async_stop_cover_tilt(self, **kwargs):
        """Stop cover tilt."""
        await self.node.stop_orientation(wait_for_completion=False)

    async def async_set_cover_tilt_position(self, **kwargs):
        """Move cover tilt to a specific position."""
        position_percent = 100 - kwargs[ATTR_TILT_POSITION]
        orientation = Position(position_percent=position_percent)
        await self.node.set_orientation(
            orientation=orientation, wait_for_completion=False
        )
