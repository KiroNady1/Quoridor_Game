
from collections import deque
from game.player import Player

def bfs_distance(board, player: Player) -> int:
    #BFS from player's current position to their goal row. Returns the shortest distance (number of steps), or 999 if no path exists
    goal = player.goal_row
    visited = set()
    queue = deque([(player.r, player.c, 0)])
    visited.add((player.r, player.c))

    while queue:
        r, c, dist = queue.popleft()
        if r == goal:
            return dist
        for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            nr, nc = r + dr, c + dc
            if (nr, nc) not in visited and board.can_step(r, c, nr, nc):
                visited.add((nr, nc))
                queue.append((nr, nc, dist + 1))

    return 999  # no path found
