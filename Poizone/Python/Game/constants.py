import pygame
from enum import Enum

DEBUG_FEATURES = True

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
MONSTER_WALK_STEP = 1
MOVBLOC_STEP = 10
CYCLONE_OFFSETS = [[-1, -1], [0, -1], [+1, -1], [+1, 0], [+1, +1], [0, +1], [-1, +1], [-1, 0]]  # 8 blocs around cyclone
BONUS_KILL = [0, 20, 50, 100, 200]  # Bonus for killing monsters crushed with one bloc
JOY_LIMIT = 0.8
SUCCESS_GOAL = 90       # % of toxic blocs to destroy to win level
ALPHABET_ROWS = 4       # For 'Enter your name'
ALPHABET_COLUMNS = 7
OPTIONS_ID = ["SFX", "MUSIC"]
CTRL_ID = [ "CTRL_LEFT", "CTRL_RIGHT", "CTRL_UP", "CTRL_DOWN", "CTRL_PUSH" ]
TUTO_PAGES = 15

class Phase:
    NONE              = 0
    INTRO             = 1
    MENU              = 2
    LEVEL             = 3
    RESULT            = 4
    END_LEVEL         = 5
    REVENGE_INTRO     = 6
    GAME_WON          = 7
    ENTER_NAME        = 8

class Menu:
    MAIN       = -1
    PLAY       = 0
    CONTINUE   = 1
    LEADERBOARD= 2     # Submenus
    CONTROLS   = 3
    TUTORIAL   = 4
    OPTIONS    = 5
    CREDITS    = 6

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

class Land:
    ICE      = 0
    ESA      = 1
    MOON     = 2
    JUNGLE   = 3
    COMPUTER = 4

# BLOC

# General Codes     00 - 23 . blocs     ; 00-15  ---  Sprites
#                   24 - 59 . background

# Codes for SCHEME data ; 00 - 23 . blocs  ( 23 = ELECTRIC )
#                         24 - 59 . EMPTY (background)

# Codes for Land data   ; 24 - 59 . background
#                         60 - 61 . Teleporters

class Bloc:
    BASIC       = 0
    ALCOOL      = 1
    BOMB        = 2
    POISON      = 3
    RED         = 4
    ALU         = 5
    BATTERY     = 6
    DDT         = 7
    CFC         = 8
    URANIUM     = 9
    GREEN_CHEM  = 10
    MAGIC       = 11
    ROCK        = 12
    GOLD        = 13
    CYCLONE     = 14
    DIAMOND     = 15
    BASIC_0     = 16       # For Land No 0 (Ice Land)
    BASIC_2     = 17       # For Land No 2 (Moon)
    BASIC_1     = 18       # For Land No 1 (Space station)
    BASIC_3     = 19       # For Land No 3 (Jungle)
    BASIC_4     = 20       # For Land No 4 (Computer)
    ELECTRO_0   = 21       # Electric border Anim
    ELECTRO_1   = 22
    ELECTRO     = 23
    TELEPORT_0  = 60       # Teleporter Anim
    TELEPORT_1  = 61
    REVENGE     = 62

# PANEL_
PANEL_DEMO  = 0
PANEL_PAUSE = 1

# Enums

class PenguinStatus(Enum):
    IDLE = 0
    WALK = 1
    DIE  = 2
    PUSH = 3

# Controls

MENU_KEYS = [
    [KEY_LEFT,      pygame.K_LEFT],
    [KEY_RIGHT,     pygame.K_RIGHT],
    [KEY_UP,        pygame.K_UP],
    [KEY_DOWN,      pygame.K_DOWN],
    [KEY_SPACE,     pygame.K_SPACE],
    [KEY_BACKSPACE, pygame.K_BACKSPACE],
    [KEY_RETURN,    pygame.K_RETURN],
    [KEY_ESCAPE,    pygame.K_ESCAPE],
    [KEY_PAUSE,     pygame.K_F12]
]

GAME_KEYS = [
    [KEY_GAME_LEFT,     "CTRL_LEFT"],
    [KEY_GAME_RIGHT,    "CTRL_RIGHT"],
    [KEY_GAME_UP,       "CTRL_UP"],
    [KEY_GAME_DOWN,     "CTRL_DOWN"],
    [KEY_GAME_PUSH,     "CTRL_PUSH"]
]
