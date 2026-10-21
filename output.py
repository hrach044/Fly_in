"""Print drone movement logs."""


def print_log(log: list[list[str]]) -> None:
    """Print each turn's drone movements.

    Args:
        log: Per-turn lists of drone movements.
    """
    for turn in log:
        print(" ".join(turn))
