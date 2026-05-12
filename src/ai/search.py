import copy

from game.board import Board
from game.player import Player
from game.rules import get_valid_moves

from ai.evaluation import evaluate
from ai.models import EvalWeights
from ai.move_ordering import order_moves

def minimax(
    board: Board,
    human: Player,
    ai: Player,
    maximise: bool,
    depth: int,
    alpha: float,
    beta: float,
    weights: EvalWeights,
    use_astar: bool = False,
) -> float:

    if ai.r == ai.goal_row:
        return float("inf")

    if human.r == human.goal_row:
        return float("-inf")

    if depth == 0:
        return evaluate(
            board,
            ai,
            human,
            weights,
            use_astar,
        )

    if maximise:
        best = float("-inf")
        
        moves = order_moves(board, ai, human, get_valid_moves(board, ai, human), use_astar)
        for move in moves:

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

    best = float("inf")

    moves = order_moves(board, human, ai, get_valid_moves(board, human, ai), use_astar)
    for move in moves:

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