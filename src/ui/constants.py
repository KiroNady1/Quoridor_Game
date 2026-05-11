# file: ui/constants.py

# ─────────────────────────────────────────────────────────────────────────────
# Constants
# ─────────────────────────────────────────────────────────────────────────────

GRID          = 9          # 9x9 board
CELL          = 60         # pixels per cell
GAP           = 10         # pixels for wall slots between cells
PAD           = 40         # board padding from window edge
WALL_THICK    = 8          # wall rectangle thickness (inside the GAP)
INITIAL_WALLS = 10

# Derived geometry
STEP  = CELL + GAP         # distance from one cell origin to the next
BOARD_PX = GRID * CELL + (GRID - 1) * GAP   # pixel width/height of the grid area
WIN_W = BOARD_PX + 2 * PAD + 260            # extra panel on the right
WIN_H = BOARD_PX + 2 * PAD + 60             # extra bar at the bottom

# Colors
C_BG         = (15,  20,  40)
C_BOARD      = (22,  30,  55)
C_CELL       = (30,  42,  75)
C_CELL_HOVER = (45,  65, 110)
C_GRID_LINE  = (50,  65, 100)
C_MOVE_HINT  = (80, 180, 100, 160)   # semi-transparent green
C_JUMP_HINT  = (220, 190,  40, 160)  # semi-transparent gold
C_WALL_P1    = (233,  69,  96)       # red  – also P1 pawn colour
C_WALL_P2    = (0,   180, 216)       # cyan – also P2 pawn colour
C_WALL_PRE_OK  = (180, 220, 120, 180)
C_WALL_PRE_BAD = (255,  80,  80, 160)
C_PANEL      = (18,  25,  48)
C_TEXT       = (230, 230, 230)
C_TEXT_MUTED = (130, 140, 165)
C_BTN        = (40,  55,  90)
C_BTN_HOVER  = (60,  80, 130)
C_BTN_BORDER = (90, 110, 160)
C_GOAL_P1    = (233,  69,  96,  25)
C_GOAL_P2    = (0,   180, 216,  25)
C_ERROR      = (255,  80,  80)
C_WIN        = (255, 215,   0)

# Menu colors
C_MENU_ACCENT  = (255, 215,   0)       # golden title
C_MENU_BTN     = (35,  50,  85)
C_MENU_BTN_HOV = (50,  70, 115)
C_MENU_DISABLED= (28,  36,  58)
C_COMING_SOON  = (255, 180,  40)

