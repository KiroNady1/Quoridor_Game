
# file: AI/AI.py

import sys
import copy
import heapq
from enum import Enum
from game.player import Player
from game.board import Board
from game.rules import get_valid_moves, is_wall_placement_valid
from game.wall import Wall
from typing import Tuple, Optional, Union


class Mode(Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


def get_config(mode: Mode):
    if mode == Mode.EASY:
        return {"depth": 2, "weights": (3, 1, 1), "search_function": easy_search}
    elif mode == Mode.MEDIUM:
        return {"depth": 3, "weights": (10, 1, 10), "search_function": medium_search}
    else:  # Hard
        return {"depth": 7, "weights": (15, 10, 5), "search_function": hard_search}


# === Choose Best Move ===
def get_best_move(board: Board, ai: Player, human: Player, mode: Mode) -> list:
    """
    Find the best move for the AI.
    Returns:
        - ('move', (r, c)) for pawn moves
        - ('wall', Wall) for wall placements
        - None if no moves available
    """
    # Defensive assertions to ensure search never mutates real game state
    original_ai_pos = (ai.r, ai.c)
    original_human_pos = (human.r, human.c)

    config = get_config(mode)
    search_function = config["search_function"]
    move_type, move_data = search_function(board, ai, human, config)

    assert (ai.r, ai.c) == original_ai_pos,         "AI position mutated during search"

    assert (human.r, human.c) == original_human_pos,         "Human position mutated during search"

    print(move_type)
    print(move_data)

    return [move_type, move_data]


# === Evaluation Functions ===


def evaluate(
    board: Board,
    ai: Player,
    human: Player,
    weights: Tuple[int, int, int],
    use_astar: bool = False,
):
    """Evaluate the current board state from AI's perspective."""
    distance_w, wall_w, mobility_w = weights

    if use_astar:
        ai_dist = a_star_distance(board, ai)
        human_dist = a_star_distance(board, human)
    else:
        ai_dist = bfs_distance(board, ai)
        human_dist = bfs_distance(board, human)

    distance_score = (human_dist - ai_dist) * distance_w
    wall_score = (ai.walls_left - human.walls_left) * wall_w

    ai_moves = len(get_valid_moves(board, ai, human))
    human_moves = len(get_valid_moves(board, human, ai))
    mobility_score = (ai_moves - human_moves) * mobility_w

    return distance_score + wall_score + mobility_score


def evaluate_wall(
    board: Board,
    ai: Player,
    original_ai_distance: int,
    human: Player,
    original_human_distance: int,
    wall: Wall,
    weights: Tuple[int, int, int],
) -> int:
    """
    Evaluate how good a wall placement is.
    Positive score means the wall benefits the AI.
    """
    distance_w, _, _ = weights
    LARGE_PENALTY = -999999

    # Create a copy and place the wall
    new_board = copy.deepcopy(board)
    new_board.add_wall(wall)

    new_ai_distance = a_star_distance(new_board, ai)
    new_human_distance = a_star_distance(new_board, human)

    # FIX: compare against sys.maxsize instead of float("inf")
    if (
        new_ai_distance == sys.maxsize
        or new_human_distance == sys.maxsize
    ):
        return LARGE_PENALTY

    human_improvement = (new_human_distance - original_human_distance) * 2
    ai_improvement = (
        original_ai_distance - new_ai_distance
    )  # Better if shorter distance

    return human_improvement + ai_improvement


# === Search Functions ===


def easy_search(board: Board, ai: Player, human: Player, config: dict):
    """Easy: depth 2, BFS evaluation."""
    best_move = _get_best_pawn_move(board, ai, human, config, use_astar=False)
    return ("move", best_move)


def medium_search(board: Board, ai: Player, human: Player, config: dict):
    """Medium: depth 3, BFS evaluation."""
    best_move = _get_best_pawn_move(board, ai, human, config, use_astar=False)
    return ("move", best_move)


def hard_search(board, ai, human, config):
    """
    Hard: depth 4, A* evaluation + wall placement.
    Returns ('move', (r,c)) or ('wall', Wall)
    """
    # 1. Find best pawn move
    best_pawn_move, best_pawn_score = _get_best_move_with_score(
        board, ai, human, config, use_astar=True
    )

    # 2. Find best wall placement
    best_wall, best_wall_score = _get_best_wall_and_score(
        board, ai, human, config["weights"]
    )

    # 3. Compare and return the better option
    if (
        ai.walls_left > 0
        and best_wall is not None
        and best_wall_score > best_pawn_score
    ):
        return ("wall", best_wall)
    else:
        return ("move", best_pawn_move)


# === Internal Helper Functions ===
def _get_best_pawn_move(
    board: Board, ai: Player, human: Player, config: dict, use_astar: bool
):
    """Return just the best pawn move (for Easy/Medium)."""
    move, _ = _get_best_move_with_score(board, ai, human, config, use_astar)
    return move


def _get_best_move_with_score(
    board: Board, ai: Player, human: Player, config: dict, use_astar: bool
) -> Tuple[Optional[tuple], float]:
    """
    Find the best pawn move using minimax.
    Returns: (best_move, best_score)
    """
    depth = config["depth"]
    weights = config["weights"]

    moves = get_valid_moves(board, ai, human)
    if not moves:
        return None, float("-inf")

    best_score = float("-inf")
    best_move = moves[0]

    for move in moves:
        # FIX: clone player instead of mutating shared object
        next_ai = copy.copy(ai)
        next_ai.r, next_ai.c = move

        score = minimax(
            board,
            human,
            next_ai,
            False,
            depth - 1,
            float("-inf"),
            float("inf"),
            weights,
            use_astar,
        )

        if score > best_score:
            best_score = score
            best_move = move

    return best_move, best_score


def _get_best_wall_and_score(
    board: Board, ai: Player, human: Player, weights: Tuple[int, int, int]
) -> Tuple[Optional[Wall], float]:
    """
    Find the best wall placement using greedy A* evaluation.
    Returns: (best_wall, best_score)
    """
    if ai.walls_left < 1:
        return None, float("-inf")

    original_ai_distance = a_star_distance(board, ai)
    original_human_distance = a_star_distance(board, human)

    candidates = _get_candidate_walls(board, ai, human)
    best_score = float("-inf")
    best_wall = None

    for wall in candidates:
        valid, _ = is_wall_placement_valid(board, wall, [ai, human])

        if not valid:
            continue

        score = evaluate_wall(
            board,
            ai,
            original_ai_distance,
            human,
            original_human_distance,
            wall,
            weights,
        )

        if score == float("inf"):
            continue

        if score > best_score:
            best_score = score
            best_wall = wall

    return best_wall, best_score


def _get_candidate_walls(board, ai, human):
    """Only return walls near players or along paths."""
    from ui.constants import GRID

    candidates = []

    # Add walls around AI position
    for dr in [-1, 0, 1]:
        for dc in [-1, 0, 1]:
            for orientation in ["H", "V"]:
                r = ai.r + dr
                c = ai.c + dc
                if 0 <= r < GRID - 1 and 0 <= c < GRID - 1:
                    candidates.append(Wall(orientation, r, c))

    # Add walls around human position
    for dr in [-1, 0, 1]:
        for dc in [-1, 0, 1]:
            for orientation in ["H", "V"]:
                r = human.r + dr
                c = human.c + dc
                if 0 <= r < GRID - 1 and 0 <= c < GRID - 1:
                    candidates.append(Wall(orientation, r, c))

    # Remove duplicates (use set with key)
    seen = set()
    unique = []

    for wall in candidates:
        key = wall.key()

        valid, _ = is_wall_placement_valid(board, wall, [ai, human])

        if key not in seen and valid:
            seen.add(key)
            unique.append(wall)

    return unique


# === Minimax Algorithm ===
def minimax(
    board: Board,
    human: Player,
    ai: Player,
    maximise: bool,
    depth: int,
    alpha: float,
    beta: float,
    weights: Tuple[int, int, int],
    use_astar: bool = False,
) -> float:
    """
    Minimax with alpha-beta pruning.
    use_astar: True for Hard mode (A* evaluation), False for Easy/Medium (BFS)
    """
    # Terminal conditions
    if ai.r == ai.goal_row:
        return float("inf")

    if human.r == human.goal_row:
        return float("-inf")

    # If no depth, stop searching
    if depth == 0:
        return evaluate(board, ai, human, weights, use_astar)

    if maximise:  # AI Turn
        best = float("-inf")

        for move in get_valid_moves(board, ai, human):

            # FIX: clone instead of mutating
            next_ai = copy.copy(ai)
            next_ai.r, next_ai.c = move

            value = minimax(
                board,
                human,
                next_ai,
                False,
                depth - 1,
                alpha,
                beta,
                weights,
                use_astar,
            )

            best = max(best, value)
            alpha = max(alpha, best)

            if beta <= alpha:
                break

        return best

    else:  # Human turn (minimising)
        best = float("inf")

        for move in get_valid_moves(board, human, ai):

            # FIX: clone instead of mutating
            next_human = copy.copy(human)
            next_human.r, next_human.c = move

            value = minimax(
                board,
                next_human,
                ai,
                True,
                depth - 1,
                alpha,
                beta,
                weights,
                use_astar,
            )

            best = min(best, value)
            beta = min(beta, best)

            if beta <= alpha:
                break

        return best


# === A* Pathfinding ===
def a_star_distance(board: Board, player: Player) -> int:
    """
    Returns shortest path length from player position to goal row.
    Uses A* with Manhattan distance heuristic.
    Returns float('inf') if no path exists.
    """
    start = (player.r, player.c)
    goal_row = player.goal_row

    if start[0] == goal_row:
        return 0

    # Priority queue: (f_score, (row, col))
    frontier = []
    heapq.heappush(frontier, (0, start))

    g_scores = {start: 0}
    explored = set()

    while frontier:
        _, current = heapq.heappop(frontier)
        current_row, current_col = current

        if current in explored:
            continue

        if current_row == goal_row:
            return g_scores[current]

        explored.add(current)

        # Explore neighbors
        for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            neighbor_row = current_row + dr
            neighbor_col = current_col + dc

            if not board.can_step(current_row, current_col, neighbor_row, neighbor_col):
                continue

            neighbor = (neighbor_row, neighbor_col)
            tentative_g = g_scores[current] + 1

            # Update if this path is better
            if neighbor not in g_scores or tentative_g < g_scores[neighbor]:
                g_scores[neighbor] = tentative_g

                # Heuristic: row distance to goal
                h = abs(neighbor_row - goal_row)
                f = tentative_g + h

                heapq.heappush(frontier, (f, neighbor))

    return sys.maxsize


# === BFS Distance (for Easy/Medium) ===
def bfs_distance(board: Board, player: Player) -> int:
    """
    Returns shortest path length using BFS.
    Returns float('inf') if no path exists.
    """
    from collections import deque

    start = (player.r, player.c)
    goal_row = player.goal_row

    if start[0] == goal_row:
        return 0

    queue = deque([(start, 0)])  # (position, distance)
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

    return sys.maxsize
