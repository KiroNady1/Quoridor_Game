# file: game/game.py

from ui.constants import C_TEXT_MUTED, C_ERROR, C_WIN
from game.board import Board
from game.player import Player
from game.wall import Wall


class Game:
    """
    Manages turns, applies validated actions, detects win conditions.
    Supports PvP and Human-vs-AI game modes.
    """

    def __init__(self, game_mode='pvp', ai_difficulty=None):
        self.board   = Board()
        self.players = [
            Player(idx=0, r=8, c=4),   # P1: bottom center, goal row 0
            Player(idx=1, r=0, c=4),   # P2: top center,    goal row 8
        ]
        self.turn       = 0            # index of active player
        self.winner     = None         # None | 0 | 1
        self.message    = ""           # feedback message
        self.msg_color  = C_TEXT_MUTED

        # AI settings
        self.game_mode     = game_mode       # 'pvp' or 'ai'
        self.ai_difficulty = ai_difficulty   # None, 'medium', 'hard'
        self.ai_turn_start = None            # timestamp for AI move delay

    @property
    def active(self) -> Player:
        return self.players[self.turn]

    @property
    def opponent(self) -> Player:
        return self.players[1 - self.turn]

    # ── AI helpers ────────────────────────────────────────────────────────────

    def is_ai_turn(self) -> bool:
        """True when it's the AI's turn to move."""
        return (self.game_mode == 'ai' and
                self.turn == 1 and
                self.winner is None)

    def do_ai_move(self):
        """Execute the AI's best move using minimax."""
        from ai.ai_controller import get_best_move, Mode
        
        # Map difficulty to Mode enum
        if self.ai_difficulty == 'hard':
            mode = Mode.HARD
        elif self.ai_difficulty == 'medium':
            mode = Mode.MEDIUM
        else:
            mode = Mode.EASY
        
        # Get the AI's move (returns tuple with type and data)
        move = get_best_move(self.board, self.players[1], self.players[0], mode)
        
        if move is None:
            # No valid moves (shouldn't happen in normal play)
            self.set_message("AI has no valid moves!", C_ERROR)
            return
        
        # Unpack the move
        move_type, move_data = move
        
        if move_type == 'move':
            # Pawn move: move_data is (r, c)
            r, c = move_data
            self.move_pawn(r, c)
        elif move_type == 'wall':
            # Wall placement: move_data is Wall object
            wall = move_data
            self.place_wall(wall)
        else:
            self.set_message(f"Unknown move type: {move_type}", C_ERROR)
        
        self.ai_turn_start = None

    # ── Player actions ────────────────────────────────────────────────────────

    def move_pawn(self, r: int, c: int) -> bool:
        """Try to move active player's pawn to (r,c). Returns True on success."""
        moves = self.board.get_valid_moves(self.active, self.opponent)
        if (r, c) not in moves:
            self.set_message("Invalid move!", C_ERROR)
            return False
        self.active.r = r
        self.active.c = c
        self._check_win()
        if self.winner is None:
            self._next_turn()
        return True

    def place_wall(self, wall: Wall) -> bool:
        """Try to place a wall. Returns True on success."""
        if self.active.walls_left == 0:
            self.set_message("No walls remaining!", C_ERROR)
            return False
        
        wall.owner = self.turn
        ok, reason = self.board.is_wall_placement_valid(wall, self.players)
        if not ok:
            self.set_message(f"Invalid wall: {reason}", C_ERROR)
            return False
        
        self.board.add_wall(wall)
        self.active.walls_left -= 1
        self._next_turn()
        return True

    def _next_turn(self):
        self.turn = 1 - self.turn
        if self.game_mode == 'ai':
            if self.turn == 1:
                self.set_message("AI is thinking...", C_TEXT_MUTED)
                self.ai_turn_start = None
            else:
                self.set_message("Your turn  –  press M / H / V to switch mode", C_TEXT_MUTED)
        else:
            name = "Player 1" if self.turn == 0 else "Player 2"
            self.set_message(f"{name}'s turn", C_TEXT_MUTED)

    def _check_win(self):
        if self.active.r == self.active.goal_row:
            self.winner = self.active.idx
            if self.game_mode == 'ai':
                if self.winner == 0:
                    self.set_message("🏆  You win!", C_WIN)
                else:
                    self.set_message("AI wins!  Better luck next time.", C_WIN)
            else:
                name = "Player 1" if self.winner == 0 else "Player 2"
                self.set_message(f"🏆  {name} wins!", C_WIN)

    def set_message(self, text: str, color=C_TEXT_MUTED):
        self.message   = text
        self.msg_color = color

    def reset(self):
        mode = self.game_mode
        diff = self.ai_difficulty
        self.__init__(game_mode=mode, ai_difficulty=diff)
