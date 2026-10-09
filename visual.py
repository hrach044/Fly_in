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
    result = ""
    for i, char in enumerate(text):
        code = RAINBOW[i % len(RAINBOW)]
        result += f"\033[{code}m{char}\033[0m"
    return result

def colorize(text: str, color: str) -> str:
    if color == "rainbow":
        return rainbow(text)
    code = COLORS.get(color)
    if code is None:
        return text
    return f"\033[{code}m{text}\033[0m"


def color_move(move: str, graph: Graph) -> str:
    parts = move.split("-")
    result = [parts[0]]
    for name in parts[1:]:
        result.append(colorize(name, graph.zones[name].color))
    return "-".join(result)

def print_colored_log(log: list[list[str]], graph: Graph) -> None:
    for turn in log:
        moves: list[str] = []
        for move in turn:
            moves.append(color_move(move, graph))
        print(" ".join(moves))

def replay(log: list[list[str]], nb_drones: int,
           start_name: str) -> list[dict[int, str]]:
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