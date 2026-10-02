from models import Zone, Connection


def link_key(first: str, second: str) -> tuple[str, str]:
    a, b = sorted((first, second))
    return (a, b)


class Graph:
    def __init__(self, start: Zone, end: Zone) -> None:
        self.start = start
        self.end = end
        self.zones: dict[str, Zone] = {}
        self.connections: list[Connection] = []
        self.links: dict[tuple[str, str], int] = {}

    def add_zone(self, zone: Zone) -> None:
        self.zones[zone.name] = zone

    def add_connection(self, connection: Connection) -> None:
        self.connections.append(connection)
        key = link_key(connection.zone1, connection.zone2)
        self.links[key] = connection.capacity

    def get_neighbors(self, zone_name: str) -> list[str]:
        neighbors = []
        for connection in self.connections:
            if connection.zone1 == zone_name:
                neighbors.append(connection.zone2)
            elif connection.zone2 == zone_name:
                neighbors.append(connection.zone1)
        return neighbors
