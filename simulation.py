"""Simulate drone movement through a graph."""

from models import Drone, ZoneType
from graph import Graph, link_key


def create_drones(paths: list[list[str]]) -> list[Drone]:
    """Create drones from the supplied paths.

    Args:
        paths: Paths assigned to the drones.

    Returns:
        The created drones.
    """
    drones: list[Drone] = []
    for i, path in enumerate(paths):
        drones.append(Drone(i + 1, path))
    return drones


def count_in_zone(drones: list[Drone], zone_name: str) -> int:
    """Count unfinished drones occupying a zone.

    Count a drone in transit as occupying its restricted destination zone.

    Args:
        drones: Drones to inspect.
        zone_name: Name of the zone to count.

    Returns:
        The number of matching drones.
    """
    count = 0
    for drone in drones:
        if drone.is_done():
            continue
        if drone.transit_to is not None:
            occupied = drone.transit_to
        else:
            occupied = drone.current_zone()
        if occupied == zone_name:
            count += 1
    return count


def leaving_to_end(drones: list[Drone], zone_name: str,
                   graph: Graph) -> int:
    """Count drones leaving a zone for the end.

    Args:
        drones: Drones to inspect.
        zone_name: Name of the zone to inspect.
        graph: Graph containing the end zone and link capacities.

    Returns:
        The count limited by the link capacity to the end.
    """
    count = 0
    for drone in drones:
        if drone.is_done() or drone.transit_to is not None:
            continue
        if drone.current_zone() != zone_name:
            continue
        if drone.path[drone.current_index + 1] == graph.end.name:
            count += 1
    if count == 0:
        return 0
    return min(count, graph.links[link_key(zone_name, graph.end.name)])


def simulate(drones: list[Drone], graph: Graph) -> list[list[str]]:
    """Simulate drones moving through the graph.

    Args:
        drones: Drones to move.
        graph: Graph containing zones and link capacities.

    Returns:
        The per-turn log of drone movements.

    Raises:
        RuntimeError: If no drone can move before all drones are done.
    """
    log: list[list[str]] = []
    while not all(drone.is_done() for drone in drones):
        turns: list[str] = []
        link_usage: dict[tuple[str, str], int] = {}
        for drone in drones:
            if drone.is_done():
                continue
            if drone.transit_to is not None:
                drone.current_index += 1
                drone.transit_to = None
                turns.append(f"D{drone.id}-{drone.current_zone()}")
                continue
            next_zone_name = drone.path[drone.current_index + 1]
            next_zone = graph.zones[next_zone_name]
            key = link_key(drone.current_zone(), next_zone_name)
            link_has_room = link_usage.get(key, 0) < graph.links[key]
            if next_zone_name == graph.end.name:
                zone_has_room = True
            else:
                occupied = count_in_zone(drones, next_zone_name)
                if next_zone.zone_type == ZoneType.RESTRICTED:
                    occupied -= leaving_to_end(drones, next_zone_name, graph)
                zone_has_room = occupied < next_zone.capacity
            if zone_has_room and link_has_room:
                if next_zone.zone_type == ZoneType.RESTRICTED:
                    drone.transit_to = next_zone_name
                    turns.append(f"D{drone.id}-{drone.current_zone()}"
                                 f"-{next_zone_name}")
                else:
                    drone.current_index += 1
                    turns.append(f"D{drone.id}-{next_zone_name}")
                link_usage[key] = link_usage.get(key, 0) + 1
        if not turns:
            raise RuntimeError("Deadlock: no drone can move")
        log.append(turns)
    return log
