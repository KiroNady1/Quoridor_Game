# file: AI/AI.py

from enum import Enum
from game.player import Player
from game.board import Board
from game.rules import get_valid_moves, get_valid_walls
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

def evaluate_wall():
    pass

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
    
    for pawn_move in get_valid_moves(board, ai, human):
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

def a_star_distance():
    pass

def get_best_wall():
    pass

