# file: game/rules.py

from ui.constants import GRID
from game.wall import Wall
from game.player import Player
from game.pathfinding import bfs_path_exists

def get_valid_moves(board, mover: Player, other: Player) -> list[tuple[int, int]]:
    """
    Returns list of (r,c) the mover can legally move to this turn.
    Handles straight moves, straight jumps, and diagonal jumps.
    """
    moves = []
    for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        nr, nc = mover.r + dr, mover.c + dc

        # Out of bounds or wall blocks first step
        if not board.can_step(mover.r, mover.c, nr, nc):
            continue

        if nr == other.r and nc == other.c:
            # Adjacent to opponent – try straight jump first
            jr, jc = nr + dr, nc + dc
            if board.can_step(nr, nc, jr, jc):
                moves.append((jr, jc))
            else:
                # Straight jump blocked – diagonal moves around opponent
                for ddr, ddc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                    if ddr == -dr and ddc == -dc:
                        continue   # don't go back the way we came
                    tr, tc = nr + ddr, nc + ddc
                    if board.can_step(nr, nc, tr, tc):
                        moves.append((tr, tc))
        else:
            moves.append((nr, nc))

    return moves

def is_wall_placement_valid(board, wall: Wall, players: list[Player]) -> tuple[bool, str]:
    """
    Returns (ok, reason).
    Checks: bounds, overlap, crossing, and path-existence for both players.
    """
    o, r, c = wall.orientation, wall.r, wall.c

    # Bounds: anchor must leave room for the 2-cell span
    if r < 0 or c < 0:
        return False, "Out of bounds"
    if o == 'H' and (r >= GRID - 1 or c >= GRID - 1):
        return False, "Out of bounds"
    if o == 'V' and (r >= GRID - 1 or c >= GRID - 1):
        return False, "Out of bounds"

    # Overlap: same orientation wall at same anchor
    if board.has_wall(o, r, c):
        return False, "Wall already there"

    # Overlap with adjacent same-orientation walls
    if o == 'H':
        if board.has_wall('H', r, c - 1) or board.has_wall('H', r, c + 1):
            return False, "Overlaps existing wall"
        # Crossing: a V wall at (r, c) would cross this H wall
        if board.has_wall('V', r, c):
            return False, "Walls would cross"
    else:  # V
        if board.has_wall('V', r - 1, c) or board.has_wall('V', r + 1, c):
            return False, "Overlaps existing wall"
        # Crossing: an H wall at (r, c) would cross this V wall
        if board.has_wall('H', r, c):
            return False, "Walls would cross"

    # Temporarily add wall and BFS-check paths for both players
    board.add_wall(wall)
    ok = True
    reason = ""
    for p in players:
        if not bfs_path_exists(board, p):
            ok = False
            reason = "Would trap a player"
            break
    # Remove the temporary wall
    board.walls.pop()
    board._wall_keys.discard(wall.key())

    return ok, reason

#To implement
def get_valid_walls():
    pass