"""
quoridor.py — Quoridor game in pygame (Human vs Human)
Run: python quoridor.py
"""

import pygame
import sys
from collections import deque

# ─────────────────────────────────────────────
#  Settings
# ─────────────────────────────────────────────
COLS = ROWS = 9
CELL        = 60
GAP         = 10
FENCES_EACH = 10

WIN_W = COLS * CELL + (COLS - 1) * GAP
WIN_H = ROWS * CELL + (ROWS - 1) * GAP + 80

# Colors
BG        = (30,  30,  40)
CELL_COL  = (220, 220, 220)
P1_COL    = (220,  60,  60)
P2_COL    = (60,  120, 220)
FENCE_P1  = (200,  50,  50)
FENCE_P2  = (50,  100, 200)
HIGHLIGHT = (255, 220,  50)
TEXT_COL  = (240, 240, 240)
WIN_COL   = (50,  200,  80)

# ─────────────────────────────────────────────
#  Grid / pixel helpers
# ─────────────────────────────────────────────
def cell_rect(col, row):
    x = col * (CELL + GAP)
    y = row * (CELL + GAP) + 80
    return pygame.Rect(x, y, CELL, CELL)

def cell_center(col, row):
    r = cell_rect(col, row)
    return r.centerx, r.centery

def pixel_to_cell(px, py):
    """Return (col, row) if mouse is over a cell, else None."""
    py -= 80
    if py < 0:
        return None
    step = CELL + GAP
    col = px // step
    row = py // step
    rx = px % step
    ry = py % step
    if col < 0 or col >= COLS or row < 0 or row >= ROWS:
        return None
    if rx < CELL and ry < CELL:
        return (col, row)
    return None

def pixel_to_fence(px, py):
    """Return (col, row, direction) for the fence slot under the mouse, else None."""
    py -= 80
    if py < 0:
        return None
    step = CELL + GAP
    col = px // step
    row = py // step
    rx = px % step
    ry = py % step

    if CELL <= rx < CELL + GAP and ry < CELL:
        fc, fr = col + 1, row
        if 0 < fc < COLS and 0 <= fr < ROWS - 1:
            return (fc, fr, 'V')

    if rx < CELL and CELL <= ry < CELL + GAP:
        fc, fr = col, row + 1
        if 0 <= fc < COLS - 1 and 0 < fr < ROWS:
            return (fc, fr, 'H')

    return None

# ─────────────────────────────────────────────
#  Game logic
# ─────────────────────────────────────────────
class Quoridor:
    def __init__(self):
        self.reset()

    def reset(self):
        self.pos = [(4, 0), (4, 8)]
        self.fences_left = [FENCES_EACH, FENCES_EACH]
        self.fences = []   # each entry: (col, row, dir, owner)
        self.turn   = 0
        self.winner = None
        self.mode   = 'move'
        self.undo_stack = []
        self.redo_stack = []

    def _snapshot(self):
        return {
            'pos':         self.pos[:],
            'fences_left': self.fences_left[:],
            'fences':      self.fences[:],
            'turn':        self.turn,
            'winner':      self.winner,
            'mode':        self.mode,
        }

    def _restore(self, snap):
        self.pos         = snap['pos'][:]
        self.fences_left = snap['fences_left'][:]
        self.fences      = snap['fences'][:]
        self.turn        = snap['turn']
        self.winner      = snap['winner']
        self.mode        = snap['mode']

    def _push_undo(self):
        self.undo_stack.append(self._snapshot())
        self.redo_stack.clear()

    def undo(self):
        if not self.undo_stack:
            return
        self.redo_stack.append(self._snapshot())
        self._restore(self.undo_stack.pop())

    def redo(self):
        if not self.redo_stack:
            return
        self.undo_stack.append(self._snapshot())
        self._restore(self.redo_stack.pop())

    def has_fence_between(self, c1, r1, c2, r2):
        """Return True if a fence blocks movement between two adjacent cells."""
        dc, dr = c2 - c1, r2 - r1

        if dr == -1:
            for f in self.fences:
                if f[2] == 'H' and f[1] == r1 and (f[0] == c1 or f[0] == c1 - 1):
                    return True

        if dr == 1:
            for f in self.fences:
                if f[2] == 'H' and f[1] == r2 and (f[0] == c2 or f[0] == c2 - 1):
                    return True

        if dc == -1:
            for f in self.fences:
                if f[2] == 'V' and f[0] == c1 and (f[1] == r1 or f[1] == r1 - 1):
                    return True

        if dc == 1:
            for f in self.fences:
                if f[2] == 'V' and f[0] == c2 and (f[1] == r2 or f[1] == r2 - 1):
                    return True

        return False

    def neighbors(self, col, row, ignore_pawns=False):
        """Return adjacent cells reachable without crossing a fence."""
        result = []
        p_other = self.pos[1 - self.turn] if not ignore_pawns else None

        for dc, dr in [(-1,0),(1,0),(0,-1),(0,1)]:
            nc, nr = col + dc, row + dr
            if 0 <= nc < COLS and 0 <= nr < ROWS:
                if not self.has_fence_between(col, row, nc, nr):
                    result.append((nc, nr))
        return result

    def valid_moves(self):
        col, row = self.pos[self.turn]
        other    = self.pos[1 - self.turn]
        moves = []

        for dc, dr in [(-1,0),(1,0),(0,-1),(0,1)]:
            nc, nr = col + dc, row + dr
            if 0 <= nc < COLS and 0 <= nr < ROWS:
                if self.has_fence_between(col, row, nc, nr):
                    continue
                if (nc, nr) == other:
                    jc, jr = nc + dc, nr + dr
                    if 0 <= jc < COLS and 0 <= jr < ROWS and not self.has_fence_between(nc, nr, jc, jr):
                        moves.append((jc, jr))
                    else:
                        for sdc, sdr in [(-1,0),(1,0),(0,-1),(0,1)]:
                            if (sdc, sdr) == (dc, dr) or (sdc, sdr) == (-dc, -dr):
                                continue
                            sc, sr = nc + sdc, nr + sdr
                            if 0 <= sc < COLS and 0 <= sr < ROWS and not self.has_fence_between(nc, nr, sc, sr):
                                moves.append((sc, sr))
                else:
                    moves.append((nc, nr))
        return moves

    def path_exists(self, start, goals, temp_fence=None):
        """BFS: return True if a path from start to any goal exists."""
        old = self.fences[:]
        if temp_fence:
            self.fences.append((*temp_fence, -1))
        visited = {start}
        queue   = deque([start])
        found   = False
        while queue:
            c, r = queue.popleft()
            if (c, r) in goals:
                found = True
                break
            for nc, nr in self.neighbors(c, r, ignore_pawns=True):
                if (nc, nr) not in visited:
                    visited.add((nc, nr))
                    queue.append((nc, nr))
        self.fences = old
        return found

    def fence_valid(self, fc, fr, fd):
        """Return True if placing fence (fc, fr, fd) is a legal move."""
        if fd == 'H':
            if not (0 <= fc < COLS - 1 and 0 < fr < ROWS):
                return False
        else:
            if not (0 < fc < COLS and 0 <= fr < ROWS - 1):
                return False

        # Check overlap with existing fences
        for f in self.fences:
            if (f[0], f[1], f[2]) == (fc, fr, fd):
                return False
            if fd == 'H' and f[2] == 'H':
                if f[1] == fr and abs(f[0] - fc) < 2:
                    return False
            if fd == 'V' and f[2] == 'V':
                if f[0] == fc and abs(f[1] - fr) < 2:
                    return False
            if fd == 'H' and f[2] == 'V':
                if f[0] == fc + 1 and f[1] == fr - 1:
                    return False
            if fd == 'V' and f[2] == 'H':
                if f[1] == fr + 1 and f[0] == fc - 1:
                    return False

        # Ensure no player is blocked
        goals = [[(c, ROWS-1) for c in range(COLS)], [(c, 0) for c in range(COLS)]]
        for i, p in enumerate(self.pos):
            if not self.path_exists(p, goals[i], temp_fence=(fc, fr, fd)):
                return False
        return True

    def do_move(self, col, row):
        self._push_undo()
        self.pos[self.turn] = (col, row)
        self._check_win()
        if not self.winner:
            self.turn = 1 - self.turn

    def do_fence(self, fc, fr, fd):
        self._push_undo()
        self.fences.append((fc, fr, fd, self.turn))
        self.fences_left[self.turn] -= 1
        self.turn = 1 - self.turn

    def _check_win(self):
        c, r = self.pos[self.turn]
        if self.turn == 0 and r == ROWS - 1:
            self.winner = 0
        elif self.turn == 1 and r == 0:
            self.winner = 1

# ─────────────────────────────────────────────
#  Drawing
# ─────────────────────────────────────────────
def draw_board(screen, game, font, small_font, hover_cell, hover_fence):
    screen.fill(BG)

    p_name = ["Player 1 (Red)", "Player 2 (Blue)"]
    p_col  = [P1_COL, P2_COL]
    mode_txt = "Move mode [M]" if game.mode == 'move' else "Fence mode [F]"

    if game.winner is not None:
        msg = f"Player {game.winner + 1} wins!   Press R to restart"
        surf = font.render(msg, True, WIN_COL)
    else:
        undo_hint = f"  |  Ctrl+Z / Ctrl+Y"
        info = (f"{p_name[game.turn]}  |  Fences: "
                f"P1={game.fences_left[0]}  P2={game.fences_left[1]}  |  {mode_txt}{undo_hint}")
        surf = small_font.render(info, True, p_col[game.turn])

    screen.blit(surf, (10, 25 - surf.get_height()//2))

    for c in range(COLS):
        for r in range(ROWS):
            rect = cell_rect(c, r)
            col  = HIGHLIGHT if hover_cell == (c, r) else CELL_COL
            pygame.draw.rect(screen, col, rect, border_radius=6)

    # Placed fences
    for fc, fr, fd, owner in game.fences:
        fence_col = FENCE_P1 if owner == 0 else FENCE_P2
        draw_fence(screen, fc, fr, fd, fence_col)

    if hover_fence and game.mode == 'fence':
        fc, fr, fd = hover_fence
        if game.fence_valid(fc, fr, fd):
            s = pygame.Surface((WIN_W, WIN_H), pygame.SRCALPHA)
            preview_col = (*(P1_COL if game.turn == 0 else P2_COL), 140)
            draw_fence(s, fc, fr, fd, preview_col)
            screen.blit(s, (0, 0))

    for i, (c, r) in enumerate(game.pos):
        cx, cy = cell_center(c, r)
        col = P1_COL if i == 0 else P2_COL
        pygame.draw.circle(screen, col, (cx, cy), CELL // 2 - 4)
        lbl = small_font.render(str(i+1), True, (255,255,255))
        screen.blit(lbl, (cx - lbl.get_width()//2, cy - lbl.get_height()//2))

    if game.winner is None and game.mode == 'move':
        for mc, mr in game.valid_moves():
            cx, cy = cell_center(mc, mr)
            pygame.draw.circle(screen, HIGHLIGHT, (cx, cy), 8)

    pygame.display.flip()


def draw_fence(surface, fc, fr, fd, color):
    step = CELL + GAP
    if fd == 'H':
        x  = fc * step
        y  = fr * step + 80 - GAP
        w  = 2 * CELL + GAP
        h  = GAP
    else:
        x  = fc * step - GAP
        y  = fr * step + 80
        w  = GAP
        h  = 2 * CELL + GAP
    pygame.draw.rect(surface, color, (x, y, w, h), border_radius=3)


# ─────────────────────────────────────────────
#  Main loop
# ─────────────────────────────────────────────
def main():
    pygame.init()
    screen = pygame.display.set_mode((WIN_W, WIN_H))
    pygame.display.set_caption("Quoridor")

    try:
        font       = pygame.font.SysFont("Arial", 20)
        small_font = pygame.font.SysFont("Arial", 16)
    except Exception:
        font       = pygame.font.Font(None, 26)
        small_font = pygame.font.Font(None, 20)

    clock = pygame.time.Clock()
    game  = Quoridor()
    hover_cell  = None
    hover_fence = None

    while True:
        mx, my = pygame.mouse.get_pos()
        hover_cell  = pixel_to_cell(mx, my)
        hover_fence = pixel_to_fence(mx, my)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            if event.type == pygame.KEYDOWN:
                ctrl = pygame.key.get_mods() & pygame.KMOD_CTRL
                if event.key == pygame.K_r:
                    game.reset()
                elif ctrl and event.key == pygame.K_z:
                    game.undo()
                elif ctrl and (event.key == pygame.K_y or
                               (event.key == pygame.K_z and pygame.key.get_mods() & pygame.KMOD_SHIFT)):
                    game.redo()
                elif event.key == pygame.K_m:
                    game.mode = 'move'
                elif event.key == pygame.K_f and game.fences_left[game.turn] > 0:
                    game.mode = 'fence'

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if game.winner is not None:
                    continue

                if game.mode == 'move' and hover_cell:
                    if hover_cell in game.valid_moves():
                        game.do_move(*hover_cell)
                        game.mode = 'move'

                elif game.mode == 'fence' and hover_fence:
                    fc, fr, fd = hover_fence
                    if game.fence_valid(fc, fr, fd):
                        game.do_fence(fc, fr, fd)
                        game.mode = 'move'

        draw_board(screen, game, font, small_font, hover_cell, hover_fence)
        clock.tick(60)


if __name__ == "__main__":
    main()