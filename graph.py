from models import Zone, Connection

class Graph:
    def __init__(self):
        self.start: Zone | None = None
        self.end: Zone | None = None
        self.zones: dict[str, Zone] = {}
        self.connections: list[Connection] = []

    def add_zone(self, zone: Zone) -> None:
        self.zones[zone.name] = zone

    def add_connection(self, connection: Connection) -> None:
        self.connections.append(connection)

    def get_neighbors(self, zone_name: str) -> list[str]:
        neighbors = []
        for connection in self.connections:
            if connection.zone1 == zone_name:
                neighbors.append(connection.zone2)
            elif connection.zone2 == zone_name:
                neighbors.append(connection.zone1)
        return neighbors