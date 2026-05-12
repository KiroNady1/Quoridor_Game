import copy
from ai.pathfinding import a_star_distance, bfs_distance
from game.player import Player
from game.board import Board


def order_moves(board: Board, ai: Player, human: Player, moves, use_astar: bool):
    """
    Returns moves sorted from best to worst for alpha-beta pruning.
    """

    def move_score(move):
        next_ai = copy.copy(ai)
        next_ai.r, next_ai.c = move

        # distance heuristic (main signal)
        if use_astar:
            ai_dist = a_star_distance(board, next_ai)
            human_dist = a_star_distance(board, human)
        else:
            ai_dist = bfs_distance(board, next_ai)
            human_dist = bfs_distance(board, human)

        # closer to goal is better
        score = -ai_dist * 10

        # pushing opponent further is good
        score += human_dist * 5

        # slight bias toward center mobility (cheap proxy)
        score += len(getattr(board, "adjacent_cells", [])) if hasattr(board, "adjacent_cells") else 0

        return score

    return sorted(moves, key=move_score, reverse=True)