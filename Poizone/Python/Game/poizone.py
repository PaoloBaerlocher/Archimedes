# POIZONE re-written in Python 3.11, july 2023 (32 years later after the original).
# 2-player mode is not supported.

import pygame
import numpy
import math
import random
import spritesheet
from enum import Enum

# Constants
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

# GAME PHASES
PHASE_INTRO     = 0
PHASE_GAME      = 1
PHASE_END_LEVEL = 2

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
BLOC_CYCLONE     = 14
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
BLOC_CHALLENGE   = 62

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
            self.setStatus(PenguinStatus.PUSH)
            if bloc == BLOC_ELECTRO:
                setElectrifyBorder(True)
            elif bloc < 24:
                nextBloc = self.getBloc(self.dirX * 2, self.dirY * 2)
                if (nextBloc >= 24):
                    self.launchBloc(bloc, self.posX, self.posY, self.dirX, self.dirY)
                    blocX = int(self.posX / BLOC_SIZE) + self.dirX
                    blocY = int(self.posY / BLOC_SIZE) + self.dirY
                    writeBloc(blocX, blocY, 26)         # Remove bloc from initial position
                    if bloc == BLOC_CYCLONE:
                        idx = cyclonesList.index(blocX + blocY * SCHEME_WIDTH)
                        print('Remove cyclone ' + str(cyclonesList[idx]) + ' from list at index ' + str(idx))
                        cyclonesList[idx] = 0

                    soundLaunch.play()

                    if bloc == BLOC_RED:        # Do NOT launch red chemical block!
                        soundOhNo.play()
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

        blocUp    = self.getBloc(self.dirX, self.dirY - 1)
        blocDown  = self.getBloc(self.dirX, self.dirY + 1)
        blocLeft  = self.getBloc(self.dirX - 1, self.dirY)
        blocRight = self.getBloc(self.dirX + 1, self.dirY)

        if bloc == BLOC_ALCOOL:
            self.invert = not self.invert
            soundAlcool.play()

        if bloc == BLOC_BOMB:
            self.die()
            soundBoom.play()

        if bloc == BLOC_MAGIC:  # Temporary invincibility
            self.ghost = 60 * 15
            soundMagic.play()

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

        if bloc == BLOC_RADIO:  # Are other RADIOACTIVE blocs nearby ?
            if (blocUp == BLOC_RADIO or blocDown == BLOC_RADIO or blocLeft == BLOC_RADIO or blocRight == BLOC_RADIO):
                self.die()

        if bloc == BLOC_GREEN_CHEM:
            self.die()

        blocX = int(self.posX / BLOC_SIZE) + self.dirX
        blocY = int(self.posY / BLOC_SIZE) + self.dirY

        if bloc == BLOC_BOMB:
            self.startBombAnim(self.posX + self.dirX * BLOC_SIZE, self.posY + self.dirY * BLOC_SIZE)
        else:
            self.startCrushAnim(bloc, self.posX + self.dirX * BLOC_SIZE, self.posY + self.dirY * BLOC_SIZE)

        writeBloc(blocX, blocY, 26)
        destroyBloc(bloc)

        soundCrash.play()

    def die(self):

        self.animPhase = 0
        self.setStatus(PenguinStatus.DIE)
        soundColl.play()
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
        if int(self.ghost / 8) % 4 <= 2:
            screen.blit(penguinSprites[self.anim], (ORIGIN_X+self.posX-baseX, ORIGIN_Y+self.posY-baseY))

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

    def update(self, keyPressed):
        global monsters, teleporters, scheme, baseX, baseY

        penguinMove = keyPressed[KEY_LEFT] or keyPressed[KEY_RIGHT] or keyPressed[KEY_UP] or keyPressed[KEY_DOWN]

        if penguinMove:
            self.canTeleport = True

        if keyPressed[KEY_SPACE] and penguinMove and isOnBlock(self.posX, self.posY) and self.status != PenguinStatus.DIE:
            self.pushBloc()

        if isOnBlock(self.posX, self.posY) and self.status != PenguinStatus.PUSH and self.status != PenguinStatus.DIE:
            if keyPressed[KEY_LEFT]:
                self.dirX = -1 if self.invert == False else +1
                self.dirY = 0
                if not blocIsWalkable(self, self.dirX, self.dirY):
                    self.setStatus(PenguinStatus.IDLE)

            if keyPressed[KEY_RIGHT]:
                self.dirX = 1 if self.invert == False else -1
                self.dirY = 0
                if not blocIsWalkable(self, self.dirX, self.dirY):
                    self.setStatus(PenguinStatus.IDLE)

            if keyPressed[KEY_UP]:
                self.dirX = 0
                self.dirY = -1 if self.invert == False else +1
                if not blocIsWalkable(self, self.dirX, self.dirY):
                    self.setStatus(PenguinStatus.IDLE)

            if keyPressed[KEY_DOWN]:
                self.dirX = 0
                self.dirY = 1 if self.invert == False else -1
                if not blocIsWalkable(self, self.dirX, self.dirY):
                    self.setStatus(PenguinStatus.IDLE)

        if (self.status == PenguinStatus.PUSH) and ((penguinMove == False) or not keyPressed[KEY_SPACE]):
            self.setStatus(PenguinStatus.IDLE)
            setElectrifyBorder(False)

        if (self.status == PenguinStatus.IDLE) and (self.dirX != 0 or self.dirY != 0) and (
                penguinMove == True):
            if blocIsWalkable(self, self.dirX, self.dirY):
                self.setStatus(PenguinStatus.WALK)

        if (self.status == PenguinStatus.WALK):
            self.posX += self.dirX * PENG_WALK_STEP
            self.posY += self.dirY * PENG_WALK_STEP
            if isOnBlock(self.posX, self.posY):  # Stop walking at next block
                if penguinMove == False:
                    self.setStatus(PenguinStatus.IDLE)
                elif blocIsWalkable(self, self.dirX, self.dirY) == False:
                    self.setStatus(PenguinStatus.IDLE)

        if (self.status == PenguinStatus.DIE) and (self.animPhase > 128):  # Re-birth
            self.setStatus(PenguinStatus.IDLE)
            self.animPhase = 0
            self.ghost = 60

        self.anim = self.getPenguinAnimOffset()
        self.animPhase += 1

        # Move camera to follow penguin, and clamp its position

        if not itsChallenge:
            offsetX = penguin1.posX + 8 - baseX - int((BLOCS_RANGE * BLOC_SIZE) / 2)
            if (offsetX < 0):
                baseX -= 4
            elif offsetX > 0:
                baseX += 4

            offsetY = penguin1.posY + 8 - baseY - int((BLOCS_RANGE * BLOC_SIZE) / 2)
            if (offsetY < 0):
                baseY -= 4
            elif offsetY > 0:
                baseY += 4

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

        # Update crushed bloc

        if self.crushBlocWhat != NONE:

            self.crushBlocTimer -= 1
            if self.crushBlocTimer == 0:
                self.crushBlocWhat = NONE

        # Update bomb anim

        if self.bombTimer > 0:
            self.bombTimer -= 1

        # Update moving bloc

        if self.movBlocWhat != NONE:

            if (self.movBlocPosX % BLOC_SIZE == 0) and (self.movBlocPosY % BLOC_SIZE == 0):
                bx = int(self.movBlocPosX / BLOC_SIZE)
                by = int(self.movBlocPosY / BLOC_SIZE)
                nextBloc = getBloc(bx + self.movBlocDirX, by + self.movBlocDirY)
                if nextBloc < 24:
                    print('End of bloc travel. Killed ' + str(self.movMonsters) + ' monsters.')

                    killBloc = (self.movBlocWhat == BLOC_GREEN_CHEM)
                    if self.movBlocWhat == BLOC_ALU and nextBloc == BLOC_ELECTRO:
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
                                self.score += 500
                    else:
                        destroyBloc(self.movBlocWhat)
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

        global itsChallenge

        self.dirX = 0
        self.dirY = 0

        self.counter = -32 - random.randrange(self.getBirthRange())

        self.dizzyCounter = 0
        self.setRandomPosition()

    def getBirthRange(self):
        global itsChallenge
        return 300 if itsChallenge == True else 2200

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
                    self.dizzyCounter = 90
                    print('Electrify monster')

            if self.isAlive() and (penguin1.movBlocWhat != NONE):
                deltaX = abs(penguin1.movBlocPosX - self.posX)
                deltaY = abs(penguin1.movBlocPosY - self.posY)
                if (deltaX <= 8) and (deltaY <= 8):
                    print('Kill monster')
                    self.killAndRebirth()
                    soundSplat.play()
                    penguin1.movMonsters += 1
                elif (deltaX <= 12) and (deltaY <= 12):
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

                    if occupyTable[blocIndex] == True:      # Forbidden destination bloc
                        continue

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
        global penguin1, scheme, itsChallenge, occupyTable

        while True:

            if itsChallenge == False:
                x = 3 + random.randrange(0, 48-2*3)
                y = 3 + random.randrange(0, 48-2*3)
            else:
                x = int(baseX / BLOC_SIZE) + 1 + random.randrange(0, 10)
                y = int(baseY / BLOC_SIZE) + 1 + random.randrange(0, 10)
            print(f"New monster at {x},{y}")

            if (occupyTable[x + y * SCHEME_WIDTH] == True):      # Already occupied
                continue

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
cyclonesPace        = 0             # For cyclones
cyclonesList        = []

itsChallenge        = False         # Challenge ?

# Functions

def resetGame():
    global level

    level = 1

def resetLevel():
    global baseX, baseY, penguin1, itsChallenge

    baseX = 18 * BLOC_SIZE
    baseY = 18 * BLOC_SIZE
    penguin1.reset()
    setElectrifyBorder(False)

    itsChallenge = False  # Challenge ?

def resetChallenge(challenge):
    global baseX, baseY, penguin1, itsChallenge

    itsChallenge = True

    px = challenge % 4
    py = int(challenge / 4)

    baseX = (12 * px) * BLOC_SIZE
    baseY = (1 + 12 * py) * BLOC_SIZE
    penguin1.reset()

    # Overrides for challenge
    penguin1.posX = baseX + 6 * BLOC_SIZE  # Center of challenge map
    penguin1.posY = baseY + 6 * BLOC_SIZE

    penguin1.ghost = 10000  # Permanent ghost in Challenge mode

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

        # 62: specific bloc for Challenge
        s.append(ss_challenge.get_indexed_image(0, BLOC_SIZE, BLOC_SIZE))

    # Monsters
    monstersSprites = []
    for index in range(36, 96):
        monstersSprites.append(ss_levels[currLand].get_indexed_image(index, BLOC_SIZE, BLOC_SIZE))

    # End Screen
    endScreenSprite = ss_endScreens[currLand].get_indexed_image(0, 244, 240)

def loadLevel():
    global level, currLand, scheme, blocsCount, countToxicBlocs, monsters, cyclonesList
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
            
    countToxicBlocs  = blocsCount[BLOC_POISON]+blocsCount[BLOC_RED]
    countToxicBlocs += blocsCount[BLOC_ALU]   +blocsCount[BLOC_BATTERY]
    countToxicBlocs += blocsCount[BLOC_DDT]   +blocsCount[BLOC_CFC]
    countToxicBlocs += blocsCount[BLOC_RADIO] +blocsCount[BLOC_GREEN_CHEM]

    print('countToxicBlocs: ' + str(countToxicBlocs))

    resetLevel()

    initOccupyTable()

    monsters = []
    for index in range(0, MONSTERS_NB):
        kind = index % 2
        m = Monster(kind)
        m.setRandomPosition()
        monsters.append(m)


def loadChallenge():
    global level, currLand, scheme, blocsCount, countToxicBlocs, monsters, cyclonesList
    print("Load challenge for level " + str(level))
    currLand = int((level - 1) / 10)
    loadSprites()

    schemeName = "Data/Schemes/CHALLENGES"
    with open(schemeName, 'rb') as f:
        scheme = f.read()

    cyclonesList = [0, 0, 0, 0, 0, 0, 0, 0]
    countToxicBlocs = 0

    resetChallenge(int((level-1) / 5))

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

    occupyTable = []
    for index in range (0, SCHEME_SIZE):
        occ = False
        if lands[currLand][4*index] == BLOC_TELEPORT_0:    # Monsters cannot go over teleporters
            occ = True

        occupyTable.append(occ)

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
    global blocsCount, countToxicBlocs, level, gamePhase, endOfLevelTimer
    print('Destroy bloc of type ' + str(bloc))
    if (bloc <= BLOC_GREEN_CHEM):
        blocsCount[bloc] -= 1
        if (bloc >= BLOC_POISON):
            countToxicBlocs -= 1
            print('countToxicBlocs: ' + str(countToxicBlocs))
            penguin1.score += 5

    if (countToxicBlocs == 0) and not itsChallenge:
        # Level finished. Show outro animation.
        gamePhase = PHASE_END_LEVEL
        endOfLevelTimer = 150
        print('PHASE_END_LEVEL')

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

    if index == 24 and itsChallenge == True:
        return BLOC_CHALLENGE

    return index

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
pauseGame = False

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
soundSplat = pygame.mixer.Sound('Data/bruitages/SPLATCH.wav')           # 34 (sample Y) - for chemical bloc
soundWow   = pygame.mixer.Sound('Data/bruitages/HMM.wav')               # 35 (sample Z) - WOW END OF LEVEL (wrong sample)

# Set volumes

soundCrash.set_volume(0.5)
soundLaunch.set_volume(0.3)
soundMagic.set_volume(0.2)
soundSplat.set_volume(0.5)

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
            j=int(i/4)
            teleporters[index].append(j)
            print('  ' + str(j%64) + ',' + str(int(j/SCHEME_WIDTH)))

# SpriteSheets

ss_shared = []
ss_shared.append(spritesheet.SpriteSheet('Data/sharedBlocs0.png'))
ss_shared.append(spritesheet.SpriteSheet('Data/sharedBlocs1.png'))
ss_shared.append(spritesheet.SpriteSheet('Data/sharedBlocs2.png'))
ss_shared.append(spritesheet.SpriteSheet('Data/sharedBlocs3.png'))

ss_start    = spritesheet.SpriteSheet('Data/startScreen.png')
ss_border   = spritesheet.SpriteSheet('Data/border.png')
ss_penguins = spritesheet.SpriteSheet('Data/pengos.png')
ss_chars    = spritesheet.SpriteSheet('Data/chars.png')
ss_challenge= spritesheet.SpriteSheet('Data/challengeTile.png')
ss_panels   = spritesheet.SpriteSheet('Data/panels.png')

ss_levels = []
ss_endScreens = []
for index in range(1, 1+LANDS_NB):
    ss_levels.append(spritesheet.SpriteSheet('Data/level' + str(index) + '.png'))
    ss_endScreens.append(spritesheet.SpriteSheet('Data/Screens/scr' + str(index) + '.png'))

# Other assets
startScreen = ss_start.get_indexed_image(0, 244, 240)
border = ss_border.get_indexed_image(0, 320, 256)

penguin1 = Penguin()

penguinSprites = []
for index in range(0, 2*36+12):
    penguinSprites.append(ss_penguins.get_indexed_image(index, BLOC_SIZE, BLOC_SIZE))

charsSprites = []
for index in range(0, 40):
    charsSprites.append((ss_chars.get_indexed_image(index, 12, 16)))

panelSprites = []
for index in range(0, 2):
    panelSprites.append((ss_panels.get_indexed_image(index, 60, 20)))

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
                    loadLevel()

            if event.key == pygame.K_ESCAPE:  # Quit game
                if gamePhase == PHASE_GAME:
                    gamePhase = PHASE_INTRO
                elif gamePhase == PHASE_INTRO:
                    running = False

            if event.key == pygame.K_F5:    # Prev level
                if (level > 1):
                    level -= 1
                    loadLevel()

            if event.key == pygame.K_F6:    # Next level
                if (level < 50):
                    level += 1
                    loadLevel()

            if event.key == pygame.K_F7:  # Prev challenge
                if (level > 5):
                    level -= 5
                    loadChallenge()

            if event.key == pygame.K_F8:  # Next challenge
                if (level < 45):
                    level += 5
                    loadChallenge()

            if event.key == pygame.K_F12:    # Pause game
                if gamePhase == PHASE_GAME:
                    pauseGame = not pauseGame

    if gamePhase == PHASE_GAME and not pauseGame:
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

                    if turningBloc < 24:
                        turningBlocs.append(turningBloc)

                # Rotate turning blocs (clockwise)
                if (len(turningBlocs) > 1):
                    turningBlocs = turningBlocs[len(turningBlocs)-1:len(turningBlocs)] + turningBlocs[:len(turningBlocs)-1]

                i = 0
                for offset in CYCLONE_OFFSETS:
                    finalOffset = cycloneIndex + offset[0] + offset[1] * SCHEME_WIDTH
                    turningBloc = scheme[finalOffset]

                    if turningBloc < 24:
                        blocX = finalOffset % SCHEME_WIDTH
                        blocY = int (finalOffset / SCHEME_WIDTH)
                        writeBloc(blocX, blocY, turningBlocs [i])
                        i += 1

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
    elif gamePhase == PHASE_END_LEVEL:
        screen.blit(endScreenSprite, (ORIGIN_X, ORIGIN_Y))
        if endOfLevelTimer > 0:
            endOfLevelTimer -= 1
            # TODO Penguin animations
        else:
            if level % 5 == 0:
                loadChallenge()
            else:
                level += 1
                loadLevel()

            print('Switch to PHASE_GAME')
            gamePhase = PHASE_GAME
    else: # PHASE_GAME
        # Draw BG

        anim = int(absTime / 4)
        for y in range(0, BLOCS_RANGE + 1):
            for x in range(0, BLOCS_RANGE + 1):

                blocOffset = (int(baseY / BLOC_SIZE) + y) * SCHEME_WIDTH + (int(baseX / BLOC_SIZE) + x)

                if itsChallenge == True:
                    index = 24      # Empty land in challenge mode
                else:
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
                    screen.blit(sprites[0][index], (ORIGIN_X + c.posX, ORIGIN_Y + c.posY), c.getCroppedRegion())

        # Display Penguin
        penguin1.display(screen, baseX, baseY)

        # Display Monsters
        for m in monsters:
            m.display(screen, baseX, baseY)

        # Display moving bloc and bonus, if any
        penguin1.displayBloc(screen, baseX, baseY)

    # Display Scores
    displayScore(penguin1.score, 256, 45)
    displayScore(0, 256, 188)   # No 2nd player supported, for now

    # Display panel (PAUSE or DEMO)

    panelIdx = -1

    if pauseGame == True:
        panelIdx = 1

    if panelIdx != -1:
        screen.blit(panelSprites[panelIdx], (8 + 244/2 - 60/2, 50))

    # Time
    if not pauseGame:
        absTime += clock.get_time()

    # flip() the display to put your work on screen
    pygame.display.flip()

    clock.tick(60)  # limits FPS to 60

pygame.quit()