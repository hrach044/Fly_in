*This project has been created as part of the 42 curriculum by hmnatsak.*

# Fly-in

## Description

Fly-in routes a fleet of drones from one start zone to one end zone through
a network of connected zones, in as few simulation turns as possible.

The network is read from a map file. Every zone and every connection has a
capacity, restricted zones cost 2 turns to enter, priority zones are
preferred, and blocked zones can never be used. The program finds a path for
every drone, simulates all movements turn by turn while respecting every
rule, and prints one line per turn.

Goals of the project:

- find short routes for many drones, spreading them over several paths;
- make drones wait when a move is not possible, without conflicts or
  deadlocks;
- respect zone capacity (`max_drones`) and connection capacity
  (`max_link_capacity`);
- show the simulation visually in the terminal.

No graph library is used. The graph is built by hand.

## Features

- Map parser with clear errors that name the line and the cause.
- Congestion-aware shortest paths (Dijkstra with a min-heap).
- Turn-by-turn simulation with zone capacity, link capacity, restricted
  zones (2-turn moves) and a deadlock guard.
- Colored terminal output: zone colors from the map, turn header, moves and
  a zone state line for every turn.
- Plain output in the exact subject format when the output is piped or
  written to a file.
- Type hints everywhere, docstrings (PEP 257, Google style), `flake8` and
  `mypy` clean.

## Instructions

### Requirements

- Python 3.10 or later
- `flake8` and `mypy` (installed by `make install`)

### Commands

| Command | What it does |
|---|---|
| `make install` | Install `flake8` and `mypy` with pip |
| `make run` | Run the simulation on `map.txt` |
| `make debug` | Run the simulation under `pdb` |
| `make lint` | Run `flake8 .` and `mypy` with the flags from the subject |
| `make clean` | Remove `__pycache__` and `.mypy_cache` |

To run another map directly:

```
python3 main.py maps/medium/02_circular_loop.txt
```

Piping or redirecting gives the plain subject format:

```
python3 main.py map.txt > result.txt
python3 main.py map.txt | wc -l      # number of turns
```

### Error handling

Every error stops the program with a message that starts with `Error:` and
exit code 1. Examples:

```
Error: line 5: Connection needs exactly two zones: connection: a-b-c
Error: line 3: Unknown metadata key: colour
Error: line 1: First line must be nb_drones
Error: No path from start_hub to end_hub
```

## Input file format

```
nb_drones: <positive integer>
start_hub: <name> <x> <y> [metadata]
end_hub:   <name> <x> <y> [metadata]
hub:       <name> <x> <y> [metadata]
connection: <name1>-<name2> [metadata]
```

- The first line must be `nb_drones`.
- Comments start with `#`. Coordinates are integers.
- Zone names may contain any character except dashes and spaces.
- Connections are bidirectional and may only link zones defined above them.
  `a-b` and `b-a` are the same connection, so a duplicate is an error.

| Metadata | Where | Values | Default |
|---|---|---|---|
| `zone=` | zones | `normal`, `blocked`, `restricted`, `priority` | `normal` |
| `color=` | zones | any single word | `none` |
| `max_drones=` | zones | positive integer | `1` |
| `max_link_capacity=` | connections | positive integer | `1` |

`max_drones` on `start_hub` and `end_hub` is ignored: both are unlimited.
Unknown metadata keys, wrong values and extra items are parsing errors.

| Zone type | Rule |
|---|---|
| normal | moving into it costs 1 turn |
| restricted | moving into it costs 2 turns |
| priority | moving into it costs 1 turn, preferred by the pathfinding |
| blocked | cannot be entered, no path may use it |

## Output format

One line per turn. A line lists the moves of that turn, separated by spaces.
Drones that did not move are omitted. Delivered drones are no longer listed.

- `D<ID>-<zone>`: the drone moved into that zone.
- `D<ID>-<from>-<to>`: the drone is on the connection from `from` to `to`,
  on its way to a restricted zone. It arrives on the next turn.

```
D1-roof1 D2-corridorA
D1-roof2 D2-tunnelB
D1-goal D2-goal
```

## Project structure

| File | Content |
|---|---|
| `models.py` | `ZoneType` (Enum), `Zone`, `Connection`, `Drone` |
| `graph.py` | `link_key()` and the `Graph` class (zones, connections, link limits) |
| `parser.py` | `parse_zone()` and `read_map()`: file to drone count and graph |
| `pathfinding.py` | `zone_cost()`, `assign_paths()`, `path_finding()` |
| `simulation.py` | `create_drones()`, `count_in_zone()`, `leaving_to_end()`, `simulate()` |
| `output.py` | `print_log()`: plain output in the subject format |
| `visual.py` | colors, `print_colored_log()`, `replay()`, `zone_state()` |
| `main.py` | entry point and error handling |
| `Makefile` | install, run, debug, lint, clean |

Data flow:

```
read_map -> assign_paths -> create_drones -> simulate -> print_log / print_colored_log
(parser)    (pathfinding)    (simulation)    (simulation)   (output / visual)
```

`simulate()` returns the log as a list of turns (one list of move strings per
turn) and prints nothing. The plain output and the colored output both read
the same log, so the simulation never depends on how the result is shown.

## Algorithm choices and implementation strategy

### 1. Parsing

`read_map()` reads the file with a context manager and checks every rule from
the subject: first line, one start and one end, unique names, no dashes in
names, integer coordinates, valid zone types, positive capacities, known
zones in connections, no duplicate connections, exactly two zones per
connection, known metadata keys. All checks raise `ValueError`. A single
`try/except` around the loop body adds the line number, so every message
says where and why.

### 2. Path assignment (Dijkstra with a congestion penalty)

Entering a zone has this cost:

| Zone | Cost |
|---|---|
| normal | 1 |
| restricted | 2 |
| priority | 0.9 |
| blocked | not usable |

Priority costs slightly less than 1, so when two paths have the same number
of turns, the one with more priority zones wins. This tie-break is exact as
long as the paths differ by fewer than 10 priority zones.

Paths are computed one drone at a time with Dijkstra (a `heapq` min-heap).
After each drone, every zone on its path (except start and end) gets +1 in a
`load` dictionary. The next drone adds `load[zone]` to the cost of entering
that zone. This makes later drones prefer other routes when a zone is
crowded, so the fleet spreads over several paths without a full flow
algorithm. If the end zone cannot be reached, the program stops with
`No path from start_hub to end_hub`.

### 3. Simulation

Each turn, drones are handled in id order, and each drone does one of three
things:

1. **Drone on a link to a restricted zone:** it must arrive now. It cannot
   wait on the connection.
2. **Drone that can enter its next zone:** it moves. If the next zone is
   restricted it starts the 2-turn crossing instead and shows up as
   `D<ID>-<from>-<to>`.
3. **Drone that cannot move:** it stays and is not listed.

A move needs two things:

- **Zone room.** The end zone always has room. Any other zone needs fewer
  drones than its `max_drones`. A drone on a link counts at its destination,
  so that spot is reserved when the crossing starts and the arrival can
  never be blocked. A drone that leaves a zone frees the place in the same
  turn.
- **Link room.** The connection must have fewer crossings this turn than
  `max_link_capacity`. A restricted connection is freed on the turn the drone
  arrives, so the next drone may start crossing in that same turn.

For a restricted destination, the drones inside it that go straight to the end
zone next turn are not counted (`leaving_to_end`). They will be gone when the
new drone arrives, because the end zone is unlimited. This is limited by the
capacity of the link to the end zone, so a promised leaver always leaves. It
lets drones queue through a restricted zone one per turn.

If a whole turn has no move, the simulation raises
`RuntimeError("Deadlock: no drone can move")` instead of running forever.

### Complexity

Let V = zones, E = connections, D = drones, T = turns, P = longest path.

| Part | Cost |
|---|---|
| Parsing | linear in the number of lines |
| One Dijkstra run | about O(V·E + E·log V), because `get_neighbors` scans the connection list |
| Path assignment | D runs: about O(D·(V·E + E·log V)) |
| Simulation | O(D²) per turn (`count_in_zone` loops over all drones), O(T·D²) in total |
| Colored output | `replay` is O(T·D) |

Any number of drones works. The cost grows with D² per turn, which is fine for
the maps of this project. A dictionary of neighbors per zone would make each
Dijkstra run cheaper.

### Caching and memory

Paths are computed once, before the simulation, and never recalculated. There
is no cache between runs. Memory:

- graph: O(V + E)
- paths: O(D·P)
- log: O(T·D) strings
- replay snapshots (terminal mode only): O(T·D)

## Visual representation

When the output goes to a terminal, the program prints, for every turn:

```
Turn 3
D1-e D2-r
e: 1  r: 1/1
```

1. a header with the turn number;
2. the moves, with every zone name in the color of its `color=` metadata;
3. a zone state line: `name: drones/capacity` for every zone that holds
   drones. Start and end show only the count, because they are unlimited.
   Drones on a link are not counted in any zone.

Colors:

- named colors (`red`, `green`, `blue`, ...) use the basic ANSI codes;
- other words used by the maps (`purple`, `orange`, `gold`, ...) use ANSI
  256-color codes;
- `rainbow` gives every letter a different color;
- `black` is shown dark gray so it stays visible on a dark terminal;
- a missing or unknown color is printed in the normal terminal color.

Why it helps: the colors show which part of the map each drone enters, and
the zone state line shows at a glance how full each zone is, so capacity
limits and bottlenecks are easy to see. When the output is piped or written
to a file, the program prints the plain subject format with no color codes,
so another program or a checker gets clean text.

## Example

Input (`map.txt`): two drones, one restricted zone, link capacity 1.

```
nb_drones: 2
start_hub: s 0 0 [color=green]
hub: r 1 0 [zone=restricted color=red]
end_hub: e 2 0 [color=yellow]
connection: s-r
connection: r-e
```

Plain output (`python3 main.py map.txt | cat`):

```
D1-s-r
D1-r D2-s-r
D1-e D2-r
D2-e
```

- Turn 1: D1 starts the 2-turn crossing to `r`.
- Turn 2: D1 arrives in `r`. The link is free again, so D2 starts crossing.
- Turn 3: D1 reaches the end and D2 arrives in `r`.
- Turn 4: D2 reaches the end. Total: 4 turns.

Colored output in a terminal (colors not shown here):

```
Turn 1
D1-s-r
s: 1

Turn 2
D1-r D2-s-r
r: 1/1

Turn 3
D1-e D2-r
e: 1  r: 1/1

Turn 4
D2-e
e: 2
```

## Results

Turns on the maps of the subject, compared with the optimum given there.
Results at the time of writing.

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

To run every map:

```
for f in maps/*/*.txt; do echo "$f: $(python3 main.py "$f" | wc -l) turns"; done
```

Besides the subject maps, edge cases were tested with my own maps: a goal
reachable only through a blocked zone, a direct start-to-end link with
capacity 1, a capacity-1 zone used as a queue, drones queueing for a
restricted connection, a tie between a normal and a priority path, and
invalid files (extra items in a connection, unknown metadata keys, a first
line that is not `nb_drones`).

## Known limitations

- Routing is greedy: drones are routed one after the other, and the
  congestion penalty is simple (+1 per drone and zone). It ignores zone and
  link capacity and the timing of the drones, so it does not always find the
  best schedule. This is why three maps are above their optimum.
- Drones are moved in id order, so a drone can use a place freed in the same
  turn only by a drone with a lower id (and by drones that leave straight to
  the end zone).
- `get_neighbors` scans the list of connections. This is fast enough for the
  given maps, but a neighbor dictionary would scale better.

## Resources

### References

- Dijkstra's algorithm: https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm
- Python `heapq` (priority queue): https://docs.python.org/3/library/heapq.html
- PEP 257, docstring conventions: https://peps.python.org/pep-0257/
- Google Python style guide (docstring sections):
  https://google.github.io/styleguide/pyguide.html
- `flake8` documentation: https://flake8.pycqa.org/
- `mypy` documentation: https://mypy.readthedocs.io/
- ANSI escape codes (terminal colors):
  https://en.wikipedia.org/wiki/ANSI_escape_code
- Python `pdb` debugger: https://docs.python.org/3/library/pdb.html

### Use of AI

I did this project alone and used AI as a tutor and pair-programmer, never
as a replacement for understanding the code.

- **Claude (chat assistant):** explained each idea before the code, reviewed
  the code I pasted and pointed out bugs, and gave small pieces of code step
  by step. I typed them in, tested them and can explain each line. Parts
  where it helped: the terminal visual layer (`visual.py`), the parser
  validation checks, the restricted-zone arrival rule in the simulation, the
  priority tie-break, the Makefile, and a draft of this README.
- **GitHub Copilot:** wrote the first draft of the docstrings. I checked that
  only docstrings were added by comparing the code with the previous commit,
  and I read every docstring against what the code really does.
- **Checking:** all code passes `flake8` and `mypy`, and was tested on the
  subject maps and on my own edge-case maps.


