from enum import Enum

# Poizone Constants

SCREEN_WIDTH = 320
SCREEN_HEIGHT = 256
WINDOW_WIDTH = 12*20+4
WINDOW_HEIGHT = 12*20
NONE = -1
LANDS_NB = 5
ORIGIN_X = 8            # In pixels
ORIGIN_Y = 8
BLOC_SIZE = 20          # In pixels
BLOCS_RANGE = 12
BORDER_SIZE = 3 * BLOC_SIZE
MONSTERS_NB = 8
SCHEME_WIDTH = 64       # In bloc units
SCHEME_SIZE = 3072      # SCHEME_WIDTH*48
PENG_WALK_STEP = 2      # In pixels
MONS_WALK_STEP = 1
MOVBLOC_STEP = 10
CYCLONE_OFFSETS = [[-1, -1], [0, -1], [+1, -1], [+1, 0], [+1, +1], [0, +1], [-1, +1], [-1, 0]]  # 8 blocs around cyclone
JOY_LIMIT = 0.8
SUCCESS_GOAL = 90       # % of toxic blocs to destroy to win level
ALPHABET_ROWS = 4       # For 'Enter your name'
ALPHABET_COLUMNS = 7
OPTIONS_ID = ["SFX", "MUSIC"]
CTRL_ID = [ "CTRL_LEFT", "CTRL_RIGHT", "CTRL_UP", "CTRL_DOWN", "CTRL_PUSH" ]
TUTO_PAGES = 15
DEBUG_FEATURES = True

# PHASE_
PHASE_NONE              = 0
PHASE_INTRO             = 1
PHASE_MENU              = 2
PHASE_LEVEL             = 3
PHASE_RESULT            = 4
PHASE_END_LEVEL         = 5
PHASE_REVENGE_INTRO     = 6
PHASE_GAME_WON          = 7
PHASE_ENTER_NAME        = 8

# MENU_
MENU_MAIN       = -1
MENU_PLAY       = 0
MENU_CONTINUE   = 1
MENU_HIGHSCORES = 2     # Submenus
MENU_CONTROLS   = 3
MENU_TUTORIAL   = 4
MENU_OPTIONS    = 5
MENU_CREDITS    = 6

# LEGEND_
LEGEND_RIGHT    = 0
LEGEND_LEFT     = 1

# KEY_
KEY_UP          = 0
KEY_DOWN        = 1
KEY_LEFT        = 2
KEY_RIGHT       = 3
KEY_SPACE       = 4
KEY_BACKSPACE   = 5
KEY_RETURN      = 6
KEY_ESCAPE      = 7
KEY_PAUSE       = 8
KEY_GAME_UP     = 9
KEY_GAME_DOWN   = 10
KEY_GAME_LEFT   = 11
KEY_GAME_RIGHT  = 12
KEY_GAME_PUSH   = 13
KEY_NB          = 14

# LANDS_
LAND_ICE      = 0
LAND_ESA      = 1
LAND_SPACE    = 2
LAND_JUNGLE   = 3
LAND_COMPUTER = 4

# BLOC

# General Codes     00 - 23 . blocs     ; 00-15  ---  Sprites
#                   24 - 59 . background

# Codes for SCHEME data ; 00 - 23 . blocs  ( 23 = ELECTRIC )
#                         24 - 59 . EMPTY (background)

# Codes for Land data   ; 24 - 59 . background
#                         60 - 61 . Teleporters

BLOC_BASIC       = 0
BLOC_ALCOOL      = 1
BLOC_BOMB        = 2
BLOC_POISON      = 3
BLOC_RED         = 4
BLOC_ALU         = 5
BLOC_BATTERY     = 6
BLOC_DDT         = 7
BLOC_CFC         = 8
BLOC_URANIUM     = 9
BLOC_GREEN_CHEM  = 10
BLOC_MAGIC       = 11
BLOC_ROCK        = 12
BLOC_GOLD        = 13
BLOC_CYCLONE     = 14
BLOC_DIAMOND     = 15
BLOC_BASIC_0     = 16       # For Land No 0 (ice)
BLOC_BASIC_2     = 17       # For Land No 2 (space)
BLOC_BASIC_1     = 18       # For Land No 1 (station)
BLOC_BASIC_3     = 19       # For Land No 3 (jungle)
BLOC_BASIC_4     = 20       # For Land No 4 (computer)
BLOC_ELECTRO_0   = 21       # Electric border Anim
BLOC_ELECTRO_1   = 22
BLOC_ELECTRO     = 23
BLOC_TELEPORT_0  = 60       # Teleporter Anim
BLOC_TELEPORT_1  = 61
BLOC_REVENGE     = 62

# PANEL_
PANEL_DEMO  = 0
PANEL_PAUSE = 1

# Enums

class PenguinStatus(Enum):
    IDLE = 0
    WALK = 1
    DIE  = 2
    PUSH = 3
    