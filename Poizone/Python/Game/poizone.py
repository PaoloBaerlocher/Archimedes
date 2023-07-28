# POIZONE re-written in Python 3.11, july 2023 (32 years later after the original).
import pygame
import numpy
import math
import random
import spritesheet
from enum import Enum

# Constants
ORIGIN_X = 8            # In pixels
ORIGIN_Y = 8
BLOC_SIZE = 20          # In pixels
BLOCS_RANGE = 12
BORDER_SIZE = 3 * BLOC_SIZE
MONSTERS_NB = 8
SCHEME_WIDTH = 64       # In bloc units
SCHEME_SIZE = 3072      # SCHEME_WIDTH*48
PENG_WALK_STEP = 4      # In pixels
MONS_WALK_STEP = 2

# GAME PHASES
PHASE_INTRO = 0
PHASE_GAME  = 1

# KEY
KEY_UP    = 0
KEY_DOWN  = 1
KEY_LEFT  = 2
KEY_RIGHT = 3
KEY_SPACE = 4

# BLOC

# General Codes     00 - 23 . blocs     ; 00-15  ---  Sprites
#                   24 - 59 . background

# Codes for SCHEME data ; 00 - 23 . blocs  ( 23 = ELECTRIC )
#                         24 - 59 . EMPTY (place au decor)

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
BLOC_RADIO       = 9
BLOC_GREEN_CHEM  = 10
BLOC_MAGIC       = 11
BLOC_ROCK        = 12
BLOC_GOLD        = 13
BLOC_GYRO        = 14
BLOC_DIAMOND     = 15
BLOC_BASIC_0     = 16       # For Land No 0 (ice)
BLOC_BASIC_2     = 17       # For Land No 2 (space)
BLOC_BASIC_1     = 18       # For Land No 1 (station)
BLOC_BASIC_3     = 19       # For Land No 3 (jungle)
BLOC_BASIC_4     = 20       # For Land No 4 (computer)
BLOC_ELECTRO_0   = 21       # Anim
BLOC_ELECTRO_1   = 22
BLOC_ELECTRO     = 23
BLOC_TELEPORT_0  = 60       # Anim
BLOC_TELEPORT_1  = 61

# Enums

class PenguinStatus(Enum):
    IDLE = 0
    WALK = 1
    DIE  = 2
    PUSH = 3

# Utility functions

def clamp(n, smallest, largest): return max(smallest, min(n, largest))

# Classes

class Penguin():
    def __init__(self):
        self.resetLevel()
        self.score = 0

    def resetLevel(self):
        self.posX = 24 * BLOC_SIZE   # Center of map
        self.posY = 24 * BLOC_SIZE
        self.dirX = 0
        self.dirY = 0
        self.anim = 0
        self.animPhase = 0
        self.status = PenguinStatus.IDLE
        self.invert = False
        self.ghost = 0              # Invincible if > 0
        self.canTeleport = True

        self.movBlocWhat = -1   # Which bloc (-1 : no bloc)
        self.movBlocPosX = 0
        self.movBlocPosY = 0
        self.movBlocDirX = 0
        self.movBlocDirY = 0
        self.movMonsters = 0    # Number of monsters killed by moving bloc
        self.movBonusTimer = 0

    def getBloc(self, dirX, dirY):
        return getBloc(int(self.posX / BLOC_SIZE) + dirX, int(self.posY / BLOC_SIZE) + dirY)

    def launchBloc(self, bloc, posX, posY, dirX, dirY):
        print('LaunchBloc')
        self.movBlocWhat = bloc
        self.movBlocPosX = posX + dirX * BLOC_SIZE
        self.movBlocPosY = posY + dirY * BLOC_SIZE
        self.movBlocDirX = dirX
        self.movBlocDirY = dirY
        self.movMonsters = 0

    def pushBloc(self):
        global electrifyBorder

        if self.dirX != 0 or self.dirY != 0:
            bloc = self.getBloc(self.dirX, self.dirY)
            self.status = PenguinStatus.PUSH
            if bloc == BLOC_ELECTRO:
                setElectrifyBorder(True)
            elif bloc < 24:
                nextBloc = self.getBloc(self.dirX * 2, self.dirY * 2)
                if (nextBloc >= 24):
                    self.launchBloc(bloc, self.posX, self.posY, self.dirX, self.dirY)
                    blocX = int(self.posX / BLOC_SIZE) + self.dirX
                    blocY = int(self.posY / BLOC_SIZE) + self.dirY
                    writeBloc(blocX, blocY, 26)         # Remove bloc from initial position
                    soundLaunch.play()
                else:
                    crushBloc(bloc, self)

    def die(self):

        self.animPhase = 0
        self.status = PenguinStatus.DIE
        print('Die')
        soundColl.play()

    def checkSquareDiamond(self, bx, by):
        if (getBloc(bx, by - 1) == BLOC_DIAMOND):
            if (getBloc(bx - 1, by - 1) == BLOC_DIAMOND) and (getBloc(bx - 1, by) == BLOC_DIAMOND):
                return True
            if (getBloc(bx + 1, by - 1) == BLOC_DIAMOND) and (getBloc(bx + 1, by) == BLOC_DIAMOND):
                return True

        if (getBloc(bx, by + 1) == BLOC_DIAMOND):
            if (getBloc(bx - 1, by + 1) == BLOC_DIAMOND) and (getBloc(bx - 1, by) == BLOC_DIAMOND):
                return True
            if (getBloc(bx + 1, by + 1) == BLOC_DIAMOND) and (getBloc(bx + 1, by) == BLOC_DIAMOND):
                return True

        return False

    def isOnBlock(self):
        return isOnBlock(self.posX, self.posY)

    def getNextTeleportIndex(self):     # Or -1 if none
        penguinIndex = int(self.posX / BLOC_SIZE) + int(self.posY / BLOC_SIZE) * SCHEME_WIDTH
        nb = len(teleporters[currLand])
        for i in range(0, nb):
            tele = teleporters[currLand][i]
            if (tele == penguinIndex):
                # Check if next teleporter is available
                nextIndex = teleporters[currLand][(i + 1) % nb]
                if scheme[nextIndex] >= 24:
                    return nextIndex
                else:
                    # Check other teleporter
                    nextIndex = teleporters[currLand][(i + 2) % nb]
                    if scheme[nextIndex] >= 24:
                        return nextIndex
        return -1

    def getPenguinAnimOffset(self):
        dir = 3  # Down
        if (self.dirX <= -1):
            dir = 0  # Left
        if (self.dirX >= +1):
            dir = 1  # Right
        if (self.dirY <= -1):
            dir = 2  # Up

        if (self.status == PenguinStatus.IDLE):
            return 4 * dir
        if (self.status == PenguinStatus.WALK):
            return 4 * dir + (int(self.animPhase / 8) % 4)
        if (self.status == PenguinStatus.DIE):
            if self.animPhase < 32:
                return 16 + 4 * dir + int(self.animPhase / 16)
            return 16 + 4 * dir + 2 + (int(self.animPhase / 8) % 2)  # End loop
        if (self.status == PenguinStatus.PUSH):
            return 32 + dir
        return 0

    def display(self, screen, baseX, baseY):
        if int(self.ghost / 4) % 2 == 0:
            screen.blit(penguinSprites[self.anim], (ORIGIN_X+self.posX-baseX, ORIGIN_Y+self.posY-baseY))

    def displayMovingBloc(self, screen, baseX, baseY):
        if self.movBlocWhat != -1:
            c = CropSprite(self.movBlocPosX - baseX, self.movBlocPosY - baseY)
            index = getAliasBlocIndex(self.movBlocWhat)
            screen.blit(sprites[index], (ORIGIN_X + c.posX, ORIGIN_Y + c.posY), c.getCroppedRegion())

        # Display killed monsters bonus, if any
        if self.movBonusTimer > 0:
            self.movBonusTimer -= 1
            if self.movMonsters > 0:  # At least one monster has been killed
                c = CropSprite(self.movBlocPosX - baseX, self.movBlocPosY - baseY)
                index = clamp(self.movMonsters - 1, 0, 3)  # Display corresponding bonus (20, 50, 100 or 200)
                screen.blit(penguinSprites[72 + index], (ORIGIN_X + c.posX, ORIGIN_Y + c.posY), c.getCroppedRegion())

    def update(self, keyPressed):
        global monsters, teleporters, scheme, baseX, baseY

        penguinMove = keyPressed[KEY_LEFT] or keyPressed[KEY_RIGHT] or keyPressed[KEY_UP] or keyPressed[KEY_DOWN]

        if penguinMove:
            self.canTeleport = True

        if keyPressed[KEY_SPACE] and penguinMove and isOnBlock(self.posX, self.posY):
            self.pushBloc()

        if isOnBlock(self.posX, self.posY) and self.status != PenguinStatus.PUSH and self.status != PenguinStatus.DIE:
            if keyPressed[KEY_LEFT]:
                self.dirX = -1 if self.invert == False else +1
                self.dirY = 0
                if not blocIsWalkable(self, self.dirX, self.dirY):
                    self.status = PenguinStatus.IDLE

            if keyPressed[KEY_RIGHT]:
                self.dirX = 1 if self.invert == False else -1
                self.dirY = 0
                if not blocIsWalkable(self, self.dirX, self.dirY):
                    self.status = PenguinStatus.IDLE

            if keyPressed[KEY_UP]:
                self.dirX = 0
                self.dirY = -1 if self.invert == False else +1
                if not blocIsWalkable(self, self.dirX, self.dirY):
                    self.status = PenguinStatus.IDLE

            if keyPressed[KEY_DOWN]:
                self.dirX = 0
                self.dirY = 1 if self.invert == False else -1
                if not blocIsWalkable(self, self.dirX, self.dirY):
                    self.status = PenguinStatus.IDLE

        if (self.status == PenguinStatus.PUSH) and ((penguinMove == False) or not keyPressed[KEY_SPACE]):
            self.status = PenguinStatus.IDLE
            setElectrifyBorder(False)

        if (self.status == PenguinStatus.IDLE) and (self.dirX != 0 or self.dirY != 0) and (
                penguinMove == True):
            if blocIsWalkable(self, self.dirX, self.dirY):
                self.status = PenguinStatus.WALK

        if (self.status == PenguinStatus.WALK):
            self.posX += self.dirX * PENG_WALK_STEP
            self.posY += self.dirY * PENG_WALK_STEP
            if isOnBlock(self.posX, self.posY):  # Stop walking at next block
                if penguinMove == False:
                    self.status = PenguinStatus.IDLE
                elif blocIsWalkable(self, self.dirX, self.dirY) == False:
                    self.status = PenguinStatus.IDLE

        if (self.status == PenguinStatus.DIE) and (self.animPhase > 128):  # Re-birth
            self.status = PenguinStatus.IDLE
            self.animPhase = 0
            self.ghost = 60

        self.anim = self.getPenguinAnimOffset()
        self.animPhase += 1

        # Move camera and clamp its position

        baseX = clamp(baseX, penguin1.posX - (BLOCS_RANGE * BLOC_SIZE - BORDER_SIZE - BLOC_SIZE),
                      penguin1.posX - BORDER_SIZE)
        baseY = clamp(baseY, penguin1.posY - (BLOCS_RANGE * BLOC_SIZE - BORDER_SIZE - BLOC_SIZE),
                      penguin1.posY - BORDER_SIZE)

        MAX_X = (48 - BLOCS_RANGE) * BLOC_SIZE - 4  # In pixels
        MAX_Y = (48 - BLOCS_RANGE) * BLOC_SIZE - 4

        baseX = clamp(baseX, 0, MAX_X)
        baseY = clamp(baseY, 0, MAX_Y)

        # Check teleporters

        if self.isOnBlock() and self.canTeleport:
            found = self.getNextTeleportIndex()
            if found != -1:
                print('Teleporter found : ' + str(found))
                newPosX = found % SCHEME_WIDTH
                newPosY = int(found / SCHEME_WIDTH)
                self.posX = newPosX * BLOC_SIZE
                self.posY = newPosY * BLOC_SIZE
                soundMagic.play()
                self.canTeleport = False

        # Update moving bloc

        if self.movBlocWhat != -1:

            if (self.movBlocPosX % BLOC_SIZE == 0) and (self.movBlocPosY % BLOC_SIZE == 0):
                bx = int(self.movBlocPosX / BLOC_SIZE)
                by = int(self.movBlocPosY / BLOC_SIZE)
                if getBloc(bx + self.movBlocDirX, by + self.movBlocDirY) < 24:
                    print('End of bloc travel. Killed ' + str(self.movMonsters) + ' monsters.')

                    if (self.movBlocWhat != BLOC_GREEN_CHEM):
                        writeBloc(int(self.movBlocPosX / BLOC_SIZE), int (self.movBlocPosY / BLOC_SIZE), self.movBlocWhat)

                        if (self.movBlocWhat == BLOC_DIAMOND):
                            if self.checkSquareDiamond(bx, by) == True:
                                print('Square Diamond assembled')
                                self.score += 500
                    else:
                        destroyBloc(self.movBlocWhat)

                    self.movBlocWhat = -1
                    self.movBlocDirX = 0
                    self.movBlocDirY = 0
                    self.movBonusTimer = 60 if self.movMonsters > 0 else 0

                    bonus = [0, 20, 50, 100, 200]       # Bonus for kill a number of monsters with one bloc
                    self.score += bonus [clamp(self.movMonsters, 0, 4)]

            self.movBlocPosX += self.movBlocDirX * 10
            self.movBlocPosY += self.movBlocDirY * 10

        if self.ghost > 0:
            self.ghost -= 1

        if self.status != PenguinStatus.DIE and self.ghost == 0:     # If penguin can die, check collision with alive monsters
            for m in monsters:
                if m.isAlive() and (abs(m.posX - self.posX) <= 8) and (abs(m.posY - self.posY) <= 8):
                    self.die()
                    break

class Monster():
    def __init__(self, kind):
        self.posX = 0
        self.posY = 0
        self.dirX = 0
        self.dirY = 0
        self.kind = kind  # 0 or 1 (monster type)

        # COUNTER = -32767.. - 1    : not yet born ( -32 .. -1 : birth )
        #         = 0..9              alive (animation phases)

        self.counter = -32 - random.randrange(2200)
        self.dizzyCounter = 0       # If > 0: dizzy

    def killAndRebirth(self):
        self.dirX = 0
        self.dirY = 0
        self.counter = -32 - random.randrange(2200)
        self.dizzyCounter = 0
        self.setRandomPosition()

    def isAlive(self):
        return self.counter >= 0

    def isBirth(self):
        return self.counter >= -32 and self.counter <= -1

    def isDizzy(self):
        return self.dizzyCounter > 0

    def display(self, screen, baseX, baseY):
        if self.isBirth() or self.isAlive():
            c = CropSprite(self.posX - baseX, self.posY - baseY)
            screen.blit(monstersSprites[self.getSpriteIndex()], (ORIGIN_X + c.posX, ORIGIN_Y + c.posY), c.getCroppedRegion())

    def update(self):
        global scheme, electrifyBorder

        self.counter += 1
        if (self.dizzyCounter > 0):
            self.dizzyCounter -= 1
            if self.dizzyCounter == 0:
                self.dirX = 0 # Stop moving
                self.dirY = 0

        if self.isAlive():
            if not self.isDizzy():
                self.posX += self.dirX
                self.posY += self.dirY

            onBlock = (self.posX % BLOC_SIZE == 0) and (self.posY % BLOC_SIZE == 0)

            if electrifyBorder and self.isAlive() and not self.isDizzy() and onBlock:
                if (self.posX == BORDER_SIZE) or (self.posY == BORDER_SIZE) or (self.posX == BLOC_SIZE*44) or (self.posY == BLOC_SIZE*44):
                    self.dizzyCounter = 90
                    print('Electrify monster')

            if self.isAlive() and (penguin1.movBlocWhat != -1):
                deltaX = abs(penguin1.movBlocPosX - self.posX)
                deltaY = abs(penguin1.movBlocPosY - self.posY)
                if (deltaX <= 8) and (deltaY <= 8):
                    print('Kill monster')
                    self.killAndRebirth()
                    penguin1.movMonsters += 1
                elif (deltaX <= 16) and (deltaY <= 16):
                    print('Dizzy monster by bloc collision')
                    self.dizzyCounter = 60

            if (self.isAlive() and not self.isDizzy() and onBlock):
                found = False
                for t in range(0, 10):      # Try 10 times
                    # Choose new direction
                    if (random.randrange(2) == 0):
                        dirX = -1 if (random.randrange(2) == 0) else +1
                        dirY = 0
                    else:
                        dirX = 0
                        dirY = -1 if (random.randrange(2) == 0) else +1

                    blocIndex = int(self.posX / BLOC_SIZE) + dirX + (int(self.posY / BLOC_SIZE) + dirY) * SCHEME_WIDTH
                    if scheme[blocIndex] >= 24: # Monster can move to empty block
                        found = True
                        break

                if not found:
                    dirX = 0
                    dirY = 0

                self.dirX = dirX * MONS_WALK_STEP
                self.dirY = dirY * MONS_WALK_STEP

    def getSpriteIndex(self):
        if self.isBirth():
            return 48 + 4 * self.kind + int((32+self.counter) / 8)

        index = self.kind * 24

        if self.dizzyCounter > 0:
            index += 8

            if (self.dirX > 0):  # Right
                index += 2
            if (self.dirY > 0):  # Down
                index += 12
            if (self.dirY < 0):  # Up
                index += 14

            return index + (int(self.dizzyCounter / 8) % 2)

        if (self.dirX > 0):       # Right
            index += 4
        if (self.dirY > 0):       # Down
            index += 12
        if (self.dirY < 0):       # Up
            index += 16

        return index + (int(self.counter / 8) % 4)

    def setRandomPosition(self):
        global penguin1, scheme
        while True:
            x = 3 + random.randrange(0, 48-2*3)
            y = 3 + random.randrange(0, 48-2*3)

            if (abs(x - int(penguin1.posX / BLOC_SIZE)) < 3) or (abs(y - int(penguin1.posY / BLOC_SIZE)) < 3):
                continue                    # Penguin too close ?
            if (scheme[x + y * SCHEME_WIDTH] < 24):   # Cell already occupied ?
                continue
            self.posX = x * BLOC_SIZE
            self.posY = y * BLOC_SIZE
            return


class CropSprite():
    def __init__(self, posX, posY):
        self.posX = posX
        self.posY = posY
        self.xRegion = 0
        self.yRegion = 0
        self.widthRegion = BLOC_SIZE
        self.heightRegion = BLOC_SIZE

        # Clip

        overX = self.posX - (BLOCS_RANGE - 1) * BLOC_SIZE - 4
        overY = self.posY - (BLOCS_RANGE - 1) * BLOC_SIZE

        if (self.posX < 0):
            self.xRegion -= self.posX
            self.widthRegion += self.posX
            self.posX = 0

        if (overX > 0):
            self.widthRegion -= overX

        if (self.posY < 0):
            self.yRegion -= self.posY
            self.heightRegion += self.posY
            self.posY = 0

        if (overY > 0):
            self.heightRegion -= overY

        return

    def getCroppedRegion(self): return (self.xRegion, self.yRegion, self.widthRegion, self.heightRegion)

# Global variables

gamePhase           = PHASE_INTRO
level               = 1             # From 1 to 50
currLand            = 0             # 0..4
electrifyBorder     = False
electrifyBorderAnim = 0
blocsCount          = []
countToxicBlocs     = 0

itsChallenge        = False       # (no / yes) Challenge ?
challengeIdx        = 0           # Quel challenge (il y en a 10) ?

# Functions

def resetGame():
    global level

    level = 1

def resetLevel():
    global baseX, baseY, penguin1, itsChallenge, challengeIdx

    baseX = 18 * BLOC_SIZE
    baseY = 18 * BLOC_SIZE
    penguin1.resetLevel()
    setElectrifyBorder(False)

    itsChallenge = False  # (no / yes) Challenge ?
    challengeIdx = 0  # Quel challenge (il y en a 10) ?

def loadSprites():
    global sprites, monstersSprites
    sprites = []
    monstersSprites = []

    # (0..23)
    for index in range(0, 24):
        sprites.append(ss_shared.get_indexed_image(index, BLOC_SIZE, BLOC_SIZE))

    # (24..59)
    for index in range(0, 36):
        sprites.append(ss_levels[currLand].get_indexed_image(index, BLOC_SIZE, BLOC_SIZE))

    # Teleport blocs (60, 61)
    for index in range(24, 26):
        sprites.append(ss_shared.get_indexed_image(index, BLOC_SIZE, BLOC_SIZE))

    # Monsters
    for index in range(36, 96):
        monstersSprites.append(ss_levels[currLand].get_indexed_image(index, BLOC_SIZE, BLOC_SIZE))

def reloadLevel():
    global level, currLand, scheme, blocsCount, countToxicBlocs, monsters
    print("Load level " + str(level))
    currLand = int((level-1) / 10)
    loadSprites()

    schemeName = "Data/Schemes/S" + str(level)
    with open(schemeName, 'rb') as f:
        scheme = f.read()

    # Counts blocs in scheme
    blocsCount = [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 ]
    for i in range(0, len(scheme)):
        blocIndex = scheme[i]
        if blocIndex <= BLOC_GREEN_CHEM:
            blocsCount[blocIndex] += 1
            
    countToxicBlocs  = blocsCount[BLOC_POISON]+blocsCount[BLOC_RED]
    countToxicBlocs += blocsCount[BLOC_ALU]   +blocsCount[BLOC_BATTERY]
    countToxicBlocs += blocsCount[BLOC_DDT]   +blocsCount[BLOC_CFC]
    countToxicBlocs += blocsCount[BLOC_RADIO] +blocsCount[BLOC_GREEN_CHEM]

    print('countToxicBlocs: ' + str(countToxicBlocs))

    monsters = []
    for index in range(0, MONSTERS_NB):
        kind = index % 2
        m = Monster(kind)
        m.setRandomPosition()
        monsters.append(m)

    resetLevel()

def displayScore(score, posX, posY):
    base = 10000
    for i in range(0, 5):
        index = int(score / base) % 10
        screen.blit(charsSprites[index + 26], (posX+12*i, posY))
        base /= 10

def getBloc(indexX, indexY):
    blocOffset = indexY * SCHEME_WIDTH + indexX
    if blocOffset >= 0 and blocOffset < SCHEME_SIZE:
        blocOfScheme = scheme[blocOffset]
    else:
        blocOfScheme = BLOC_BASIC

    return blocOfScheme

def blocIsWalkable(penguin, dirX, dirY):
    return penguin.getBloc(dirX, dirY) >= 24

def isOnBlock(posX, posY):
    return ((posX % BLOC_SIZE) == 0) and ((posY % BLOC_SIZE) == 0)

def destroyBloc(bloc):
    global blocsCount, countToxicBlocs, level
    print('Destroy bloc of type ' + str(bloc))
    if (bloc <= BLOC_GREEN_CHEM):
        blocsCount[bloc] -= 1
        if (bloc >= BLOC_POISON):
            countToxicBlocs -= 1
            print('countToxicBlocs: ' + str(countToxicBlocs))
            penguin1.score += 5

    if (countToxicBlocs == 0):
        # Level finished
        level += 1
        reloadLevel()

def writeBloc(indexX, indexY, blocIndex):
    global scheme
    index = indexY * SCHEME_WIDTH + indexX
    newBloc = [ blocIndex ]
    scheme = scheme[:index] + bytes(newBloc) + scheme[(index+1):]

def getAliasBlocIndex(index):
    if index == BLOC_ELECTRO:  # Electric border (animation)
        return BLOC_ELECTRO_0 + (int(electrifyBorderAnim / 8) % 2)

    if index == BLOC_BASIC:
        if currLand == 0: return BLOC_BASIC_0
        if currLand == 1: return BLOC_BASIC_1
        if currLand == 2: return BLOC_BASIC_2
        if currLand == 3: return BLOC_BASIC_3
        if currLand == 4: return BLOC_BASIC_4

    if index == BLOC_TELEPORT_0 or index == BLOC_TELEPORT_1:
        return BLOC_TELEPORT_0 + (int(absTime / 256) % 2)

    return index

def crushBloc(bloc, penguin):

    if bloc >= BLOC_ROCK:       # Cannot crush that bloc
        return

    blocUp    = penguin.getBloc(penguin.dirX, penguin.dirY-1)
    blocDown  = penguin.getBloc(penguin.dirX, penguin.dirY+1)
    blocLeft  = penguin.getBloc(penguin.dirX-1, penguin.dirY)
    blocRight = penguin.getBloc(penguin.dirX+1, penguin.dirY)

    if bloc == BLOC_ALCOOL:
        penguin.invert = not penguin.invert
        soundAlcool.play()

    if bloc == BLOC_BOMB:
        penguin.die()
        soundBoom.play()
        #TODO add bomb animation

    if bloc == BLOC_MAGIC:          # Temporary invincibility
        penguin.ghost = 60*15
        soundMagic.play()

    if bloc == BLOC_POISON:     # Must be in contact with at least one ALU bloc
        if not (blocUp == BLOC_ALU or blocDown == BLOC_ALU or blocLeft == BLOC_ALU or blocRight == BLOC_ALU):
            penguin.die()

    if bloc == BLOC_ALU:        # Cannot crush ALU blob
        penguin.die()

    if bloc == BLOC_BATTERY:
        if penguin.dirY == 0:  # Crushed from up or down ?
            penguin.die()

    if bloc == BLOC_DDT:
        if not (blocUp == BLOC_DDT or blocDown == BLOC_DDT or blocLeft == BLOC_DDT or blocRight == BLOC_DDT):
            penguin.die()

    if bloc == BLOC_CFC:
        if penguin.dirY != 1:  # Crushed from up ?
            penguin.die()

    if bloc == BLOC_RADIO:  # Are other RADIOACTIVE blocs nearby ?
        if (blocUp == BLOC_RADIO or blocDown == BLOC_RADIO or blocLeft == BLOC_RADIO or blocRight == BLOC_RADIO):
            penguin.die()

    if bloc == BLOC_GREEN_CHEM:
        penguin.die()

    blocX = int(penguin.posX / BLOC_SIZE) + penguin.dirX
    blocY = int(penguin.posY / BLOC_SIZE) + penguin.dirY

    writeBloc(blocX, blocY, 26)
    destroyBloc(bloc)

    soundCrash.play()

def setElectrifyBorder(newStatus):
    global electrifyBorder

    if  newStatus == True and electrifyBorder == False:
        soundElec.play(100)

    if newStatus == False and electrifyBorder == True:
        soundElec.stop()

    electrifyBorder = newStatus

# pygame setup
pygame.init()
pygame.mixer.init()  # Initialize the mixer module.
screen = pygame.display.set_mode((320, 256), pygame.SCALED)
clock = pygame.time.Clock()
running = True

# Load sounds
# From TRACKER: samples indexes from 24 to 35
soundLaunch= pygame.mixer.Sound('Data/bruitages/LAUNCHBLCK.wav')        # 24 (sample O)
soundCrash = pygame.mixer.Sound('Data/bruitages/CRASHblock.wav')        # 25 (sample P)
soundBoom  = pygame.mixer.Sound('Data/bruitages/BOOM.wav')              # 26 (sample Q)
soundElec  = pygame.mixer.Sound('Data/bruitages/ELECTRIC.wav')          # 27 (sample R)
soundMagic = pygame.mixer.Sound('Data/bruitages/MAGIC.wav')             # 28 (sample S)
# soundDiam  = pygame.mixer.Sound('Data/bruitages/DIAMOND.wav')           # 29 (sample T) - diamond (wrong)
soundFun   = pygame.mixer.Sound('Data/bruitages/Fun.wav')               # 30 (sample U) - laugh
soundOhNo  = pygame.mixer.Sound('Data/bruitages/OH_NO.wav')             # 31 (sample V)
soundAlcool= pygame.mixer.Sound('Data/bruitages/BEER_BLOCK.wav')        # 32 (sample W)
soundColl  = pygame.mixer.Sound('Data/bruitages/COLLISION.wav')         # 33 (sample X)
soundWow   = pygame.mixer.Sound('Data/bruitages/HMM.wav')               # 35 (sample Z) - WOW END OF LEVEL (wrong sample)

soundSplat = pygame.mixer.Sound('Data/bruitages/SPLATCH.wav')

# READY = ?

# Set volumes

soundCrash.set_volume(0.5)
soundLaunch.set_volume(0.3)
soundMagic.set_volume(0.2)

# Load Lands and extract teleporters positions.

lands = []
teleporters = []

for index in range(0, 5):
    landsName = "Data/Lands/L" + str(index) + "_SET"
    with open(landsName, 'rb') as f:
        land = f.read()
    lands.append(land)
    teleporters.append([])
    print('Teleporters in land #' + str(index) + ':')
    for i in range(0, len(land), 4):
        if land[i] >= BLOC_TELEPORT_0:
            j=int(i/4)
            teleporters[index].append(j)
            print('  ' + str(j%64) + ',' + str(int(j/SCHEME_WIDTH)))

# SpriteSheets

ss_start    = spritesheet.SpriteSheet('Data/startScreen.png')
ss_bg       = spritesheet.SpriteSheet('Data/border.png')
ss_shared   = spritesheet.SpriteSheet('Data/sharedBlocs.png')
ss_Penguins = spritesheet.SpriteSheet('Data/pengos.png')
ss_chars    = spritesheet.SpriteSheet('Data/chars.png')

ss_levels = []
for index in range(1, 6):
    ss_levels.append(spritesheet.SpriteSheet('Data/level' + str(index) + '.png'))

# Other graphic assets

image_maskCrash = pygame.image.load("Data/maskCrash.png").convert_alpha()

# BORDER

startScreen = ss_start.get_indexed_image(0, 244, 240)
border = ss_bg.get_indexed_image(0, 320, 256)

penguin1 = Penguin()

reloadLevel()

penguinSprites = []
for index in range(0, 2*36+12):
    penguinSprites.append(ss_Penguins.get_indexed_image(index, BLOC_SIZE, BLOC_SIZE))

charsSprites = []
for index in range(0, 40):
    charsSprites.append((ss_chars.get_indexed_image(index, 12, 16)))

# Variables
absTime = 0

keyPressed = [False, False, False, False, False]   # Up Down Left Right Space

while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT:
                keyPressed[KEY_LEFT] = False

            if event.key == pygame.K_RIGHT:
                keyPressed[KEY_RIGHT] = False

            if event.key == pygame.K_UP:
                keyPressed[KEY_UP] = False

            if event.key == pygame.K_DOWN:
                keyPressed[KEY_DOWN] = False

            if event.key == pygame.K_SPACE:
                keyPressed[KEY_SPACE] = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                keyPressed[KEY_LEFT] = True

            if event.key == pygame.K_RIGHT:
                keyPressed[KEY_RIGHT] = True

            if event.key == pygame.K_UP:
                keyPressed[KEY_UP] = True

            if event.key == pygame.K_DOWN:
                keyPressed[KEY_DOWN] = True

            if event.key == pygame.K_SPACE:
                keyPressed[KEY_SPACE] = True

            if event.key == pygame.K_F1:    # Start game
                if gamePhase == PHASE_INTRO:
                    gamePhase = PHASE_GAME
                    resetGame()
                    reloadLevel()

            if event.key == pygame.K_ESCAPE:  # Quit game
                if gamePhase == PHASE_GAME:
                    gamePhase = PHASE_INTRO

            if event.key == pygame.K_F6:    # Next level
                if (level < 50):
                    level += 1
                    reloadLevel()

            if event.key == pygame.K_F5:    # Prev level
                if (level > 1):
                    level -= 1
                    reloadLevel()

    # Animate electric border
    if electrifyBorder == True:
        electrifyBorderAnim += 1

    # Update Penguin
    penguin1.update(keyPressed)

    # Update Monsters
    for m in monsters:
        m.update()

    ######
    # DRAW
    ######

    # Fill the screen with a color to wipe away anything from last frame
    screen.fill("black")
    screen.blit(border, (0, 0))

    if gamePhase == PHASE_INTRO:
        screen.blit(startScreen, (ORIGIN_X, ORIGIN_Y))
    else:
        # Draw BG

        anim = int(absTime / 4)
        for y in range(0, BLOCS_RANGE + 1):
            for x in range(0, BLOCS_RANGE + 1):

                blocOffset = (int(baseY / BLOC_SIZE) + y) * SCHEME_WIDTH + (int(baseX / BLOC_SIZE) + x)
                index = int(lands[currLand][4 * blocOffset + (anim % 4)])

                if blocOffset < SCHEME_SIZE:
                    blocOfSchemes = scheme[blocOffset]
                    if blocOfSchemes < 24:
                        index = blocOfSchemes

                posX = x * BLOC_SIZE - int(baseX % BLOC_SIZE)
                posY = y * BLOC_SIZE - int(baseY % BLOC_SIZE)

                c = CropSprite(posX, posY)

                if index >= 0 and index < 120:
                    index = getAliasBlocIndex(index)
                    screen.blit(sprites[index], (ORIGIN_X + c.posX, ORIGIN_Y + c.posY), c.getCroppedRegion())

        # Display Penguin
        penguin1.display(screen, baseX, baseY)

        # Display Monsters
        for m in monsters:
            m.display(screen, baseX, baseY)

        # Display moving bloc and bonus, if any
        penguin1.displayMovingBloc(screen, baseX, baseY)

    # Display Scores
    displayScore(penguin1.score, 256, 45)
    displayScore(0, 256, 188)   # No 2nd player supported, for now

    # Time
    absTime += clock.get_time()

    # flip() the display to put your work on screen
    pygame.display.flip()

    clock.tick(60)  # limits FPS to 60

pygame.quit()