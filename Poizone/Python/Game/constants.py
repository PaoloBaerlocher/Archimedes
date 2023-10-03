import pygame

DEBUG_FEATURES = False

# Poizone Constants

SCREEN_WIDTH = 320
SCREEN_HEIGHT = 256

WINDOW_WIDTH = 12*20+4
WINDOW_HEIGHT = 12*20

NONE = -1

LEVELS_NB = 50

ORIGIN_X = 8            # Game Window origin (in pixels)
ORIGIN_Y = 8

BLOC_SIZE = 20          # In pixels
BLOCS_RANGE = 12
BORDER_SIZE = 3 * BLOC_SIZE

MONSTERS_NB = 8

SCHEME_WIDTH = 64       # In bloc units
SCHEME_HEIGHT = 48
SCHEME_SIZE = SCHEME_WIDTH*SCHEME_HEIGHT

PENG_WALK_STEP = 2      # In pixels
MONSTER_WALK_STEP = 1
MOVBLOC_STEP = 10

CYCLONE_OFFSETS = [[-1, -1], [0, -1], [+1, -1], [+1, 0], [+1, +1], [0, +1], [-1, +1], [-1, 0]]  # 8 blocs around cyclone

BONUS_KILL = [0, 20, 50, 100, 200]  # Bonus for killing N monsters crushed with one bloc

PUSH_DURATION = 16      # Frames
DIE_DURATION = 128      # Frames

JOY_LIMIT = 0.8

SUCCESS_GOAL = 90       # % of toxic blocs to destroy to win level

ALPHABET_ROWS = 4       # For 'Enter your name' screen
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
    PLAY_MULTI = 1
    CONTINUE   = 2
    LEADERBOARD= 3     # Submenus
    CONTROLS   = 4
    TUTORIAL   = 5
    OPTIONS    = 6
    CREDITS    = 7
    WAIT_CLIENT= 8

    NB         = 9

class Legend:
    RIGHT    = 0
    LEFT     = 1

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

    NB       = 5

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
    ELECTRO_0   = 21       # Electric border Anim (2 frames)
    ELECTRO_1   = 22
    ELECTRO     = 23
    TELEPORT_0  = 60       # Teleporter Anim (2 frames)
    TELEPORT_1  = 61
    REVENGE     = 62

BASIC_BLOC = [Bloc.BASIC_0, Bloc.BASIC_1, Bloc.BASIC_2, Bloc.BASIC_3, Bloc.BASIC_4]

class Panel:
    DEMO  = 0
    PAUSE = 1

class Music:
    INTRO       = 0
    REVENGE     = 1
    WIN         = 2
    WIN_GAME    = 3
    END         = 4
    PLAY_0      = 5
    PLAY_1      = 6
    PLAY_2      = 7
    PLAY_3      = 8
    PLAY_4      = 9

    NB          = 10

class Sfx:
    READY   = 0
    LAUNCH  = 1
    CRASH   = 2
    BOOM    = 3
    ELEC    = 4
    MAGIC   = 5
    DIAMOND = 6
    OH_NO   = 7
    ALCOOL  = 8
    COLL    = 9
    SPLATCH = 10
    WOW     = 11
    TICK    = 12
    VALID   = 13
    TELEPORT= 14

    NB      = 15

# Enums

class PenguinStatus:
    IDLE     = 0
    WALK     = 1
    DIE      = 2
    PUSH     = 3
    ZAPPED   = 4

class NetworkMode:
    NONE   = 0
    CLIENT = 1
    SERVER = 2

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
