# file: ui/input_handler.py

import pygame
from typing import Optional
from ui.constants import *
from game.wall import Wall
from game.game import Game
from ui.renderer import GameRenderer


class InputHandler:
    """
    Maintains UI state (mode, selection, hover) and dispatches to Game.
    Blocks player interaction during AI turns.
    """

    def __init__(self, game: Game, renderer: GameRenderer):
        self.game     = game
        self.renderer = renderer

        self.mode          = 'move'     # 'move' | 'wall_h' | 'wall_v'
        self.pawn_selected = False
        self.valid_moves   : list[tuple[int, int]] = []
        self.hover_cell    : Optional[tuple[int, int]] = None
        self.hover_wall    : Optional[Wall] = None
        self.hover_wall_ok : bool = False

    # ── Build ui_state dict for renderer ─────────────────────────────────────

    def ui_state(self, mouse_pos) -> dict:
        return {
            'mode'           : self.mode,
            'selected_pawn'  : self.pawn_selected,
            'valid_moves'    : self.valid_moves,
            'hover_cell'     : self.hover_cell,
            'hover_wall'     : self.hover_wall,
            'hover_wall_ok'  : self.hover_wall_ok,
            'btn_reset_hover': self.renderer.btn_reset.collidepoint(mouse_pos),
        }

    # ── Mouse move ────────────────────────────────────────────────────────────

    def handle_mouse_motion(self, pos):
        self.hover_cell = None
        self.hover_wall = None
        self.hover_wall_ok = False

        if self.game.winner is not None:
            return

        # Block hover effects during AI turn
        if self.game.is_ai_turn():
            return

        cell = self._pixel_to_cell(pos)
        zone = self._pixel_zone(pos)

        if self.mode == 'move':
            if zone == 'cell' and cell:
                self.hover_cell = cell
        elif self.mode in ('wall_h', 'wall_v'):
            wall = self._pixel_to_wall(pos)
            if wall:
                self.hover_wall = wall
                ok, _ = self.game.board.is_wall_placement_valid(
                    wall, self.game.players)
                self.hover_wall_ok = ok and self.game.active.walls_left > 0

    # ── Mouse click ───────────────────────────────────────────────────────────

    def handle_mouse_click(self, pos):
        if self.game.winner is not None:
            if self.renderer.btn_reset.collidepoint(pos):
                self._reset()
            return

        # Reset button is always allowed
        if self.renderer.btn_reset.collidepoint(pos):
            self._reset()
            return

        # Block clicks during AI turn
        if self.game.is_ai_turn():
            return

        if self.mode == 'move':
            self._handle_move_click(pos)
        else:
            self._handle_wall_click(pos)

    def _handle_move_click(self, pos):
        cell = self._pixel_to_cell(pos)
        if not cell:
            self.pawn_selected = False
            self.valid_moves   = []
            return

        r, c = cell
        ap = self.game.active

        if r == ap.r and c == ap.c:
            # Select / deselect own pawn
            if self.pawn_selected:
                self.pawn_selected = False
                self.valid_moves   = []
            else:
                self.pawn_selected = True
                self.valid_moves   = self.game.board.get_valid_moves(
                    ap, self.game.opponent)
            return

        if self.pawn_selected:
            success = self.game.move_pawn(r, c)
            self.pawn_selected = False
            self.valid_moves   = []
            if success:
                pass  # message set by game
        else:
            # Clicking elsewhere without selection
            self.game.set_message("Select your pawn first", C_TEXT_MUTED)

    def _handle_wall_click(self, pos):
        if not self.hover_wall:
            return
        if not self.hover_wall_ok:
            ok, reason = self.game.board.is_wall_placement_valid(
                self.hover_wall, self.game.players)
            if self.game.active.walls_left == 0:
                self.game.set_message("No walls remaining!", C_ERROR)
            else:
                self.game.set_message(f"Invalid: {reason}", C_ERROR)
            return
        self.game.place_wall(self.hover_wall)

    # ── Keyboard ──────────────────────────────────────────────────────────────

    def handle_key(self, key):
        """Handle in-game keys (R, M, H, V). ESC is handled by main loop."""
        if key == pygame.K_r:
            self._reset()
        elif self.game.is_ai_turn():
            # Block mode-switching during AI turn
            return
        elif key == pygame.K_m:
            self._set_mode('move')
        elif key == pygame.K_h:
            self._set_mode('wall_h')
        elif key == pygame.K_v:
            self._set_mode('wall_v')

    # ── Mode switching ────────────────────────────────────────────────────────

    def _set_mode(self, mode: str):
        self.mode          = mode
        self.pawn_selected = False
        self.valid_moves   = []
        self.hover_wall    = None
        labels = {'move': 'Move mode', 'wall_h': 'Horizontal wall mode',
                  'wall_v': 'Vertical wall mode'}
        self.game.set_message(labels[mode], C_TEXT_MUTED)

    def _reset(self):
        self.game.reset()
        self.mode          = 'move'
        self.pawn_selected = False
        self.valid_moves   = []
        self.hover_wall    = None
        self.hover_cell    = None

    # ── Coordinate helpers ────────────────────────────────────────────────────

    @staticmethod
    def _pixel_to_cell(pos) -> Optional[tuple[int, int]]:
        """Returns (row, col) if pos is inside a cell, else None."""
        px, py = pos[0] - PAD, pos[1] - PAD
        if px < 0 or py < 0:
            return None
        c_idx = px // STEP
        r_idx = py // STEP
        if c_idx >= GRID or r_idx >= GRID:
            return None
        # Make sure we're in the cell region, not the gap
        if px - c_idx * STEP < CELL and py - r_idx * STEP < CELL:
            return (r_idx, c_idx)
        return None

    @staticmethod
    def _pixel_zone(pos) -> str:
        """Returns 'cell', 'hgap', 'vgap', or 'corner'."""
        px, py = pos[0] - PAD, pos[1] - PAD
        if px < 0 or py < 0:
            return 'none'
        col_off = px % STEP
        row_off = py % STEP
        in_cell_x = col_off < CELL
        in_cell_y = row_off < CELL
        if in_cell_x and in_cell_y:
            return 'cell'
        if not in_cell_x and in_cell_y:
            return 'vgap'
        if in_cell_x and not in_cell_y:
            return 'hgap'
        return 'corner'

    def _pixel_to_wall(self, pos) -> Optional[Wall]:
        """
        Snaps mouse position to the nearest wall slot.
        """
        px, py = pos[0] - PAD, pos[1] - PAD
        if px < 0 or py < 0:
            return None

        col_f   = px / STEP
        row_f   = py / STEP
        col_idx = int(col_f)
        row_idx = int(row_f)
        col_off = px - col_idx * STEP
        row_off = py - row_idx * STEP

        if self.mode == 'wall_h':
            if row_off < CELL * 0.5:
                row_idx -= 1
            col_idx = max(0, min(col_idx, GRID - 2))
            row_idx = max(0, min(row_idx, GRID - 2))
            return Wall('H', row_idx, col_idx)

        else:  # wall_v
            if col_off < CELL * 0.5:
                col_idx -= 1
            row_idx = max(0, min(row_idx, GRID - 2))
            col_idx = max(0, min(col_idx, GRID - 2))
            return Wall('V', row_idx, col_idx)
