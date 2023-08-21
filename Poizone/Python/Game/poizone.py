# POIZONE re-written in Python 3.11, july 2023 (32 years later after the original).
# 2-player mode is not supported.

import pygame
import numpy
import math
import random
from constants import *
import spritesheet
import leaderboard
import options
import particles
import tuto
import texts
from cropsprite import CropSprite

# Global variables

gamePhase           = Phase.NONE
absTime             = 0
gameTimer           = 0.0           # 0 - 300 ( 5 minutes ) - in seconds
level               = 1             # From 1 to 50
currLand            = 0             # 0..4 (Land.)
electrifyBorder     = False
electrifyBorderAnim = 0
blocsCount          = []
toxicBlocsLeft      = 0

cyclonesPace        = 0             # For cyclones
cyclonesList        = []

isRevenge           = False         # Revenge mode ?
windowFade          = 0             # 0..255
menuCounter         = 0

tutoCounter         = 0
currTutoPage        = 0

maxLevelReached     = 1     # For CONTINUE option

lastKeyDown         = NONE

running             = True
pauseGame           = False

# Utility functions

def blitGameSprite(sprite, cropSprite):
    screen.blit(sprite, (ORIGIN_X + cropSprite.posX, ORIGIN_Y + cropSprite.posY), cropSprite.getCroppedRegion())

def debugPrint(text):
    if DEBUG_FEATURES == True:
        print(text)

# Classes

class Penguin():
    def __init__(self):
        self.reset()
        self.score = 0
        self.points = 0             # Will be gradually added to score

    def reset(self):
        self.posX = 24 * BLOC_SIZE   # Center of map
        self.posY = 24 * BLOC_SIZE
        self.dirX = 0
        self.dirY = 0
        self.anim = 0
        self.animPhase = 0
        self.status = PenguinStatus.IDLE
        self.pushCounter = 0
        self.invert = False
        self.ghost = 0              # Invincible if > 0
        self.canTeleport = True
        self.diamondsAssembled = False

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
            debugPrint('New Penguin status: ' + str(status))
            self.status = status

    def getBlocOnDir(self, dirX, dirY):
        return getBloc(self.posX // BLOC_SIZE + dirX, self.posY // BLOC_SIZE + dirY)

    def launchBloc(self, bloc, posX, posY, dirX, dirY):
        debugPrint('LaunchBloc')
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
            self.pushCounter = PUSH_DURATION
            if bloc == Bloc.ELECTRO:
                setElectrifyBorder(True)
            elif bloc < 24:
                nextBloc = self.getBlocOnDir(self.dirX * 2, self.dirY * 2)
                if (nextBloc >= 24):
                    if self.movBlocWhat == NONE:        # Avoid overriding ongoing launch bloc
                        self.launchBloc(bloc, self.posX, self.posY, self.dirX, self.dirY)
                        blocX = self.posX // BLOC_SIZE + self.dirX
                        blocY = self.posY // BLOC_SIZE + self.dirY
                        writeBloc(blocX, blocY, 26)         # Remove bloc from initial position
                        if bloc == Bloc.CYCLONE:
                            idx = cyclonesList.index(blocX + blocY * SCHEME_WIDTH)
                            debugPrint('Remove cyclone ' + str(cyclonesList[idx]) + ' from list at index ' + str(idx))
                            cyclonesList[idx] = 0

                        playSFX(soundLaunch)

                        if bloc == Bloc.RED:        # Do NOT launch red chemical block!
                            self.die(True)
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

        if bloc >= Bloc.ROCK:  # Cannot crush that bloc
            return

        blocUp    = self.getBlocOnDir(self.dirX, self.dirY - 1)
        blocDown  = self.getBlocOnDir(self.dirX, self.dirY + 1)
        blocLeft  = self.getBlocOnDir(self.dirX - 1, self.dirY)
        blocRight = self.getBlocOnDir(self.dirX + 1, self.dirY)

        match bloc:
            case Bloc.ALCOOL:
                self.invert = not self.invert
                playSFX(soundAlcool)

            case Bloc.BOMB:
                self.die()
                playSFX(soundBoom)

            case Bloc.MAGIC:  # Temporary invincibility
                self.ghost = 60 * 15
                playSFX(soundMagic)

            case Bloc.POISON:  # Must be in contact with at least one ALU bloc
                if not (blocUp == Bloc.ALU or blocDown == Bloc.ALU or blocLeft == Bloc.ALU or blocRight == Bloc.ALU):
                    self.die(True)

            case Bloc.ALU:  # Cannot crush ALU bloc
                self.die(True)

            case Bloc.BATTERY:
                if self.dirY == 0:  # Crushed from up or down ?
                    self.die(True)

            case Bloc.DDT:
                if not (blocUp == Bloc.DDT or blocDown == Bloc.DDT or blocLeft == Bloc.DDT or blocRight == Bloc.DDT):
                    self.die(True)

            case Bloc.CFC:
                if self.dirY != 1:  # Crushed from up ?
                    self.die(True)

            case Bloc.URANIUM:  # Are other Bloc.URANIUM blocs nearby ?
                if (blocUp == Bloc.URANIUM or blocDown == Bloc.URANIUM or
                    blocLeft == Bloc.URANIUM or blocRight == Bloc.URANIUM):
                    self.die(True)

            case Bloc.GREEN_CHEM:
                self.die(True)

        blocX = self.posX // BLOC_SIZE + self.dirX
        blocY = self.posY // BLOC_SIZE + self.dirY

        if bloc == Bloc.BOMB:
            self.startBombAnim(self.posX + self.dirX * BLOC_SIZE, self.posY + self.dirY * BLOC_SIZE)
        else:
            self.startCrushAnim(bloc, self.posX + self.dirX * BLOC_SIZE, self.posY + self.dirY * BLOC_SIZE)

        writeBloc(blocX, blocY, 26)
        destroyBloc(bloc)

        playSFX(soundCrash)

    def die(self, playOhNo = False):

        self.animPhase = 0
        self.setStatus(PenguinStatus.DIE)
        self.invert = False         # Reset malus

        if playOhNo:
            playSFX(soundOhNo)
        else:
            playSFX(soundColl)

        setElectrifyBorder(False)

    def checkSquareDiamond(self, bx, by):
        if (getBloc(bx, by - 1) == Bloc.DIAMOND):
            if (getBloc(bx - 1, by - 1) == Bloc.DIAMOND) and (getBloc(bx - 1, by) == Bloc.DIAMOND):
                return True
            if (getBloc(bx + 1, by - 1) == Bloc.DIAMOND) and (getBloc(bx + 1, by) == Bloc.DIAMOND):
                return True

        if (getBloc(bx, by + 1) == Bloc.DIAMOND):
            if (getBloc(bx - 1, by + 1) == Bloc.DIAMOND) and (getBloc(bx - 1, by) == Bloc.DIAMOND):
                return True
            if (getBloc(bx + 1, by + 1) == Bloc.DIAMOND) and (getBloc(bx + 1, by) == Bloc.DIAMOND):
                return True

        return False

    def isOnBlock(self):
        return isOnBlock(self.posX, self.posY)

    def blocIsWalkable(self, dirX, dirY):

        # Check occupy table
        blocIndex = (self.posX // BLOC_SIZE + dirX) + (self.posY // BLOC_SIZE + dirY) * SCHEME_WIDTH
        if (occupyTable[blocIndex] & 0b10) != 0:
            return False

        return self.getBlocOnDir(dirX, dirY) >= 24

    def getNextTeleportIndex(self):     # Or NONE
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
        return NONE

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
        if (self.ghost / 2) % 8 <= 6:
            c = CropSprite(self.posX - baseX, self.posY - baseY)
            blitGameSprite(penguinSprites[self.anim], c)

    def displayBloc(self, screen, baseX, baseY):

        if self.bombTimer > 0:
            c = CropSprite(self.bombPosX - baseX, self.bombPosY - baseY)
            index = 76 + int((32 - self.bombTimer) / 4)
            blitGameSprite(penguinSprites[index], c)

        if self.crushBlocWhat != NONE:
            c = CropSprite(self.crushBlocPosX - baseX, self.crushBlocPosY - baseY)
            index = getAliasBlocIndex(self.crushBlocWhat)
            maskIndex = 3-int(self.crushBlocTimer / 4)
            blitGameSprite(sprites[maskIndex][index], c)

        if self.movBlocWhat != NONE:
            c = CropSprite(self.movBlocPosX - baseX, self.movBlocPosY - baseY)
            index = getAliasBlocIndex(self.movBlocWhat)
            blitGameSprite(sprites[0][index], c)

        # Display killed monsters bonus, if any
        if self.movBonusTimer > 0:
            self.movBonusTimer -= 1
            if self.movMonsters > 0:  # At least one monster has been killed
                c = CropSprite(self.movBlocPosX - baseX, self.movBlocPosY - baseY)
                index = pygame.math.clamp(self.movMonsters - 1, 0, 3) # Display corresponding bonus (20, 50, 100 or 200)
                blitGameSprite(penguinSprites[72 + index], c)

    def update(self, keyDown):
        global monsters, teleporters, scheme, baseX, baseY

        # Update score by increments of 10 points
        toAdd = pygame.math.clamp(self.points, 0, 10)
        self.points -= toAdd
        self.score += toAdd

        if self.pushCounter > 0:
            self.pushCounter -= 1

        penguinMove = keyDown[KEY_GAME_LEFT] or keyDown[KEY_GAME_RIGHT] or keyDown[KEY_GAME_UP] or keyDown[KEY_GAME_DOWN]

        if penguinMove:
            self.canTeleport = True

        if self.status != PenguinStatus.DIE:
            onBlock = self.isOnBlock()

            if (self.posY % BLOC_SIZE) == 0:    # Cannot change X direction if not aligned on bloc vertically
                if keyDown[KEY_GAME_LEFT]:
                    self.dirX = -1 if self.invert == False else +1
                    self.dirY = 0
                    if onBlock and not self.blocIsWalkable(self.dirX, self.dirY):
                        self.setStatus(PenguinStatus.IDLE)

                if keyDown[KEY_GAME_RIGHT]:
                    self.dirX = 1 if self.invert == False else -1
                    self.dirY = 0
                    if onBlock and not self.blocIsWalkable(self.dirX, self.dirY):
                        self.setStatus(PenguinStatus.IDLE)

            if (self.posX % BLOC_SIZE) == 0:    # Cannot change Y direction if not aligned on bloc horizontally
                if keyDown[KEY_GAME_UP]:
                    self.dirX = 0
                    self.dirY = -1 if self.invert == False else +1
                    if onBlock and not self.blocIsWalkable(self.dirX, self.dirY):
                        self.setStatus(PenguinStatus.IDLE)

                if keyDown[KEY_GAME_DOWN]:
                    self.dirX = 0
                    self.dirY = 1 if self.invert == False else -1
                    if onBlock and not self.blocIsWalkable(self.dirX, self.dirY):
                        self.setStatus(PenguinStatus.IDLE)

            if keyDown[KEY_GAME_PUSH] and penguinMove and onBlock:
                # Check if there is a bloc to push
                if (self.dirX != 0 or self.dirY != 0) and (self.getBlocOnDir(self.dirX, self.dirY) < 24):
                    self.pushBloc()
                elif self.pushCounter == 0:               # Stop pushing
                    self.setStatus(PenguinStatus.IDLE)
                    setElectrifyBorder(False)

        if (self.status == PenguinStatus.PUSH) and ((penguinMove == False) or not keyDown[KEY_GAME_PUSH]):
            self.setStatus(PenguinStatus.IDLE)
            setElectrifyBorder(False)
            self.pushCounter = 0

        if (self.status == PenguinStatus.IDLE) and (self.dirX != 0 or self.dirY != 0) and (
                penguinMove == True):
            if self.blocIsWalkable(self.dirX, self.dirY):
                self.setStatus(PenguinStatus.WALK)

        if (self.status == PenguinStatus.WALK):
            self.posX += self.dirX * PENG_WALK_STEP
            self.posY += self.dirY * PENG_WALK_STEP
            if self.isOnBlock():  # Stop walking at next block
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
            if offsetX < -PENG_WALK_STEP:
                baseX -= PENG_WALK_STEP * 2     # Fast move speed
            elif offsetX < 0:
                baseX -= PENG_WALK_STEP         # Normal move speed
            elif offsetX > PENG_WALK_STEP:
                baseX += PENG_WALK_STEP * 2
            elif offsetX > 0:
                baseX += PENG_WALK_STEP

            offsetY = penguin1.posY + 8 - baseY - (BLOCS_RANGE * BLOC_SIZE) // 2
            if offsetY < -PENG_WALK_STEP:
                baseY -= PENG_WALK_STEP * 2
            elif offsetY < 0:
                baseY -= PENG_WALK_STEP
            elif offsetY > PENG_WALK_STEP:
                baseY += PENG_WALK_STEP * 2
            elif offsetY > 0:
                baseY += PENG_WALK_STEP

        MAX_X = (48 - BLOCS_RANGE) * BLOC_SIZE - 4  # In pixels
        MAX_Y = (48 - BLOCS_RANGE) * BLOC_SIZE - 4

        baseX = pygame.math.clamp(baseX, 0, MAX_X)
        baseY = pygame.math.clamp(baseY, 0, MAX_Y)

        # Check teleporters

        if self.isOnBlock() and self.canTeleport:
            found = self.getNextTeleportIndex()
            if found != NONE:
                debugPrint('Teleporter found : ' + str(found))
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
                    debugPrint('End of bloc travel. Killed ' + str(self.movMonsters) + ' monsters.')

                    killBloc = (self.movBlocWhat == Bloc.GREEN_CHEM)
                    if self.movBlocWhat == Bloc.ALU:
                        if (getBloc(bx+1, by) == Bloc.ELECTRO) or (getBloc(bx-1, by) == Bloc.ELECTRO) or \
                           (getBloc(bx, by-1) == Bloc.ELECTRO) or (getBloc(bx, by+1) == Bloc.ELECTRO):
                            killBloc = True     # Kill ALU when launched against electro border

                    if not killBloc:
                        writeBloc(bx, by, self.movBlocWhat)

                        if self.movBlocWhat == Bloc.CYCLONE:
                            # Insert it back in the cyclonesList
                            for index in range(0, len(cyclonesList)):
                                if cyclonesList[index] == 0:
                                    cyclonesList[index] = bx + by * SCHEME_WIDTH
                                    break

                        if (self.movBlocWhat == Bloc.DIAMOND):
                            if not self.diamondsAssembled and self.checkSquareDiamond(bx, by) == True:
                                debugPrint('Square Diamond assembled')
                                playSFX(soundDiam)
                                self.addScore(500)
                                self.diamondsAssembled = True    # This bonus can be obtained only once per level
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

                    self.addScore(BONUS_KILL [pygame.math.clamp(self.movMonsters, 0, len(BONUS_KILL)-1)])

            self.movBlocPosX += self.movBlocDirX * MOVBLOC_STEP
            self.movBlocPosY += self.movBlocDirY * MOVBLOC_STEP

        if self.ghost > 0:
            self.ghost -= 1

        if self.status != PenguinStatus.DIE and self.ghost == 0:     # If penguin can die, check collision with alive monsters
            for m in monsters:
                if m.isAlive() and (abs(m.posX - self.posX) <= 8) and (abs(m.posY - self.posY) <= 8):
                    self.die()
                    break

    def addScore(self, points):
        self.points += points

class Monster():
    def __init__(self, kind, isBaddie):
        self.posX = 0
        self.posY = 0
        self.dirX = 0
        self.dirY = 0
        self.kind = kind                # 0 or 1 (graphic monster type (skin))
        self.isBaddie = isBaddie        # Baddies are monsters targeting the Penguin, the others move randomly

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
            blitGameSprite(monstersSprites[self.getSpriteIndex()], c)

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
                    debugPrint('Electrify monster')
                    
            if self.isAlive() and (penguin1.movBlocWhat != NONE):
                deltaX = abs(penguin1.movBlocPosX - self.posX)
                deltaY = abs(penguin1.movBlocPosY - self.posY)
                if (deltaX <= 10) and (deltaY <= 10):
                    debugPrint('Kill monster')
                    self.killAndRebirth()
                    playSFX(soundColl)
                    penguin1.movMonsters += 1
                elif (deltaX <= 12) and (deltaY <= 12):
                    debugPrint('Dizzy monster by bloc collision')
                    self.dizzyCounter = 4*60

            if (self.isAlive() and not self.isDizzy() and onBlock):
                found = False
                for t in range(0, 10):      # Try 10 times
                    # Choose new direction

                    if self.isBaddie and random.randrange(2) == 0:
                        # Target Penguin
                        dirX = penguin1.posX - self.posX
                        dirY = penguin1.posY - self.posY
                        if abs(dirX) > abs(dirY):
                            dirX = 1 if dirX > 0 else -1
                            dirY = 0
                        else:
                            dirX = 0
                            dirY = 1 if dirY > 0 else -1

                    elif (random.randrange(2) == 0):
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

                self.dirX = dirX * MONSTER_WALK_STEP
                self.dirY = dirY * MONSTER_WALK_STEP

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
            # debugPrint(f"New monster at {x},{y}")

            if (occupyTable[x + y * SCHEME_WIDTH] != 0):      # Already occupied
                continue

            if (abs(x - int(penguin1.posX / BLOC_SIZE)) < 3) or (abs(y - int(penguin1.posY / BLOC_SIZE)) < 3):
                continue                    # Penguin too close ?
            if (scheme[x + y * SCHEME_WIDTH] < 24):   # Cell already occupied ?
                continue
            self.posX = x * BLOC_SIZE
            self.posY = y * BLOC_SIZE
            return

# Global Functions

def resetGame():
    global level, penguin1

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
    debugPrint("Load level " + str(level))
    currLand = (level-1) % LANDS_NB
    loadSprites()

    schemeName = "Data/Schemes/S" + str(level)
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
            cyclonesList [cyclonesNb] = i
            debugPrint('Cyclone #' + str(cyclonesNb) + ' at index ' + str(i))
            cyclonesNb += 1
            
    toxicBlocsLeft  = blocsCount[Bloc.POISON]  + blocsCount[Bloc.RED]
    toxicBlocsLeft += blocsCount[Bloc.ALU]     + blocsCount[Bloc.BATTERY]
    toxicBlocsLeft += blocsCount[Bloc.DDT]     + blocsCount[Bloc.CFC]
    toxicBlocsLeft += blocsCount[Bloc.URANIUM] + blocsCount[Bloc.GREEN_CHEM]

    debugPrint('toxicBlocsLeft: ' + str(toxicBlocsLeft))
    totalToxicBlocs = toxicBlocsLeft

    resetLevel()
    initOccupyTable()

    monsters = []
    baddiesNumber = level / 8
    for index in range(0, MONSTERS_NB):
        kind = index % 2
        m = Monster(kind, index < baddiesNumber)
        m.setRandomPosition()
        monsters.append(m)

def loadRevenge():
    global level, currLand, scheme, blocsCount, monsters, cyclonesList
    debugPrint("Load revenge for level " + str(level))
    currLand = (level - 1) // 10
    loadSprites()

    schemeName = "Data/Schemes/CHALLENGES"
    with open(schemeName, 'rb') as f:
        scheme = f.read()

    cyclonesList = [0] * 8

    resetRevenge((level-1) // 5)

    initOccupyTable()

    monsters = []
    for index in range(0, MONSTERS_NB):
        kind = index % 2
        m = Monster(kind, False)
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
        if lands[currLand][4*index] == Bloc.TELEPORT_0:    # Monsters cannot go over teleporters
            occ = 1

        occupyTable.append(occ)

def displayScore(score, posX, posY):
    base = 10000
    for i in range(0, 5):
        index = (score // base) % 10
        screen.blit(charsSprites_gr[index + 26], (posX+12*i, posY))
        base //= 10

def displayPanel():
    panelIdx = NONE

    if pauseGame == True:
        panelIdx = PANEL_PAUSE

    if panelIdx != NONE:
        screen.blit(panelSprites[panelIdx], (ORIGIN_X + WINDOW_WIDTH//2 - 60/2, 30))

def getBloc(indexX, indexY):
    blocOffset = indexX + indexY * SCHEME_WIDTH
    if blocOffset >= 0 and blocOffset < SCHEME_SIZE:
        blocOfScheme = scheme[blocOffset]
    else:
        blocOfScheme = Bloc.BASIC

    return blocOfScheme

def isOnBlock(posX, posY):
    return ((posX % BLOC_SIZE) == 0) and ((posY % BLOC_SIZE) == 0)

def destroyBloc(bloc):
    global blocsCount, toxicBlocsLeft
    debugPrint('Destroy bloc of type ' + str(bloc))
    if (bloc <= Bloc.GREEN_CHEM):
        blocsCount[bloc] -= 1
        if (bloc >= Bloc.POISON):
            toxicBlocsLeft -= 1
            debugPrint('toxicBlocsLeft: ' + str(toxicBlocsLeft))
            penguin1.addScore(5)

def writeBloc(indexX, indexY, blocIndex):
    global scheme
    index = indexX + indexY * SCHEME_WIDTH
    newBloc = [ blocIndex ]
    scheme = scheme[:index] + bytes(newBloc) + scheme[(index+1):]

def getAliasBlocIndex(index):
    if index == Bloc.ELECTRO:  # Electric border (animation)
        return Bloc.ELECTRO_0 + (int(electrifyBorderAnim / 8) % 2)

    if index == Bloc.BASIC:
        if currLand == 0: return Bloc.BASIC_0
        if currLand == 1: return Bloc.BASIC_1
        if currLand == 2: return Bloc.BASIC_2
        if currLand == 3: return Bloc.BASIC_3
        if currLand == 4: return Bloc.BASIC_4

    if index == Bloc.TELEPORT_0 or index == Bloc.TELEPORT_1:
        return Bloc.TELEPORT_0 + (int(absTime / 256) % 2)

    if index == 24 and isRevenge == True:
        return Bloc.REVENGE

    return index

def setElectrifyBorder(newStatus):
    global electrifyBorder

    if  newStatus == True and electrifyBorder == False:
        playSFX(soundElec, 100)

    if newStatus == False and electrifyBorder == True:
        soundElec.stop()

    electrifyBorder = newStatus

# Starting Game phases

def startIntroPhase():
    global gamePhase, windowFade, introTimer, pauseGame

    debugPrint('Phase.INTRO')
    gamePhase = Phase.INTRO
    playMusic(musicIntro, -1)
    windowFade = 0
    introTimer = 0
    pauseGame = False

def startMenuPhase():
    global gamePhase, menuCounter, windowFade, pauseGame, menuCursor, subMenu, currLand

    debugPrint('Phase.MENU')
    gamePhase = Phase.MENU
    menuCounter = 0
    pauseGame = False
    menuCursor = 0
    subMenu = Menu.MAIN

    # Load sprites for tutos
    currLand = 0
    loadSprites()

def startLevelPhase():
    global gamePhase, windowFade

    debugPrint('Phase.LEVEL')
    gamePhase = Phase.LEVEL
    loadLevel()
    windowFade = 128

def startResultPhase():
    global gamePhase, windowFade, resultTimer, bonus, toxicBlocsLeft, totalToxicBlocs

    debugPrint('Phase.RESULT')
    gamePhase = Phase.RESULT
    windowFade = 200
    resultTimer = 0

    # Compute bonus
    percent = ((totalToxicBlocs - toxicBlocsLeft) * 100) // totalToxicBlocs
    bonus = 25 * pygame.math.clamp(percent - SUCCESS_GOAL, 0, 100)

    if percent == 100:                              # Perfect
        bonus += 500 + 5 * int(gameTimer)           # 1 second = 5 points

def startEndLevelPhase():
    global gamePhase, endOfLevelTimer, windowFade, part, rocketOriginX, rocketOriginY

    debugPrint('Phase.END_LEVEL')
    gamePhase = Phase.END_LEVEL
    endOfLevelTimer = 250
    playMusic(musicEnd)
    windowFade = 0

    # Create rocket particles, if needed in this land
    if currLand == Land.ESA or currLand == Land.MOON:
        rocketOriginX = 70 if currLand == Land.ESA else 105
        rocketOriginY = 60 if currLand == Land.ESA else 35
        part = particles.Particles(rocketOriginX + 28, rocketOriginY + 182, 100)

def startRevengeIntroPhase():
    global gamePhase, windowFade, introTimer

    debugPrint('Phase.REVENGE_INTRO')
    gamePhase = Phase.REVENGE_INTRO
    windowFade = 0
    loadRevenge()
    introTimer = 0

def startRevengeLevelPhase():
    global gamePhase, windowFade

    windowFade = 0
    playMusic(musicRevenge)
    debugPrint('Phase.LEVEL')
    gamePhase = Phase.LEVEL

def startGameWonPhase():
    global gamePhase, resultTimer, windowFade

    resultTimer = 0
    debugPrint('Phase.GAME_WON')
    gamePhase = Phase.GAME_WON
    windowFade = 128
    playMusic(musicWinGame)

def startEnterNamePhase():
    global gamePhase, yourName, cursorTx, cursorTy, cursorPx, cursorPy, resultTimer

    debugPrint('Phase.ENTER_NAME')
    gamePhase = Phase.ENTER_NAME
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
    debugPrint('playMusic loop=' + str(loop))
    musicChannel = pygame.mixer.Channel(1)
    pygame.mixer.stop()
    musicChannel.play(m, loop)

def applyChannelVolumes():
    musicChannel = pygame.mixer.Channel(1)
    musicChannel.set_volume(1 if opt.getValue(OPTIONS_ID [1]) == True else 0)

# HUD

def displayText(font, str, col, text_x, text_y, fx = False):            # Centered
    # Shadow
    text = font.render(str, True, (0, 0, 0))
    textRect = text.get_rect()
    textRect.center = (text_x + 1, text_y + 1)
    screen.blit(text, textRect)

    if fx == False:
        text = font.render(str, True, col)
        textRect = text.get_rect()
        textRect.center = (text_x, text_y)
        screen.blit(text, textRect)
    else:
        # Display text with vertical color gradient FX
        for line in range(0, textRect.height):
            t = 1 - 1.5 * abs(line - textRect.height / 2) / (textRect.height / 2)
            t = pygame.math.clamp(t, 0, 1) * 0.9
            finalCol = (
                pygame.math.lerp(col[0], 255, t),
                pygame.math.lerp(col[1], 255, t),
                pygame.math.lerp(col[2], 255, t)
            )

            text = font.render(str, True, finalCol)
            textRect = text.get_rect()

            # Select source line
            area = [ 0, line, textRect.width, 1]

            textRect.center = (text_x, text_y + line)
            screen.blit(text, textRect, area)

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
    global tutoCounter, currTutoPage, electrifyBorderAnim

    TITLE_COLOR = (255, 255, 155)
    TEXT_COLOR = (225, 225, 255)
    BORDER_COLOR = (0, 0, 0)

    CENTER_X = ORIGIN_X + WINDOW_WIDTH//2

    # Title
    displayText(font_big, texts.MAIN_MENU [Menu.TUTORIAL], TITLE_COLOR, CENTER_X, 80, True)

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
            deltaX = offsetX + d * (1 if dir == tuto.DIR_RIGHT else -1 if dir == tuto.DIR_LEFT else 0)
            deltaY = offsetY + d * (1 if dir == tuto.DIR_DOWN  else -1 if dir == tuto.DIR_UP   else 0)
            screen.blit(arrowsSprites[dir+4*arrowType], (deltaX + arrow [0] * BLOC_SIZE, deltaY + arrow [1] * BLOC_SIZE))

def displayControls():

    TITLE_COLOR = (255, 255, 155)
    OPT_COLOR = (180, 255, 255)
    VALUE_COLOR = (195, 195, 195)
    HIGHLIGHT_COLOR = (230, 255, 255)
    DONE_COLOR = (50, 250, 130)

    # Title
    displayText(font_big, texts.MAIN_MENU [Menu.CONTROLS], TITLE_COLOR, ORIGIN_X + WINDOW_WIDTH // 2, 80, True)

    i = 0
    for i in range(0, len(CTRL_ID)):
        y = 120 + 15 * i
        highlight = (ctrlCursor == i)
        col = HIGHLIGHT_COLOR if highlight else OPT_COLOR

        displayTextRight(font, texts.CTRL[i] + " :", col, ORIGIN_X + 100, y)
        if ((absTime // 200) % 4 == 0):
            highlight = False
        col = HIGHLIGHT_COLOR if highlight else VALUE_COLOR
        displayTextLeft(font, pygame.key.name(tmpKeys[i]), col, ORIGIN_X + 140, y)

    if ctrlCursor == 0:
        y = 220
        for line in texts.CTRL_START:
            displayText(font, line, DONE_COLOR, ORIGIN_X + WINDOW_WIDTH // 2, y)
            y += 12
    elif ctrlCursor == len(CTRL_ID):
        displayText(font, texts.CTRL_DONE, DONE_COLOR, ORIGIN_X + WINDOW_WIDTH // 2, 220)

def displayOptions():
    global optCursor

    TITLE_COLOR = (255, 255, 155)
    OPT_COLOR = (180, 255, 255)
    VALUE_COLOR = (180, 255, 255)
    HIGHLIGHT_COLOR = (230, 255, 255)

    # Title
    displayText(font_big, texts.MAIN_MENU [Menu.OPTIONS], TITLE_COLOR, ORIGIN_X + WINDOW_WIDTH // 2, 80, True)

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
    displayText(font_big, texts.MAIN_MENU [Menu.CREDITS], TITLE_COLOR, ORIGIN_X + WINDOW_WIDTH // 2, 80, True)

    y = 110
    for line in texts.CREDITS:
        displayText(font, line, TEXT_COLOR, ORIGIN_X + WINDOW_WIDTH // 2, y)
        y += 12

def displayMainMenu():
    TEXT_COLOR = (155, 155,  55)
    HIGH_COLOR = (255, 255, 155)
    DEACT_COLOR= (40,   40,  30)
    
    CENTER_X = ORIGIN_X + WINDOW_WIDTH // 2

    for i in range(0, len(texts.MAIN_MENU)):
        deactivated = isMenuDeactivated(i)
        col = DEACT_COLOR if deactivated else (HIGH_COLOR if (menuCursor == i) else TEXT_COLOR)
        displayText(font, texts.MAIN_MENU[i], col, CENTER_X, 120 + 15*i)

def displayMenu():
    match subMenu:
        case Menu.MAIN:
            displayMainMenu()
        case Menu.LEADERBOARD:
            displayLeaderboard()
        case Menu.TUTORIAL:
            displayTuto()
        case Menu.CONTROLS:
            displayControls()
        case Menu.OPTIONS:
            displayOptions()
        case Menu.CREDITS:
            displayCredits()

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

    # Title
    displayText(font_big, texts.MAIN_MENU [Menu.LEADERBOARD], TITLE_COLOR, ORIGIN_X + WINDOW_WIDTH // 2, 80, True)

    # Legend
    displayTextLeft(font, "SCORE       NAME               ZONE", LEGEND_COLOR, 50, 114)

    for index in range (0, leaderboard.LB_MAX_ENTRIES):
        entry = lb.entries [index]

        y = 130 + 9 * index
        score = entry [0]
        name = entry [1]
        level = entry [2]

        # Score
        displayTextRight(font, str(score), SCORE_COLOR, 85, y)

        # Name
        displayTextLeft(font, name, NAME_COLOR, 105, y)

        # Level
        displayTextRight(font, str(level), LEVEL_COLOR, 208, y)

def displayResult():
    TITLE_COLOR = (50, 240, 200)
    DECONTAMINATED_COLOR = (50, 255, 140)
    TIME_LEFT_COLOR = (200, 200, 240)
    BONUS_COLOR = (40, 200, 240)
    GAMEOVER_COLOR = (255, 200, 230)
    GOOD_COLOR = (0, 255, 0)
    BAD_COLOR = (255, 0, 0)

    # Title
    displayText(font_big, f"END OF ZONE {level}",  TITLE_COLOR, ORIGIN_X + WINDOW_WIDTH // 2, 40, True)

    if toxicBlocsLeft == 0:
        if ((resultTimer // 8) % 4 != 0):      # Flash FX
            displayText(font_big, "TOTAL", DECONTAMINATED_COLOR, ORIGIN_X + WINDOW_WIDTH // 2, 90, True)
            displayText(font_big, "DECONTAMINATION!", DECONTAMINATED_COLOR, ORIGIN_X + WINDOW_WIDTH // 2, 130, True)
    else:
        displayText(font_big, "DECONTAMINATION:", DECONTAMINATED_COLOR, ORIGIN_X + WINDOW_WIDTH // 2, 80, True)

        percent = (100 * (totalToxicBlocs - toxicBlocsLeft)) // totalToxicBlocs
        percentDisplay = pygame.math.clamp(percent, 0, resultTimer // 2)
        displayText(font_big, f"{percentDisplay} %", BAD_COLOR if percentDisplay < SUCCESS_GOAL else GOOD_COLOR, ORIGIN_X + WINDOW_WIDTH // 2, 130, True)

        if percent < SUCCESS_GOAL and resultTimer >= 200:
            displayText(font_big, "GAME OVER", GAMEOVER_COLOR, ORIGIN_X + WINDOW_WIDTH // 2, 220, True)

    # Time left
    timeLeft = int(gameTimer)
    if timeLeft > 0:
        displayText(font_big, f"TIME LEFT: {timeLeft} s", TIME_LEFT_COLOR, ORIGIN_X + WINDOW_WIDTH // 2, 200, True)

    # Bonus
    displayText(font_big, f"BONUS: {bonus} POINTS", BONUS_COLOR, ORIGIN_X + WINDOW_WIDTH // 2, 180, True)

    if toxicBlocsLeft == 0:
        displayDancingPenguins(resultTimer - 50)

def displayDancingPenguins(d):
    # According to d value:
    # 0..100: move right
    # 100..120: still, upfront
    # 120..140: still, left front
    # 140..160: still, upfront
    # 160..   : move right

    px = d if d < 100 else (100 if d < 160 else d-60)
    py = 95
    dir = 0 if (d > 100 and d < 120) or (d > 140 and d < 160) else (-1 if (d > 120 and d < 140) else +1)
    for i in range(0, len(dancingPenguins)):
        p = dancingPenguins [i]
        p.status = PenguinStatus.WALK
        p.dirX = dir
        p.dirY = 1 if dir == 0 else 0
        p.anim = p.getPenguinAnimOffset()
        p.animPhase += 1
        p.posX = px + 20 * i - 10
        p.posY = py
        p.display(screen, 0, 0)

def displayRevengeIntroMode():
    TITLE_COLOR = (105, 255, 255)
    TEXT_COLOR = (50, 255, 140)

    displayText(font_big, texts.REVENGE_TITLE, TITLE_COLOR, ORIGIN_X + WINDOW_WIDTH // 2, 60, True)

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

    displayText(font_big, "CONGRATULATIONS!", TITLE_COLOR, ORIGIN_X + WINDOW_WIDTH // 2, 40, True)
    displayText(font_big, "ENTER YOUR NAME:", TITLE_COLOR, ORIGIN_X + WINDOW_WIDTH // 2, 60, True)

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
        displayText(font_big, line, TEXT_COLOR, ORIGIN_X + WINDOW_WIDTH // 2, y, True)
        y += 20

def displayBGMap(baseX, baseY):

    anim = (absTime // 4) % 4       # The land map has 4 animation frames
    for y in range(0, BLOCS_RANGE + 1):
        for x in range(0, BLOCS_RANGE + 2):

            blocOffset = (baseX // BLOC_SIZE + x) + (baseY // BLOC_SIZE + y) * SCHEME_WIDTH

            if isRevenge == True:
                index = 24  # Empty land in Revenge mode
            else:
                index = int(lands[currLand][4 * blocOffset + anim])

            if blocOffset < SCHEME_SIZE:
                blocOfSchemes = scheme[blocOffset]
                if blocOfSchemes < 24:
                    index = blocOfSchemes

            posX = x * BLOC_SIZE - (baseX % BLOC_SIZE)
            posY = y * BLOC_SIZE - (baseY % BLOC_SIZE)

            c = CropSprite(posX, posY)
            index = getAliasBlocIndex(index)
            blitGameSprite(sprites[0][index], c)

def displayEndLevel():

    screen.blit(endScreenSprite, (ORIGIN_X, ORIGIN_Y))

    # Penguin and 3 Monsters animation
    yByLand = [190, 210, 190, 135, 138]
    dirByLand = [-1, -1, -1, -1, +1]
    limitMinXByLand = [145, 140, 160, 140, -20]
    limitMaxXByLand = [500, 500, 500, 500, 70]
    monstersNb = 2 if currLand == Land.COMPUTER else 3

    x = 20 + endOfLevelTimer if currLand != Land.COMPUTER else 250 - endOfLevelTimer
    y = yByLand[currLand]
    dir = dirByLand[currLand]
    limitMinX = limitMinXByLand[currLand]
    limitMaxX = limitMaxXByLand[currLand]
    baseX = 0
    baseY = 0
    mx = pygame.math.clamp(x, limitMinX, limitMaxX)

    # Show Penguin
    if (currLand == Land.ICE or currLand == Land.JUNGLE or currLand == Land.COMPUTER):

        if currLand == Land.COMPUTER:
            px = x + 60  # Penguin on the right side of monsters
            py = y

            if px >= 90:  # Jump parabola
                dy = math.pow(px - 90, 2) / 15
                py += pygame.math.clamp(dy, 0, 50)
        else:
            px = x - 40  # Penguin on the left side of monsters
            py = y

        if currLand == Land.ICE:
            if px >= 120 and px <= 150:  # Jump parabola
                py -= (15 * 15 - math.pow(px - 135, 2)) / 15

        penguin1.status = PenguinStatus.WALK
        penguin1.posX = px
        penguin1.posY = py
        penguin1.dirX = dir
        penguin1.dirY = 0
        penguin1.anim = penguin1.getPenguinAnimOffset()
        penguin1.animPhase += 1
        penguin1.display(screen, 0, 0)

    # Show monsters
    for index in range(0, monstersNb):
        m = monsters[index]
        m.posX = mx + 25 * index
        m.posY = y
        m.dirX = dir
        m.dirY = 0
        m.counter = 1000 - endOfLevelTimer + 16 * index
        m.display(screen, 0, 0)

    # Show Rocket
    if currLand == Land.ESA or currLand == Land.MOON:
        propelY = pow(250 - endOfLevelTimer, 2) / 250
        c = CropSprite(rocketOriginX, rocketOriginY - propelY, rocket.get_width(), rocket.get_height())
        blitGameSprite(rocket, c)
        part.originY = ORIGIN_Y + c.posY + c.heightRegion
        part.update(1. / 60.)  # TODO: should be dt
        part.display(screen, ORIGIN_X, ORIGIN_Y, WINDOW_WIDTH, WINDOW_HEIGHT)

    # For COMPUTER level: redraw a part of the disk drive, over monsters
    if currLand == Land.COMPUTER:
        screen.blit(endScreenSprite, (ORIGIN_X, ORIGIN_Y + 138), (0, 138, 17 * 4, 20))

def applyFade():
    if windowFade > 0:
        blackSurface.fill((0, 0, 0, windowFade))
        screen.blit(blackSurface, (ORIGIN_X, ORIGIN_Y))

def isMenuDeactivated(index):
    return index == Menu.CONTINUE and maxLevelReached == 1

# pygame setup
pygame.init()
pygame.display.set_caption('Poizone')
pygame.mixer.init()  # Initialize the mixer module.
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SCALED)
clock = pygame.time.Clock()

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
#soundFun   = pygame.mixer.Sound('Data/bruitages/Fun.wav')               # 30 (sample U) - (not used in 1-player mode)
soundOhNo   = pygame.mixer.Sound('Data/bruitages/OH_NO.wav')             # 31 (sample V) - wrong move / death
soundAlcool = pygame.mixer.Sound('Data/bruitages/BEER_BLOCK.wav')        # 32 (sample W)
soundColl   = pygame.mixer.Sound('Data/bruitages/COLLISION.wav')         # 33 (sample X) - penguin or monster death
soundSplatch= pygame.mixer.Sound('Data/bruitages/SPLATCH.wav')           # 34 (sample Y) - green glass breaking
soundWow    = pygame.mixer.Sound('Data/bruitages/WOW.wav')               # 35 (sample Z) - END OF LEVEL
soundTick   = pygame.mixer.Sound('Data/bruitages/TICK.wav')              # New sample (same as R but with higher pitch)
soundValid  = pygame.mixer.Sound('Data/bruitages/VALIDATE.wav')          # New sample for menus
soundTele   = pygame.mixer.Sound('Data/bruitages/TELEPORT.wav')          # New sample (same as S but with lower pitch)

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
    #debugPrint('Teleporters in land #' + str(index) + ':')
    for i in range(0, len(land), 4):
        if land[i] >= Bloc.TELEPORT_0:
            j = i // 4
            teleporters[index].append(j)
            #debugPrint('  ' + str(j%64) + ',' + str(j // SCHEME_WIDTH))

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
ss_panels   = spritesheet.SpriteSheet('Data/panels.png')    # DEMO and PAUSE
ss_arrows   = spritesheet.SpriteSheet('Data/arrows.png')    # 4 red and 4 green arrows
ss_legend   = spritesheet.SpriteSheet('Data/legend.png')    # 2 blue arrows

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

# Init input
keyDown    = [False] * KEY_NB
keyPressed = [False] * KEY_NB

old_x_axis = 0.0
old_y_axis = 0.0
try:
    joy = pygame.joystick.Joystick(0)
    joy.init()
    debugPrint('Found JOY ' + joy.get_name())
    joyFound = 0
except pygame.error:
    debugPrint('JOY not found')
    joyFound = NONE

startIntroPhase()

while running:

    # Time
    dt = clock.get_time()
    absTime += dt

    if gamePhase == Phase.LEVEL and not pauseGame:
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

    if joyFound != NONE:
        # Test joystick stick
        x_axis = joy.get_axis(0)
        y_axis = joy.get_axis(1)

        # D-pad
        hat = joy.get_hat(0)
        x_axis += hat [0]
        y_axis -= hat [1]
        
        # X

        if x_axis > JOY_LIMIT:
            keyDown[KEY_RIGHT] = keyDown[KEY_GAME_RIGHT] = True

        if x_axis < -JOY_LIMIT:
            keyDown[KEY_LEFT] = keyDown[KEY_GAME_LEFT] = True

        if x_axis < JOY_LIMIT and old_x_axis >= JOY_LIMIT:
            keyDown[KEY_RIGHT] = keyDown[KEY_GAME_RIGHT] = False

        if x_axis > -JOY_LIMIT and old_x_axis <= -JOY_LIMIT:
            keyDown[KEY_LEFT] =  keyDown[KEY_GAME_LEFT] = False

        # Y

        if y_axis > JOY_LIMIT:
            keyDown[KEY_DOWN] = keyDown[KEY_GAME_DOWN] = True

        if y_axis < -JOY_LIMIT:
            keyDown[KEY_UP] = keyDown [KEY_GAME_UP] = True

        if y_axis < JOY_LIMIT and old_y_axis >= JOY_LIMIT:
            keyDown[KEY_DOWN] = keyDown[KEY_GAME_DOWN] = False

        if y_axis > -JOY_LIMIT and old_y_axis <= -JOY_LIMIT:
            keyDown[KEY_UP] = keyDown[KEY_GAME_UP] = False

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
                keyDown[KEY_GAME_PUSH] = buttonIsDown
            if event.button == 1 and gamePhase != Phase.LEVEL:      # B button only used in menus
                keyDown[KEY_ESCAPE] = buttonIsDown
            elif event.button == 6:
                keyDown[KEY_ESCAPE] = buttonIsDown
            elif event.button == 7:
                keyDown[KEY_PAUSE] = buttonIsDown
            else:
                debugPrint('Unhandled JOY button ' + str(event.button))

        if event.type == pygame.KEYUP or event.type == pygame.KEYDOWN:

            if event.type == pygame.KEYDOWN:
                lastKeyDown = event.key

            down = (event.type == pygame.KEYDOWN)

            # MENU KEYS processing
            for keyPair in MENU_KEYS:
                if event.key == keyPair [1]:
                    keyDown[keyPair [0]] = down

            # GAME KEYS processing
            for keyPair in GAME_KEYS:
                if event.key == opt.getValue(keyPair [1]):
                    keyDown[keyPair [0]] = down

            if not down:

                # Cheat
                if event.key == pygame.K_F5:  # Prev level
                    if (level > 1):
                        level -= 1
                        loadLevel()

                if event.key == pygame.K_F6:  # Next level
                    if (level < 50):
                        level += 1
                        loadLevel()

                if DEBUG_FEATURES == True:

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
        if gamePhase == Phase.LEVEL:
            pauseGame = not pauseGame

    if keyPressed[KEY_ESCAPE] == True:
        if gamePhase == Phase.LEVEL:
            startIntroPhase()
        elif gamePhase == Phase.INTRO:
            running = False
        elif gamePhase == Phase.MENU:
            if subMenu == Menu.MAIN:
                startIntroPhase()
            else:
                subMenu = Menu.MAIN        # Return to Main Menu
            playSFX(soundValid)

    if gamePhase == Phase.INTRO:
        introTimer += 1
        if keyPressed[KEY_SPACE] or keyPressed[KEY_RETURN]:
            startMenuPhase()
            playSFX(soundValid)
    elif gamePhase == Phase.MENU:
        menuCounter += 1
        if windowFade < 160:
            windowFade += 16

        # Main Menu navigation
        if subMenu == Menu.MAIN:
            if keyPressed[KEY_DOWN] and menuCursor < 6:
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
                if menuCursor == Menu.PLAY or menuCursor == Menu.CONTINUE:
                    resetGame()

                    if menuCursor == Menu.CONTINUE:
                        level = maxLevelReached

                    startLevelPhase()
                else:
                    subMenu = menuCursor

                    if subMenu == Menu.OPTIONS:
                        optCursor = 0
                    if subMenu == Menu.CONTROLS:
                        controlsCounter = 0
                        ctrlCursor = 0
                        lastKeyDown = NONE      # To avoid using unwanted SPACE key event
                        tmpKeys = []
                        for i in range(0, len(CTRL_ID)):
                            tmpKeys.append(opt.getValue((CTRL_ID[i])))
                    if subMenu == Menu.TUTORIAL:
                        tutoCounter = 0
                        currTutoPage = 0

                    playSFX(soundValid)

        elif subMenu == Menu.TUTORIAL:
            if keyPressed[KEY_LEFT]:
                currTutoPage = (currTutoPage + TUTO_PAGES - 1) % TUTO_PAGES
                tutoCounter = 0
                playSFX(soundValid)

            if keyPressed[KEY_RIGHT]:
                currTutoPage = (currTutoPage + 1) % TUTO_PAGES
                tutoCounter = 0
                playSFX(soundValid)

        elif subMenu == Menu.OPTIONS:
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

        elif subMenu == Menu.CONTROLS:
            if controlsCounter > 0:
                controlsCounter -= 1
                if controlsCounter == 0:
                    subMenu = Menu.MAIN  # Back to main menu
            elif lastKeyDown != NONE and lastKeyDown != pygame.K_ESCAPE:
                # Check if new key is already in use
                inUse = False
                for i in range(0, ctrlCursor):
                    if tmpKeys[i] == lastKeyDown:
                        inUse = True
                        break

                if not inUse:
                    tmpKeys [ctrlCursor] = lastKeyDown
                    ctrlCursor += 1
                    playSFX(soundValid)
                    if ctrlCursor == len(CTRL_ID):
                        # Setup all keys at once
                        for i in range(0, ctrlCursor):
                            opt.setValue(CTRL_ID[i], tmpKeys[i])
                        opt.save()
                        controlsCounter = 90        # Wait a bit before quitting page
                else:
                    debugPrint('Invalid choice - key already used.')

                lastKeyDown = NONE

    elif gamePhase == Phase.LEVEL and not pauseGame:

        # Fade out
        if windowFade > 0:
            windowFade -= 16
            windowFade = pygame.math.clamp(windowFade, 0, 255)

        # Animate electric border
        if electrifyBorder == True:
            electrifyBorderAnim += 1

        # Animate cyclones
        cyclonesPace = (cyclonesPace + 1) % 16

        if cyclonesPace % 2 == 0:      # To slow down process, process once every two passes
            cycloneIndex = cyclonesList [cyclonesPace >> 1]
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
                if (len(turningBlocs) > 1):
                    turningBlocs = turningBlocs[len(turningBlocs)-1:] + turningBlocs[:len(turningBlocs)-1]
                    
                i = 0
                for offset in CYCLONE_OFFSETS:
                    finalOffset = cycloneIndex + offset[0] + offset[1] * SCHEME_WIDTH
                    turningBloc = scheme[finalOffset]

                    if turningBloc < 24 and turningBloc != Bloc.ELECTRO:
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
                    gamePhase = Phase.LEVEL  # Move to next level
                    level += 1  # End of level - display results
                    loadLevel()
            else:
                if (toxicBlocsLeft == 0):
                    playSFX(soundWow)

                startResultPhase()

    elif gamePhase == Phase.RESULT:
        resultTimer += 1
        if resultTimer > 60*8:
            percent = (100 * toxicBlocsLeft / totalToxicBlocs)
            gameOver = (percent >= (100-SUCCESS_GOAL))
            penguin1.score += bonus             # Take bonus into account
            penguin1.score += penguin1.points   # Apply unaccounted points (if any)
            penguin1.points = 0

            debugPrint(f"percent: {percent} gameOver : {gameOver}")
            
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

    elif gamePhase == Phase.REVENGE_INTRO:

        if windowFade < 128:
            windowFade += 16

        introTimer += 1

        if keyPressed[KEY_GAME_PUSH] or (introTimer > 60*4):
            startRevengeLevelPhase()

    elif gamePhase == Phase.GAME_WON:
        resultTimer += 1
        if resultTimer > 60*21:     # Match music duration
            startMenuPhase()
            playMusic(musicIntro, -1)

    elif gamePhase == Phase.ENTER_NAME:
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

    match gamePhase:
        case Phase.INTRO:
            screen.blit(startScreen, (ORIGIN_X, ORIGIN_Y))

            if ((introTimer // 16) % 4 != 0):
                displayText(font, "Press START", (215, 235, 125), ORIGIN_X + WINDOW_WIDTH // 2, 230)

        case Phase.MENU:
            screen.blit(startScreen, (ORIGIN_X, ORIGIN_Y))

            applyFade()
            displayMenu()

        case Phase.END_LEVEL:

            displayEndLevel()

            if endOfLevelTimer > 0:
                endOfLevelTimer -= 1
            else:
                if level % 5 == 0:
                    startRevengeIntroPhase()
                else:
                    level += 1
                    startLevelPhase()

        case _: # other phases where game map is displayed (Phase.LEVEL, Phase.RESULT, Phase.REVENGE_INTRO, etc)

            # Draw Background Map
            displayBGMap(baseX, baseY)

            # Display Penguin
            penguin1.display(screen, baseX, baseY)

            # Display Monsters
            for m in monsters:
                m.display(screen, baseX, baseY)

            # Display moving bloc and bonus, if any
            penguin1.displayBloc(screen, baseX, baseY)

            applyFade()

            # Display menus over game
            match gamePhase:
                case Phase.RESULT:
                    displayResult()
                case Phase.REVENGE_INTRO:
                    displayRevengeIntroMode()
                case Phase.GAME_WON:
                    displayGameWon()
                case Phase.ENTER_NAME:
                    displayEnterYourName()

            # Display HUD (in the panel on the right side)
            displayGameHud()

    # Display Player Score
    displayScore(penguin1.score, 256, 45)

    # Display panel (PAUSE)
    displayPanel()

    # flip() the display to put your work on screen
    pygame.display.flip()

    clock.tick(60)  # limits FPS to 60

pygame.quit()