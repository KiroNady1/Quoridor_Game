# file: ui/renderer.py

import pygame
from ui.constants import *
from game.wall import Wall
from game.player import Player
from game.game import Game


class GameRenderer:
    """
    Stateless renderer: draws whatever state it receives.
    Includes main menu and difficulty selection screens.
    """

    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        pygame.font.init()
        self.font_lg    = pygame.font.SysFont("Segoe UI", 22, bold=True)
        self.font_md    = pygame.font.SysFont("Segoe UI", 17)
        self.font_sm    = pygame.font.SysFont("Segoe UI", 14)
        self.font_title = pygame.font.SysFont("Segoe UI", 52, bold=True)
        self.font_sub   = pygame.font.SysFont("Segoe UI", 18)
        self.font_btn   = pygame.font.SysFont("Segoe UI", 21, bold=True)
        self.font_badge = pygame.font.SysFont("Segoe UI", 13, bold=True)

        # Overlay surface for transparent hints
        self.overlay = pygame.Surface((WIN_W, WIN_H), pygame.SRCALPHA)

        # Button rect (reset)
        self.btn_reset = pygame.Rect(WIN_W - 220, WIN_H - 52, 180, 38)

        # ── Menu button rects ────────────────────────────────────────────────
        btn_w, btn_h = 320, 58
        cx = WIN_W // 2

        # Main menu
        self.btn_pvp = pygame.Rect(cx - btn_w // 2, 320, btn_w, btn_h)
        self.btn_ai  = pygame.Rect(cx - btn_w // 2, 400, btn_w, btn_h)

        # Difficulty menu
        self.btn_easy   = pygame.Rect(cx - btn_w // 2, 270, btn_w, btn_h)
        self.btn_medium = pygame.Rect(cx - btn_w // 2, 350, btn_w, btn_h)
        self.btn_hard   = pygame.Rect(cx - btn_w // 2, 430, btn_w, btn_h)
        self.btn_back   = pygame.Rect(cx - btn_w // 2, 540, btn_w, 46)

    # ══════════════════════════════════════════════════════════════════════════
    # MENU SCREENS
    # ══════════════════════════════════════════════════════════════════════════

    def draw_menu(self, mouse_pos):
        """Draw the main menu (mode selection)."""
        self.screen.fill(C_BG)
        self._draw_menu_grid_bg()

        # Title
        title = self.font_title.render("QUORIDOR", True, C_MENU_ACCENT)
        self.screen.blit(title, title.get_rect(center=(WIN_W // 2, 150)))

        # Subtitle
        sub = self.font_sub.render("A Strategic Board Game", True, C_TEXT_MUTED)
        self.screen.blit(sub, sub.get_rect(center=(WIN_W // 2, 210)))

        # Divider line
        div_y = 260
        pygame.draw.line(self.screen, (50, 65, 100),
                         (WIN_W // 2 - 120, div_y), (WIN_W // 2 + 120, div_y), 1)

        lbl = self.font_sm.render("Choose Game Mode", True, C_TEXT_MUTED)
        self.screen.blit(lbl, lbl.get_rect(center=(WIN_W // 2, div_y + 20)))

        # Buttons
        self._draw_styled_btn(self.btn_pvp, "Human  vs  Human", mouse_pos, C_WALL_P2)
        self._draw_styled_btn(self.btn_ai,  "Human  vs  AI",    mouse_pos, C_WALL_P1)

        # Footer
        foot = self.font_sm.render("ESC during game to return here", True, (60, 70, 95))
        self.screen.blit(foot, foot.get_rect(center=(WIN_W // 2, WIN_H - 40)))

    def draw_difficulty_menu(self, mouse_pos, coming_soon_flash=False):
        """Draw the difficulty selection screen."""
        self.screen.fill(C_BG)
        self._draw_menu_grid_bg()

        # Title
        title = self.font_title.render("SELECT DIFFICULTY", True, C_MENU_ACCENT)
        self.screen.blit(title, title.get_rect(center=(WIN_W // 2, 150)))

        sub = self.font_sub.render("Human vs AI", True, C_TEXT_MUTED)
        self.screen.blit(sub, sub.get_rect(center=(WIN_W // 2, 210)))

        # Easy – disabled with Coming Soon badge
        self._draw_styled_btn(self.btn_easy, "Easy", mouse_pos, C_WALL_P2)

        # Medium
        self._draw_styled_btn(self.btn_medium, "Medium", mouse_pos, C_WALL_P2)

        # Hard
        self._draw_styled_btn(self.btn_hard, "Hard", mouse_pos, C_WALL_P1)

        # Back button
        hover = self.btn_back.collidepoint(mouse_pos)
        col = (45, 55, 80) if hover else (30, 40, 65)
        pygame.draw.rect(self.screen, col, self.btn_back, border_radius=6)
        pygame.draw.rect(self.screen, C_BTN_BORDER, self.btn_back, 1, border_radius=6)
        lbl = self.font_md.render("<  Back to Menu", True, C_TEXT_MUTED)
        self.screen.blit(lbl, lbl.get_rect(center=self.btn_back.center))

    # ── Menu helpers ─────────────────────────────────────────────────────────

    def _draw_menu_grid_bg(self):
        """Draw a faint decorative grid behind the menu."""
        overlay = pygame.Surface((WIN_W, WIN_H), pygame.SRCALPHA)
        for r in range(GRID):
            for c in range(GRID):
                x = WIN_W // 2 - (GRID * 28) // 2 + c * 28
                y = WIN_H - 200 + r * 28
                pygame.draw.rect(overlay, (30, 42, 75, 30),
                                 pygame.Rect(x, y, 22, 22), border_radius=2)
        self.screen.blit(overlay, (0, 0))

    def _draw_styled_btn(self, rect, text, mouse_pos, accent_color):
        """Draw a menu button with hover effect and accent left-bar."""
        hover = rect.collidepoint(mouse_pos)
        bg = C_MENU_BTN_HOV if hover else C_MENU_BTN
        pygame.draw.rect(self.screen, bg, rect, border_radius=8)
        # Accent bar on left
        bar = pygame.Rect(rect.x, rect.y, 5, rect.h)
        pygame.draw.rect(self.screen, accent_color, bar,
                         border_top_left_radius=8, border_bottom_left_radius=8)
        # Border
        border_col = accent_color if hover else C_BTN_BORDER
        pygame.draw.rect(self.screen, border_col, rect, 2, border_radius=8)
        # Label
        col = (255, 255, 255) if hover else C_TEXT
        lbl = self.font_btn.render(text, True, col)
        self.screen.blit(lbl, lbl.get_rect(center=rect.center))

    def _draw_disabled_btn(self, rect, text, mouse_pos):
        """Draw a disabled button with 'Coming Soon' badge."""
        pygame.draw.rect(self.screen, C_MENU_DISABLED, rect, border_radius=8)
        pygame.draw.rect(self.screen, (50, 60, 85), rect, 2, border_radius=8)
        # Label (dimmed)
        lbl = self.font_btn.render(text, True, (80, 90, 110))
        self.screen.blit(lbl, lbl.get_rect(center=(rect.centerx - 50, rect.centery)))
        # Coming Soon badge
        badge_w, badge_h = 120, 24
        badge = pygame.Rect(rect.right - badge_w - 12, rect.centery - badge_h // 2,
                            badge_w, badge_h)
        pygame.draw.rect(self.screen, (60, 45, 10), badge, border_radius=12)
        pygame.draw.rect(self.screen, C_COMING_SOON, badge, 1, border_radius=12)
        badge_lbl = self.font_badge.render("Coming Soon", True, C_COMING_SOON)
        self.screen.blit(badge_lbl, badge_lbl.get_rect(center=badge.center))

    def get_menu_button_at(self, pos):
        """Return 'pvp', 'ai', or None for main menu."""
        if self.btn_pvp.collidepoint(pos):
            return 'pvp'
        if self.btn_ai.collidepoint(pos):
            return 'ai'
        return None

    def get_difficulty_button_at(self, pos):
        """Return 'easy', 'medium', 'hard', 'back', or None."""
        if self.btn_easy.collidepoint(pos):
            return 'easy'
        if self.btn_medium.collidepoint(pos):
            return 'medium'
        if self.btn_hard.collidepoint(pos):
            return 'hard'
        if self.btn_back.collidepoint(pos):
            return 'back'
        return None

    # ══════════════════════════════════════════════════════════════════════════
    # GAME RENDERING (existing, with AI-aware updates)
    # ══════════════════════════════════════════════════════════════════════════

    # ── Coordinate helpers ────────────────────────────────────────────────────

    @staticmethod
    def cell_rect(r: int, c: int) -> pygame.Rect:
        x = PAD + c * STEP
        y = PAD + r * STEP
        return pygame.Rect(x, y, CELL, CELL)

    @staticmethod
    def cell_center(r: int, c: int) -> tuple[int, int]:
        rect = GameRenderer.cell_rect(r, c)
        return rect.centerx, rect.centery

    # ── Master draw ───────────────────────────────────────────────────────────

    def draw(self, game: Game, ui_state):
        """
        ui_state: dict with keys
          selected_pawn: bool – pawn is selected
          valid_moves  : list[(r,c)]
          hover_wall   : Wall | None  – wall under mouse cursor
          hover_wall_ok: bool
          hover_cell   : (r,c) | None
        """
        self.screen.fill(C_BG)
        self.overlay.fill((0, 0, 0, 0))

        self._draw_goal_rows()
        self._draw_cells(ui_state)
        self._draw_walls(game.board.walls)
        self._draw_wall_preview(ui_state)
        self._draw_move_hints(ui_state)
        self._draw_pawns(game.players)
        self._draw_panel(game, ui_state)
        self._draw_message(game)
        self._draw_reset_button(ui_state)

        self.screen.blit(self.overlay, (0, 0))

    # ── Goal rows ─────────────────────────────────────────────────────────────

    def _draw_goal_rows(self):
        for c in range(GRID):
            r0 = GameRenderer.cell_rect(0, c)
            r8 = GameRenderer.cell_rect(8, c)
            pygame.draw.rect(self.overlay, C_GOAL_P1, r8.inflate(0, 0))
            pygame.draw.rect(self.overlay, C_GOAL_P2, r0.inflate(0, 0))

    # ── Cells ─────────────────────────────────────────────────────────────────

    def _draw_cells(self, ui_state):
        hover = ui_state.get('hover_cell')
        for r in range(GRID):
            for c in range(GRID):
                rect  = GameRenderer.cell_rect(r, c)
                color = C_CELL_HOVER if hover == (r, c) else C_CELL
                pygame.draw.rect(self.screen, color, rect, border_radius=4)
                pygame.draw.rect(self.screen, C_GRID_LINE, rect, 1, border_radius=4)

    # ── Move hints ────────────────────────────────────────────────────────────

    def _draw_move_hints(self, ui_state):
        if not ui_state.get('selected_pawn'):
            return
        hover = ui_state.get('hover_cell')
        for (r, c) in ui_state.get('valid_moves', []):
            rect  = GameRenderer.cell_rect(r, c)
            color = (120, 220, 140, 200) if hover == (r, c) else C_MOVE_HINT
            pygame.draw.rect(self.overlay, color, rect, border_radius=4)
            # Ring marker
            pygame.draw.rect(self.overlay, (80, 200, 100, 230), rect, 2, border_radius=4)

    # ── Walls ─────────────────────────────────────────────────────────────────

    def _wall_rect(self, wall: Wall) -> pygame.Rect:
        """Return the screen Rect for a wall."""
        r, c, o = wall.r, wall.c, wall.orientation
        if o == 'H':
            # Below row r, spanning col c to c+1
            x = PAD + c * STEP
            y = PAD + r * STEP + CELL + (GAP - WALL_THICK) // 2
            w = 2 * CELL + GAP
            h = WALL_THICK
        else:
            # Right of col c, spanning row r to r+1
            x = PAD + c * STEP + CELL + (GAP - WALL_THICK) // 2
            y = PAD + r * STEP
            w = WALL_THICK
            h = 2 * CELL + GAP
        return pygame.Rect(x, y, w, h)

    def _draw_walls(self, walls: list[Wall]):
        colors = [C_WALL_P1, C_WALL_P2]
        highlights = [(255, 120, 140), (100, 210, 240)]
        for wall in walls:
            rect  = self._wall_rect(wall)
            color = colors[wall.owner] if wall.owner >= 0 else C_WALL_P1
            pygame.draw.rect(self.screen, color, rect, border_radius=4)
            # Subtle inner highlight
            inner = rect.inflate(-2, -2)
            hl = highlights[wall.owner] if wall.owner >= 0 else highlights[0]
            pygame.draw.rect(self.screen, hl, inner, 1, border_radius=3)

    def _draw_wall_preview(self, ui_state):
        hw = ui_state.get('hover_wall')
        if hw is None:
            return
        rect  = self._wall_rect(hw)
        color = C_WALL_PRE_OK if ui_state.get('hover_wall_ok') else C_WALL_PRE_BAD
        pygame.draw.rect(self.overlay, color, rect, border_radius=4)

    # ── Pawns ─────────────────────────────────────────────────────────────────

    def _draw_pawns(self, players: list[Player]):
        colors = [C_WALL_P1, C_WALL_P2]
        for p in players:
            cx, cy = GameRenderer.cell_center(p.r, p.c)
            rad    = CELL // 2 - 6

            # Shadow
            pygame.draw.circle(self.screen, (0, 0, 0, 120), (cx + 2, cy + 3), rad)
            # Body
            pygame.draw.circle(self.screen, colors[p.idx], (cx, cy), rad)
            # Inner ring
            pygame.draw.circle(self.screen, (255, 255, 255, 60), (cx, cy), rad, 2)
            # Highlight
            pygame.draw.circle(self.screen, (255, 255, 255, 80),
                               (cx - rad//4, cy - rad//4), rad//3)
            # Label
            lbl = self.font_md.render(str(p.idx + 1), True, (255, 255, 255))
            self.screen.blit(lbl, lbl.get_rect(center=(cx, cy)))

    # ── Side panel ────────────────────────────────────────────────────────────

    def _draw_panel(self, game: Game, ui_state):
        px = PAD + BOARD_PX + 20
        py = PAD

        # Panel background
        panel = pygame.Rect(px - 10, PAD - 10, 250, BOARD_PX + 20)
        pygame.draw.rect(self.screen, C_PANEL, panel, border_radius=8)

        colors = [C_WALL_P1, C_WALL_P2]

        # Determine player names based on game mode
        if game.game_mode == 'ai':
            diff_label = game.ai_difficulty.capitalize() if game.ai_difficulty else ""
            names = ["You (P1)", f"AI ({diff_label})"]
        else:
            names = ["Player 1", "Player 2"]

        for i, p in enumerate(game.players):
            active = (game.turn == i and game.winner is None)
            cy_off = i * 180

            # Player card
            card = pygame.Rect(px, py + cy_off, 220, 160)
            border_col = colors[i] if active else C_BTN_BORDER
            pygame.draw.rect(self.screen, C_BTN if not active else (30, 45, 80),
                             card, border_radius=8)
            pygame.draw.rect(self.screen, border_col, card, 2, border_radius=8)

            # Color dot
            pygame.draw.circle(self.screen, colors[i], (px + 18, py + cy_off + 22), 8)

            # Name
            col = colors[i] if active else C_TEXT_MUTED
            name_surf = self.font_lg.render(names[i], True, col)
            self.screen.blit(name_surf, (px + 34, py + cy_off + 10))

            # Active indicator
            if active:
                if game.game_mode == 'ai' and i == 1:
                    ind_text = "THINKING..."
                elif game.game_mode == 'ai' and i == 0:
                    ind_text = "YOUR TURN"
                else:
                    ind_text = "YOUR TURN"
                ind = self.font_sm.render(f"<- {ind_text}", True, colors[i])
                self.screen.blit(ind, (px + 10, py + cy_off + 40))

            # Walls remaining
            walls_lbl = self.font_sm.render("Walls remaining:", True, C_TEXT_MUTED)
            self.screen.blit(walls_lbl, (px + 10, py + cy_off + 65))
            walls_num = self.font_lg.render(str(p.walls_left), True, C_TEXT)
            self.screen.blit(walls_num, (px + 10, py + cy_off + 85))

            # Wall icons
            for w in range(p.walls_left):
                wx = px + 10 + w * 18
                wy = py + cy_off + 120
                pygame.draw.rect(self.screen, colors[i],
                                 pygame.Rect(wx, wy, 12, 26), border_radius=2)

        # Mode indicator
        mode_y = py + 380
        mode_lbl = self.font_sm.render("Mode:", True, C_TEXT_MUTED)
        self.screen.blit(mode_lbl, (px, mode_y))

        mode_map = {
            'move':   ("Move Pawn",   C_WALL_P2),
            'wall_h': ("Wall H",      C_WALL_P1),
            'wall_v': ("Wall V",      C_WALL_P1),
        }
        mode = ui_state.get('mode', 'move')
        mode_text, mode_col = mode_map.get(mode, ("Move Pawn", C_WALL_P2))
        mode_surf = self.font_md.render(mode_text, True, mode_col)
        self.screen.blit(mode_surf, (px, mode_y + 22))

        # Controls legend
        legend = [
            ("M", "Move mode"),
            ("H", "Horizontal wall"),
            ("V", "Vertical wall"),
            ("U", "Undo"),
            ("Y", "Redo"),
            ("R", "Reset game"),
            ("ESC", "Back to menu"),
        ]
        legend_y = mode_y + 70
        lbl = self.font_sm.render("Controls:", True, C_TEXT_MUTED)
        self.screen.blit(lbl, (px, legend_y))
        for i, (key, desc) in enumerate(legend):
            ky_surf = self.font_sm.render(f"[{key}]", True, C_WALL_P2)
            ds_surf = self.font_sm.render(f" {desc}", True, C_TEXT_MUTED)
            self.screen.blit(ky_surf, (px, legend_y + 20 + i * 20))
            self.screen.blit(ds_surf, (px + 36, legend_y + 20 + i * 20))

    # ── Message bar ───────────────────────────────────────────────────────────

    def _draw_message(self, game: Game):
        msg_y = PAD + BOARD_PX + 10
        surf  = self.font_md.render(game.message, True, game.msg_color)
        self.screen.blit(surf, surf.get_rect(centerx=PAD + BOARD_PX // 2,
                                              top=msg_y))

        # Win overlay
        if game.winner is not None:
            ov = pygame.Surface((WIN_W, WIN_H), pygame.SRCALPHA)
            ov.fill((0, 0, 0, 140))
            self.screen.blit(ov, (0, 0))

            if game.game_mode == 'ai':
                win_text = "You Win!" if game.winner == 0 else "AI Wins!"
            else:
                name = "Player 1" if game.winner == 0 else "Player 2"
                win_text = f"{name} Wins!"

            win_font = pygame.font.SysFont("Segoe UI", 48, bold=True)
            sub_font = pygame.font.SysFont("Segoe UI", 24)

            win_surf = win_font.render(win_text, True, C_WIN)
            sub_surf = sub_font.render("Press R to play again  |  ESC for menu", True, C_TEXT_MUTED)

            cx, cy = WIN_W // 2, WIN_H // 2 - 30
            self.screen.blit(win_surf, win_surf.get_rect(center=(cx, cy)))
            self.screen.blit(sub_surf, sub_surf.get_rect(center=(cx, cy + 56)))

    # ── Reset button ──────────────────────────────────────────────────────────

    def _draw_reset_button(self, ui_state):
        hover = ui_state.get('btn_reset_hover', False)
        color = C_BTN_HOVER if hover else C_BTN
        pygame.draw.rect(self.screen, color, self.btn_reset, border_radius=6)
        pygame.draw.rect(self.screen, C_BTN_BORDER, self.btn_reset, 1, border_radius=6)
        lbl = self.font_md.render("New Game  [R]", True, C_TEXT)
        self.screen.blit(lbl, lbl.get_rect(center=self.btn_reset.center))
