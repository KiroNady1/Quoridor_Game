import sys
import heapq

from game.board import Board
from game.player import Player

INF = sys.maxsize


def a_star_distance(board: Board, player: Player) -> int:
    start = (player.r, player.c)
    goal_row = player.goal_row

    if start[0] == goal_row:
        return 0

    frontier = []
    heapq.heappush(frontier, (0, start))

    g_scores = {start: 0}
    explored = set()

    while frontier:
        _, current = heapq.heappop(frontier)

        if current in explored:
            continue

        current_row, current_col = current

        if current_row == goal_row:
            return g_scores[current]

        explored.add(current)

        for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            nr, nc = current_row + dr, current_col + dc

            if not board.can_step(current_row, current_col, nr, nc):
                continue

            neighbor = (nr, nc)
            tentative_g = g_scores[current] + 1

            if neighbor not in g_scores or tentative_g < g_scores[neighbor]:
                g_scores[neighbor] = tentative_g

                heuristic = abs(nr - goal_row)
                f_score = tentative_g + heuristic

                heapq.heappush(frontier, (f_score, neighbor))

    return INF


def bfs_distance(board: Board, player: Player) -> int:
    from collections import deque

    start = (player.r, player.c)
    goal_row = player.goal_row

    if start[0] == goal_row:
        return 0

    queue = deque([(start, 0)])
    visited = {start}

    while queue:
        (r, c), dist = queue.popleft()

        for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            nr, nc = r + dr, c + dc

            if not board.can_step(r, c, nr, nc):
                continue

            if (nr, nc) in visited:
                continue

            if nr == goal_row:
                return dist + 1

            visited.add((nr, nc))
            queue.append(((nr, nc), dist + 1))

    return INF
