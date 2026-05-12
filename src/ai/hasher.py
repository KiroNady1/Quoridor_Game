# ai/zobrist.py
import random

class Hasher:
    """
    Lightweight Zobrist-style hashing for Quoridor state.
    """

    def __init__(self, board_size=9, max_walls=20):
        self.board_size = board_size
        self.max_walls = max_walls

        # Player position hashing
        self.pos_table = {}
        for r in range(board_size):
            for c in range(board_size):
                self.pos_table[("A", r, c)] = random.getrandbits(64)
                self.pos_table[("H", r, c)] = random.getrandbits(64)

        # Wall hashing (simplified encoding)
        self.wall_table = {}

    def wall_key(self, wall):
        # assumes wall has orientation, row, col
        return (wall.orientation, wall.r, wall.c)

    def hash(self, board, ai, human):
        h = 0

        # players
        h ^= self.pos_table[("A", ai.r, ai.c)]
        h ^= self.pos_table[("H", human.r, human.c)]

        # walls
        for wall in board.walls:
            key = self.wall_key(wall)
            if key not in self.wall_table:
                self.wall_table[key] = random.getrandbits(64)
            h ^= self.wall_table[key]

        return h