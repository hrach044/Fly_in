from models import Zone, ZoneType, Connection
from graph import Graph, link_key


def parse_zone(line: str) -> Zone:
    cut = line.split()
    metadata: dict[str, str] = {}
    zone_type = ZoneType.NORMAL
    color = "none"
    max_drones = 1
    name = cut[1]
    if "-" in name:
        raise ValueError(f"Zone name cannot contain a dash: {name}")
    x = int(cut[2])
    y = int(cut[3])
    cut = cut[4:]
    for i in cut:
        metadata[i.strip("[]").split("=")[0]] = i.strip("[]").split("=")[1]
    for key, value in metadata.items():
        if key == "color":
            color = value
        elif key == "zone":
            zone_type = ZoneType(value)
        elif key == "max_drones":
            max_drones = int(value)
    zone = Zone(name, x, y, zone_type, color, max_drones)
    return zone


def read_map(path: str) -> tuple[int, Graph]:
    with open(path, "r") as f:
        zones: dict[str, Zone] = {}
        connections: list[Connection] = []
        seen_links: set[tuple[str, str]] = set()
        start: Zone | None = None
        end: Zone | None = None
        nb_drones: int = 0
        for line_number, line in enumerate(f, 1):
            try:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                elif line.startswith("nb_drones:"):
                    cut = line.split(":")
                    nb_drones = int(cut[1].strip())
                    if nb_drones < 1:
                        raise ValueError("nb_drones must be a positive integer")
                elif line.startswith("start_hub:"):
                    zone = parse_zone(line)
                    if zone.name in zones:
                        raise ValueError(f"Duplicate zone name: {zone.name}")
                    zones[zone.name] = zone
                    if start is not None:
                        raise ValueError("Second start_hub found")
                    start = zone
                elif line.startswith("end_hub:"):
                    zone = parse_zone(line)
                    if zone.name in zones:
                        raise ValueError(f"Duplicate zone name: {zone.name}")
                    zones[zone.name] = zone
                    if end is not None:
                        raise ValueError("Second end_hub found")
                    end = zone
                elif line.startswith("hub:"):
                    zone = parse_zone(line)
                    if zone.capacity < 1:
                        raise ValueError("max_drones must be "
                                         "a positive integer")
                    if zone.name in zones:
                        raise ValueError(f"Duplicate zone name: {zone.name}")
                    zones[zone.name] = zone
                elif line.startswith("connection:"):
                    max_link_capacity = 1
                    cut = line.split()
                    names = cut[1].split("-")
                    if names[0] not in zones or names[1] not in zones:
                        raise ValueError(f"Unknown zone in connection: {line}")
                    key = link_key(names[0], names[1])
                    if key in seen_links:
                        raise ValueError(f"Duplicate connection: "
                                         f"{names[0]}-{names[1]}")
                    seen_links.add(key)
                    if len(cut) == 3:
                        max_link_capacity = int(
                            cut[2].strip("[]").split("=")[1]
                            )
                    if max_link_capacity < 1:
                        raise ValueError("max_link_capacity must "
                                         "be a positive integer")
                    connection = Connection(
                        names[0], names[1], max_link_capacity
                        )
                    connections.append(connection)
            except (ValueError, IndexError) as e:
                raise ValueError(f"line {line_number}: {e}")
        if start is None or end is None:
            raise ValueError("Map needs one start_hub and one end_hub")
        graph = Graph(start, end)
        for zone in zones.values():
            graph.add_zone(zone)
        for connection in connections:
            graph.add_connection(connection)
    return nb_drones, graph
