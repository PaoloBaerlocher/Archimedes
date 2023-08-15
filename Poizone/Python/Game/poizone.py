# POIZONE re-written in Python 3.11, july 2023 (32 years later after the original).
# 2-player mode is not supported.

import pygame
import numpy
import math
import random
import spritesheet
import leaderboard
import options
import particles
import tuto
import texts
from enum import Enum

# Constants
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
PENG_WALK_STEP = 4      # In pixels
MONS_WALK_STEP = 2
MOVBLOC_STEP = 10
CYCLONE_OFFSETS = [[-1, -1], [0, -1], [+1, -1], [+1, 0], [+1, +1], [0, +1], [-1, +1], [-1, 0]]  # 8 blocs around cyclone
JOY_LIMIT = 0.8
SUCCESS_GOAL = 90       # % of toxic blocs to destroy to win level
ALPHABET_ROWS = 4       # For 'Enter your name'
ALPHABET_COLUMNS = 7
OPTIONS_ID = ["SFX", "MUSIC"]
TUTO_PAGES = 15

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
MENU_TUTORIAL   = 3
MENU_OPTIONS    = 4
MENU_CREDITS    = 5

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

# Enums

class PenguinStatus(Enum):
    IDLE = 0
    WALK = 1
    DIE  = 2
    PUSH = 3

# Global variables

gamePhase           = PHASE_NONE
gameTimer           = 0.0           # 0 - 300 ( 5 minutes ) - in seconds
level               = 1             # From 1 to 50
currLand            = 0             # 0..4 (LAND_...)
electrifyBorder     = False
electrifyBorderAnim = 0
blocsCount          = []
toxicBlocsLeft      = 0
cyclonesPace        = 0             # For cyclones
cyclonesList        = []

isRevenge           = False         # Revenge mode ?
windowFade          = 0             # 0..255
menuCounter         = 0

# Utility functions

def clamp(n, smallest, largest): return max(smallest, min(n, largest))

# Classes

class Penguin():
    def __init__(self):
        self.reset()
        self.score = 0

    def reset(self):
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

        self.movBlocWhat = NONE   # Which bloc (NONE : no bloc)
        self.movBlocPosX = 0
        self.movBlocPosY = 0
        self.movBlocDirX = 0
        self.movBlocDirY = 0
        self.movMonsters = 0    # Number of monsters killed by moving bloc
        self.movBonusTimer = 0  # Timer for displaying the bonus

        self.crushBlocWhat = NONE   # Which bloc (NONE : no bloc)
        self.crushBlocPosX = 0
        self.crushBlocPosY = 0
        self.crushBlocTimer = 0

        self.bombTimer = 0              # Exploding Bomb animation
        self.bombPosX = 0
        self.bombPosY = 0

    def setStatus(self, status):
        if status != self.status:
            print('New Penguin status: ' + str(status))
            self.status = status

    def getBlocOnDir(self, dirX, dirY):
        return getBloc(self.posX // BLOC_SIZE + dirX, self.posY // BLOC_SIZE + dirY)

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
            bloc = self.getBlocOnDir(self.dirX, self.dirY)
            self.setStatus(PenguinStatus.PUSH)
            if bloc == BLOC_ELECTRO:
                setElectrifyBorder(True)
            elif bloc < 24:
                nextBloc = self.getBlocOnDir(self.dirX * 2, self.dirY * 2)
                if (nextBloc >= 24):
                    if self.movBlocWhat == NONE:        # Avoid overriding ongoing launch bloc
                        self.launchBloc(bloc, self.posX, self.posY, self.dirX, self.dirY)
                        blocX = self.posX // BLOC_SIZE + self.dirX
                        blocY = self.posY // BLOC_SIZE + self.dirY
                        writeBloc(blocX, blocY, 26)         # Remove bloc from initial position
                        if bloc == BLOC_CYCLONE:
                            idx = cyclonesList.index(blocX + blocY * SCHEME_WIDTH)
                            print('Remove cyclone ' + str(cyclonesList[idx]) + ' from list at index ' + str(idx))
                            cyclonesList[idx] = 0

                        playSFX(soundLaunch)

                        if bloc == BLOC_RED:        # Do NOT launch red chemical block!
                            playSFX(soundOhNo)
                            self.die()
                else:
                    self.crushBloc(bloc)

    def startBombAnim(self, posX, posY):
        # Start exploding bomb animation
        self.bombTimer = 32
        self.bombPosX = posX
        self.bombPosY = posY

    def startCrushAnim(self, bloc, posX, posY):
        # Start crush animation
        self.crushBlocWhat = bloc
        self.crushBlocPosX = posX
        self.crushBlocPosY = posY
        self.crushBlocTimer = 11

    def crushBloc(self, bloc):

        if bloc >= BLOC_ROCK:  # Cannot crush that bloc
            return

        blocUp    = self.getBlocOnDir(self.dirX, self.dirY - 1)
        blocDown  = self.getBlocOnDir(self.dirX, self.dirY + 1)
        blocLeft  = self.getBlocOnDir(self.dirX - 1, self.dirY)
        blocRight = self.getBlocOnDir(self.dirX + 1, self.dirY)

        if bloc == BLOC_ALCOOL:
            self.invert = not self.invert
            playSFX(soundAlcool)

        if bloc == BLOC_BOMB:
            self.die()
            playSFX(soundBoom)

        if bloc == BLOC_MAGIC:  # Temporary invincibility
            self.ghost = 60 * 15
            playSFX(soundMagic)

        if bloc == BLOC_POISON:  # Must be in contact with at least one ALU bloc
            if not (blocUp == BLOC_ALU or blocDown == BLOC_ALU or blocLeft == BLOC_ALU or blocRight == BLOC_ALU):
                self.die()

        if bloc == BLOC_ALU:  # Cannot crush ALU blob
            self.die()

        if bloc == BLOC_BATTERY:
            if self.dirY == 0:  # Crushed from up or down ?
                self.die()

        if bloc == BLOC_DDT:
            if not (blocUp == BLOC_DDT or blocDown == BLOC_DDT or blocLeft == BLOC_DDT or blocRight == BLOC_DDT):
                self.die()

        if bloc == BLOC_CFC:
            if self.dirY != 1:  # Crushed from up ?
                self.die()

        if bloc == BLOC_URANIUM:  # Are other BLOC_URANIUM blocs nearby ?
            if (blocUp == BLOC_URANIUM or blocDown == BLOC_URANIUM or blocLeft == BLOC_URANIUM or blocRight == BLOC_URANIUM):
                self.die()

        if bloc == BLOC_GREEN_CHEM:
            self.die()

        blocX = self.posX // BLOC_SIZE + self.dirX
        blocY = self.posY // BLOC_SIZE + self.dirY

        if bloc == BLOC_BOMB:
            self.startBombAnim(self.posX + self.dirX * BLOC_SIZE, self.posY + self.dirY * BLOC_SIZE)
        else:
            self.startCrushAnim(bloc, self.posX + self.dirX * BLOC_SIZE, self.posY + self.dirY * BLOC_SIZE)

        writeBloc(blocX, blocY, 26)
        destroyBloc(bloc)

        playSFX(soundCrash)

    def die(self):

        self.animPhase = 0
        self.setStatus(PenguinStatus.DIE)
        playSFX(soundColl)
        setElectrifyBorder(False)

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

    def blocIsWalkable(self, dirX, dirY):

        # Check occupy table
        blocIndex =(self.posX // BLOC_SIZE + dirX) + (self.posY // BLOC_SIZE + dirY) * SCHEME_WIDTH
        if (occupyTable[blocIndex] & 0b10) != 0:
            return False

        return self.getBlocOnDir(dirX, dirY) >= 24

    def getNextTeleportIndex(self):     # Or -1 if none
        penguinIndex = self.posX // BLOC_SIZE + (self.posY // BLOC_SIZE) * SCHEME_WIDTH
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
        if (self.ghost / 4) % 4 <= 2:
            c = CropSprite(self.posX - baseX, self.posY - baseY)
            screen.blit(penguinSprites[self.anim], (ORIGIN_X+c.posX, ORIGIN_Y+c.posY), c.getCroppedRegion())

    def displayBloc(self, screen, baseX, baseY):

        if self.bombTimer > 0:
            c = CropSprite(self.bombPosX - baseX, self.bombPosY - baseY)
            index = 76 + int((32 - self.bombTimer) / 4)
            screen.blit(penguinSprites[index], (ORIGIN_X + c.posX, ORIGIN_Y + c.posY), c.getCroppedRegion())

        if self.crushBlocWhat != NONE:
            c = CropSprite(self.crushBlocPosX - baseX, self.crushBlocPosY - baseY)
            index = getAliasBlocIndex(self.crushBlocWhat)
            maskIndex = 3-int(self.crushBlocTimer / 4)
            screen.blit(sprites[maskIndex][index], (ORIGIN_X + c.posX, ORIGIN_Y + c.posY), c.getCroppedRegion())

        if self.movBlocWhat != NONE:
            c = CropSprite(self.movBlocPosX - baseX, self.movBlocPosY - baseY)
            index = getAliasBlocIndex(self.movBlocWhat)
            screen.blit(sprites[0][index], (ORIGIN_X + c.posX, ORIGIN_Y + c.posY), c.getCroppedRegion())

        # Display killed monsters bonus, if any
        if self.movBonusTimer > 0:
            self.movBonusTimer -= 1
            if self.movMonsters > 0:  # At least one monster has been killed
                c = CropSprite(self.movBlocPosX - baseX, self.movBlocPosY - baseY)
                index = clamp(self.movMonsters - 1, 0, 3)  # Display corresponding bonus (20, 50, 100 or 200)
                screen.blit(penguinSprites[72 + index], (ORIGIN_X + c.posX, ORIGIN_Y + c.posY), c.getCroppedRegion())

    def update(self, keyDown):
        global monsters, teleporters, scheme, baseX, baseY

        penguinMove = keyDown[KEY_LEFT] or keyDown[KEY_RIGHT] or keyDown[KEY_UP] or keyDown[KEY_DOWN]

        if penguinMove:
            self.canTeleport = True

        if keyDown[KEY_SPACE] and penguinMove and isOnBlock(self.posX, self.posY) and self.status != PenguinStatus.DIE:
            self.pushBloc()

        if isOnBlock(self.posX, self.posY) and self.status != PenguinStatus.PUSH and self.status != PenguinStatus.DIE:
            if keyDown[KEY_LEFT]:
                self.dirX = -1 if self.invert == False else +1
                self.dirY = 0
                if not self.blocIsWalkable(self.dirX, self.dirY):
                    self.setStatus(PenguinStatus.IDLE)

            if keyDown[KEY_RIGHT]:
                self.dirX = 1 if self.invert == False else -1
                self.dirY = 0
                if not self.blocIsWalkable(self.dirX, self.dirY):
                    self.setStatus(PenguinStatus.IDLE)

            if keyDown[KEY_UP]:
                self.dirX = 0
                self.dirY = -1 if self.invert == False else +1
                if not self.blocIsWalkable(self.dirX, self.dirY):
                    self.setStatus(PenguinStatus.IDLE)

            if keyDown[KEY_DOWN]:
                self.dirX = 0
                self.dirY = 1 if self.invert == False else -1
                if not self.blocIsWalkable(self.dirX, self.dirY):
                    self.setStatus(PenguinStatus.IDLE)

        if (self.status == PenguinStatus.PUSH) and ((penguinMove == False) or not keyDown[KEY_SPACE]):
            self.setStatus(PenguinStatus.IDLE)
            setElectrifyBorder(False)

        if (self.status == PenguinStatus.IDLE) and (self.dirX != 0 or self.dirY != 0) and (
                penguinMove == True):
            if self.blocIsWalkable(self.dirX, self.dirY):
                self.setStatus(PenguinStatus.WALK)

        if (self.status == PenguinStatus.WALK):
            self.posX += self.dirX * PENG_WALK_STEP
            self.posY += self.dirY * PENG_WALK_STEP
            if isOnBlock(self.posX, self.posY):  # Stop walking at next block
                if penguinMove == False:
                    self.setStatus(PenguinStatus.IDLE)
                elif self.blocIsWalkable(self.dirX, self.dirY) == False:
                    self.setStatus(PenguinStatus.IDLE)

        if (self.status == PenguinStatus.DIE) and (self.animPhase > 128):  # Re-birth
            self.setStatus(PenguinStatus.IDLE)
            self.animPhase = 0
            self.ghost = 60
            # Snap to grid
            self.posX = ((self.posX + BLOC_SIZE // 2) // BLOC_SIZE) * BLOC_SIZE
            self.posY = ((self.posY + BLOC_SIZE // 2) // BLOC_SIZE) * BLOC_SIZE

        self.anim = self.getPenguinAnimOffset()
        self.animPhase += 1

        # Move camera to follow penguin, and clamp its position

        if not isRevenge:
            offsetX = penguin1.posX + 8 - baseX - (BLOCS_RANGE * BLOC_SIZE) // 2
            if (offsetX < 0):
                baseX -= PENG_WALK_STEP
            elif offsetX > 0:
                baseX += PENG_WALK_STEP

            offsetY = penguin1.posY + 8 - baseY - (BLOCS_RANGE * BLOC_SIZE) // 2
            if (offsetY < 0):
                baseY -= PENG_WALK_STEP
            elif offsetY > 0:
                baseY += PENG_WALK_STEP

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
                newPosY = found // SCHEME_WIDTH
                self.posX = newPosX * BLOC_SIZE
                self.posY = newPosY * BLOC_SIZE
                playSFX(soundTele)
                self.canTeleport = False

        # Update crushed bloc

        if self.crushBlocWhat != NONE:
            self.crushBlocTimer -= 1
            if self.crushBlocTimer == 0:
                self.crushBlocWhat = NONE

            # Update occupyTable
            blocIndex = self.crushBlocPosX // BLOC_SIZE + (self.crushBlocPosY // BLOC_SIZE) * SCHEME_WIDTH
            occupyTable[blocIndex] = 0b10 if self.crushBlocTimer > 3 else 0  # Cell is forbidden until bloc is crushed

        # Update bomb anim

        if self.bombTimer > 0:
            self.bombTimer -= 1

        # Update moving bloc

        if self.movBlocWhat != NONE:

            if (self.movBlocPosX % BLOC_SIZE == 0) and (self.movBlocPosY % BLOC_SIZE == 0):
                bx = self.movBlocPosX // BLOC_SIZE
                by = self.movBlocPosY // BLOC_SIZE
                nextBloc = getBloc(bx + self.movBlocDirX, by + self.movBlocDirY)
                if nextBloc < 24:
                    print('End of bloc travel. Killed ' + str(self.movMonsters) + ' monsters.')

                    killBloc = (self.movBlocWhat == BLOC_GREEN_CHEM)
                    if self.movBlocWhat == BLOC_ALU:
                        if (getBloc(bx+1, by) == BLOC_ELECTRO) or (getBloc(bx-1, by) == BLOC_ELECTRO) or \
                           (getBloc(bx, by-1) == BLOC_ELECTRO) or (getBloc(bx, by+1) == BLOC_ELECTRO):
                            killBloc = True     # Kill ALU when launched against electro border

                    if not killBloc:
                        writeBloc(bx, by, self.movBlocWhat)

                        if self.movBlocWhat == BLOC_CYCLONE:
                            # Insert it back in the cyclonesList
                            for index in range(0, len(cyclonesList)):
                                if cyclonesList[index] == 0:
                                    cyclonesList[index] = bx + by * SCHEME_WIDTH
                                    break

                        if (self.movBlocWhat == BLOC_DIAMOND):
                            if self.checkSquareDiamond(bx, by) == True:
                                print('Square Diamond assembled')
                                playSFX(soundDiam)
                                self.score += 500
                    else:
                        destroyBloc(self.movBlocWhat)
                        playSFX(soundSplatch)
                        # Start crush animation
                        self.startCrushAnim(self.movBlocWhat, self.movBlocPosX, self.movBlocPosY)

                    # Stop moving bloc animation
                    self.movBlocWhat = NONE
                    self.movBlocDirX = 0
                    self.movBlocDirY = 0
                    self.movBonusTimer = 60 if self.movMonsters > 0 else 0

                    bonusKill = [0, 20, 50, 100, 200]       # Bonus for killing monsters with one bloc
                    self.score += bonusKill [clamp(self.movMonsters, 0, 4)]

            self.movBlocPosX += self.movBlocDirX * MOVBLOC_STEP
            self.movBlocPosY += self.movBlocDirY * MOVBLOC_STEP

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

        self.counter = -32 - random.randrange(self.getBirthRange())
        self.dizzyCounter = 0       # If > 0: dizzy

    def killAndRebirth(self):

        global isRevenge

        self.dirX = 0
        self.dirY = 0

        self.counter = -32 - random.randrange(self.getBirthRange())

        self.dizzyCounter = 0
        self.setRandomPosition()

    def getBirthRange(self):
        global isRevenge
        return 300 if isRevenge == True else 2200

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

        if self.isAlive():
            if not self.isDizzy():
                self.posX += self.dirX
                self.posY += self.dirY

            if (self.dizzyCounter > 0):
                self.dizzyCounter -= 1

            onBlock = (self.posX % BLOC_SIZE == 0) and (self.posY % BLOC_SIZE == 0)

            if electrifyBorder and self.isAlive() and not self.isDizzy() and onBlock:
                if (self.posX == BORDER_SIZE) or (self.posY == BORDER_SIZE) or (self.posX == BLOC_SIZE*44) or (self.posY == BLOC_SIZE*44):
                    self.dizzyCounter = 4*60
                    print('Electrify monster')
                    
            if self.isAlive() and (penguin1.movBlocWhat != NONE):
                deltaX = abs(penguin1.movBlocPosX - self.posX)
                deltaY = abs(penguin1.movBlocPosY - self.posY)
                if (deltaX <= 10) and (deltaY <= 10):
                    print('Kill monster')
                    self.killAndRebirth()
                    playSFX(soundColl)
                    penguin1.movMonsters += 1
                elif (deltaX <= 12) and (deltaY <= 12):
                    print('Dizzy monster by bloc collision')
                    self.dizzyCounter = 4*60

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

                    blocIndex = self.posX // BLOC_SIZE + dirX + (self.posY // BLOC_SIZE + dirY) * SCHEME_WIDTH

                    if occupyTable[blocIndex] != 0:      # Forbidden destination bloc
                        continue

                    if scheme[blocIndex] >= 24: # Monster can move to empty block
                        found = True
                        break

                if not found:
                    dirX = 0
                    dirY = 0
                else:
                    # Update Occupy Table
                    currentBlocIndex = self.posX // BLOC_SIZE + (self.posY // BLOC_SIZE) * SCHEME_WIDTH
                    occupyTable[currentBlocIndex] = 0
                    occupyTable[blocIndex] = 1

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
        global penguin1, scheme, isRevenge, occupyTable

        while True:

            if isRevenge == False:
                x = 3 + random.randrange(0, 48-2*3)
                y = 3 + random.randrange(0, 48-2*3)
            else:
                x = baseX // BLOC_SIZE + 1 + random.randrange(0, 10)
                y = baseY // BLOC_SIZE + 1 + random.randrange(0, 10)
            print(f"New monster at {x},{y}")

            if (occupyTable[x + y * SCHEME_WIDTH] != 0):      # Already occupied
                continue

            if (abs(x - int(penguin1.posX / BLOC_SIZE)) < 3) or (abs(y - int(penguin1.posY / BLOC_SIZE)) < 3):
                continue                    # Penguin too close ?
            if (scheme[x + y * SCHEME_WIDTH] < 24):   # Cell already occupied ?
                continue
            self.posX = x * BLOC_SIZE
            self.posY = y * BLOC_SIZE
            return


class CropSprite():
    def __init__(self, posX, posY, widthRegion = BLOC_SIZE, heightRegion = BLOC_SIZE):
        self.posX = posX
        self.posY = posY
        self.xRegion = 0
        self.yRegion = 0
        self.widthRegion = widthRegion
        self.heightRegion = heightRegion

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

# Functions

def resetGame():
    global level

    level = 1
    penguin1.score = 0

def resetLevel():
    global baseX, baseY, penguin1, isRevenge, gameTimer

    baseX = 18 * BLOC_SIZE + 8
    baseY = 18 * BLOC_SIZE + 8
    penguin1.reset()
    setElectrifyBorder(False)

    # Time available for finishing this level
    if level == 1 or level == 2:
        gameTimer = 90      # 1m30
    elif level == 3 or level == 4:
        gameTimer = 150     # 2m30
    else:
        gameTimer = 180     # 3m00

    gameTimer += 0.99       # To see the first full second, initially

    isRevenge = False
    
    playMusic(musicPlay[currLand], -1)
    playSFX(soundReady)

def resetRevenge(revenge):
    global baseX, baseY, penguin1, isRevenge, gameTimer

    isRevenge = True

    px = revenge % 4
    py = revenge // 4

    baseX = (12 * px) * BLOC_SIZE
    baseY = (1 + 12 * py) * BLOC_SIZE
    penguin1.reset()

    # Overrides for Revenge mode
    penguin1.posX = baseX + 6 * BLOC_SIZE  # Center of revenge map
    penguin1.posY = baseY + 6 * BLOC_SIZE
    
    penguin1.ghost = 10000  # Permanent ghost in Revenge mode
    
    gameTimer = 30.99

    setElectrifyBorder(False)

def loadSprites():
    global sprites, monstersSprites, endScreenSprite

    sprites = []

    for maskIndex in range(0, 4):
        sprites.append([])
        s = sprites[maskIndex]

        # (0..23)
        for index in range(0, 24):
            s.append(ss_shared [maskIndex].get_indexed_image(index, BLOC_SIZE, BLOC_SIZE))

        # (24..59)
        for index in range(0, 36):
            s.append(ss_levels[currLand].get_indexed_image(index, BLOC_SIZE, BLOC_SIZE))

        # Teleport blocs (60, 61)
        for index in range(24, 26):
            s.append(ss_shared [0].get_indexed_image(index, BLOC_SIZE, BLOC_SIZE))

        # 62: specific bloc for Revenge
        s.append(ss_revenge.get_indexed_image(0, BLOC_SIZE, BLOC_SIZE))

    # Monsters
    monstersSprites = []
    for index in range(36, 96):
        monstersSprites.append(ss_levels[currLand].get_indexed_image(index, BLOC_SIZE, BLOC_SIZE))

    # End Screen
    endScreenSprite = ss_endScreens[currLand].get_indexed_image(0, WINDOW_WIDTH, WINDOW_HEIGHT)

def loadLevel():
    global level, currLand, scheme, blocsCount, toxicBlocsLeft, totalToxicBlocs, monsters, cyclonesList
    print("Load level " + str(level))
    currLand = (level-1) % LANDS_NB
    loadSprites()

    schemeName = "Data/Schemes/S" + str(level)
    with open(schemeName, 'rb') as f:
        scheme = f.read()

    # Counts blocs in scheme
    blocsCount = [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 ]
    cyclonesList = [0, 0, 0, 0, 0, 0, 0, 0]
    cyclonesNb = 0

    for i in range(0, len(scheme)):
        blocIndex = scheme[i]
        if blocIndex <= BLOC_GREEN_CHEM:
            blocsCount[blocIndex] += 1

        if blocIndex == BLOC_CYCLONE:
            cyclonesList [cyclonesNb] = i
            print('Cyclone #' + str(cyclonesNb) + ' at index ' + str(i))
            cyclonesNb += 1
            
    toxicBlocsLeft  = blocsCount[BLOC_POISON]  + blocsCount[BLOC_RED]
    toxicBlocsLeft += blocsCount[BLOC_ALU]     + blocsCount[BLOC_BATTERY]
    toxicBlocsLeft += blocsCount[BLOC_DDT]     + blocsCount[BLOC_CFC]
    toxicBlocsLeft += blocsCount[BLOC_URANIUM] + blocsCount[BLOC_GREEN_CHEM]

    print('toxicBlocsLeft: ' + str(toxicBlocsLeft))
    totalToxicBlocs = toxicBlocsLeft

    resetLevel()

    initOccupyTable()

    monsters = []
    for index in range(0, MONSTERS_NB):
        kind = index % 2
        m = Monster(kind)
        m.setRandomPosition()
        monsters.append(m)

def loadRevenge():
    global level, currLand, scheme, blocsCount, monsters, cyclonesList
    print("Load revenge for level " + str(level))
    currLand = (level - 1) // 10
    loadSprites()

    schemeName = "Data/Schemes/CHALLENGES"
    with open(schemeName, 'rb') as f:
        scheme = f.read()

    cyclonesList = [0, 0, 0, 0, 0, 0, 0, 0]

    resetRevenge((level-1) // 5)

    initOccupyTable()

    monsters = []
    for index in range(0, MONSTERS_NB):
        kind = index % 2
        m = Monster(kind)
        m.setRandomPosition()
        monsters.append(m)

# Setup table for monsters
def initOccupyTable():
    global occupyTable

    # Bit 0: for monsters only
    # Bit 1: for penguin and monsters
    occupyTable = []
    for index in range (0, SCHEME_SIZE):
        occ = 0
        if lands[currLand][4*index] == BLOC_TELEPORT_0:    # Monsters cannot go over teleporters
            occ = 1

        occupyTable.append(occ)

def displayScore(score, posX, posY):
    base = 10000
    for i in range(0, 5):
        index = (score // base) % 10
        screen.blit(charsSprites_gr[index + 26], (posX+12*i, posY))
        base //= 10

def getBloc(indexX, indexY):
    blocOffset = indexY * SCHEME_WIDTH + indexX
    if blocOffset >= 0 and blocOffset < SCHEME_SIZE:
        blocOfScheme = scheme[blocOffset]
    else:
        blocOfScheme = BLOC_BASIC

    return blocOfScheme

def isOnBlock(posX, posY):
    return ((posX % BLOC_SIZE) == 0) and ((posY % BLOC_SIZE) == 0)

def destroyBloc(bloc):
    global blocsCount, toxicBlocsLeft, level, gamePhase
    print('Destroy bloc of type ' + str(bloc))
    if (bloc <= BLOC_GREEN_CHEM):
        blocsCount[bloc] -= 1
        if (bloc >= BLOC_POISON):
            toxicBlocsLeft -= 1
            print('toxicBlocsLeft: ' + str(toxicBlocsLeft))
            penguin1.score += 5

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

    if index == 24 and isRevenge == True:
        return BLOC_REVENGE

    return index

def setElectrifyBorder(newStatus):
    global electrifyBorder

    if  newStatus == True and electrifyBorder == False:
        playSFX(soundElec, 100)

    if newStatus == False and electrifyBorder == True:
        soundElec.stop()

    electrifyBorder = newStatus

# Game phases

def startIntroPhase():
    global gamePhase, menuCounter, windowFade, pauseGame, menuCursor, introTimer

    print('PHASE_INTRO')
    gamePhase = PHASE_INTRO
    playMusic(musicIntro, -1)
    windowFade = 0
    introTimer = 0

def startMenuPhase():
    global gamePhase, menuCounter, windowFade, pauseGame, menuCursor, subMenu, currLand

    print('PHASE_MENU')
    gamePhase = PHASE_MENU
    menuCounter = 0
    pauseGame = False
    menuCursor = 0
    subMenu = MENU_MAIN

    # Load sprites for tutos
    currLand = 0
    loadSprites()

def startLevelPhase():
    global gamePhase, windowFade

    print('PHASE_LEVEL')
    gamePhase = PHASE_LEVEL
    loadLevel()
    windowFade = 0

def startResultPhase():
    global gamePhase, windowFade, resultTimer, bonus, toxicBlocsLeft, totalToxicBlocs

    print('PHASE_RESULT')
    gamePhase = PHASE_RESULT
    windowFade = 200
    resultTimer = 0

    # Compute bonus
    percent = ((totalToxicBlocs - toxicBlocsLeft) * 100) // totalToxicBlocs
    bonus = 25 * clamp(percent - SUCCESS_GOAL, 0, 100)

    if percent == 100:                              # Perfect
        bonus += 500 + 5 * int(gameTimer)           # 1 second = 5 points

def startEndLevelPhase():
    global gamePhase, endOfLevelTimer, windowFade, part, rocketOriginX, rocketOriginY

    print('PHASE_END_LEVEL')
    gamePhase = PHASE_END_LEVEL
    endOfLevelTimer = 250
    playMusic(musicEnd)
    windowFade = 0

    # Create rocket particles, if needed in this land
    if currLand == LAND_ESA or currLand == LAND_SPACE:
        rocketOriginX = 70 if currLand == LAND_ESA else 105
        rocketOriginY = 60 if currLand == LAND_ESA else 35
        part = particles.Particles(rocketOriginX + 28, rocketOriginY + 182, 100)

def startRevengeIntroPhase():
    global gamePhase, windowFade, introTimer

    print('PHASE_REVENGE_INTRO')
    gamePhase = PHASE_REVENGE_INTRO
    windowFade = 0
    loadRevenge()
    introTimer = 0

def startRevengeLevelPhase():
    global gamePhase, windowFade

    windowFade = 0
    playMusic(musicRevenge)
    gamePhase = PHASE_LEVEL

def startGameWonPhase():
    global gamePhase, resultTimer, windowFade

    resultTimer = 0
    print('PHASE_GAME_WON')
    gamePhase = PHASE_GAME_WON
    windowFade = 128
    playMusic(musicWinGame)

def startEnterNamePhase():
    global gamePhase, yourName, cursorTx, cursorTy, cursorPx, cursorPy, resultTimer

    print('PHASE_ENTER_NAME')
    gamePhase = PHASE_ENTER_NAME
    yourName = ""
    cursorTx = 0
    cursorTy = 0
    cursorPx = 0    # In pixels
    cursorPy = 0
    resultTimer = 0
    playMusic(musicWin, -1)

# Sound/Music

def playSFX(sfx, loop=0):
    if opt.getValue(OPTIONS_ID[0]) == True:
        sfx.play(loop)

def playMusic(m, loop=0):
    print('playMusic loop=' + str(loop))
    musicChannel = pygame.mixer.Channel(1)
    pygame.mixer.stop()
    musicChannel.play(m, loop)

def applyChannelVolumes():
    musicChannel = pygame.mixer.Channel(1)
    musicChannel.set_volume(1 if opt.getValue(OPTIONS_ID [1]) == True else 0)

# HUD

def displayText(font, str, col, text_x, text_y):            # Centered
    # Shadow
    text = font.render(str, True, (0, 0, 0))
    textRect = text.get_rect()
    textRect.center = (text_x + 1, text_y + 1)
    screen.blit(text, textRect)

    text = font.render(str, True, col)
    textRect = text.get_rect()
    textRect.center = (text_x, text_y)
    screen.blit(text, textRect)

def displayTextLeft(font, str, col, text_x, text_y):        # Left-Aligned
    # Shadow
    text = font.render(str, True, (0, 0, 0))
    textRect = text.get_rect()
    textRect.left = text_x + 1
    textRect.centery = text_y + 1
    screen.blit(text, textRect)

    text = font.render(str, True, col)
    textRect = text.get_rect()
    textRect.left = text_x
    textRect.centery = text_y
    screen.blit(text, textRect)

def displayTextRight(font, str, col, text_x, text_y):        # Right-Aligned
    # Shadow
    text = font.render(str, True, (0, 0, 0))
    textRect = text.get_rect()
    textRect.right = text_x + 1
    textRect.centery = text_y + 1
    screen.blit(text, textRect)

    text = font.render(str, True, col)
    textRect = text.get_rect()
    textRect.right = text_x
    textRect.centery = text_y
    screen.blit(text, textRect)

def displayLegend(legendIdx):
    x = 2 if legendIdx == LEGEND_LEFT else WINDOW_WIDTH-2-20
    screen.blit(legendSprites[legendIdx], (ORIGIN_X + x, ORIGIN_Y + 220))

def displayTuto():
    global tutoCounter, currTutoPage, electrifyBorderAnim, tutoCounter

    TEXT_COLOR = (235, 235, 255)
    TITLE_COLOR = (255, 255, 155)
    BORDER_COLOR = (0, 0, 0)

    CENTER_X = ORIGIN_X + WINDOW_WIDTH//2

    # Title
    displayText(font_big, "TUTORIAL", TITLE_COLOR, CENTER_X, 80)

    if currTutoPage == 0:
        y = 105
        for line in texts.TUTO_INTRO:
            displayText(font, line, TEXT_COLOR, CENTER_X, y)
            y += 10

    # Animate electric border if green arrows are displayed
    if (tutoCounter % 32) >= 4 and ((tutoCounter // 64) % 2 == 1):
        electrifyBorderAnim += 1

    if currTutoPage >= 1:
        blocIndex = currTutoPage-1

        # Bloc Icon
        blocIconIndex = tuto.bloc[blocIndex]
        if blocIconIndex != -1:
            screen.fill(BORDER_COLOR, (CENTER_X - BLOC_SIZE // 2 - 2, 105 - 2, BLOC_SIZE + 4, BLOC_SIZE + 4))
            screen.blit(sprites[0][blocIconIndex], (CENTER_X-BLOC_SIZE//2, 105))
            y = 135
        else:
            y = 115

        for line in texts.TUTO_BLOC[blocIndex]:
            displayText(font, line, TEXT_COLOR, CENTER_X, y)
            y += 10
        displayTutoMap(blocIndex, 82, 150)

    displayLegend(LEGEND_LEFT)
    displayLegend(LEGEND_RIGHT)

    tutoCounter += 1

def displayTutoMap(tutoIndex, offsetX, offsetY):
    global tutoCounter, currLand

    offsetX += ORIGIN_X
    offsetY += ORIGIN_Y

    # Mini-map
    currLand = tutoIndex // 2
    if len(tuto.maps [tutoIndex]) == 16:
        FRAME_SIZE = 1
        sz = 4 * BLOC_SIZE + 2 * FRAME_SIZE
        screen.fill((220, 220, 220), (offsetX - FRAME_SIZE, offsetY - FRAME_SIZE, sz, sz))
        screen.fill((20, 20, 20), (offsetX, offsetY, 4 * BLOC_SIZE, 4 * BLOC_SIZE))
        for y in range(0, 4):
            for x in range(0, 4):
                b = tuto.maps [tutoIndex][x + y * 4]
                if b != -1:
                    b = getAliasBlocIndex(b)
                    screen.blit(sprites[0][b], (offsetX + x * BLOC_SIZE, offsetY + y * BLOC_SIZE))

    # Animated arrows (red or green)
    if (tutoCounter % 32) >= 4:
        arrowType = (tutoCounter // 64) % 2
        d = 4 + ((tutoCounter % 32) / 8)        # Animate arrow
        for arrow in tuto.arrows[tutoIndex][arrowType]:
            dir = arrow [2]
            deltaX = offsetX + d * (1 if dir == 0 else -1 if dir == 1 else 0)
            deltaY = offsetY + d * (1 if dir == 3 else -1 if dir == 2 else 0)
            screen.blit(arrowsSprites[dir+4*arrowType], (deltaX + arrow [0] * BLOC_SIZE, deltaY + arrow [1] * BLOC_SIZE))

def displayOptions():
    global optCursor

    TITLE_COLOR = (255, 255, 155)
    OPT_COLOR = (180, 255, 255)
    VALUE_COLOR = (180, 255, 255)
    HIGHLIGHT_COLOR = (230, 255, 255)

    # Title
    displayText(font_big, "OPTIONS", TITLE_COLOR, ORIGIN_X + WINDOW_WIDTH // 2, 80)

    for i in range(0, len(OPTIONS_ID)):
        y = 120 + 15 * i
        highlight = (optCursor == i)
        col = HIGHLIGHT_COLOR if highlight else OPT_COLOR
        displayTextRight(font, texts.OPTIONS [i], col, ORIGIN_X + WINDOW_WIDTH // 2, y)

        value = opt.getValue(OPTIONS_ID [i])
        textValue = texts.VALUES [0 if value == True else 1]
        col = HIGHLIGHT_COLOR if highlight else VALUE_COLOR
        displayTextLeft(font, textValue, col, ORIGIN_X + WINDOW_WIDTH // 2 + 30, y)

    displayLegend(LEGEND_LEFT)
    displayLegend(LEGEND_RIGHT)

def displayCredits():

    TITLE_COLOR = (255, 255, 155)
    TEXT_COLOR = (180, 255, 255)

    # Title
    displayText(font_big, "CREDITS", TITLE_COLOR, ORIGIN_X + WINDOW_WIDTH // 2, 80)

    y = 120
    for line in texts.CREDITS:
        displayText(font, line, TEXT_COLOR, ORIGIN_X + WINDOW_WIDTH // 2, y)
        y += 15

def displayMainMenu():
    TEXT_COLOR = (155, 155,  55)
    HIGH_COLOR = (255, 255, 155)
    DEACT_COLOR  = (40,   40,  30)
    
    CENTER_X = ORIGIN_X + WINDOW_WIDTH // 2

    for i in range(0, len(texts.MAIN_MENU)):
        deactivated = isMenuDeactivated(i)
        col = DEACT_COLOR if deactivated else (HIGH_COLOR if (menuCursor == i) else TEXT_COLOR)
        displayText(font, texts.MAIN_MENU[i], col, CENTER_X, 120 + 15*i)

def displayGameHud():
    WHITE = (255, 255, 255)
    LEVEL_COLOR = (180, 255, 255)
    COMPLETION_COLOR = (255, 255, 180)
    SUCCESS_COLOR = (50, 255, 140)

    HUD_WIDTH = (320 - 244 - 8)
    HUD_CENTER = 320 - HUD_WIDTH / 2

    y = 110

    # Level
    if not isRevenge:
        displayText(font, "ZONE", LEVEL_COLOR, HUD_CENTER, y)
        y += 12
        displayText(font, f"{level:02d}", LEVEL_COLOR, HUD_CENTER, y)
        y += 30

    # Completion
    if not isRevenge:
        percent = int(100 * (totalToxicBlocs - toxicBlocsLeft) / totalToxicBlocs)
        col = COMPLETION_COLOR if percent < SUCCESS_GOAL else SUCCESS_COLOR
        displayText(font, "GOAL", col, HUD_CENTER, y)
        y += 12
        displayText(font, f"{percent:02d} %", col, HUD_CENTER, y)
        y += 30

    # TIME
    displayText(font, 'TIME', WHITE, HUD_CENTER, y)
    y += 12

    # Time value
    seconds = int(gameTimer % 60)
    timeStr = str(int(gameTimer / 60)) + ":" + f"{seconds:02d}"
    displayText(font, timeStr, WHITE, HUD_CENTER, y)

def displayLeaderboard():

    TITLE_COLOR = (255, 255, 155)
    SCORE_COLOR = (225, 250, 200)
    NAME_COLOR  = (255, 255, 255)
    LEVEL_COLOR = (55, 155, 155)
    LEGEND_COLOR = (50, 240, 200)
    BLACK = (10, 10, 10)

    # Title
    displayText(font_big, "HIGH SCORES", TITLE_COLOR, ORIGIN_X + WINDOW_WIDTH // 2, 80)

    # Legend
    displayTextLeft(font, "SCORE       NAME             ZONE", LEGEND_COLOR, 55, 114)

    for index in range (0, leaderboard.LB_MAX_ENTRIES):
        entry = lb.entries [index]

        y = 130 + 9 * index
        score = entry [0]
        name = entry [1]
        level = entry [2]

        # Score
        displayTextRight(font, str(score), SCORE_COLOR, 90, y)

        # Name
        displayTextLeft(font, name, NAME_COLOR, 110, y)

        # Level
        displayTextRight(font, str(level), LEVEL_COLOR, 206, y)

def displayResult():
    TITLE_COLOR = (50, 240, 200)
    DECONTAMINATED_COLOR = (50, 255, 140)
    TIME_LEFT_COLOR = (200, 200, 240)
    BONUS_COLOR = (40, 200, 240)
    GAMEOVER_COLOR = (255, 200, 230)
    GOOD_COLOR = (0, 255, 0)
    BAD_COLOR = (255, 0, 0)

    # Title
    displayText(font_big, f"END OF ZONE {level}",  TITLE_COLOR, ORIGIN_X + WINDOW_WIDTH // 2, 40)

    if toxicBlocsLeft == 0:
        if ((resultTimer // 8) % 4 != 0):      # Flash FX
            displayText(font_big, "TOTAL", DECONTAMINATED_COLOR, ORIGIN_X + WINDOW_WIDTH // 2, 80)
            displayText(font_big, "DECONTAMINATION!", DECONTAMINATED_COLOR, ORIGIN_X + WINDOW_WIDTH // 2, 130)
    else:
        displayText(font_big, "DECONTAMINATION:", DECONTAMINATED_COLOR, ORIGIN_X + WINDOW_WIDTH // 2, 80)

        percent = (100 * (totalToxicBlocs - toxicBlocsLeft)) // totalToxicBlocs
        percentDisplay = clamp(percent, 0, resultTimer // 2)
        displayText(font_big, f"{percentDisplay} %", BAD_COLOR if percentDisplay < SUCCESS_GOAL else GOOD_COLOR, ORIGIN_X + WINDOW_WIDTH // 2, 130)

        if percent < SUCCESS_GOAL and resultTimer >= 200:
            displayText(font_big, "GAME OVER", GAMEOVER_COLOR, ORIGIN_X + WINDOW_WIDTH // 2, 220)

    # Time left
    timeLeft = int(gameTimer)
    if timeLeft > 0:
        displayText(font_big, f"TIME LEFT: {timeLeft} s", TIME_LEFT_COLOR, ORIGIN_X + WINDOW_WIDTH // 2, 200)

    # Bonus
    displayText(font_big, f"BONUS: {bonus} POINTS", BONUS_COLOR, ORIGIN_X + WINDOW_WIDTH // 2, 180)

    if toxicBlocsLeft == 0:
        displayDancingPenguins()

def displayDancingPenguins():
    # According to d value:
    # 0..100: move right
    # 100..120: still, upfront
    # 120..140: still, left front
    # 140..160: still, upfront
    # 160..   : move right

    d = resultTimer - 50
    px = d if d < 100 else (100 if d < 160 else d-60)
    py = 95
    dir = 0 if (d > 100 and d < 120) or (d > 140 and d < 160) else (-1 if (d > 120 and d < 140) else +1)
    for i in range(0, len(dancingPenguins)):
        p = dancingPenguins [i]
        p.dirX = dir
        p.dirY = 1 if dir == 0 else 0
        p.update([False, dir == 0, dir == -1, dir == 1, False])
        p.posX = px + 20 * i - 10
        p.posY = py
        p.display(screen, 0, 0)

def displayRevengeIntroMode():
    TITLE_COLOR = (105, 255, 255)
    TEXT_COLOR = (50, 255, 140)

    displayText(font_big, texts.REVENGE_TITLE, TITLE_COLOR, ORIGIN_X + WINDOW_WIDTH // 2, 60)

    if (int(absTime) // 4) % 4 != 0:        # Flash
        y = 110
        for line in texts.REVENGE_TEXTS:
            displayText(font, line, TEXT_COLOR, ORIGIN_X + WINDOW_WIDTH // 2, y)
            y += 15

def displayEnterYourName():
    global cursorPx, cursorPy

    TITLE_COLOR = (50, 240, 200)
    LETTER_COLOR = (250, 240, 230)
    HIGHLIGHT_LETTER_COLOR = (255, 255, 0)
    NAME_COLOR = (255, 255, 66)

    displayText(font_big, "CONGRATULATIONS!", TITLE_COLOR, ORIGIN_X + WINDOW_WIDTH // 2, 40)
    displayText(font_big, "ENTER YOUR NAME:", TITLE_COLOR, ORIGIN_X + WINDOW_WIDTH // 2, 60)

    for ty in range (0, ALPHABET_ROWS):
        for tx in range(0, ALPHABET_COLUMNS):
            charIndex = tx + ty * ALPHABET_COLUMNS
            ch = chr(ord('A')+charIndex)

            if ch == '\\':
                ch = '>'        # Exit

            if ch <= 'Z':
                displayText(font_big, ch, LETTER_COLOR, ORIGIN_X + WINDOW_WIDTH // 2 + (tx-3) * 25, 150 + (ty-2) * 24)

    # Display cursor
    targetPx = ORIGIN_X + WINDOW_WIDTH // 2 + (cursorTx - 3) * 25
    targetPy = 150 + (cursorTy - 2) * 24
    if cursorPx == 0 and cursorPy == 0:
        cursorPx = targetPx
        cursorPy = targetPy
    else:
        deltaPx = targetPx - cursorPx
        cursorPx += 5 if deltaPx > 0 else -5 if deltaPx < 0 else 0
        deltaPy = targetPy - cursorPy
        cursorPy += 4 if deltaPy > 0 else -4 if deltaPy < 0 else 0

    displayText(font_big, '_', HIGHLIGHT_LETTER_COLOR, cursorPx, cursorPy + 2)
    displayText(font_big, '_', HIGHLIGHT_LETTER_COLOR, cursorPx, cursorPy - 16)

    displayName = yourName
    if (resultTimer // 8) % 4 != 0:
        if len(yourName) < leaderboard.LB_MAX_NAME_LENGTH:
            displayName += '_'
        else:
            displayName += ' '

    displayTextLeft(font_big, displayName, NAME_COLOR, ORIGIN_X + 40, 220)

def displayGameWon():
    TEXT_COLOR = (80, 250, 230)

    y = 80
    for line in texts.GAME_WON:
        displayText(font_big, line, TEXT_COLOR, ORIGIN_X + WINDOW_WIDTH // 2, y)
        y += 20
        
def applyFade():
    if windowFade > 0:
        blackSurface.fill((0, 0, 0, windowFade))
        screen.blit(blackSurface, (ORIGIN_X, ORIGIN_Y))

def isMenuDeactivated(index):
    return index == MENU_CONTINUE and maxLevelReached == 1

# pygame setup
pygame.init()
pygame.display.set_caption('Poizone')
pygame.mixer.init()  # Initialize the mixer module.
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SCALED)
clock = pygame.time.Clock()
running = True
pauseGame = False

lb = leaderboard.Leaderboard()
lb.load()

opt = options.Options()
opt.load()

# For fade effect
blackSurface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
blackSurface.fill((0, 0, 0, 128))

# Fonts
font = pygame.font.Font('Data/font/small/8-bit-hud.ttf', 5)
font_big = pygame.font.Font('Data/font/big/VCR_OSD_MONO_1.001.ttf', 20)

# Load musics recorded from SoundTracker
musicIntro  = pygame.mixer.Sound('Data/musics/intro.wav')        # Patterns 0-15
musicRevenge= pygame.mixer.Sound('Data/musics/revenge.wav')      # Patterns 16-20
musicWin    = pygame.mixer.Sound('Data/musics/win.wav')          # Patterns 21-26
musicWinGame= pygame.mixer.Sound('Data/musics/winGame.wav')      # Patterns 27-29
musicEnd    = pygame.mixer.Sound('Data/musics/endLand.wav')      # Pattern 29

musicPlay = []
musicPlay.append(pygame.mixer.Sound('Data/musics/play1.wav'))   # Patterns 30-35
musicPlay.append(pygame.mixer.Sound('Data/musics/play2.wav'))   # Patterns 36-44
musicPlay.append(pygame.mixer.Sound('Data/musics/play3.wav'))   # Patterns 45-50
musicPlay.append(pygame.mixer.Sound('Data/musics/play4.wav'))   # Patterns 51-56
musicPlay.append(pygame.mixer.Sound('Data/musics/play5.wav'))   # Patterns 57-62

# Load sounds recorded from SoundTracker: samples indexes from 23 to 35
soundReady  = pygame.mixer.Sound('Data/bruitages/READY.wav')             # 23 (sample N) - START OF LEVEL
soundLaunch = pygame.mixer.Sound('Data/bruitages/LAUNCHBLCK.wav')        # 24 (sample O)
soundCrash  = pygame.mixer.Sound('Data/bruitages/CRASHblock.wav')        # 25 (sample P)
soundBoom   = pygame.mixer.Sound('Data/bruitages/BOOM.wav')              # 26 (sample Q) - bomb
soundElec   = pygame.mixer.Sound('Data/bruitages/ELECTRIC.wav')          # 27 (sample R) - border
soundMagic  = pygame.mixer.Sound('Data/bruitages/MAGIC.wav')             # 28 (sample S)
soundDiam   = pygame.mixer.Sound('Data/bruitages/DIAMOND.wav')           # 29 (sample T) - when 4 diamonds assembled
# soundFun   = pygame.mixer.Sound('Data/bruitages/Fun.wav')               # 30 (sample U) - laugh (not used)
soundOhNo   = pygame.mixer.Sound('Data/bruitages/OH_NO.wav')             # 31 (sample V) - wrong move / death
soundAlcool = pygame.mixer.Sound('Data/bruitages/BEER_BLOCK.wav')        # 32 (sample W)
soundColl   = pygame.mixer.Sound('Data/bruitages/COLLISION.wav')         # 33 (sample X) - penguin or monster death
soundSplatch= pygame.mixer.Sound('Data/bruitages/SPLATCH.wav')           # 34 (sample Y) - green glass breaking
soundWow    = pygame.mixer.Sound('Data/bruitages/WOW.wav')               # 35 (sample Z) - END OF LEVEL
soundTick   = pygame.mixer.Sound('Data/bruitages/TICK.wav')              # New sample (same as R but with higher pitch)
soundValid  = pygame.mixer.Sound('Data/bruitages/VALIDATE.wav')          # New sample for menus
soundTele   = pygame.mixer.Sound('Data/bruitages/TELEPORT.wav')          # New sample (same as S but with lower ptich)

# Set volumes

soundCrash.set_volume(0.5)
soundLaunch.set_volume(0.3)
soundMagic.set_volume(0.2)
soundSplatch.set_volume(0.5)
soundTick.set_volume(0.7)
soundValid.set_volume(0.3)
soundTele.set_volume(0.5)

applyChannelVolumes()

# Load Lands and extract teleporters positions.

lands = []
teleporters = []

for index in range(0, LANDS_NB):
    landsName = "Data/Lands/L" + str(index) + "_SET"
    with open(landsName, 'rb') as f:
        land = f.read()
    lands.append(land)
    teleporters.append([])
    print('Teleporters in land #' + str(index) + ':')
    for i in range(0, len(land), 4):
        if land[i] >= BLOC_TELEPORT_0:
            j=i // 4
            teleporters[index].append(j)
            print('  ' + str(j%64) + ',' + str(j // SCHEME_WIDTH))

# SpriteSheets

ss_shared = []
ss_shared.append(spritesheet.SpriteSheet('Data/sharedBlocs0.png'))
ss_shared.append(spritesheet.SpriteSheet('Data/sharedBlocs1.png'))
ss_shared.append(spritesheet.SpriteSheet('Data/sharedBlocs2.png'))
ss_shared.append(spritesheet.SpriteSheet('Data/sharedBlocs3.png'))

ss_start    = spritesheet.SpriteSheet('Data/startScreen.png')
ss_border   = spritesheet.SpriteSheet('Data/border.png')
ss_rocket   = spritesheet.SpriteSheet('Data/rocket.png')
ss_penguins = spritesheet.SpriteSheet('Data/pengos.png')
ss_chars_gr = spritesheet.SpriteSheet('Data/chars_green.png')
ss_revenge  = spritesheet.SpriteSheet('Data/revengeTile.png')
ss_panels   = spritesheet.SpriteSheet('Data/panels.png')
ss_arrows   = spritesheet.SpriteSheet('Data/arrows.png')    # 4 red and 4 green arrows
ss_legend   = spritesheet.SpriteSheet('Data/legend.png')

ss_levels = []
ss_endScreens = []
for index in range(1, 1+LANDS_NB):
    ss_levels.append(spritesheet.SpriteSheet('Data/level' + str(index) + '.png'))
    ss_endScreens.append(spritesheet.SpriteSheet('Data/Screens/scr' + str(index) + '.png'))

# Other assets
startScreen = ss_start.get_indexed_image(0, 244, 240)
border = ss_border.get_indexed_image(0, 320, 256)
rocket = ss_rocket.get_indexed_image(0, 40, 174)

penguin1 = Penguin()

# Three dancing penguins, for result screen
dancingPenguins = []
dancingPenguins.append(Penguin())
dancingPenguins.append(Penguin())
dancingPenguins.append(Penguin())
dancingPenguins[1].animPhase += 8

penguinSprites = []
for index in range(0, 2*36+12):
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

# Variables
absTime = 0
tutoCounter = 0
currTutoPage = 0
maxLevelReached = 1     # For CONTINUE option

#             Up     Down   Left   Right  Space  Backsp Return Escape Pause
keyDown    = [False, False, False, False, False, False, False, False, False]
keyPressed = [False, False, False, False, False, False, False, False, False]

old_x_axis = 0.0
old_y_axis = 0.0
try:
    joy = pygame.joystick.Joystick(0)
    joy.init()
    print('JOY ' + joy.get_name())
    joyFound = 0
except pygame.error:
    print('JOY not found')
    joyFound = -1

startIntroPhase()

while running:

    # Time
    dt = clock.get_time()
    absTime += dt

    if gamePhase == PHASE_LEVEL and not pauseGame:
        prevGameTimer = gameTimer
        gameTimer -= dt / 1000
        if gameTimer < 0.0:
            gameTimer = 0.0

        for tick in range(1, 6):
            if (prevGameTimer >= tick and gameTimer <= tick):
                playSFX(soundTick)

    # INPUT
    #######

    oldKeyDown = keyDown.copy()

    if joyFound != -1:
        # Test joystick stick
        x_axis = joy.get_axis(0)
        y_axis = joy.get_axis(1)

        # X

        if x_axis > JOY_LIMIT:
            keyDown[KEY_RIGHT] = True

        if x_axis < -JOY_LIMIT:
            keyDown[KEY_LEFT] = True

        if x_axis < JOY_LIMIT and old_x_axis >= JOY_LIMIT:
            keyDown[KEY_RIGHT] = False

        if x_axis > -JOY_LIMIT and old_x_axis <= -JOY_LIMIT:
            keyDown[KEY_LEFT] = False

        # Y

        if y_axis > JOY_LIMIT:
            keyDown[KEY_DOWN] = True

        if y_axis < -JOY_LIMIT:
            keyDown[KEY_UP] = True

        if y_axis < JOY_LIMIT and old_y_axis >= JOY_LIMIT:
            keyDown[KEY_DOWN] = False

        if y_axis > -JOY_LIMIT and old_y_axis <= -JOY_LIMIT:
            keyDown[KEY_UP] = False

        old_x_axis = x_axis
        old_y_axis = y_axis

    # Poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.JOYBUTTONDOWN or event.type == pygame.JOYBUTTONUP:
            buttonIsDown = (event.type == pygame.JOYBUTTONDOWN)
            # Map joy buttons to virtual keys
            if event.button == 0:
                keyDown[KEY_SPACE] = buttonIsDown
            if event.button == 1:
                keyDown[KEY_ESCAPE] = buttonIsDown
            elif event.button == 6:
                keyDown[KEY_ESCAPE] = buttonIsDown
            elif event.button == 7:
                keyDown[KEY_PAUSE] = buttonIsDown
            else:
                print('Unhandled JOY button ' + str(event.button))

        if event.type == pygame.KEYUP or event.type == pygame.KEYDOWN:
            down = (event.type == pygame.KEYDOWN)
            if event.key == pygame.K_LEFT:
                keyDown[KEY_LEFT] = down

            if event.key == pygame.K_RIGHT:
                keyDown[KEY_RIGHT] = down

            if event.key == pygame.K_UP:
                keyDown[KEY_UP] = down

            if event.key == pygame.K_DOWN:
                keyDown[KEY_DOWN] = down

            if event.key == pygame.K_SPACE:
                keyDown[KEY_SPACE] = down

            if event.key == pygame.K_BACKSPACE:
                keyDown[KEY_BACKSPACE] = down

            if event.key == pygame.K_RETURN:
                keyDown[KEY_RETURN] = down

            if event.key == pygame.K_ESCAPE:
                keyDown[KEY_ESCAPE] = down

            if event.key == pygame.K_F12:
                keyDown[KEY_PAUSE] = down

            if not down:

                if event.key == pygame.K_F5:    # Prev level
                    if (level > 1):
                        level -= 1
                        loadLevel()

                if event.key == pygame.K_F6:    # Next level
                    if (level < 50):
                        level += 1
                        loadLevel()

                if event.key == pygame.K_F7:  # Prev revenge map
                    if (level > 5):
                        level -= 5
                        startRevengeIntroPhase()

                if event.key == pygame.K_F8:  # Next revenge map
                    if (level < 45):
                        level += 5
                        startRevengeIntroPhase()

    for i in range(0, len(keyDown)):
        keyPressed [i] = (keyDown[i] == True and oldKeyDown[i] == False)

    if keyPressed[KEY_PAUSE]:  # Pause game
        if gamePhase == PHASE_LEVEL:
            pauseGame = not pauseGame

    if keyPressed[KEY_ESCAPE] == True:
        if gamePhase == PHASE_LEVEL:
            startIntroPhase()
        elif gamePhase == PHASE_INTRO:
            running = False
        elif gamePhase == PHASE_MENU:
            if subMenu == MENU_MAIN:
                running = False  # Quit game
            else:
                subMenu = MENU_MAIN        # Return to Main Menu
                playSFX(soundValid)

    if gamePhase == PHASE_INTRO:
        introTimer += 1
        if keyPressed[KEY_SPACE] or keyPressed[KEY_RETURN]:
            startMenuPhase()
            playSFX(soundValid)
    elif gamePhase == PHASE_MENU:
        menuCounter += 1
        if windowFade < 160:
            windowFade += 16

        # Main Menu navigation
        if subMenu == MENU_MAIN:
            if keyPressed[KEY_DOWN] and menuCursor < 5:
                menuCursor += 1
                while isMenuDeactivated(menuCursor):
                    menuCursor += 1
                playSFX(soundValid)

            if keyPressed[KEY_UP] and menuCursor > 0:
                menuCursor -= 1
                while isMenuDeactivated(menuCursor):
                    menuCursor -= 1
                playSFX(soundValid)

            if keyPressed[KEY_SPACE] or keyPressed[KEY_RETURN]:
                if menuCursor == MENU_PLAY or menuCursor == MENU_CONTINUE:
                    resetGame()

                    if menuCursor == MENU_CONTINUE:
                        level = maxLevelReached

                    startLevelPhase()
                else:
                    subMenu = menuCursor

                    if subMenu == MENU_OPTIONS:
                        optCursor = 0
                    if subMenu == MENU_TUTORIAL:
                        tutoCounter = 0
                        currTutoPage = 0

                    playSFX(soundValid)

        elif subMenu == MENU_TUTORIAL:
            if keyPressed[KEY_LEFT]:
                currTutoPage = (currTutoPage + TUTO_PAGES - 1) % TUTO_PAGES
                tutoCounter = 0
                playSFX(soundValid)

            if keyPressed[KEY_RIGHT]:
                currTutoPage = (currTutoPage + 1) % TUTO_PAGES
                tutoCounter = 0
                playSFX(soundValid)

        elif subMenu == MENU_OPTIONS:
            if keyPressed[KEY_DOWN] and optCursor < 1:
                optCursor += 1
                playSFX(soundValid)

            if keyPressed[KEY_UP] and optCursor > 0:
                optCursor -= 1
                playSFX(soundValid)

            if keyPressed[KEY_SPACE] or keyPressed[KEY_RETURN] or keyPressed[KEY_LEFT] or keyPressed[KEY_RIGHT]:
                opt.setValue(OPTIONS_ID[optCursor], not opt.getValue(OPTIONS_ID[optCursor]))     # Invert value
                opt.save()
                applyChannelVolumes()
                playSFX(soundValid)

    elif gamePhase == PHASE_LEVEL and not pauseGame:
        # Animate electric border
        if electrifyBorder == True:
            electrifyBorderAnim += 1

        # Animate cyclones
        cyclonesPace = (cyclonesPace + 1) % 16

        if cyclonesPace % 2 == 0:      # To slow down process, process once every two passes
            cycloneIndex = cyclonesList [cyclonesPace >> 1]
            if cycloneIndex != 0:
                print('Process cyclone #' + str(cycloneIndex))
                # Collect blocs around cyclone
                turningBlocs = []

                for offset in CYCLONE_OFFSETS:
                    finalOffset = cycloneIndex + offset[0] + offset[1] * SCHEME_WIDTH
                    turningBloc = scheme[finalOffset]

                    if turningBloc < 24 and turningBloc != BLOC_ELECTRO:
                        turningBlocs.append(turningBloc)

                # Rotate turning blocs (clockwise)
                if (len(turningBlocs) > 1):
                    turningBlocs = turningBlocs[len(turningBlocs)-1:len(turningBlocs)] + turningBlocs[:len(turningBlocs)-1]

                i = 0
                for offset in CYCLONE_OFFSETS:
                    finalOffset = cycloneIndex + offset[0] + offset[1] * SCHEME_WIDTH
                    turningBloc = scheme[finalOffset]

                    if turningBloc < 24 and turningBloc != BLOC_ELECTRO:
                        blocX = finalOffset % SCHEME_WIDTH
                        blocY = int (finalOffset / SCHEME_WIDTH)
                        writeBloc(blocX, blocY, turningBlocs [i])
                        i += 1

        # Update Penguin
        penguin1.update(keyDown)

        # Update Monsters
        for m in monsters:
            m.update()

        # Check end of game
        if (gameTimer <= 0.0) or ((toxicBlocsLeft == 0) and not isRevenge):
            
            if isRevenge == True:
                if level >= 50:             # End of game reached!
                    startGameWonPhase()
                else:
                    gamePhase = PHASE_LEVEL  # Move to next level
                    level += 1  # End of level - display results
                    loadLevel()
            else:
                if (toxicBlocsLeft == 0):
                    playSFX(soundWow)

                startResultPhase()

    elif gamePhase == PHASE_RESULT:
        resultTimer += 1
        if resultTimer > 60*8:
            percent = (100 * toxicBlocsLeft / totalToxicBlocs)
            gameOver = (percent >= (100-SUCCESS_GOAL))
            penguin1.score += bonus         # Take bonus into account

            print(f"percent: {percent} gameOver : {gameOver}")

            if gameOver == True:
                if lb.canEnter(penguin1.score):
                    startEnterNamePhase()
                else:
                    startMenuPhase()
                    playMusic(musicIntro, -1)

                # Store level for Continue
                maxLevelReached = max(level, maxLevelReached)

            else:
                startEndLevelPhase()

    elif gamePhase == PHASE_REVENGE_INTRO:

        if windowFade < 128:
            windowFade += 16

        introTimer += 1

        if keyPressed[KEY_SPACE] or (introTimer > 60*4):
            startRevengeLevelPhase()

    elif gamePhase == PHASE_GAME_WON:
        resultTimer += 1
        if resultTimer > 60*21:     # Match music duration
            startMenuPhase()
            playMusic(musicIntro, -1)

    elif gamePhase == PHASE_ENTER_NAME:
        resultTimer += 1
        quitEnterName = False

        if keyPressed[KEY_LEFT]:
            cursorTx = (cursorTx + ALPHABET_COLUMNS - 1) % ALPHABET_COLUMNS
        if keyPressed[KEY_RIGHT]:
            cursorTx = (cursorTx + 1) % ALPHABET_COLUMNS
        if keyPressed[KEY_UP]:
            cursorTy = (cursorTy + ALPHABET_ROWS - 1) % ALPHABET_ROWS
        if keyPressed[KEY_DOWN]:
            cursorTy = (cursorTy + 1) % ALPHABET_ROWS
        if keyPressed[KEY_SPACE]:
            ch = chr(ord('A') + cursorTx + cursorTy * ALPHABET_COLUMNS)
            if ch == '\\' and len(yourName) > 0:
                quitEnterName = True
            elif (len(yourName) < leaderboard.LB_MAX_NAME_LENGTH):
                if (ch <= 'Z'):
                    yourName += ch
                else:
                    yourName += ' '
                playSFX(soundValid)

        if keyPressed[KEY_BACKSPACE]:
            if len(yourName) > 0:
                yourName = yourName[:-1]
                playSFX(soundValid)

        if keyPressed[KEY_RETURN] or quitEnterName == True:
            lb.add(penguin1.score, yourName, level)
            lb.save()  # Add new entry and save leaderboard
            startMenuPhase()

    ######
    # DRAW
    ######

    # Fill the screen with a color to wipe away anything from last frame
    screen.fill("black")
    screen.blit(border, (0, 0))

    if gamePhase == PHASE_INTRO:
        screen.blit(startScreen, (ORIGIN_X, ORIGIN_Y))

        if ((introTimer // 16) % 4 != 0):
            displayText(font, "Press START", (215, 235, 125), ORIGIN_X + WINDOW_WIDTH // 2, 230)

    elif gamePhase == PHASE_MENU:
        screen.blit(startScreen, (ORIGIN_X, ORIGIN_Y))
        
        # Fade
        applyFade()

        if subMenu == MENU_MAIN:
            displayMainMenu()
        elif subMenu == MENU_HIGHSCORES:
            displayLeaderboard()
        elif subMenu == MENU_TUTORIAL:
            displayTuto()
        elif subMenu == MENU_OPTIONS:
            displayOptions()
        elif subMenu == MENU_CREDITS:
            displayCredits()

    elif gamePhase == PHASE_END_LEVEL:
        screen.blit(endScreenSprite, (ORIGIN_X, ORIGIN_Y))
        if endOfLevelTimer > 0:
            endOfLevelTimer -= 1

            # Penguin and 3 Monsters animation
            yByLand = [190, 210, 190, 135, 138]
            dirByLand = [-1, -1, -1, -1, +1]
            limitMinXByLand = [145, 140, 160, 140, -20]
            limitMaxXByLand = [500, 500, 500, 500, 70]
            monstersNb = 2 if currLand == LAND_COMPUTER else 3
            
            x = 20 + endOfLevelTimer if currLand != LAND_COMPUTER else 250 - endOfLevelTimer
            y = yByLand [currLand]
            dir = dirByLand [currLand]
            limitMinX = limitMinXByLand [currLand]
            limitMaxX = limitMaxXByLand [currLand]
            baseX = 0
            baseY = 0
            mx = clamp(x, limitMinX, limitMaxX)

            # Show Penguin
            if (currLand == LAND_ICE or currLand == LAND_JUNGLE or currLand == LAND_COMPUTER):

                if currLand == LAND_COMPUTER:
                    px = x + 60         # Penguin on the right side of monsters
                    py = y

                    if px >= 90:       # Jump parabola
                        dy = math.pow(px-90, 2) / 15
                        py += clamp(dy, 0, 50)
                else:
                    px = x - 40         # Penguin on the left side of monsters
                    py = y

                if currLand == LAND_ICE:
                    if px >= 120 and px <= 150:     # Jump parabola
                        py -= (15*15 - math.pow(px-135, 2)) / 15

                penguin1.posX = px
                penguin1.posY = py

                penguin1.dirX = dir
                penguin1.dirY = 0
                penguin1.update([False, False, dir == -1, dir == 1, False])
                penguin1.display(screen, 0, 0)

            # Show monsters
            for index in range(0, monstersNb):
                monsters[index].posX = mx + 25 * index
                monsters[index].posY = y
                monsters[index].dirX = dir
                monsters[index].dirY = 0
                monsters[index].counter = 1000-endOfLevelTimer + 16 * index
                monsters[index].display(screen, 0, 0)

            # Show Rocket
            if currLand == LAND_ESA or currLand == LAND_SPACE:
                propelY = pow(250-endOfLevelTimer, 2) / 250
                c = CropSprite(rocketOriginX, rocketOriginY - propelY, rocket.get_width(), rocket.get_height())
                screen.blit(rocket, (ORIGIN_X + c.posX, ORIGIN_Y + c.posY), c.getCroppedRegion())
                part.originY = ORIGIN_Y + c.posY + c.heightRegion
                part.update(1./60.)     # TODO: should be dt
                part.display(screen, ORIGIN_X, ORIGIN_Y, WINDOW_WIDTH, WINDOW_HEIGHT)

            # For COMPUTER level: redraw a part of the disk drive, over monsters
            if currLand == LAND_COMPUTER:
                screen.blit(endScreenSprite, (ORIGIN_X, ORIGIN_Y+138), (0, 138, 17*4, 20))

        else:
            if level % 5 == 0:
                startRevengeIntroPhase()
            else:
                level += 1
                startLevelPhase()
    else: # PHASE_LEVEL or PHASE_RESULT or PHASE_REVENGE_INTRO
        # Draw BG

        anim = absTime // 4
        for y in range(0, BLOCS_RANGE + 1):
            for x in range(0, BLOCS_RANGE + 1):

                blocOffset = (baseY // BLOC_SIZE + y) * SCHEME_WIDTH + (baseX // BLOC_SIZE + x)

                if isRevenge == True:
                    index = 24      # Empty land in Revenge mode
                else:
                    index = int(lands[currLand][4 * blocOffset + (anim % 4)])

                if blocOffset < SCHEME_SIZE:
                    blocOfSchemes = scheme[blocOffset]
                    if blocOfSchemes < 24:
                        index = blocOfSchemes

                posX = x * BLOC_SIZE - (baseX % BLOC_SIZE)
                posY = y * BLOC_SIZE - (baseY % BLOC_SIZE)

                c = CropSprite(posX, posY)

                index = getAliasBlocIndex(index)
                screen.blit(sprites[0][index], (ORIGIN_X + c.posX, ORIGIN_Y + c.posY), c.getCroppedRegion())

        # Display Penguin
        penguin1.display(screen, baseX, baseY)

        # Display Monsters
        for m in monsters:
            m.display(screen, baseX, baseY)

        # Display moving bloc and bonus, if any
        penguin1.displayBloc(screen, baseX, baseY)

        applyFade()
        
        if gamePhase == PHASE_RESULT:
            # Display result over game
            displayResult()
        elif gamePhase == PHASE_REVENGE_INTRO:
            displayRevengeIntroMode()
        elif gamePhase == PHASE_GAME_WON:
            displayGameWon()
        elif gamePhase == PHASE_ENTER_NAME:
            displayEnterYourName()

        # Display HUD
        displayGameHud()

    # Display Scores
    displayScore(penguin1.score, 256, 45)
    # displayScore(0, 256, 188)   # No 2nd player supported, for now

    # Display panel (PAUSE or DEMO)

    panelIdx = -1

    if pauseGame == True:
        panelIdx = 1

    if panelIdx != -1:
        screen.blit(panelSprites[panelIdx], (8 + 244/2 - 60/2, 40))

    # flip() the display to put your work on screen
    pygame.display.flip()

    clock.tick(60)  # limits FPS to 60

pygame.quit()