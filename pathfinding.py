from models import Zone, ZoneType
from graph import Graph

def zone_cost(zone: Zone) -> int | None:
    if zone.zone_type in (ZoneType.NORMAL, ZoneType.PRIORITY):
        return 1
    elif zone.zone_type == ZoneType.RESTRICTED:
        return 2
    else:
        return None


def path_finding(graph: Graph, start_name: str, end_name: str) -> dict[str, float]:
    distances: dict[str, float] = {}
    for name in graph.zones.keys():
        distances[name] = float('inf')
    distances[start_name] = 0
    return distances