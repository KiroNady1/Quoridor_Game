# file: AI/AI.py
import copy
import heapq
from enum import Enum
from game.player import Player
from game.board import Board
from game.rules import get_valid_moves, get_valid_walls, is_wall_placement_valid
from ai.bfs_distance import bfs_distance
from typing import Tuple

class Mode(Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD   = "hard"

# Difficulty Configurations
def get_config(mode : str):
    if mode == Mode.EASY:
        return{
            "depth" : 2,
            "weights": (3,1,1),
            "search_function" : easy_search
        }
    elif mode == Mode.MEDIUM:
        return{
            "depth" : 3,
            "weights": (10,10,10),
            "search_function" : medium_search
        }
    else: # Hard
        return{
            "depth": 4,
            "weights": (15, 10, 5),
            "search_function" : hard_search

        }

# === Choose Best Move ===
def get_best_move(board, ai, human, mode):
    """Find the best pawn move for the AI using minimax with alpha-beta pruning."""
    config = get_config(mode)
    depth = config["depth"]
    weigths = config["weights"]
    search_function = config["search_function"]

    best_score = float('-inf')
    best_move = None

    moves = get_valid_moves(board, ai, human)
    if not moves:
        return None

    for move in moves:
        orig_r, orig_c = ai.r, ai.c
        ai.r, ai.c = move

        score = search_function(board, ai, human, config)

        ai.r, ai.c = orig_r, orig_c

        if score > best_score:
            best_score = score
            best_move = move

    return best_move

# === Evaulating score ===
def evaluate(board: Board, ai: Player, human: Player, weights : Tuple[int, int, int]):
    distance_w, wall_w, mobility_w = weights

    ai_dist    = bfs_distance(board, ai)
    human_dist = bfs_distance(board, human)

    distance_score = (human_dist - ai_dist) * distance_w

    wall_score = (ai.walls_left - human.walls_left) * wall_w

    ai_moves    = len(get_valid_moves(board, ai, human))
    human_moves = len(get_valid_moves(board, human, ai))

    mobility_score = (ai_moves - human_moves) * mobility_w

    return distance_score + wall_score + mobility_score

def evaluate_wall(board: Board, ai: Player, original_ai_distance : int, human: Player,
                  original_human_distance : int, wall) -> int:
    # Temporarily place wall and calculate distance
    new_board = copy.deepcopy(board)

    new_board.add_wall(wall)
    new_ai_distance = a_star_distance(new_board, ai)
    new_human_distance = a_star_distance(new_board, human)

    human_distance_score = new_human_distance - original_human_distance
    wall_distance_score = (original_ai_distance - new_ai_distance)

    return (human_distance_score + wall_distance_score) 


# === Searching best move ===
def easy_search(board, ai, human, config):
    return minimax(board, human, ai, False, config["depth"] - 1,
                        float('-inf'), float('inf'), config["weights"])

def medium_search(board, ai, human, config):
    return minimax(board, human, ai, False, config["depth"] - 1,
                        float('-inf'), float('inf'), config["weights"])

def hard_search(board, ai, human, config):
    best_pawn_move = None
    best_pawn_score = -float('-inf')
    
    for move in get_valid_moves(board, ai, human):
        pass
        # Apply move temporarily
        # Call minimax(depth=4, using A* evaluation)
        # Track best
    
    best_wall = get_best_wall(board, ai, human)
    best_wall_score = evaluate_wall(board, ai, human, best_wall)
    
    # Step 3: Compare and decide
    if ai.walls_left > 0 and best_wall_score > best_pawn_score:
        # Execute wall placement (need to modify board)
        # Return special signal or place wall directly
        return best_wall  # or (best_wall, is_wall=True)
    else:
        return best_pawn_move

# === Algorithms ===
def minimax(board: Board, human: Player, ai: Player, maximise: bool,
            depth: int, alpha: float, beta: float, weights : Tuple[int, int, int]):
    # Terminal conditions
    if depth == 0:
        return evaluate(board, ai, human, weights)
    if ai.r == ai.goal_row:
        return float('inf')
    if human.r == human.goal_row:
        return float('-inf')

    if maximise:  # AI Turn
        best = float('-inf')

        for move in get_valid_moves(board, ai, human):
            # Save original position
            orig_r, orig_c = ai.r, ai.c
            ai.r, ai.c = move

            value = minimax(board, human, ai, False, depth - 1, alpha, beta, weights)

            # Restore position
            ai.r, ai.c = orig_r, orig_c

            best  = max(best, value)
            alpha = max(alpha, best)
            if beta <= alpha:
                break

        return best
    else:  # Human turn (minimising)
        best = float('inf')

        for move in get_valid_moves(board, human, ai):
            # Save original position
            orig_r, orig_c = human.r, human.c
            human.r, human.c = move

            value = minimax(board, human, ai, True, depth - 1, alpha, beta, weights)

            # Restore position
            human.r, human.c = orig_r, orig_c

            best = min(best, value)
            beta = min(beta, best)
            if beta <= alpha:
                break

        return best

def a_star_distance(board: Board, player : Player) -> int:
    """
    Returns shortest path length from player position to goal row.
    Uses A* with Manhattan distance heuristic.
    Returns float('inf') if no path exists.
    """
    start = (player.r, player.c)
    goal_row = player.goal_row

    if start[0] == goal_row:
        return 0

    # Priority queue (f_score, (row, col))
    frontier = []
    heapq.heappush(frontier, (0,start))

    g_scores = {start: 0}
    explored = set()

    while frontier:
        _, current = heapq.heappop(frontier)
        current_row, current_column = current
        
        # Skip if already explored with better score
        if current in explored:
            continue        
        if current_row == goal_row:
            return g_scores[current]
        
        explored.add(current)
        for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            # Move
            neighbour_row, neighbour_column = current_row + dr, current_column + dc
            if not board.can_step(current_row, current_column, neighbour_row, neighbour_column):
                continue
            
            neighbor = (neighbour_row, neighbour_column)
            neighbor_not_visited = neighbor not in g_scores

            tentative_g = g_scores[current] + 1     # Moved one cell
            this_path_shorter = tentative_g < g_scores[neighbor]

            if neighbor_not_visited or this_path_shorter:
                g_scores[neighbor] = tentative_g    # Update score with shorter score

                # Heuristic: row distance to goal (Manhattan)
                h = abs(neighbour_row - goal_row)
                f = tentative_g + h
                heapq.heappush(frontier, (f, neighbor))

    return int('inf')


def get_best_wall(board, ai, human, weights):
    if ai.walls_left < 1:
        return None

    original_ai_distance = a_star_distance(board, ai)
    original_human_distance = a_star_distance(board, human)
    
    walls = get_valid_walls()
    if not walls:
        return None

    best_wall_score = float('-inf')
    best_wall = None
    for wall in walls:
        if not is_wall_placement_valid(board, wall, ai):
            continue

        current_wall_score = evaluate_wall(board, ai, original_ai_distance, human, original_human_distance, wall)
        if current_wall_score > best_wall_score:
            best_wall_score = current_wall_score
            best_wall = wall

    return best_wall

