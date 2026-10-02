from enum import Enum


class ZoneType(Enum):
    NORMAL = "normal"
    BLOCKED = "blocked"
    RESTRICTED = "restricted"
    PRIORITY = "priority"


class Zone:
    def __init__(self, name: str, x: int, y: int, zone_type: ZoneType,
                 color: str = "none", capacity: int = 1):
        self.name = name
        self.x = x
        self.y = y
        self.zone_type = zone_type
        self.color = color
        self.capacity = capacity

    def __repr__(self) -> str:
        return (f"Zone(name={self.name!r}, x={self.x}, y={self.y}, "
                f"zone_type={self.zone_type}, color={self.color!r}, "
                f"capacity={self.capacity})")


class Connection:
    def __init__(self, zone1: str, zone2: str, capacity: int = 1):
        self.zone1 = zone1
        self.zone2 = zone2
        self.capacity = capacity

    def __repr__(self) -> str:
        return (f"Connection(zone1={self.zone1!r}, zone2={self.zone2!r}, "
                f"capacity={self.capacity})")


class Drone:
    def __init__(self, id: int, path: list[str], current_index: int = 0):
        self.id = id
        self.path = path
        self.current_index = current_index
        self.transit_to: str | None = None

    def is_done(self) -> bool:
        return self.current_index == len(self.path) - 1

    def current_zone(self) -> str:
        return self.path[self.current_index]
