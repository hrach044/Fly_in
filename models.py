"""Define the data models used by the drone simulation."""

from enum import Enum


class ZoneType(Enum):
    """Define the supported zone types."""

    NORMAL = "normal"
    BLOCKED = "blocked"
    RESTRICTED = "restricted"
    PRIORITY = "priority"


class Zone:
    """Store a zone's location and settings.

    Attributes:
        name: Zone name.
        x: Horizontal coordinate.
        y: Vertical coordinate.
        zone_type: Type of zone.
        color: Display color name.
        capacity: Maximum number of drones allowed in the zone.
    """

    def __init__(self, name: str, x: int, y: int, zone_type: ZoneType,
                 color: str = "none", capacity: int = 1):
        self.name = name
        self.x = x
        self.y = y
        self.zone_type = zone_type
        self.color = color
        self.capacity = capacity


class Connection:
    """Store a connection between two zones.

    Attributes:
        zone1: Name of the first connected zone.
        zone2: Name of the second connected zone.
        capacity: Maximum number of drones using the connection per turn.
    """

    def __init__(self, zone1: str, zone2: str, capacity: int = 1):
        self.zone1 = zone1
        self.zone2 = zone2
        self.capacity = capacity


class Drone:
    """Track a drone along its assigned path.

    Attributes:
        id: Drone identifier.
        path: Ordered zone names assigned to the drone.
        current_index: Index of the drone's current zone in its path.
        transit_to: Restricted zone the drone is currently entering, if any.
    """

    def __init__(self, id: int, path: list[str], current_index: int = 0):
        self.id = id
        self.path = path
        self.current_index = current_index
        self.transit_to: str | None = None

    def is_done(self) -> bool:
        """Check whether the drone has reached the last zone.

        Returns:
            Whether the drone is at the end of its path.
        """
        return self.current_index == len(self.path) - 1

    def current_zone(self) -> str:
        """Return the zone at the drone's current path index.

        While the drone is on a link to a restricted zone, this is the
        zone it left, not the one it is heading to.

        Returns:
            The zone at the drone's current path index.
        """
        return self.path[self.current_index]
