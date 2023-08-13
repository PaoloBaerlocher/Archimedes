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

arrows = [
[ # Bloc 0 (CFC)
    [ # Red
        [ 2, 2, 1 ],
        [ 3, 3, 2 ]
    ],
    [ # Green
        [ 1, 1, 3 ]
    ]
],

[ # Bloc 1 (GREEN)
    [ # Red
        [ 2, 0, 3 ]
    ],
    [ # Green
        [ 2, 1, 0 ],
        [ 2, 1, 1 ]
    ]
],

[  # Bloc 2
    [  # Red
        [ 1, 1, 0 ],
        [ 1, 1, 1 ]
    ],
    [  # Green
        [ 1, 0, 3 ],
        [ 2, 1, 3 ],
        [ 3, 2, 1 ]
    ]
],

[ # Bloc 3
    [ # Red
        [ 2, 1, 1 ],
        [ 1, 3, 2 ]
    ],
    [ # Green
        [ 3, 2, 2 ]
    ]
],

[  # Bloc 4
    [  # Red
        [ 2, 2, 2 ],
        [ 1, 1, 0 ]
    ],
    [  # Green
        [ 0, 1, 3 ],
        [ 2, 2, 1 ]
    ]
],

[  # Bloc 5
    [  # Red
        [ 1, 1, 0 ],
        [ 3, 2, 1 ]
    ],
    [  # Green
        [ 2, 0, 3 ],
        [ 2, 3, 2 ]
    ]
],

[  # Bloc 6
    [  # Red
        [ 3, 0, 1 ],
        [ 2, 3, 2 ]
    ],
    [  # Green
        [ 2, 2, 1]
    ]
],

[  # Bloc 7
    [  # Red
        [ 0, 1, 3]
    ],
    [  # Green
        [ 3, 1, 1 ]
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

