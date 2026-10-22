*This project has been created as part of the 42 curriculum by hmnatsak.*

# Fly-in

## Description

Fly-in routes a fleet of drones from one start zone to one end zone through
a network of connected zones, in as few simulation turns as possible.
Zones and connections have capacities, restricted zones cost 2 turns,
priority zones are preferred and blocked zones cannot be used. The program
reads a map file, finds a path for every drone, simulates the movement turn
by turn and prints one line per turn. No graph library is used: the graph is
built by hand.

The code uses Python 3.10+, type hints everywhere, passes `flake8` and `mypy`,
and has docstrings (PEP 257, Google style) on every module, class and function.

## Instructions

Requirements: Python 3.10+, `flake8` and `mypy` (installed by `make install`).

| Command | What it does |
|---|---|
| `make install` | Install `flake8` and `mypy` with pip |
| `make run` | Run the simulation on `map.txt` |
| `make debug` | Run the simulation under `pdb` |
| `make lint` | Run `flake8 .` and `mypy` with the flags from the subject |
| `make clean` | Remove `__pycache__` and `.mypy_cache` |

Run any map directly, and pipe or redirect to get the plain output:

```
python3 main.py maps/medium/02_circular_loop.txt
python3 main.py map.txt > result.txt
```

Every error stops the program with `Error: ...` and exit code 1, for example
`Error: line 3: Unknown metadata key: colour` or
`Error: No path from start_hub to end_hub`.

## Input and output format

```
nb_drones: <positive integer>
start_hub: <name> <x> <y> [metadata]
end_hub:   <name> <x> <y> [metadata]
hub:       <name> <x> <y> [metadata]
connection: <name1>-<name2> [metadata]
```

- The first line must be `nb_drones`. Comments start with `#`.
- Zone names may not contain dashes or spaces. Connections link only
  zones defined above them, and `a-b` and `b-a` are the same connection.
- Zone metadata: `zone=` (`normal`, `restricted`, `priority`, `blocked`),
  `color=` (any word), `max_drones=` (positive integer, default 1).
- Connection metadata: `max_link_capacity=` (positive integer, default 1).
- `max_drones` on the start and end zone is ignored: both are unlimited.

Output: one line per turn with the moves of that turn, separated by spaces.
`D<ID>-<zone>` means the drone entered that zone. `D<ID>-<from>-<to>` means
the drone is on the connection to a restricted zone and arrives next turn.
Drones that do not move are omitted, delivered drones are no longer listed.

## Project structure

| File | Content |
|---|---|
| `models.py` | `ZoneType`, `Zone`, `Connection`, `Drone` |
| `graph.py` | `link_key()` and the `Graph` class |
| `parser.py` | `parse_zone()`, `read_map()` |
| `pathfinding.py` | `zone_cost()`, `assign_paths()`, `path_finding()` |
| `simulation.py` | `create_drones()`, `count_in_zone()`, `leaving_to_end()`, `simulate()` |
| `output.py` | `print_log()` (plain output) |
| `visual.py` | colors, `replay()`, `zone_state()`, `print_colored_log()` |
| `main.py` | entry point and error handling |

```
read_map -> assign_paths -> create_drones -> simulate -> print_log / print_colored_log
```

`simulate()` returns the log (a list of turns) and prints nothing, so the plain
and the colored output both use the same log.

## Algorithm choices and implementation strategy

**Parsing.** `read_map()` reads the file with a context manager and checks
every rule of the subject. All checks raise `ValueError`, and one `try/except`
adds the line number, so each message says where and why.

**Paths.** Dijkstra with a `heapq` min-heap. Entering a zone costs 1 (normal),
2 (restricted) or 0.9 (priority); blocked zones are never used. The 0.9 breaks
ties in favor of priority zones. Drones are routed one at a time. After each
drone, every zone on its path gets +1 in a `load` dictionary, and the next
drone pays that load as an extra cost, so later drones spread over other routes.

**Simulation.** Each turn, drones are handled in id order:

1. A drone on a link to a restricted zone must arrive now.
2. A drone with room moves. For a restricted zone it starts the 2-turn crossing.
3. Other drones wait and are not listed.

A move needs room in the zone and on the link. The end zone is unlimited. A
drone on a link counts at its destination, so its place is reserved and the
arrival is never blocked. Leaving a zone frees its place in the same turn, and a
restricted connection is free again on the turn the drone arrives. For a
restricted zone, drones inside it that go straight to the end zone next turn are
not counted (`leaving_to_end`, limited by the link capacity to the end), so
drones can queue through it one per turn. If a turn has no move, the simulation
raises `RuntimeError("Deadlock: no drone can move")`.

**Complexity.** With V zones, E connections, D drones, T turns: one Dijkstra run
is about O(V·E + E·log V), because `get_neighbors` scans the connection list, so
path assignment is D runs. The simulation is O(D²) per turn, O(T·D²) in total.
Paths are computed once and never recalculated. Memory: O(V+E) for the graph,
O(D·path length) for the paths and O(T·D) for the log.

## Visual representation

In a terminal, every turn is printed with a header, the moves and a zone state
line. Zone names get the color of their `color=` metadata. The state line shows
`name: drones/capacity` for every zone that holds drones (start and end show only
the count; drones on a link are not counted).

```
Turn 3
D1-e D2-r
e: 1  r: 1/1
```

Named colors use basic ANSI codes, other words (`purple`, `gold`, ...) use ANSI
256-color codes, `rainbow` colors every letter differently, `black` is shown
dark gray, and an unknown color is printed plain. The colors show where drones
go, and the state line shows how full each zone is, so bottlenecks are easy to
see. When the output is piped or redirected, the program prints the plain format
with no color codes.

## Example

```
nb_drones: 2
start_hub: s 0 0 [color=green]
hub: r 1 0 [zone=restricted color=red]
end_hub: e 2 0 [color=yellow]
connection: s-r
connection: r-e
```

Plain output (4 turns): D1 starts crossing to `r`, then D1 arrives while D2
starts crossing, then D1 reaches the end while D2 arrives, then D2 reaches the end.

```
D1-s-r
D1-r D2-s-r
D1-e D2-r
D2-e
```

## Results

| Map | Drones | Optimum | Mine |
|---|---|---|---|
| Linear path | 2 | 4 | 4 |
| Simple fork | 4 | 4 | 4 |
| Basic capacity | 4 | 4 | 4 |
| Dead end trap | 5 | 8 | 8 |
| Circular loop | 6 | 10 | 10 |
| Priority puzzle | 5 | 6 | 7 |
| Maze nightmare | 8 | 13 | 13 |
| Capacity hell | 12 | 16 | 16 |
| Ultimate challenge | 15 | 26 | 28 |
| The Impossible Dream (optional) | 25 | 43 | 54 |

I also tested my own edge-case maps: a goal behind a blocked zone, a direct link
with capacity 1, a capacity-1 queue, drones queueing for a restricted connection,
a tie between a normal and a priority path, and invalid files.

Known limitations: routing is greedy and the congestion penalty is simple, so
three maps are above their optimum; drones are moved in id order; `get_neighbors`
scans a list instead of using a dictionary.

## Resources

- Dijkstra's algorithm: https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm
- Python `heapq`: https://docs.python.org/3/library/heapq.html
- PEP 257 (docstrings): https://peps.python.org/pep-0257/
- Google Python style guide: https://google.github.io/styleguide/pyguide.html
- `flake8`: https://flake8.pycqa.org/ and `mypy`: https://mypy.readthedocs.io/
- ANSI escape codes: https://en.wikipedia.org/wiki/ANSI_escape_code

### Use of AI

I used AI as an assistant for this project. It helped me to understand
algorithms and Python concepts, to review and debug my code, to think through
test cases and edge cases, and to write the docstrings and a draft of this
README. I checked that the docstrings match the code, and I tested everything
on the subject maps and on my own maps. I understand all the code and can
explain it.
