# file: game/wall.py

from dataclasses import dataclass

@dataclass
class Wall:
    """
    A placed wall.
    orientation: 'H' (horizontal) or 'V' (vertical)
    r, c: anchor cell (top-left of the two-cell span)

    Horizontal wall at (r,c):
      - Fills the gap BELOW row r, spanning columns c and c+1
      - Blocks movement between (r,c)↔(r+1,c)  and  (r,c+1)↔(r+1,c+1)

    Vertical wall at (r,c):
      - Fills the gap RIGHT of col c, spanning rows r and r+1
      - Blocks movement between (r,c)↔(r,c+1)  and  (r+1,c)↔(r+1,c+1)
    """
    orientation: str   # 'H' or 'V'
    r: int
    c: int
    owner: int = -1    # 0 = P1, 1 = P2, -1 = unassigned

    def key(self):
        return (self.orientation, self.r, self.c)
