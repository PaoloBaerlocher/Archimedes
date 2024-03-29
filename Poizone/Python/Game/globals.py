from constants import *
import leaderboard
import options
import spritesheet
import monster
import penguin
import audio
from utility import *

# Global graphics resources

penguinSprites = None
charsSprites_gr = None
panelSprites = None
arrowsSprites = None
legendSprites = None
startScreen = None
border = None
rocket = None

# Global game variables

gameTimer = 0.0     # 0 - 300 ( 5 minutes ) - in seconds
currLevel = 1       # From 1 to LEVELS_NB
currLand = 0        # 0..4 (Land.)
electrifyBorder = False
electrifyBorderAnim = 0
blocsCount = []
toxicBlocsLeft = 0

# For cyclones
cyclonesPace = 0
cyclonesList = []

# Camera offset (in pixels)
baseX = 0
baseY = 0

isRevenge = False  # Is Revenge mode ?

occupyTable = []    # Where monsters are allowed to go or not
lands = []
teleporters = []

penguin1 = None

# Init

def initPenguin():
    global penguin1

    # Create player's penguin
    penguin1 = penguin.Penguin()


def resetGame():
    global currLevel, penguin1

    currLevel = 1
    penguin1.score = 0


def loadSettings():
    global lb, opt

    lb = leaderboard.Leaderboard()
    lb.load()

    opt = options.Options()
    opt.load()


# Game logic

def getBloc(indexX, indexY):
    blocOffset = indexX + indexY * SCHEME_WIDTH
    if blocOffset >= 0 and blocOffset < SCHEME_SIZE:
        return scheme[blocOffset]
    else:
        return Bloc.BASIC


def isOnBlock(posX, posY):
    return ((posX % BLOC_SIZE) == 0) and ((posY % BLOC_SIZE) == 0)


# Returns number of points earned
def destroyBloc(bloc):
    global blocsCount, toxicBlocsLeft

    debugPrint('Destroy bloc of type ' + str(bloc))
    if bloc <= Bloc.GREEN_CHEM:
        blocsCount[bloc] -= 1
        if bloc >= Bloc.POISON:
            toxicBlocsLeft -= 1
            debugPrint('toxicBlocsLeft: ' + str(toxicBlocsLeft))
            return 5

    return 0


def writeBloc(indexX, indexY, blocIndex):
    global scheme

    index = indexX + indexY * SCHEME_WIDTH
    newBloc = [blocIndex]
    scheme = scheme[:index] + bytes(newBloc) + scheme[(index + 1):]


def getAliasBlocIndex(index):
    if index == Bloc.ELECTRO:  # Electric border (2-frames animation)
        return Bloc.ELECTRO_0 + ((electrifyBorderAnim // 8) % 2)

    if index == Bloc.BASIC:     # Basic bloc is different for each land
        return BASIC_BLOC[currLand]

    if index == Bloc.TELEPORT_0 or index == Bloc.TELEPORT_1:
        return Bloc.TELEPORT_0 + (int(gameTimer / 0.256) % 2)

    if index == 24 and isRevenge:
        return Bloc.REVENGE

    return index


def setElectrifyBorder(newStatus):
    global electrifyBorder

    if newStatus and not electrifyBorder:
        audio.playSFX(Sfx.ELEC, 100)

    if not newStatus and electrifyBorder:
        audio.stopSFX(Sfx.ELEC)

    electrifyBorder = newStatus

# Setup table for monsters
def initOccupyTable():
    global occupyTable, lands

    # Bit 0: for monsters only
    # Bit 1: for penguin and monsters
    occupyTable = []
    for index in range(0, SCHEME_SIZE):
        occ = 0
        if lands[currLand][4 * index] == Bloc.TELEPORT_0:  # Monsters cannot go over teleporters
            occ = 1

        occupyTable.append(occ)

def initLandsAndTeleporters():
    global lands, teleporters

    # Load Lands and extract teleporters positions.

    lands = []
    teleporters = []

    for index in range(0, Land.NB):
        landsName = "Data/Lands/L" + str(index) + "_SET"
        with open(landsName, 'rb') as f:
            land = f.read()
        lands.append(land)
        teleporters.append([])
        # debugPrint('Teleporters in land #' + str(index) + ':')
        for i in range(0, len(land), 4):
            if land[i] >= Bloc.TELEPORT_0:
                j = i // 4
                teleporters[index].append(j)
                # debugPrint('  ' + str(j%64) + ',' + str(j // SCHEME_WIDTH))


def updateCyclones():
    global cyclonesPace, cyclonesList

    cyclonesPace = (cyclonesPace + 1) % 16

    if cyclonesPace % 2 == 0:  # To slow down process, process once every two passes
        cycloneIndex = cyclonesList[cyclonesPace >> 1]
        if cycloneIndex != 0:
            debugPrint('Process cyclone #' + str(cycloneIndex))
            # Collect blocs around cyclone
            turningBlocs = []

            for offset in CYCLONE_OFFSETS:
                finalOffset = cycloneIndex + offset[0] + offset[1] * SCHEME_WIDTH
                turningBloc = scheme[finalOffset]

                if turningBloc < 24 and turningBloc != Bloc.ELECTRO:
                    turningBlocs.append(turningBloc)

            # Rotate turning blocs (clockwise)
            if len(turningBlocs) > 1:
                turningBlocs = turningBlocs[len(turningBlocs) - 1:] + turningBlocs[:len(turningBlocs) - 1]

            i = 0
            for offset in CYCLONE_OFFSETS:
                finalOffset = cycloneIndex + offset[0] + offset[1] * SCHEME_WIDTH
                turningBloc = scheme[finalOffset]

                if turningBloc < 24 and turningBloc != Bloc.ELECTRO:
                    blocX = finalOffset % SCHEME_WIDTH
                    blocY = finalOffset // SCHEME_WIDTH
                    writeBloc(blocX, blocY, turningBlocs[i])
                    i += 1

def updateMonsters():
    for m in monsters:
        m.update()


# 0% - 100%
def getGoalPercent():
    return ((totalToxicBlocs - toxicBlocsLeft) * 100) // totalToxicBlocs


###


def resetLevel():
    global baseX, baseY, penguin1, isRevenge, gameTimer

    baseX = 18 * BLOC_SIZE + 8
    baseY = 18 * BLOC_SIZE + 8
    penguin1.reset()
    setElectrifyBorder(False)

    # Time available for finishing this level
    if currLevel == 1 or currLevel == 2:
        gameTimer = 90  # 1m30
    elif currLevel == 3 or currLevel == 4:
        gameTimer = 150  # 2m30
    else:
        gameTimer = 180  # 3m00

    gameTimer += 0.99  # To see the first full second, initially

    isRevenge = False

    audio.playMusic(Music.PLAY_0 + currLand, -1)
    audio.playSFX(Sfx.READY)


def resetRevenge(revenge):
    global baseX, baseY, penguin1, isRevenge, gameTimer

    isRevenge = True

    mapX = revenge % 4
    mapY = revenge // 4

    baseX = (12 * mapX) * BLOC_SIZE
    baseY = (1 + 12 * mapY) * BLOC_SIZE
    penguin1.reset()

    # Overrides for Revenge mode
    penguin1.posX = baseX + 6 * BLOC_SIZE  # Center of revenge map
    penguin1.posY = baseY + 6 * BLOC_SIZE

    penguin1.ghost = 10000  # Permanent ghost in Revenge mode

    gameTimer = 30.99

    setElectrifyBorder(False)


def loadLevel():
    global currLevel, currLand, scheme, blocsCount, toxicBlocsLeft, totalToxicBlocs, monsters, cyclonesList, cyclonesNb

    debugPrint("Load level " + str(currLevel))
    currLand = (currLevel - 1) % Land.NB
    loadSprites()

    schemeName = "Data/Schemes/S" + str(currLevel)
    with open(schemeName, 'rb') as f:
        scheme = f.read()

    # Counts blocs in scheme
    blocsCount = [0] * 11
    cyclonesList = [0] * 8
    cyclonesNb = 0

    for i in range(0, len(scheme)):
        blocIndex = scheme[i]
        if blocIndex <= Bloc.GREEN_CHEM:
            blocsCount[blocIndex] += 1

        if blocIndex == Bloc.CYCLONE:
            cyclonesList[cyclonesNb] = i
            debugPrint('Cyclone #' + str(cyclonesNb) + ' at index ' + str(i))
            cyclonesNb += 1

    toxicBlocsLeft = blocsCount[Bloc.POISON] + blocsCount[Bloc.RED]
    toxicBlocsLeft += blocsCount[Bloc.ALU] + blocsCount[Bloc.BATTERY]
    toxicBlocsLeft += blocsCount[Bloc.DDT] + blocsCount[Bloc.CFC]
    toxicBlocsLeft += blocsCount[Bloc.URANIUM] + blocsCount[Bloc.GREEN_CHEM]

    debugPrint('toxicBlocsLeft: ' + str(toxicBlocsLeft))
    totalToxicBlocs = toxicBlocsLeft

    resetLevel()
    initOccupyTable()

    monsters = []
    baddiesNumber = currLevel / 8
    for index in range(0, MONSTERS_NB):
        kind = index % 2
        m = monster.Monster(kind, index < baddiesNumber)
        m.setRandomPosition()
        monsters.append(m)


def loadRevenge():
    global currLevel, currLand, scheme, blocsCount, monsters, cyclonesList

    debugPrint("Load revenge for level " + str(currLevel))
    currLand = Land.COMPUTER
    loadSprites()

    schemeName = "Data/Schemes/CHALLENGES"
    with open(schemeName, 'rb') as f:
        scheme = f.read()

    cyclonesList = [0] * 8

    resetRevenge((currLevel - 1) // 5)

    initOccupyTable()

    monsters = []
    for index in range(0, MONSTERS_NB):
        kind = index % 2
        m = monster.Monster(kind, False)
        m.setRandomPosition()
        monsters.append(m)


def loadSpriteSheets():
    global penguinSprites, charsSprites_gr, panelSprites, arrowsSprites, legendSprites, startScreen, border, rocket
    global ss_shared, ss_levels, ss_revenge, ss_endScreens

    ss_shared = [  # 4 versions with 'destroy mask' animation
        spritesheet.SpriteSheet('Data/sharedBlocs0.png'),
        spritesheet.SpriteSheet('Data/sharedBlocs1.png'),
        spritesheet.SpriteSheet('Data/sharedBlocs2.png'),
        spritesheet.SpriteSheet('Data/sharedBlocs3.png')
    ]

    ss_start = spritesheet.SpriteSheet('Data/startScreen.png')      # 3D pre-rendered screen
    ss_border = spritesheet.SpriteSheet('Data/border.png')          # Blue border around game window
    ss_rocket = spritesheet.SpriteSheet('Data/rocket.png')          # For end-level animation
    ss_penguins = spritesheet.SpriteSheet('Data/pengos.png')        # Penguin animations (white and yellow ones)
    ss_chars_gr = spritesheet.SpriteSheet('Data/chars_green.png')   # Font used for score
    ss_revenge = spritesheet.SpriteSheet('Data/revengeTile.png')
    ss_panels = spritesheet.SpriteSheet('Data/panels.png')          # DEMO and PAUSE
    ss_arrows = spritesheet.SpriteSheet('Data/arrows.png')          # 4 red and 4 green arrows
    ss_legend = spritesheet.SpriteSheet('Data/legend.png')          # 2 blue arrows

    ss_levels = []
    ss_endScreens = []
    for index in range(0, Land.NB):
        ss_levels.append(spritesheet.SpriteSheet('Data/level' + str(index + 1) + '.png'))
        ss_endScreens.append(spritesheet.SpriteSheet('Data/Screens/scr' + str(index + 1) + '.png'))

    # Other assets
    startScreen = ss_start.get_indexed_image(0, 244, 240)
    border = ss_border.get_indexed_image(0, 320, 256)
    rocket = ss_rocket.get_indexed_image(0, 40, 174)

    penguinSprites = []
    for index in range(0, 2 * 36 + 12):
        penguinSprites.append(ss_penguins.get_indexed_image(index, BLOC_SIZE, BLOC_SIZE))

    charsSprites_gr = []
    for index in range(0, 40):
        charsSprites_gr.append(ss_chars_gr.get_indexed_image(index, 12, 16))

    panelSprites = []
    for index in range(0, 2):
        panelSprites.append(ss_panels.get_indexed_image(index, 60, 20))

    arrowsSprites = []
    for index in range(0, 8):
        arrowsSprites.append(ss_arrows.get_indexed_image(index, 20, 20))

    legendSprites = []
    for index in range(0, 2):
        legendSprites.append(ss_legend.get_indexed_image(index, 20, 20))


def loadSprites():
    global sprites, monstersSprites, endScreenSprite

    sprites = []

    for maskIndex in range(0, 4):
        sprites.append([])
        s = sprites[maskIndex]

        # (0..23)
        for index in range(0, 24):
            s.append(ss_shared[maskIndex].get_indexed_image(index, BLOC_SIZE, BLOC_SIZE))

        # (24..59)
        for index in range(0, 36):
            s.append(ss_levels[currLand].get_indexed_image(index, BLOC_SIZE, BLOC_SIZE))

        # Teleport blocs (60, 61)
        for index in range(24, 26):
            s.append(ss_shared[0].get_indexed_image(index, BLOC_SIZE, BLOC_SIZE))

        # 62: specific bloc for Revenge
        s.append(ss_revenge.get_indexed_image(0, BLOC_SIZE, BLOC_SIZE))

    # Monsters
    monstersSprites = []
    for index in range(36, 96):
        monstersSprites.append(ss_levels[currLand].get_indexed_image(index, BLOC_SIZE, BLOC_SIZE))

    # End Screen
    endScreenSprite = ss_endScreens[currLand].get_indexed_image(0, WINDOW_WIDTH, WINDOW_HEIGHT)
