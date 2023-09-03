from constants import *
import globals
from utility import *
from cropsprite import CropSprite
import random
import audio

class Monster():
    def __init__(self, kind, isBaddie):
        self.posX = 0
        self.posY = 0
        self.dirX = 0
        self.dirY = 0
        self.kind = kind  # 0 or 1 (graphic monster type (skin))
        self.isBaddie = isBaddie  # Baddies are monsters targeting the Penguin, the others move randomly

        # COUNTER = -32767.. - 1    : not yet born ( -32 .. -1 : birth )
        #         = 0..9              alive (animation phases)

        self.counter = -32 - random.randrange(self.getBirthRange())
        self.dizzyCounter = 0  # If > 0: dizzy

    def killAndRebirth(self):

        self.dirX = 0
        self.dirY = 0

        self.counter = -32 - random.randrange(self.getBirthRange())

        self.dizzyCounter = 0
        self.setRandomPosition()

    def getBirthRange(self):
        return 300 if globals.isRevenge else 2200

    def isAlive(self):
        return self.counter >= 0

    def isBirth(self):
        return self.counter >= -32 and self.counter <= -1

    def isDizzy(self):
        return self.dizzyCounter > 0

    def display(self, screen, baseX, baseY):
        if self.isBirth() or self.isAlive():
            c = CropSprite(self.posX - baseX, self.posY - baseY)
            blitGameSprite(screen, globals.monstersSprites[self.getSpriteIndex()], c)

    def update(self):

        penguin = globals.penguin1

        self.counter += 1

        if self.isAlive():
            if not self.isDizzy():
                self.posX += self.dirX
                self.posY += self.dirY

            if self.dizzyCounter > 0:
                self.dizzyCounter -= 1

            onBlock = (self.posX % BLOC_SIZE == 0) and (self.posY % BLOC_SIZE == 0)

            if globals.electrifyBorder and self.isAlive() and not self.isDizzy() and onBlock:
                if (self.posX == BORDER_SIZE) or (self.posY == BORDER_SIZE) or (
                        self.posX == BLOC_SIZE * 44) or (self.posY == BLOC_SIZE * 44):
                    self.dizzyCounter = 4 * 60
                    debugPrint('Electrify monster')

            if self.isAlive() and (penguin.movBlocWhat != NONE):
                deltaX = abs(penguin.movBlocPosX - self.posX)
                deltaY = abs(penguin.movBlocPosY - self.posY)
                if (deltaX <= 10) and (deltaY <= 10):
                    debugPrint('Kill monster')
                    self.killAndRebirth()
                    audio.playSFX(Sfx.COLL)
                    penguin.movMonsters += 1
                elif (deltaX <= 12) and (deltaY <= 12):
                    debugPrint('Dizzy monster by bloc collision')
                    self.dizzyCounter = 4 * 60

            if self.isAlive() and not self.isDizzy() and onBlock:
                found = False
                for t in range(0, 10):  # Try 10 times
                    # Choose new direction

                    if self.isBaddie and random.randrange(2) == 0:
                        # Target Penguin
                        dirX = penguin.posX - self.posX
                        dirY = penguin.posY - self.posY
                        if abs(dirX) > abs(dirY):
                            dirX = 1 if dirX > 0 else -1
                            dirY = 0
                        else:
                            dirX = 0
                            dirY = 1 if dirY > 0 else -1

                    elif random.randrange(2) == 0:
                        dirX = -1 if (random.randrange(2) == 0) else +1
                        dirY = 0
                    else:
                        dirX = 0
                        dirY = -1 if (random.randrange(2) == 0) else +1

                    blocIndex = self.posX // BLOC_SIZE + dirX + (self.posY // BLOC_SIZE + dirY) * SCHEME_WIDTH

                    if globals.occupyTable[blocIndex] != 0:  # Forbidden destination bloc
                        continue

                    if globals.scheme[blocIndex] >= 24:  # Monster can move to empty block
                        found = True
                        break

                if not found:
                    dirX = 0
                    dirY = 0
                else:
                    # Update Occupy Table
                    currentBlocIndex = self.posX // BLOC_SIZE + (self.posY // BLOC_SIZE) * SCHEME_WIDTH
                    globals.occupyTable[currentBlocIndex] = 0
                    globals.occupyTable[blocIndex] = 1

                self.dirX = dirX * MONSTER_WALK_STEP
                self.dirY = dirY * MONSTER_WALK_STEP

    def getSpriteIndex(self):
        if self.isBirth():
            return 48 + 4 * self.kind + int((32 + self.counter) / 8)

        index = self.kind * 24

        if self.dizzyCounter > 0:
            index += 8

            if self.dirX > 0:  # Right
                index += 2
            if self.dirY > 0:  # Down
                index += 12
            if self.dirY < 0:  # Up
                index += 14

            return index + (int(self.dizzyCounter / 8) % 2)

        if self.dirX > 0:  # Right
            index += 4
        if self.dirY > 0:  # Down
            index += 12
        if self.dirY < 0:  # Up
            index += 16

        return index + (int(self.counter / 8) % 4)

    def setRandomPosition(self):

        while True:

            if not globals.isRevenge:
                x = 3 + random.randrange(0, 48 - 2 * 3)
                y = 3 + random.randrange(0, 48 - 2 * 3)
            else:
                x = globals.baseX // BLOC_SIZE + 1 + random.randrange(0, 10)
                y = globals.baseY // BLOC_SIZE + 1 + random.randrange(0, 10)
            # debugPrint(f"New monster at {x},{y}")

            if globals.occupyTable[x + y * SCHEME_WIDTH] != 0:  # Already occupied
                continue

            if (abs(x - globals.penguin1.posX // BLOC_SIZE) < 3) or (abs(y - globals.penguin1.posY // BLOC_SIZE) < 3):
                continue  # Penguin too close ?
            if globals.scheme[x + y * SCHEME_WIDTH] < 24:  # Cell already occupied ?
                continue
            self.posX = x * BLOC_SIZE
            self.posY = y * BLOC_SIZE
            return
