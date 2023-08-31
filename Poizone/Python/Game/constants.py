import pygame
from enum import Enum

DEBUG_FEATURES = False

# Poizone Constants
SCREEN_WIDTH = 320
SCREEN_HEIGHT = 256
WINDOW_WIDTH = 12*20+4
WINDOW_HEIGHT = 12*20
NONE = -1
LANDS_NB = 5
LEVELS_NB = 50
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
PUSH_DURATION = 16      # Frames
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

class Key:
    UP          = 0
    DOWN        = 1
    LEFT        = 2
    RIGHT       = 3
    SPACE       = 4
    BACKSPACE   = 5
    RETURN      = 6
    ESCAPE      = 7
    PAUSE       = 8
    GAME_UP     = 9
    GAME_DOWN   = 10
    GAME_LEFT   = 11
    GAME_RIGHT  = 12
    GAME_PUSH   = 13
    NB          = 14

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
    [Key.LEFT,      pygame.K_LEFT],
    [Key.RIGHT,     pygame.K_RIGHT],
    [Key.UP,        pygame.K_UP],
    [Key.DOWN,      pygame.K_DOWN],
    [Key.SPACE,     pygame.K_SPACE],
    [Key.BACKSPACE, pygame.K_BACKSPACE],
    [Key.RETURN,    pygame.K_RETURN],
    [Key.ESCAPE,    pygame.K_ESCAPE],
    [Key.PAUSE,     pygame.K_F12]
]

GAME_KEYS = [
    [Key.GAME_LEFT,     "CTRL_LEFT"],
    [Key.GAME_RIGHT,    "CTRL_RIGHT"],
    [Key.GAME_UP,       "CTRL_UP"],
    [Key.GAME_DOWN,     "CTRL_DOWN"],
    [Key.GAME_PUSH,     "CTRL_PUSH"]
]
