import copy

from game.board import Board
from game.player import Player
from game.rules import get_valid_moves

from ai.evaluation import evaluate
from ai.models import EvalWeights
from ai.move_ordering import order_moves
from ai.transposition import Transposition_Table
from ai.hasher import Hasher

hasher = Hasher()

def minimax(
    board,
    human,
    ai,
    maximise,
    depth,
    alpha,
    beta,
    weights,
    use_astar=False,
):

    key = hasher.hash(board, ai, human)

    if key in Transposition_Table:
        stored_depth, stored_value = Transposition_Table[key]
        if stored_depth >= depth:
            return stored_value

    if ai.r == ai.goal_row:
        return float("inf")

    if human.r == human.goal_row:
        return float("-inf")

    if depth == 0:
        return evaluate(board, ai, human, weights, use_astar)

    if maximise:
        best = float("-inf")

        for move in get_valid_moves(board, ai, human):

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

    else:
        best = float("inf")

        for move in get_valid_moves(board, human, ai):

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

    Transposition_Table[key] = (depth, best)
    return best