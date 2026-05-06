# pathfinder.py — BFS grid pathfinder for NPC navigation
from __future__ import annotations
from collections import deque


def bfs_path(blocked_fn, start: tuple[int, int], goal: tuple[int, int],
             max_cols: int, max_rows: int) -> list[tuple[int, int]]:
    """
    BFS from start (col, row) to goal (col, row).
    blocked_fn(col, row) -> bool
    Returns list of (col, row) steps from start to goal (inclusive of goal, exclusive of start).
    Returns empty list if no path found.
    """
    if start == goal:
        return []

    queue: deque[tuple[int, int]] = deque([start])
    came_from: dict[tuple[int, int], tuple[int, int] | None] = {start: None}

    directions = [(0, -1), (0, 1), (-1, 0), (1, 0),
                  (-1, -1), (-1, 1), (1, -1), (1, 1)]  # 8-directional

    while queue:
        current = queue.popleft()
        if current == goal:
            # Reconstruct path
            path: list[tuple[int, int]] = []
            node = goal
            while node != start:
                path.append(node)
                node = came_from[node]
            path.reverse()
            return path

        c, r = current
        for dc, dr in directions:
            nc, nr = c + dc, r + dr
            neighbor = (nc, nr)
            if (0 <= nc < max_cols and 0 <= nr < max_rows
                    and neighbor not in came_from
                    and not blocked_fn(nc, nr)):
                came_from[neighbor] = current
                queue.append(neighbor)

    return []  # no path
