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


class Connection:
    def __init__(self, zone1: str, zone2: str, capacity: int = 1):
        self.zone1 = zone1
        self.zone2 = zone2
        self.capacity = capacity