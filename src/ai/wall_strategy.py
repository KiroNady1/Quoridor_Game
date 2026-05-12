from game.rules import is_wall_placement_valid
from game.wall import Wall

from ai.evaluation import evaluate_wall
from ai.pathfinding import a_star_distance


def get_candidate_walls(board, ai, human):
    from ui.constants import GRID

    candidates = []

    for player in [ai, human]:
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                for orientation in ["H", "V"]:

                    r = player.r + dr
                    c = player.c + dc

                    if 0 <= r < GRID - 1 and 0 <= c < GRID - 1:
                        candidates.append(Wall(orientation, r, c))

    seen = set()
    unique = []

    for wall in candidates:
        key = wall.key()

        valid, _ = is_wall_placement_valid(
            board,
            wall,
            [ai, human],
        )

        if key not in seen and valid:
            seen.add(key)
            unique.append(wall)

    return unique


def get_best_wall_and_score(
    board,
    ai,
    human,
):
    if ai.walls_left < 1:
        return None, float("-inf")

    original_ai_distance = a_star_distance(board, ai)
    original_human_distance = a_star_distance(board, human)

    candidates = get_candidate_walls(
        board,
        ai,
        human,
    )

    best_score = float("-inf")
    best_wall = None

    for wall in candidates:

        score = evaluate_wall(
            board,
            ai,
            original_ai_distance,
            human,
            original_human_distance,
            wall,
        )

        if score > best_score:
            best_score = score
            best_wall = wall

    return best_wall, best_score
