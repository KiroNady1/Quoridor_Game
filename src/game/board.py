# file: game/board.py

from ui.constants import GRID
from game.wall import Wall
from game.rules import get_valid_moves, is_wall_placement_valid

class Board:
    """
    Owns the wall set and basic blocking logic.
    """

    def __init__(self):
        self.walls: list[Wall] = []
        self._wall_keys: set   = set()   # fast lookup

    # ── Wall helpers ──────────────────────────────────────────────────────────

    def has_wall(self, orientation: str, r: int, c: int) -> bool:
        return (orientation, r, c) in self._wall_keys

    def add_wall(self, wall: Wall):
        self.walls.append(wall)
        self._wall_keys.add(wall.key())

    def remove_wall(self, wall: Wall):
        """Remove a wall from the board (used by undo)."""
        if wall in self.walls:
            self.walls.remove(wall)
        self._wall_keys.discard(wall.key())

    # ── Movement blocking ─────────────────────────────────────────────────────

    def is_blocked(self, r1: int, c1: int, r2: int, c2: int) -> bool:
        """
        Returns True if a wall blocks the single-step move from (r1,c1) to (r2,c2).
        Only orthogonal single steps are supported here.
        """
        if r1 == r2:
            # Horizontal move – blocked by a vertical wall
            cc = min(c1, c2)   # wall anchor column
            return (self.has_wall('V', r1, cc) or
                    self.has_wall('V', r1 - 1, cc))
        else:
            # Vertical move – blocked by a horizontal wall
            rr = min(r1, r2)
            return (self.has_wall('H', rr, c1) or
                    self.has_wall('H', rr, c1 - 1))

    def can_step(self, r1: int, c1: int, r2: int, c2: int) -> bool:
        """True if the step is on-board and not wall-blocked."""
        if r2 < 0 or r2 >= GRID or c2 < 0 or c2 >= GRID:
            return False
        return not self.is_blocked(r1, c1, r2, c2)

    # ── Delegated rules ───────────────────────────────────────────────────────

    def get_valid_moves(self, mover, other):
        return get_valid_moves(self, mover, other)

    def is_wall_placement_valid(self, wall, players):
        return is_wall_placement_valid(self, wall, players)
