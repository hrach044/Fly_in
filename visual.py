"""Render movement logs with zone colors."""

from graph import Graph


COLORS: dict[str, str] = {
    "black": "90",
    "red": "31",
    "green": "32",
    "yellow": "33",
    "blue": "34",
    "magenta": "35",
    "cyan": "36",
    "white": "37",
    "purple": "38;5;129",
    "violet": "38;5;177",
    "brown": "38;5;94",
    "orange": "38;5;208",
    "maroon": "38;5;88",
    "darkred": "38;5;124",
    "crimson": "38;5;161",
    "gold": "38;5;220",
    "rainbow": "38;5;213",
}


RAINBOW: list[str] = ["31", "33", "32", "36", "34", "35"]


def rainbow(text: str) -> str:
    """Apply cycling ANSI colors to text characters.

    Args:
        text: Text to color.

    Returns:
        Text with ANSI color codes around each character.
    """
    result = ""
    for i, char in enumerate(text):
        code = RAINBOW[i % len(RAINBOW)]
        result += f"\033[{code}m{char}\033[0m"
    return result


def colorize(text: str, color: str) -> str:
    """Apply a named ANSI color to text.

    Args:
        text: Text to color.
        color: Color name from the color table.

    Returns:
        Colored text, or the original text for an unknown color.
    """
    if color == "rainbow":
        return rainbow(text)
    code = COLORS.get(color)
    if code is None:
        return text
    return f"\033[{code}m{text}\033[0m"


def color_move(move: str, graph: Graph) -> str:
    """Color the zone names in one movement string.

    Args:
        move: Movement string to color.
        graph: Graph providing zone colors.

    Returns:
        Movement string with colored zone names.
    """
    parts = move.split("-")
    result = [parts[0]]
    for name in parts[1:]:
        result.append(colorize(name, graph.zones[name].color))
    return "-".join(result)


def print_colored_log(log: list[list[str]], graph: Graph,
                      nb_drones: int) -> None:
    """Print turns, colored movements, and zone occupancy.

    Args:
        log: Per-turn lists of drone movements.
        graph: Graph providing zone names, colors, and capacities.
        nb_drones: Number of drones in the simulation.
    """
    states = replay(log, nb_drones, graph.start.name)
    for number, turn in enumerate(log, 1):
        moves: list[str] = []
        for move in turn:
            moves.append(color_move(move, graph))
        print(f"Turn {number}")
        print(" ".join(moves))
        print(zone_state(states[number - 1], graph))
        print()


def replay(log: list[list[str]], nb_drones: int,
           start_name: str) -> list[dict[int, str]]:
    """Build each turn's drone positions from the movement log.

    Args:
        log: Per-turn lists of drone movements.
        nb_drones: Number of drones to track.
        start_name: Name of the initial zone.

    Returns:
        A position snapshot for each turn.
    """
    positions: dict[int, str] = {}
    for drone_id in range(1, nb_drones + 1):
        positions[drone_id] = start_name
    states: list[dict[int, str]] = []
    for turn in log:
        for move in turn:
            parts = move.split("-")
            drone_id = int(parts[0][1:])
            positions[drone_id] = "-".join(parts[1:])
        states.append(dict(positions))
    return states


def zone_state(positions: dict[int, str], graph: Graph) -> str:
    """Format zone occupancy counts with zone colors.

    Args:
        positions: Mapping from drone IDs to their positions.
        graph: Graph providing zone capacities and colors.

    Returns:
        A colored string of zone occupancy counts.
    """
    counts: dict[str, int] = {}
    for place in positions.values():
        if "-" in place:
            continue
        counts[place] = counts.get(place, 0) + 1
    parts: list[str] = []
    for name, count in counts.items():
        zone = graph.zones[name]
        if name in (graph.start.name, graph.end.name):
            text = f"{name}: {count}"
        else:
            text = f"{name}: {count}/{zone.capacity}"
        parts.append(colorize(text, zone.color))
    return "  ".join(parts)
