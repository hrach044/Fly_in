"""Represent zones and connections as a graph."""

from models import Zone, Connection


def link_key(first: str, second: str) -> tuple[str, str]:
    """Return a sorted key for a link between two zones.

    Args:
        first: Name of one zone.
        second: Name of the other zone.

    Returns:
        The zone names in sorted order.
    """
    a, b = sorted((first, second))
    return (a, b)


class Graph:
    """Store zones, connections, and link capacities.

    Attributes:
        start: Starting zone in the graph.
        end: Ending zone in the graph.
        zones: Zones indexed by name.
        connections: Connections in the graph.
        links: Link capacities indexed by sorted zone-name pairs.
    """

    def __init__(self, start: Zone, end: Zone) -> None:
        self.start = start
        self.end = end
        self.zones: dict[str, Zone] = {}
        self.connections: list[Connection] = []
        self.links: dict[tuple[str, str], int] = {}

    def add_zone(self, zone: Zone) -> None:
        """Add a zone indexed by its name.

        Args:
            zone: Zone to add.
        """
        self.zones[zone.name] = zone

    def add_connection(self, connection: Connection) -> None:
        """Add a connection and record its link capacity.

        Args:
            connection: Connection to add.
        """
        self.connections.append(connection)
        key = link_key(connection.zone1, connection.zone2)
        self.links[key] = connection.capacity

    def get_neighbors(self, zone_name: str) -> list[str]:
        """Return zones directly connected to the named zone.

        Args:
            zone_name: Name of the zone whose neighbors to find.

        Returns:
            Names of connected zones.
        """
        neighbors = []
        for connection in self.connections:
            if connection.zone1 == zone_name:
                neighbors.append(connection.zone2)
            elif connection.zone2 == zone_name:
                neighbors.append(connection.zone1)
        return neighbors
