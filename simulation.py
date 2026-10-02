from models import Drone, ZoneType
from graph import Graph, link_key


def create_drones(paths: list[list[str]]) -> list[Drone]:
    drones: list[Drone] = []
    for i, path in enumerate(paths):
        drones.append(Drone(i + 1, path))
    return drones


def count_in_zone(drones: list[Drone], zone_name: str) -> int:
    count = 0
    occupied: str
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


def simulate(drones: list[Drone], graph: Graph) -> list[list[str]]:
    turn = 0
    log: list[list[str]] = []
    while not all(drone.is_done() for drone in drones):
        turn += 1
        turns: list[str] = []
        link_usage: dict[tuple[str, str], int] = {}
        for drone in drones:
            if drone.transit_to is not None:
                key = link_key(drone.current_zone(), drone.transit_to)
                link_usage[key] = link_usage.get(key, 0) + 1
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
            if ((next_zone_name == graph.end.name or
                count_in_zone(drones, next_zone_name) < next_zone.capacity) and
                    link_has_room):
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
