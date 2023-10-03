from constants import *
import globals
from utility import *
from cropsprite import CropSprite
import audio

class Penguin():

    # Penguin types
    WHITE  = 0
    YELLOW = 1

    def __init__(self, penguinType):
        self.reset()
        self.score = 0
        self.points = 0                     # Will be gradually added to score
        self.penguinType = penguinType      # White or Yellow penguin ?

    def reset(self):
        self.posX = 24 * BLOC_SIZE  # Center of map
        self.posY = 24 * BLOC_SIZE
        self.dirX = 0
        self.dirY = 0
        self.anim = 0
        self.animPhase = 0
        self.status = PenguinStatus.IDLE
        self.pushCounter = 0
        self.invert = False
        self.ghost = 0  # Invincible if > 0
        self.canTeleport = True
        self.pushElectricBorder = False

        # 2-players mode
        if globals.networkMode != NetworkMode.NONE:
            self.posX += BLOC_SIZE * (-1 if self.penguinType == Penguin.WHITE else 1)

        self.movBlocWhat = NONE  # Which bloc (NONE : no bloc)
        self.movBlocPosX = 0
        self.movBlocPosY = 0
        self.movBlocDirX = 0
        self.movBlocDirY = 0
        self.movMonsters = 0  # Number of monsters killed by moving bloc
        self.movBonusTimer = 0  # Timer for displaying the bonus

        self.crushBlocWhat = NONE  # Which bloc (NONE : no bloc)
        self.crushBlocPosX = 0
        self.crushBlocPosY = 0
        self.crushBlocTimer = 0

        self.bombTimer = 0  # Exploding Bomb animation
        self.bombPosX = 0
        self.bombPosY = 0

    def setStatus(self, status):
        if status != self.status:
            debugPrint('New Penguin status: ' + str(status))
            self.status = status

    def getBlocOnDir(self, dirX, dirY):
        return globals.getBloc(self.posX // BLOC_SIZE + dirX, self.posY // BLOC_SIZE + dirY)

    def launchBloc(self, bloc, posX, posY, dirX, dirY):
        debugPrint('LaunchBloc')
        self.movBlocWhat = bloc
        self.movBlocPosX = posX + dirX * BLOC_SIZE
        self.movBlocPosY = posY + dirY * BLOC_SIZE
        self.movBlocDirX = dirX
        self.movBlocDirY = dirY
        self.movMonsters = 0

    def pushBloc(self):

        if self.dirX != 0 or self.dirY != 0:
            bloc = self.getBlocOnDir(self.dirX, self.dirY)
            self.setStatus(PenguinStatus.PUSH)
            self.pushCounter = PUSH_DURATION
            if bloc == Bloc.ELECTRO:
                self.pushElectricBorder = True
            elif bloc < 24:
                nextBloc = self.getBlocOnDir(self.dirX * 2, self.dirY * 2)
                if nextBloc >= 24:
                    if self.movBlocWhat == NONE:  # Avoid overriding ongoing launch bloc
                        self.launchBloc(bloc, self.posX, self.posY, self.dirX, self.dirY)
                        blocX = self.posX // BLOC_SIZE + self.dirX
                        blocY = self.posY // BLOC_SIZE + self.dirY
                        globals.writeBloc(blocX, blocY, 26)  # Remove bloc from initial position
                        if bloc == Bloc.CYCLONE:
                            idx = globals.cyclonesList.index(blocX + blocY * SCHEME_WIDTH)
                            debugPrint('Remove cyclone ' + str(globals.cyclonesList[idx]) + ' at index ' + str(idx))
                            globals.cyclonesList[idx] = 0

                        audio.playSFX(Sfx.LAUNCH)

                        if bloc == Bloc.RED:  # Do NOT launch red chemical block!
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

        blocUp = self.getBlocOnDir(self.dirX, self.dirY - 1)
        blocDown = self.getBlocOnDir(self.dirX, self.dirY + 1)
        blocLeft = self.getBlocOnDir(self.dirX - 1, self.dirY)
        blocRight = self.getBlocOnDir(self.dirX + 1, self.dirY)

        match bloc:
            case Bloc.ALCOOL:
                self.invert = not self.invert
                audio.playSFX(Sfx.ALCOOL)

            case Bloc.BOMB:
                self.die()
                audio.playSFX(Sfx.BOOM)

            case Bloc.MAGIC:  # Temporary invincibility
                self.ghost = 60 * 15
                audio.playSFX(Sfx.MAGIC)

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

        globals.writeBloc(blocX, blocY, 26)
        points = globals.destroyBloc(bloc)
        self.addScore(points)

        audio.playSFX(Sfx.CRASH)

    def die(self, playOhNo=False):

        self.animPhase = 0
        self.setStatus(PenguinStatus.DIE)
        self.invert = False  # Reset malus

        if playOhNo:
            audio.playSFX(Sfx.OH_NO)
        else:
            audio.playSFX(Sfx.COLL)

        self.pushElectricBorder = False

    def zap(self):        # Penguin crushed by moving block
        self.animPhase = 0
        self.setStatus(PenguinStatus.ZAPPED)
        self.invert = False

        audio.playSFX(Sfx.OH_NO)

        self.pushElectricBorder = False

    def checkSquareDiamond(self, bx, by):
        if globals.getBloc(bx, by - 1) == Bloc.DIAMOND:
            if (globals.getBloc(bx - 1, by - 1) == Bloc.DIAMOND) and (globals.getBloc(bx - 1, by) == Bloc.DIAMOND):
                return True
            if (globals.getBloc(bx + 1, by - 1) == Bloc.DIAMOND) and (globals.getBloc(bx + 1, by) == Bloc.DIAMOND):
                return True

        if globals.getBloc(bx, by + 1) == Bloc.DIAMOND:
            if (globals.getBloc(bx - 1, by + 1) == Bloc.DIAMOND) and (globals.getBloc(bx - 1, by) == Bloc.DIAMOND):
                return True
            if (globals.getBloc(bx + 1, by + 1) == Bloc.DIAMOND) and (globals.getBloc(bx + 1, by) == Bloc.DIAMOND):
                return True

        return False

    def isOnBlock(self):
        return globals.isOnBlock(self.posX, self.posY)

    def blocIsWalkable(self, dirX, dirY):

        # Check occupy table
        blocIndex = (self.posX // BLOC_SIZE + dirX) + (self.posY // BLOC_SIZE + dirY) * SCHEME_WIDTH
        if (globals.occupyTable[blocIndex] & 0b10) != 0:
            return False

        if self.getBlocOnDir(dirX, dirY) < 24:
            return False

        # Check if other penguin is walking to the same target block
        for p in globals.penguins:
            if p != self and p.status in [PenguinStatus.IDLE, PenguinStatus.DIE, PenguinStatus.PUSH]:
                otherBlocIndex = (p.posX // BLOC_SIZE) + (p.posY // BLOC_SIZE) * SCHEME_WIDTH
                if blocIndex == otherBlocIndex:
                    return False

            if p != self and p.status == PenguinStatus.WALK:
                otherBlocIndex = (p.posX // BLOC_SIZE + p.dirX) + (p.posY // BLOC_SIZE + p.dirY) * SCHEME_WIDTH
                if blocIndex == otherBlocIndex:
                    return False

        return True

    def getNextTeleportIndex(self):  # Or NONE
        penguinIndex = self.posX // BLOC_SIZE + (self.posY // BLOC_SIZE) * SCHEME_WIDTH
        nb = len(globals.teleporters[globals.currLand])
        for i in range(0, nb):
            tele = globals.teleporters[globals.currLand][i]
            if tele == penguinIndex:
                # Check if next teleporter is available
                nextIndex = globals.teleporters[globals.currLand][(i + 1) % nb]
                if globals.scheme[nextIndex] >= 24:
                    return nextIndex
                else:
                    # Check other teleporter
                    nextIndex = globals.teleporters[globals.currLand][(i + 2) % nb]
                    if globals.scheme[nextIndex] >= 24:
                        return nextIndex
        return NONE

    def getPenguinAnimOffset(self):     # Check animations.py for details

        base = 0 if self.penguinType == Penguin.WHITE else 36

        dir = 3  # Down
        if self.dirX <= -1:
            dir = 0  # Left
        if self.dirX >= +1:
            dir = 1  # Right
        if self.dirY <= -1:
            dir = 2  # Up

        if self.status == PenguinStatus.IDLE:
            return base + 4 * dir
        if self.status == PenguinStatus.WALK:
            return base + 4 * dir + (int(self.animPhase / 8) % 4)
        if self.status == PenguinStatus.DIE:
            if self.animPhase < 32:
                return base + 16 + 4 * dir + int(self.animPhase / 16)
            return base + 16 + 4 * dir + 2 + (int(self.animPhase / 8) % 2)  # End loop
        if self.status == PenguinStatus.PUSH:
            return base + 32 + dir
        return 0

    def display(self, screen, baseX, baseY):
        if (self.status != PenguinStatus.ZAPPED) and (self.ghost / 2) % 8 <= 6:
            c = CropSprite(self.posX - baseX, self.posY - baseY)
            blitGameSprite(screen, globals.penguinSprites[self.anim], c)

    def displayBloc(self, screen, baseX, baseY):

        if self.bombTimer > 0:
            c = CropSprite(self.bombPosX - baseX, self.bombPosY - baseY)
            index = 76 + int((32 - self.bombTimer) / 4)
            blitGameSprite(screen, globals.penguinSprites[index], c)

        if self.crushBlocWhat != NONE:
            c = CropSprite(self.crushBlocPosX - baseX, self.crushBlocPosY - baseY)
            index = globals.getAliasBlocIndex(self.crushBlocWhat)
            maskIndex = 3 - int(self.crushBlocTimer / 4)
            blitGameSprite(screen, globals.sprites[maskIndex][index], c)

        if self.movBlocWhat != NONE:
            c = CropSprite(self.movBlocPosX - baseX, self.movBlocPosY - baseY)
            index = globals.getAliasBlocIndex(self.movBlocWhat)
            blitGameSprite(screen, globals.sprites[0][index], c)

        # Display killed monsters bonus, if any
        if self.movBonusTimer > 0:
            self.movBonusTimer -= 1
            if self.movMonsters > 0:  # At least one monster has been killed
                c = CropSprite(self.movBlocPosX - baseX, self.movBlocPosY - baseY)
                # Display corresponding bonus (20, 50, 100 or 200 points)
                index = pygame.math.clamp(self.movMonsters - 1, 0, 3)
                blitGameSprite(screen, globals.penguinSprites[72 + index], c)

    def update(self, keyDown, monsters, mainPenguin):
        global scheme

        # Update score by increments of 10 points
        toAdd = pygame.math.clamp(self.points, 0, 10)
        self.points -= toAdd
        self.score += toAdd

        if self.pushCounter > 0:
            self.pushCounter -= 1

        askMove = keyDown[Key.GAME_LEFT] or keyDown[Key.GAME_RIGHT] or keyDown[Key.GAME_UP] or keyDown[Key.GAME_DOWN]

        if askMove:
            self.canTeleport = True

        if self.status != PenguinStatus.DIE and self.status != PenguinStatus.ZAPPED:
            onBlock = self.isOnBlock()

            if (self.posY % BLOC_SIZE) == 0:  # Cannot change X direction if not aligned on bloc vertically
                if keyDown[Key.GAME_LEFT]:
                    self.dirX = -1 if not self.invert else +1
                    self.dirY = 0
                    if onBlock and not self.blocIsWalkable(self.dirX, self.dirY):
                        self.setStatus(PenguinStatus.IDLE)

                if keyDown[Key.GAME_RIGHT]:
                    self.dirX = 1 if not self.invert else -1
                    self.dirY = 0
                    if onBlock and not self.blocIsWalkable(self.dirX, self.dirY):
                        self.setStatus(PenguinStatus.IDLE)

            if (self.posX % BLOC_SIZE) == 0:  # Cannot change Y direction if not aligned on bloc horizontally
                if keyDown[Key.GAME_UP]:
                    self.dirX = 0
                    self.dirY = -1 if not self.invert else +1
                    if onBlock and not self.blocIsWalkable(self.dirX, self.dirY):
                        self.setStatus(PenguinStatus.IDLE)

                if keyDown[Key.GAME_DOWN]:
                    self.dirX = 0
                    self.dirY = 1 if not self.invert else -1
                    if onBlock and not self.blocIsWalkable(self.dirX, self.dirY):
                        self.setStatus(PenguinStatus.IDLE)

            if not keyDown[Key.GAME_PUSH]:
                self.pushElectricBorder = False
                self.pushCounter = 0
            elif askMove and onBlock:
                # Check if there is a bloc to push
                if (self.dirX != 0 or self.dirY != 0) and (self.getBlocOnDir(self.dirX, self.dirY) < 24):
                    self.pushBloc()
                elif self.pushCounter == 0:  # Stop pushing
                    self.setStatus(PenguinStatus.IDLE)
                    self.pushElectricBorder = False

        if (self.status == PenguinStatus.PUSH) and (not askMove or not keyDown[Key.GAME_PUSH]):
            self.setStatus(PenguinStatus.IDLE)
            self.pushElectricBorder = False
            self.pushCounter = 0

        if (self.status == PenguinStatus.IDLE) and (self.dirX != 0 or self.dirY != 0) and askMove:
            if self.blocIsWalkable(self.dirX, self.dirY):
                self.setStatus(PenguinStatus.WALK)

        if self.status == PenguinStatus.WALK:
            self.posX += self.dirX * PENG_WALK_STEP
            self.posY += self.dirY * PENG_WALK_STEP
            if self.isOnBlock():  # Stop walking at next block
                if not askMove:
                    self.setStatus(PenguinStatus.IDLE)
                elif not self.blocIsWalkable(self.dirX, self.dirY):
                    self.setStatus(PenguinStatus.IDLE)

        if (self.status in [PenguinStatus.DIE, PenguinStatus.ZAPPED]) and (self.animPhase >= DIE_DURATION):
            # Re-birth
            self.setStatus(PenguinStatus.IDLE)
            self.animPhase = 0
            self.ghost = 60
            # Snap to grid
            self.posX = ((self.posX + BLOC_SIZE // 2) // BLOC_SIZE) * BLOC_SIZE
            self.posY = ((self.posY + BLOC_SIZE // 2) // BLOC_SIZE) * BLOC_SIZE
            # Find a free cell to place the penguin
            while not self.blocIsWalkable(0, 0):
                self.posX = (self.posX + BLOC_SIZE) % (SCHEME_WIDTH*BLOC_SIZE)
                if self.posX == 0:
                    self.posY = (self.posY + BLOC_SIZE) % (SCHEME_HEIGHT*BLOC_SIZE)

        self.anim = self.getPenguinAnimOffset()
        self.animPhase += 1

        # Move camera to follow main penguin, and clamp its position
        if mainPenguin and not globals.isRevenge:
            offsetX = self.posX + 8 - globals.baseX - (BLOCS_RANGE * BLOC_SIZE) // 2
            if offsetX < -PENG_WALK_STEP:
                globals.baseX -= PENG_WALK_STEP * 2  # Fast move speed
            elif offsetX < 0:
                globals.baseX -= PENG_WALK_STEP  # Normal move speed
            elif offsetX > PENG_WALK_STEP:
                globals.baseX += PENG_WALK_STEP * 2
            elif offsetX > 0:
                globals.baseX += PENG_WALK_STEP

            offsetY = self.posY + 8 - globals.baseY - (BLOCS_RANGE * BLOC_SIZE) // 2
            if offsetY < -PENG_WALK_STEP:
                globals.baseY -= PENG_WALK_STEP * 2
            elif offsetY < 0:
                globals.baseY -= PENG_WALK_STEP
            elif offsetY > PENG_WALK_STEP:
                globals.baseY += PENG_WALK_STEP * 2
            elif offsetY > 0:
                globals.baseY += PENG_WALK_STEP

        MAX_X = (48 - BLOCS_RANGE) * BLOC_SIZE - 4  # In pixels
        MAX_Y = (48 - BLOCS_RANGE) * BLOC_SIZE - 4

        globals.baseX = pygame.math.clamp(globals.baseX, 0, MAX_X)
        globals.baseY = pygame.math.clamp(globals.baseY, 0, MAX_Y)

        # Check teleporters

        if self.isOnBlock() and self.canTeleport:
            found = self.getNextTeleportIndex()
            if found != NONE:
                debugPrint('Teleporter found : ' + str(found))
                newPosX = found % SCHEME_WIDTH
                newPosY = found // SCHEME_WIDTH
                self.posX = newPosX * BLOC_SIZE
                self.posY = newPosY * BLOC_SIZE
                audio.playSFX(Sfx.TELEPORT)
                self.canTeleport = False

        # Update crushed bloc

        if self.crushBlocWhat != NONE:
            self.crushBlocTimer -= 1
            if self.crushBlocTimer == 0:
                self.crushBlocWhat = NONE

            # Update occupyTable
            blocIndex = self.crushBlocPosX // BLOC_SIZE + (self.crushBlocPosY // BLOC_SIZE) * SCHEME_WIDTH
            # Cell is forbidden until bloc is crushed
            globals.occupyTable[blocIndex] = 0b10 if self.crushBlocTimer > 3 else 0

        # Update bomb anim

        if self.bombTimer > 0:
            self.bombTimer -= 1

        # Update moving bloc

        if self.movBlocWhat != NONE:

            if (self.movBlocPosX % BLOC_SIZE == 0) and (self.movBlocPosY % BLOC_SIZE == 0):
                bx = self.movBlocPosX // BLOC_SIZE
                by = self.movBlocPosY // BLOC_SIZE
                nextBloc = globals.getBloc(bx + self.movBlocDirX, by + self.movBlocDirY)
                if nextBloc < 24:
                    debugPrint('End of bloc travel. Killed ' + str(self.movMonsters) + ' monsters.')

                    killBloc = (self.movBlocWhat == Bloc.GREEN_CHEM)
                    if self.movBlocWhat == Bloc.ALU:
                        if (globals.getBloc(bx + 1, by) == Bloc.ELECTRO) or (globals.getBloc(bx - 1, by) == Bloc.ELECTRO) or \
                                (globals.getBloc(bx, by - 1) == Bloc.ELECTRO) or (globals.getBloc(bx, by + 1) == Bloc.ELECTRO):
                            killBloc = True  # Kill ALU when launched against electro border

                    if not killBloc:
                        globals.writeBloc(bx, by, self.movBlocWhat)

                        if self.movBlocWhat == Bloc.CYCLONE:
                            # Insert it back in the cyclonesList
                            for index in range(0, len(globals.cyclonesList)):
                                if globals.cyclonesList[index] == 0:
                                    globals.cyclonesList[index] = bx + by * SCHEME_WIDTH
                                    break

                        if self.movBlocWhat == Bloc.DIAMOND:
                            if not globals.diamondsAssembled and self.checkSquareDiamond(bx, by):
                                debugPrint('Square Diamond assembled')
                                audio.playSFX(Sfx.DIAMOND)
                                self.addScore(500)
                                globals.diamondsAssembled = True  # This bonus can be obtained only once per level
                    else:
                        points = globals.destroyBloc(self.movBlocWhat)
                        self.addScore(points)
                        audio.playSFX(Sfx.SPLATCH)
                        # Start crush animation
                        self.startCrushAnim(self.movBlocWhat, self.movBlocPosX, self.movBlocPosY)

                    # Stop moving bloc animation
                    self.movBlocWhat = NONE
                    self.movBlocDirX = 0
                    self.movBlocDirY = 0
                    self.movBonusTimer = 60 if self.movMonsters > 0 else 0

                    self.addScore(BONUS_KILL[pygame.math.clamp(self.movMonsters, 0, len(BONUS_KILL) - 1)])

            self.movBlocPosX += self.movBlocDirX * MOVBLOC_STEP
            self.movBlocPosY += self.movBlocDirY * MOVBLOC_STEP

        if self.ghost > 0:
            self.ghost -= 1

        # If penguin can die, check collision with alive monsters
        if (self.status != PenguinStatus.DIE) and (self.status != PenguinStatus.ZAPPED) and (self.ghost == 0):
            for m in monsters:
                if m.isAlive() and (abs(m.posX - self.posX) <= 8) and (abs(m.posY - self.posY) <= 8):
                    self.die()
                    break

        if self.status != PenguinStatus.ZAPPED:
            for pen in globals.penguins:
                if pen != self and pen.movBlocWhat != NONE:
                    deltaX = abs(pen.movBlocPosX - self.posX)
                    deltaY = abs(pen.movBlocPosY - self.posY)
                    if (deltaX <= 10) and (deltaY <= 10):
                        debugPrint('Zap penguin')
                        self.zap()
                        break

    def addScore(self, points):
        self.points += points

    def addPointsToScore(self):
        self.score += self.points  # Apply unaccounted points (if any)
        self.points = 0
