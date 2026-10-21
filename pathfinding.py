"""Find paths through a graph using zone costs."""

from models import Zone, ZoneType
from graph import Graph
import heapq


def zone_cost(zone: Zone) -> float | None:
    """Return the traversal cost for a zone type.

    Args:
        zone: Zone whose type determines the cost.

    Returns:
        The cost, or None when the zone type has no cost.
    """
    if zone.zone_type == ZoneType.PRIORITY:
        return 0.9
    elif zone.zone_type == ZoneType.NORMAL:
        return 1
    elif zone.zone_type == ZoneType.RESTRICTED:
        return 2
    else:
        return None


def assign_paths(graph: Graph, nb_drones: int) -> list[list[str]]:
    """Assign a path to each drone while tracking zone load.

    Args:
        graph: Graph through which to find paths.
        nb_drones: Number of paths to assign.

    Returns:
        The assigned paths.
    """
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
    """Find a lowest-cost path between two zones.

    Args:
        graph: Graph to search.
        start_name: Name of the starting zone.
        end_name: Name of the ending zone.
        extra: Additional cost for each zone.

    Returns:
        The ordered zone names along the path.

    Raises:
        ValueError: If the ending zone is unreachable.
    """
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
