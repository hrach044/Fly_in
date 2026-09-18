from enum import Enum

class ZoneType(Enum):
    NORMAL = "normal"
    BLOCKED = "blocked"
    RESTRICTED = "restricted"
    PRIORITY = "priority"


class Zone:
    def __init__(self, name: str, x: int, y: int, zone_type: ZoneType, color: str = "none", capacity: int = 1):
        self.name = name
        self.x = x
        self.y = y
        self.zone_type = zone_type
        self.color = color
        self.capacity = capacity

    def __repr__(self) -> str:
        return f"Zone(name={self.name!r}, x={self.x}, y={self.y}, zone_type={self.zone_type}, color={self.color!r}, capacity={self.capacity})"
        


class Connection:
    def __init__(self, zone1: str, zone2: str, capacity: int = 1):
        self.zone1 = zone1
        self.zone2 = zone2
        self.capacity = capacity

    def __repr__(self) -> str:
        return f"Connection(zone1={self.zone1!r}, zone2={self.zone2!r}, capacity={self.capacity})"