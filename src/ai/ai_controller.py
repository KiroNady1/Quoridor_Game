import copy

from ai.config import Mode, get_config
from ai.logger import logger
from ai.search import minimax
from ai.wall_strategy import get_best_wall_and_score
from game.rules import get_valid_moves
from ai.transposition import Transposition_Table


def get_best_move(board, ai, human, mode):
    # Clear transposition table cache to avoid stale values from previous turns / games
    Transposition_Table.clear()

    config = get_config(mode)

    moves = get_valid_moves(board, ai, human)

    if not moves:
        return None

    best_score = float("-inf")
    best_move = moves[0]

    for move in moves:
        next_ai = copy.copy(ai)
        next_ai.r, next_ai.c = move

        score = minimax(
            board,
            human,
            next_ai,
            False,
            config.depth - 1,
            float("-inf"),
            float("inf"),
            config.weights,
            config.use_astar,
        )

        if score > best_score:
            best_score = score
            best_move = move

    if mode in [Mode.EASY, Mode.MEDIUM]:
        return ["move", best_move]

    best_wall, best_wall_score = get_best_wall_and_score(
        board,
        ai,
        human,
    )

    if best_wall is not None and best_wall_score > best_score:
        logger.debug(f"Selected wall: {best_wall}")

        return ["wall", best_wall]

    logger.debug(f"Selected move: {best_move}")

    return ["move", best_move]
