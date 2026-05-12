import copy
import sys

from game.board import Board
from game.player import Player
from game.rules import get_valid_moves
from game.wall import Wall

from ai.models import EvalWeights
from ai.pathfinding import (
    a_star_distance,
    bfs_distance,
)


def evaluate(
    board: Board,
    ai: Player,
    human: Player,
    weights: EvalWeights,
    use_astar: bool = False,
) -> int:

    if use_astar:
        ai_dist = a_star_distance(board, ai)
        human_dist = a_star_distance(board, human)
    else:
        ai_dist = bfs_distance(board, ai)
        human_dist = bfs_distance(board, human)

    distance_score = (human_dist - ai_dist) * weights.distance

    wall_score = (ai.walls_left - human.walls_left) * weights.walls

    ai_moves = len(get_valid_moves(board, ai, human))
    human_moves = len(get_valid_moves(board, human, ai))

    mobility_score = (ai_moves - human_moves) * weights.mobility

    return distance_score + wall_score + mobility_score


def evaluate_wall(
    board: Board,
    ai: Player,
    original_ai_distance: int,
    human: Player,
    original_human_distance: int,
    wall: Wall,
) -> int:

    LARGE_PENALTY = -999999

    new_board = copy.deepcopy(board)
    new_board.add_wall(wall)

    new_ai_distance = a_star_distance(new_board, ai)
    new_human_distance = a_star_distance(new_board, human)

    if new_ai_distance == sys.maxsize or new_human_distance == sys.maxsize:
        return LARGE_PENALTY

    human_improvement = (new_human_distance - original_human_distance) * 2

    ai_improvement = original_ai_distance - new_ai_distance

    return human_improvement + ai_improvement
