from models import Zone, ZoneType, Connection
from graph import Graph

def parse_zone(line: str) -> Zone:
    cut = line.split()
    metadata: dict = {}
    zone_type = ZoneType.NORMAL
    color = "none"
    max_drones = 1
    name = cut[1]
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
        graph = Graph()
        nb_drones: int = 0
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            elif line.startswith("nb_drones:"):
                cut = line.split(":")
                nb_drones = int(cut[1].strip())
            elif line.startswith("start_hub:"):
                zone = parse_zone(line)
                graph.add_zone(zone)
                graph.start = zone
            elif line.startswith("end_hub:"):
                zone = parse_zone(line)
                graph.add_zone(zone)
                graph.end = zone
            elif line.startswith("hub:"):
                zone = parse_zone(line)
                graph.add_zone(zone)
            elif line.startswith("connection:"):
                max_link_capacity = 1
                cut = line.split()
                names = cut[1].split("-")
                if names[0] not in graph.zones or names[1] not in graph.zones:
                    raise ValueError(f"Unknown zone in connection: {line}")
                if len(cut) == 3:
                    max_link_capacity = int(cut[2].strip("[]").split("=")[1])
                connection = Connection(names[0], names[1], max_link_capacity)
                graph.add_connection(connection)

            
    return nb_drones, graph


