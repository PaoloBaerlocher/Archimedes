# -1 = no bloc

maps = [
# CFC
[
    00, 00, 00, 00,
    00, -1, -1, 00,
    00,  8, -1,  8,
    00, 00, 00, -1
],
# GREEN CHEM
[
    00, 00, -1, 00,
    00, -1, 10, -1,
    00, -1, 00, -1,
    00, 00, 00, 00
],
# RED
[
    00, -1, -1, -1,
    -1,  4, -1, 00,
    -1, 00,  4, -1,
    00, -1, 00, 00
],
# URANIUM
[
    00, 00, 00, 00,
    00,  9, -1,  9,
    00,  9, -1, -1,
    00, -1, -1, 00
],
# DDT
[
    -1, -1, 00, -1,
    -1, -1,  7, 00,
     7,  7, -1, -1,
    00, 00, -1, -1
],
# BATTERY
[
    -1, -1, -1, 00,
    00, -1,  6, 00,
    00, 00,  6, -1,
    00, 00, -1, -1
],
# ALU
[
    22, 00, 5, -1,
    22, -1, 00, -1,
    22, -1, 5, -1,
    22, -1, -1, -1
],
# Poison
[
    -1, 00, -1, 00,
    -1,  5,  3, -1,
     3, -1, -1, 00,
    00, -1, 00, 00
],
# Diamond
[
    -1, -1, -1, -1,
    -1, 15, 15, -1,
    -1, 15, 15, -1,
    -1, -1, -1, -1
],

# Electric Border
[
    23, -1, -1, -1,
    23, -1, -1, -1,
    23, -1, -1, -1,
    23, 23, 23, 23
],

# Magic
[
],

# Alcool
[
],

# Teleport
[
    13, 13, -1, 60,
    -1, 13, -1, -1,
    -1, 13, -1, -1,
    60, 13, 13, 13
],

# Other blocs
[
],

]

# x,y (0..3) & direction (0..3) (RIGHT,LEFT,UP,DOWN)

DIR_RIGHT = 0
DIR_LEFT  = 1
DIR_UP    = 2
DIR_DOWN  = 3

arrows = [
[ # Bloc 0 (CFC)
    [ # Red
        [ 2, 2, DIR_LEFT ],
        [ 3, 3, DIR_UP ]
    ],
    [ # Green
        [ 1, 1, DIR_DOWN ]
    ]
],

[ # Bloc 1 (GREEN)
    [ # Red
        [ 2, 0, DIR_DOWN ]
    ],
    [ # Green
        [ 2, 1, DIR_RIGHT ],
        [ 2, 1, DIR_LEFT ]
    ]
],

[  # Bloc 2
    [  # Red
        [ 1, 1, DIR_RIGHT ],
        [ 1, 1, DIR_LEFT ]
    ],
    [  # Green
        [ 1, 0, DIR_DOWN ],
        [ 2, 1, DIR_DOWN ],
        [ 3, 2, DIR_LEFT ]
    ]
],

[ # Bloc 3
    [ # Red
        [ 2, 1, DIR_LEFT ],
        [ 1, 3, DIR_UP ]
    ],
    [ # Green
        [ 3, 2, DIR_UP ]
    ]
],

[  # Bloc 4
    [  # Red
        [ 2, 2, DIR_UP ],
        [ 1, 1, DIR_RIGHT ]
    ],
    [  # Green
        [ 0, 1, DIR_DOWN ],
        [ 2, 2, DIR_LEFT ]
    ]
],

[  # Bloc 5
    [  # Red
        [ 1, 1, DIR_RIGHT ],
        [ 3, 2, DIR_LEFT ]
    ],
    [  # Green
        [ 2, 0, DIR_DOWN ],
        [ 2, 3, DIR_UP ]
    ]
],

[  # Bloc 6
    [  # Red
        [ 3, 0, DIR_LEFT ],
        [ 2, 3, DIR_UP ]
    ],
    [  # Green
        [ 2, 2, DIR_LEFT ]
    ]
],

[  # Bloc 7
    [  # Red
        [ 0, 1, DIR_DOWN ]
    ],
    [  # Green
        [ 3, 1, DIR_LEFT ]
    ]
],

[   # Diamond (no arrows)
    [],
    []
],

[   # Electric border
    [],
    [
        [ 1, 0, 1],
        [ 1, 1, 1],
        [ 1, 2, 1],

        [ 1, 2, 3],
        [ 2, 2, 3],
        [ 3, 2, 3],
    ]
],

[   # Magic (no arrows)
    [],
    []
],

[   # Alcool (no arrows)
    [],
    []
],

[   # Teleport (no arrows)
    [],
    []
],

[   # Other blocs
    [],
    []
],
]

bloc = [
    8,      # CFC
    10,     # GREEN
    4,      # RED
    9,      # URANIUM
    7,      # DDT
    6,      # BATTERY
    5,      # ALU
    3,      # POISON
    -1,     # DIAMOND
    -1,     # ELECTRIC BORDER
    11,     # MAGIC
    1,      # ALCOOL
    60,     # TELEPORT
    -1,     # Other blocs
]

