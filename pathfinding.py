from models import Zone, ZoneType
from graph import Graph
import heapq


def zone_cost(zone: Zone) -> int | None:
    if zone.zone_type in (ZoneType.NORMAL, ZoneType.PRIORITY):
        return 1
    elif zone.zone_type == ZoneType.RESTRICTED:
        return 2
    else:
        return None


def assign_paths(graph: Graph, nb_drones: int) -> list[list[str]]:
    load: dict[str, int] = {}
    paths: list[list[str]] = []
    for _ in range(nb_drones):
        path = path_finding(graph, graph.start.name, graph.end.name, load)
        paths.append(path)
        for name in path[1:-1]:
            load[name] = load.get(name, 0) + 1
    return paths


def path_finding(graph: Graph, start_name: str, end_name: str,
                 extra: dict[str, int]) -> list[str]:
    distances: dict[str, float] = {}
    for name in graph.zones.keys():
        distances[name] = float('inf')
    distances[start_name] = 0
    came_from: dict[str, str] = {}
    heap: list[tuple[float, str]] = [(0, start_name)]
    while heap:
        current_cost, current_name = heapq.heappop(heap)
        for neighbor_name in graph.get_neighbors(current_name):
            neighbor_zone = graph.zones[neighbor_name]
            cost = zone_cost(neighbor_zone)
            if cost is None:
                continue
            new_cost = current_cost + cost + extra.get(neighbor_name, 0)
            if new_cost < distances[neighbor_name]:
                distances[neighbor_name] = new_cost
                came_from[neighbor_name] = current_name
                heapq.heappush(heap, (new_cost, neighbor_name))
    if distances[end_name] == float('inf'):
        raise ValueError("No path from start_hub to end_hub")
    path = [end_name]
    while path[-1] != start_name:
        path.append(came_from[path[-1]])
    path.reverse()
    return path
