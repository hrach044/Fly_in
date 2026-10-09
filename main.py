import sys
from parser import read_map
from pathfinding import assign_paths
from simulation import create_drones, simulate
from visual import print_colored_log
from output import print_log


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: python3 main.py <map_file>")
        sys.exit(1)
    try:
        nb_drones, graph = read_map(sys.argv[1])
    except (ValueError, OSError) as e:
        print(f"Error: {e}")
        sys.exit(1)
    try:
        paths = assign_paths(graph, nb_drones)
        log = simulate(create_drones(paths), graph)
    except (ValueError, RuntimeError) as e:
        print(f"Error: {e}")
        sys.exit(1)
    if sys.stdout.isatty():
        print_colored_log(log, graph)
    else:
        print_log(log)


if __name__ == "__main__":
    main()
