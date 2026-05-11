# file: game/player.py

from dataclasses import dataclass
from ui.constants import INITIAL_WALLS

@dataclass
class Player:
    idx: int          # 0 = P1, 1 = P2
    r:   int          # current row
    c:   int          # current col
    walls_left: int = INITIAL_WALLS

    @property
    def goal_row(self) -> int:
        """P1 (idx=0) starts at row 8, must reach row 0.
           P2 (idx=1) starts at row 0, must reach row 8."""
        return 0 if self.idx == 0 else 8
