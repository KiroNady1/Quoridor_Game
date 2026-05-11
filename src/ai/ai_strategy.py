# file: AI/AI.py

from enum import Enum
from game.player import Player
from game.board import Board
from game.rules import get_valid_moves
from ai.bfs_distance import bfs_distance
from abc import ABC

class AIStrategy(Enum):
    MEDIUM = "medium"
    HARD   = "hard"

def get_weights(mode: AIStrategy):
    #Return (distance_weight, wall_weight, mobility_weight) based on difficulty.
    if mode == AIStrategy.HARD:
        return 10, 10, 10
    else:  # MEDIUM
        return 5, 5, 5

def evaluate(board: Board, ai: Player, human: Player, mode: AIStrategy):
    distance_w, wall_w, mobility_w = get_weights(mode)

    ai_dist    = bfs_distance(board, ai)
    human_dist = bfs_distance(board, human)

    distance_score = (human_dist - ai_dist) * distance_w

    wall_score = (ai.walls_left - human.walls_left) * wall_w

    ai_moves    = len(get_valid_moves(board, ai, human))
    human_moves = len(get_valid_moves(board, human, ai))

    mobility_score = (ai_moves - human_moves) * mobility_w

    return distance_score + wall_score + mobility_score

def minimax(board: Board, human: Player, ai: Player, maximise: bool,
            depth: int, alpha: float, beta: float, mode: AIStrategy):
    """Minimax Algorithm to choose the best move"""
    """Choose the move that leads to """
    # Terminal conditions
    if depth == 0:
        return evaluate(board, ai, human, mode)
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

            value = minimax(board, human, ai, False, depth - 1, alpha, beta, mode)

            # Restore position
            ai.r, ai.c = orig_r, orig_c

            # Pruning
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

            value = minimax(board, human, ai, True, depth - 1, alpha, beta, mode)

            # Restore position
            human.r, human.c = orig_r, orig_c

            best = min(best, value)
            beta = min(beta, best)
            if beta <= alpha:
                break

        return best


def get_best_move(board, ai, human, mode):
    """Find the best pawn move for the AI using minimax with alpha-beta pruning."""
    depth = 3 if mode == AIStrategy.HARD else 2

    best_score = float('-inf')
    best_move = None

    moves = get_valid_moves(board, ai, human)
    if not moves:
        return None

    for move in moves:
        orig_r, orig_c = ai.r, ai.c
        ai.r, ai.c = move

        score = minimax(board, human, ai, False, depth - 1,
                        float('-inf'), float('inf'), mode)

        ai.r, ai.c = orig_r, orig_c

        if score > best_score:
            best_score = score
            best_move = move

    return best_move



