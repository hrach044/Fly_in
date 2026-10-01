from models import Zone, ZoneType
from graph import Graph
import heapq
from simulation import simulate, create_drones

def zone_cost(zone: Zone) -> int | None:
    if zone.zone_type in (ZoneType.NORMAL, ZoneType.PRIORITY):
        return 1
    elif zone.zone_type == ZoneType.RESTRICTED:
        return 2
    else:
        return None


def path_finding(graph: Graph, start_name: str, end_name: str) -> list[str]:
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
            new_cost = current_cost + cost
            if new_cost < distances[neighbor_name]:
                distances[neighbor_name] = new_cost
                came_from[neighbor_name] = current_name
                heapq.heappush(heap, (new_cost, neighbor_name))
    path = [end_name]
    while path[-1] != start_name:
        path.append(came_from[path[-1]])
    path.reverse()
    return path

if __name__ == "__main__":
    from parser import read_map
    try:
        nb_drones, graph = read_map("map.txt")
        path = path_finding(graph, graph.start.name, graph.end.name)
        print(path)
        print(simulate(create_drones(nb_drones, path), graph))
    except ValueError as e:
        print(f"Error: {e}")
       
    