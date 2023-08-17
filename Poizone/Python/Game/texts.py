# Texts

MAIN_MENU = [
    "PLAY (Single Player)",
    "CONTINUE",
    "HIGH SCORES",
    "CONTROLS",
    "TUTORIAL",
    "OPTIONS",
    "CREDITS"
]

OPTIONS = [ "SOUND FX", "MUSIC" ]
VALUES = [ "ON", "OFF"]

TUTO_INTRO = [
    "Looking at the ecological disaster due to",
    "human irresponsibility, penguin Zozo",
    "decided it was time to do something.",
    "",
    "Help him to decontaminate the 50 polluted",
    "zones where dangerous creatures live: they",
    "were born from the toxic elements, and",
    "will try to catch you.",
    "",
    "In each zone, destroy at least 90% of the",
    "toxic blocks before time runs out.",
    "",
    "Now let's go:",
    "Your sacrifice is our hope...!",
]

TUTO_BLOC = [
    [ # BLOC_CFC
        "Destroy CFC by crushing it",
        "from the top side only.",
    ],

    [ # BLOC_GREEN_CHEM
        "Throw this chemical substance away.",
        "Don't crush it!"
    ],

    [ # BLOC_RED
        "Crush this reactive substance.",
        "Don't throw it away!"
    ],

    [ # BLOC_URANIUM
        "Crush uranium block only when it",
        "is not near another one.",
    ],

    [ # BLOC_DDT
        "Destroy DDT only when",
        "near another DDT block.",
    ],

    [ # BLOC_BATTERY
        "Crush battery from the top or",
        "bottom sides only.",
    ],

    [ # BLOC_ALU
        "Fling ALU against the electric",
        "border. Don't crush it!",
    ],

    [  # BLOC_POISON
        "Crush poison only when near",
        "an ALU block.",
    ],

    [   # DIAMOND
        "If you have spare time, try to assemble",
        "the 4 magic diamonds to get a bonus",
        "of 500 points."
    ],

    [   # ELECTRIC BORDER
        "Push the electric border to freeze the",
        "creatures in contact with the border."
    ],

    [   # MAGIC
        "The magic pill provides invincibility",
        "for few seconds."
    ],

    [  # ALCOOL
        "Crushing this substance makes you clumsy:",
        "Left becomes Right, and Up becomes Down...",
        "Avoid that, if possible."
    ],

    [  # TELEPORT
        "Three teleporter gates are available.",
        "Toxic creatures are not allowed to use them."
    ],

    [  # Others
        "Discover the power of the other blocks",
        "by yourself.",
        "You're a grown penguin now."
    ]
]

REVENGE_TITLE = "REVENGE ZONE"
REVENGE_TEXTS = [
    "CRUSH ALL THE",
    "NAUGHTIES YOU CAN!"
]

GAME_WON = [
    "IT'S UNBELIEVABLE!",
    "YOU HAVE FINISHED",
    "THE GAME!!! HAVE",
    "YOU CHEATED ?",
]

CTRL = [
    "LEFT",
    "RIGHT",
    "UP",
    "DOWN",
    "PUSH"
]

CREDITS = [ "CODE by Paolo Baerlocher",
            "GRAPHICS by Marc Andreoli",
            "MUSIC by Fabrice Hautecloque",
            "",
            "Game originally developed for the",
            "Acorn Archimedes in 1991 and published",
            "by ETERNA.",
            "",
            "Ported to PC using pygame engine in 2023.",
            "",
            "Thanks to Robin Francois for extracting the",
            "sources from the old 3''1/2 floppy disks."
]
