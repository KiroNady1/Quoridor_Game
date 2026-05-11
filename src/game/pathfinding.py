# file: game/pathfinding.py

from collections import deque
from game.player import Player

def bfs_path_exists(board, player: Player) -> bool:
    """BFS from player's current position to their goal row."""
    goal = player.goal_row
    visited = set()
    queue   = deque([(player.r, player.c)])
    visited.add((player.r, player.c))

    while queue:
        r, c = queue.popleft()
        if r == goal:
            return True
        for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            nr, nc = r + dr, c + dc
            if (nr, nc) not in visited and board.can_step(r, c, nr, nc):
                visited.add((nr, nc))
                queue.append((nr, nc))
    return False
