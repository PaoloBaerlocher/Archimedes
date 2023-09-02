# POIZONE re-written in Python 3.11, july 2023 (32 years later after the original).
# 2-player mode is not supported.

import pygame
import numpy
import math
import random
from constants import *
import spritesheet
import leaderboard
import particles
import tuto
import texts
from cropsprite import CropSprite
from penguin import *
from monster import *
import globals
from utility import *

# Global variables

running = True
pauseGame = False

gamePhase = Phase.NONE
absTime = 0
windowFade = 0  # 0..255
menuCounter = 0

tutoCounter = 0
currTutoPage = 0

lastKeyDown = NONE

# Global Functions

def resetGame():
    globals.currLevel = 1
    globals.penguin1.score = 0


def displayScore(score, posX, posY):
    base = 10000
    for i in range(0, 5):
        index = (score // base) % 10
        screen.blit(globals.charsSprites_gr[index + 26], (posX + 12 * i, posY))
        base //= 10


def displayPanel():
    panelIdx = NONE

    if pauseGame:
        panelIdx = Panel.PAUSE

    if panelIdx != NONE:
        screen.blit(globals.panelSprites[panelIdx], (ORIGIN_X + WINDOW_WIDTH // 2 - 60 / 2, 30))


# Starting Game phases

def startIntroPhase():
    global gamePhase, windowFade, introTimer, pauseGame

    debugPrint('Phase.INTRO')
    gamePhase = Phase.INTRO
    globals.playMusic(Music.INTRO, -1)
    windowFade = 0
    introTimer = 0
    pauseGame = False


def startMenuPhase():
    global gamePhase, menuCounter, windowFade, pauseGame, menuCursor, subMenu

    debugPrint('Phase.MENU')
    gamePhase = Phase.MENU
    menuCounter = 0
    pauseGame = False
    menuCursor = 0
    subMenu = Menu.MAIN

    # Load sprites for tutos
    globals.currLand = 0
    globals.loadSprites()


def startLevelPhase():
    global gamePhase, windowFade

    debugPrint('Phase.LEVEL')
    gamePhase = Phase.LEVEL
    globals.loadLevel()
    windowFade = 128


def startResultPhase():
    global gamePhase, windowFade, resultTimer, bonus

    debugPrint('Phase.RESULT')
    gamePhase = Phase.RESULT
    windowFade = 200
    resultTimer = 0

    # Compute bonus
    percent = globals.getGoalPercent()
    bonus = 25 * pygame.math.clamp(percent - SUCCESS_GOAL, 0, 100)

    if percent == 100:  # Perfect
        bonus += 500 + 5 * int(globals.gameTimer)  # 1 second = 5 points


def startEndLevelPhase():
    global gamePhase, endOfLevelTimer, windowFade, part, rocketOriginX, rocketOriginY

    debugPrint('Phase.END_LEVEL')
    gamePhase = Phase.END_LEVEL
    endOfLevelTimer = 250
    globals.playMusic(Music.END)
    windowFade = 0

    # Create rocket particles, if needed in this land
    if globals.currLand in [Land.ESA, Land.MOON]:
        rocketOriginX = 70 if globals.currLand == Land.ESA else 105
        rocketOriginY = 60 if globals.currLand == Land.ESA else 35
        part = particles.Particles(rocketOriginX + 28, rocketOriginY + 182, 100)


def startRevengeIntroPhase():
    global gamePhase, windowFade, introTimer

    debugPrint('Phase.REVENGE_INTRO')
    gamePhase = Phase.REVENGE_INTRO
    windowFade = 0
    globals.loadRevenge()
    introTimer = 0


def startRevengeLevelPhase():
    global gamePhase, windowFade

    windowFade = 0
    globals.playMusic(Music.REVENGE)
    debugPrint('Phase.LEVEL')
    gamePhase = Phase.LEVEL


def startGameWonPhase():
    global gamePhase, resultTimer, windowFade

    resultTimer = 0
    debugPrint('Phase.GAME_WON')
    gamePhase = Phase.GAME_WON
    windowFade = 128
    globals.playMusic(Music.WIN_GAME)


def startEnterNamePhase():
    global gamePhase, yourName, cursorTx, cursorTy, cursorPx, cursorPy, resultTimer

    debugPrint('Phase.ENTER_NAME')
    gamePhase = Phase.ENTER_NAME
    yourName = ""
    cursorTx = 0
    cursorTy = 0
    cursorPx = 0  # In pixels
    cursorPy = 0
    resultTimer = 0
    globals.playMusic(Music.WIN, -1)

# HUD

def displayText(font, str, col, text_x, text_y, fx=False):  # Centered
    # Shadow
    text = font.render(str, True, (0, 0, 0))
    textRect = text.get_rect()
    textRect.center = (text_x + 1, text_y + 1)
    screen.blit(text, textRect)

    if not fx:
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
            area = [0, line, textRect.width, 1]

            textRect.center = (text_x, text_y + line)
            screen.blit(text, textRect, area)


def displayTextLeft(font, str, col, text_x, text_y):  # Left-Aligned
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


def displayTextRight(font, str, col, text_x, text_y):  # Right-Aligned
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
    x = 2 if legendIdx == Legend.LEFT else WINDOW_WIDTH - 2 - 20
    screen.blit(globals.legendSprites[legendIdx], (ORIGIN_X + x, ORIGIN_Y + 220))


def displayTuto():
    global tutoCounter, currTutoPage, electrifyBorderAnim

    TITLE_COLOR = (255, 255, 155)
    TEXT_COLOR = (225, 225, 255)
    BORDER_COLOR = (0, 0, 0)

    CENTER_X = ORIGIN_X + WINDOW_WIDTH // 2

    # Title
    displayText(font_big, texts.MAIN_MENU[Menu.TUTORIAL], TITLE_COLOR, CENTER_X, 80, True)

    if currTutoPage == 0:
        y = 105
        for line in texts.TUTO_INTRO:
            displayText(font, line, TEXT_COLOR, CENTER_X, y)
            y += 10

    # Animate electric border if green arrows are displayed
    if (tutoCounter % 32) >= 4 and ((tutoCounter // 64) % 2 == 1):
        globals.electrifyBorderAnim += 1

    if currTutoPage >= 1:
        blocIndex = currTutoPage - 1

        # Bloc Icon
        blocIconIndex = tuto.bloc[blocIndex]
        if blocIconIndex != -1:
            screen.fill(BORDER_COLOR, (CENTER_X - BLOC_SIZE // 2 - 2, 105 - 2, BLOC_SIZE + 4, BLOC_SIZE + 4))
            screen.blit(globals.sprites[0][blocIconIndex], (CENTER_X - BLOC_SIZE // 2, 105))
            y = 135
        else:
            y = 115

        for line in texts.TUTO_BLOC[blocIndex]:
            displayText(font, line, TEXT_COLOR, CENTER_X, y)
            y += 10
        displayTutoMap(blocIndex, 82, 150)

    displayLegend(Legend.LEFT)
    displayLegend(Legend.RIGHT)

    tutoCounter += 1


def displayTutoMap(tutoIndex, offsetX, offsetY):
    global tutoCounter

    offsetX += ORIGIN_X
    offsetY += ORIGIN_Y

    # Mini-map
    globals.currLand = tutoIndex // 2
    if len(tuto.maps[tutoIndex]) == 16:
        FRAME_SIZE = 1
        sz = 4 * BLOC_SIZE + 2 * FRAME_SIZE
        screen.fill((220, 220, 220), (offsetX - FRAME_SIZE, offsetY - FRAME_SIZE, sz, sz))
        screen.fill((20, 20, 20), (offsetX, offsetY, 4 * BLOC_SIZE, 4 * BLOC_SIZE))
        for y in range(0, 4):
            for x in range(0, 4):
                b = tuto.maps[tutoIndex][x + y * 4]
                if b != -1:
                    b = globals.getAliasBlocIndex(b)
                    screen.blit(globals.sprites[0][b], (offsetX + x * BLOC_SIZE, offsetY + y * BLOC_SIZE))

    # Animated arrows (red or green)
    if (tutoCounter % 32) >= 4:
        arrowType = (tutoCounter // 64) % 2
        d = 4 + ((tutoCounter % 32) / 8)  # Animate arrow
        for arrow in tuto.arrows[tutoIndex][arrowType]:
            dir = arrow[2]
            deltaX = offsetX + d * (1 if dir == tuto.DIR_RIGHT else -1 if dir == tuto.DIR_LEFT else 0)
            deltaY = offsetY + d * (1 if dir == tuto.DIR_DOWN else -1 if dir == tuto.DIR_UP else 0)
            screen.blit(globals.arrowsSprites[dir + 4 * arrowType],
                        (deltaX + arrow[0] * BLOC_SIZE, deltaY + arrow[1] * BLOC_SIZE))


def displayControls():
    TITLE_COLOR = (255, 255, 155)
    OPT_COLOR = (180, 255, 255)
    VALUE_COLOR = (195, 195, 195)
    HIGHLIGHT_COLOR = (230, 255, 255)
    DONE_COLOR = (50, 250, 130)

    # Title
    displayText(font_big, texts.MAIN_MENU[Menu.CONTROLS], TITLE_COLOR, ORIGIN_X + WINDOW_WIDTH // 2, 80, True)

    i = 0
    for i in range(0, len(CTRL_ID)):
        y = 120 + 15 * i
        highlight = (ctrlCursor == i)
        col = HIGHLIGHT_COLOR if highlight else OPT_COLOR

        displayTextRight(font, texts.CTRL[i] + " :", col, ORIGIN_X + 100, y)
        if (absTime // 200) % 4 == 0:
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
    displayText(font_big, texts.MAIN_MENU[Menu.OPTIONS], TITLE_COLOR, ORIGIN_X + WINDOW_WIDTH // 2, 80, True)

    for i in range(0, len(OPTIONS_ID)):
        y = 120 + 15 * i
        highlight = (optCursor == i)
        col = HIGHLIGHT_COLOR if highlight else OPT_COLOR
        displayTextRight(font, texts.OPTIONS[i], col, ORIGIN_X + WINDOW_WIDTH // 2, y)

        value =  globals.opt.getValue(OPTIONS_ID[i])
        textValue = texts.VALUES[0 if value else 1]
        col = HIGHLIGHT_COLOR if highlight else VALUE_COLOR
        displayTextLeft(font, textValue, col, ORIGIN_X + WINDOW_WIDTH // 2 + 30, y)

    displayLegend(Legend.LEFT)
    displayLegend(Legend.RIGHT)


def displayCredits():
    TITLE_COLOR = (255, 255, 155)
    TEXT_COLOR = (180, 255, 255)

    # Title
    displayText(font_big, texts.MAIN_MENU[Menu.CREDITS], TITLE_COLOR, ORIGIN_X + WINDOW_WIDTH // 2, 80, True)

    y = 110
    for line in texts.CREDITS:
        displayText(font, line, TEXT_COLOR, ORIGIN_X + WINDOW_WIDTH // 2, y)
        y += 12


def displayMainMenu():
    TEXT_COLOR = (155, 155, 55)
    HIGH_COLOR = (255, 255, 155)
    DEACT_COLOR = (40, 40, 30)

    CENTER_X = ORIGIN_X + WINDOW_WIDTH // 2

    for i in range(0, len(texts.MAIN_MENU)):
        deactivated = isMenuDeactivated(i)
        col = DEACT_COLOR if deactivated else (HIGH_COLOR if (menuCursor == i) else TEXT_COLOR)
        displayText(font, texts.MAIN_MENU[i], col, CENTER_X, 120 + 15 * i)


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

def displayInGameMenu():
    match gamePhase:
        case Phase.RESULT:
            displayResult()
        case Phase.REVENGE_INTRO:
            displayRevengeIntroMode()
        case Phase.GAME_WON:
            displayGameWon()
        case Phase.ENTER_NAME:
            displayEnterYourName()

def displayGameHud():
    WHITE = (255, 255, 255)
    LEVEL_COLOR = (180, 255, 255)
    COMPLETION_COLOR = (255, 255, 180)
    SUCCESS_COLOR = (50, 255, 140)

    HUD_WIDTH = (320 - 244 - 8)
    HUD_CENTER = 320 - HUD_WIDTH / 2

    y = 110

    # Level
    if not globals.isRevenge:
        displayText(font, "ZONE", LEVEL_COLOR, HUD_CENTER, y)
        y += 12
        displayText(font, f"{globals.currLevel:02d}", LEVEL_COLOR, HUD_CENTER, y)
        y += 30

    # Completion
    if not globals.isRevenge:
        percent = globals.getGoalPercent()
        col = COMPLETION_COLOR if percent < SUCCESS_GOAL else SUCCESS_COLOR
        displayText(font, "GOAL", col, HUD_CENTER, y)
        y += 12
        displayText(font, f"{percent:02d} %", col, HUD_CENTER, y)
        y += 30

    # TIME
    displayText(font, 'TIME', WHITE, HUD_CENTER, y)
    y += 12

    # Time value
    seconds = int(globals.gameTimer % 60)
    timeStr = str(int(globals.gameTimer / 60)) + ":" + f"{seconds:02d}"
    displayText(font, timeStr, WHITE, HUD_CENTER, y)


def displayLeaderboard():
    TITLE_COLOR = (255, 255, 155)
    SCORE_COLOR = (225, 250, 200)
    NAME_COLOR = (255, 255, 255)
    LEVEL_COLOR = (55, 155, 155)
    LEGEND_COLOR = (50, 240, 200)

    # Title
    displayText(font_big, texts.MAIN_MENU[Menu.LEADERBOARD], TITLE_COLOR, ORIGIN_X + WINDOW_WIDTH // 2, 80, True)

    # Legend
    displayTextLeft(font, "SCORE       NAME               ZONE", LEGEND_COLOR, 50, 114)

    for index in range(0, leaderboard.LB_MAX_ENTRIES):
        entry = globals.lb.entries[index]

        y = 130 + 9 * index
        score = entry[0]
        name = entry[1]
        level = entry[2]

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
    displayText(font_big, f"END OF ZONE {globals.currLevel}", TITLE_COLOR, ORIGIN_X + WINDOW_WIDTH // 2, 40, True)

    if globals.toxicBlocsLeft == 0:
        if (resultTimer // 8) % 4 != 0:  # Flash FX
            displayText(font_big, "TOTAL", DECONTAMINATED_COLOR, ORIGIN_X + WINDOW_WIDTH // 2, 90, True)
            displayText(font_big, "DECONTAMINATION!", DECONTAMINATED_COLOR, ORIGIN_X + WINDOW_WIDTH // 2, 130, True)
    else:
        displayText(font_big, "DECONTAMINATION:", DECONTAMINATED_COLOR, ORIGIN_X + WINDOW_WIDTH // 2, 80, True)

        percent = globals.getGoalPercent()
        percentDisplay = pygame.math.clamp(percent, 0, resultTimer // 2)
        col = BAD_COLOR if percentDisplay < SUCCESS_GOAL else GOOD_COLOR
        displayText(font_big, f"{percentDisplay} %", col, ORIGIN_X + WINDOW_WIDTH // 2, 130, True)

        if percent < SUCCESS_GOAL and resultTimer >= 200:
            displayText(font_big, "GAME OVER", GAMEOVER_COLOR, ORIGIN_X + WINDOW_WIDTH // 2, 220, True)

    # Time left
    timeLeft = int(globals.gameTimer)
    if timeLeft > 0:
        displayText(font_big, f"TIME LEFT: {timeLeft} s", TIME_LEFT_COLOR, ORIGIN_X + WINDOW_WIDTH // 2, 200, True)

    # Bonus
    displayText(font_big, f"BONUS: {bonus} POINTS", BONUS_COLOR, ORIGIN_X + WINDOW_WIDTH // 2, 180, True)

    if globals.toxicBlocsLeft == 0:
        displayDancingPenguins(resultTimer - 50)


def displayDancingPenguins(d):
    # According to d value:
    # 0..100: move right
    # 100..120: still, upfront
    # 120..140: still, left front
    # 140..160: still, upfront
    # 160..   : move right

    px = d if d < 100 else (100 if d < 160 else d - 60)
    py = 95
    dir = 0 if (d > 100 and d < 120) or (d > 140 and d < 160) else (-1 if (d > 120 and d < 140) else +1)
    for i in range(0, len(dancingPenguins)):
        p = dancingPenguins[i]
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

    if (int(absTime) // 4) % 4 != 0:  # Flash
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

    for ty in range(0, ALPHABET_ROWS):
        for tx in range(0, ALPHABET_COLUMNS):
            charIndex = tx + ty * ALPHABET_COLUMNS
            ch = chr(ord('A') + charIndex)

            if ch == '\\':
                ch = '>'  # Exit

            if ch <= 'Z':
                displayText(font_big, ch, LETTER_COLOR, ORIGIN_X + WINDOW_WIDTH // 2 + (tx - 3) * 25,
                            150 + (ty - 2) * 24)

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
    anim = (absTime // 4) % 4  # The land map has 4 animation frames
    for y in range(0, BLOCS_RANGE + 1):
        for x in range(0, BLOCS_RANGE + 2):

            blocOffset = (baseX // BLOC_SIZE + x) + (baseY // BLOC_SIZE + y) * SCHEME_WIDTH

            if globals.isRevenge:
                index = 24  # Empty land in Revenge mode
            else:
                index = int(globals.lands[globals.currLand][4 * blocOffset + anim])

            if blocOffset < SCHEME_SIZE:
                blocOfSchemes = globals.scheme[blocOffset]
                if blocOfSchemes < 24:
                    index = blocOfSchemes

            posX = x * BLOC_SIZE - (baseX % BLOC_SIZE)
            posY = y * BLOC_SIZE - (baseY % BLOC_SIZE)

            c = CropSprite(posX, posY)
            index = globals.getAliasBlocIndex(index)
            blitGameSprite(screen, globals.sprites[0][index], c)


def displayEndLevel():
    screen.blit(globals.endScreenSprite, (ORIGIN_X, ORIGIN_Y))

    # Penguin and 3 Monsters animation
    yByLand = [190, 210, 190, 135, 138]
    dirByLand = [-1, -1, -1, -1, +1]
    limitMinXByLand = [145, 140, 160, 140, -20]
    limitMaxXByLand = [500, 500, 500, 500, 70]
    monstersNb = 2 if globals.currLand == Land.COMPUTER else 3

    x = 20 + endOfLevelTimer if globals.currLand != Land.COMPUTER else 250 - endOfLevelTimer
    y = yByLand[globals.currLand]
    dir = dirByLand[globals.currLand]
    limitMinX = limitMinXByLand[globals.currLand]
    limitMaxX = limitMaxXByLand[globals.currLand]
    baseX = 0
    baseY = 0
    mx = pygame.math.clamp(x, limitMinX, limitMaxX)

    # Show Penguin
    if globals.currLand in [Land.ICE, Land.JUNGLE, Land.COMPUTER]:

        if globals.currLand == Land.COMPUTER:
            px = x + 60  # Penguin on the right side of monsters
            py = y

            if px >= 90:  # Jump parabola
                dy = math.pow(px - 90, 2) / 15
                py += pygame.math.clamp(dy, 0, 50)
        else:
            px = x - 40  # Penguin on the left side of monsters
            py = y

        if globals.currLand == Land.ICE:
            if (px >= 120) and (px <= 150):  # Jump parabola
                py -= (15 * 15 - math.pow(px - 135, 2)) / 15

        p = globals.penguin1
        p.status = PenguinStatus.WALK
        p.posX = px
        p.posY = py
        p.dirX = dir
        p.dirY = 0
        p.anim = p.getPenguinAnimOffset()
        p.animPhase += 1
        p.display(screen, 0, 0)

    # Show monsters
    for index in range(0, monstersNb):
        m = globals.monsters[index]
        m.posX = mx + 25 * index
        m.posY = y
        m.dirX = dir
        m.dirY = 0
        m.counter = 1000 - endOfLevelTimer + 16 * index
        m.display(screen, 0, 0)

    # Show Rocket
    if globals.currLand in [Land.ESA, Land.MOON]:
        propelY = pow(250 - endOfLevelTimer, 2) / 250
        c = CropSprite(rocketOriginX, rocketOriginY - propelY, globals.rocket.get_width(), globals.rocket.get_height())
        blitGameSprite(screen, globals.rocket, c)
        part.originY = ORIGIN_Y + c.posY + c.heightRegion
        part.update(1. / 60.)  # TODO: should be dt
        part.display(screen, ORIGIN_X, ORIGIN_Y, WINDOW_WIDTH, WINDOW_HEIGHT)

    # For COMPUTER level: redraw a part of the disk drive, over monsters
    if glboals.currLand == Land.COMPUTER:
        screen.blit(globals.endScreenSprite, (ORIGIN_X, ORIGIN_Y + 138), (0, 138, 17 * 4, 20))


def applyFade():
    if windowFade > 0:
        blackSurface.fill((0, 0, 0, windowFade))
        screen.blit(blackSurface, (ORIGIN_X, ORIGIN_Y))


def isMenuDeactivated(index):
    return index == Menu.CONTINUE and globals.maxLevelReached == 1


##########################
# MAIN PROGRAM STARTS HERE
##########################

# pygame setup
pygame.init()
pygame.display.set_caption('Poizone')
pygame.mixer.init()  # Initialize the mixer module.
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SCALED)
clock = pygame.time.Clock()

globals.loadSettings()

# For fade effect
blackSurface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
blackSurface.fill((0, 0, 0, 128))

# Load Fonts
font = pygame.font.Font('Data/font/small/8-bit-hud.ttf', 5)
font_big = pygame.font.Font('Data/font/big/VCR_OSD_MONO_1.001.ttf', 20)

globals.initAudio()
globals.initLandsAndTeleporters()
globals.loadSpriteSheets()
globals.initPenguin()

# Three dancing penguins, for result screen
dancingPenguins = [Penguin(), Penguin(), Penguin()]
dancingPenguins[1].animPhase += 8

# Init input
keyDown = [False] * Key.NB
keyPressed = [False] * Key.NB

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
        prevGameTimer = globals.gameTimer
        globals.gameTimer -= dt / 1000
        if globals.gameTimer < 0.0:
            globals.gameTimer = 0.0

        # Warning sound for last seconds before time runs out
        for tick in range(1, 6):
            if (prevGameTimer >= tick) and (globals.gameTimer <= tick):
                globals.playSFX(Sfx.TICK)

    #######
    # INPUT
    #######

    oldKeyDown = keyDown.copy()

    if joyFound != NONE:
        # Test joystick stick
        x_axis = joy.get_axis(0)
        y_axis = joy.get_axis(1)

        # D-pad
        hat = joy.get_hat(0)
        x_axis += hat[0]
        y_axis -= hat[1]

        # X

        if x_axis > JOY_LIMIT:
            keyDown[Key.RIGHT] = keyDown[Key.GAME_RIGHT] = True

        if x_axis < -JOY_LIMIT:
            keyDown[Key.LEFT] = keyDown[Key.GAME_LEFT] = True

        if (x_axis < JOY_LIMIT) and (old_x_axis >= JOY_LIMIT):
            keyDown[Key.RIGHT] = keyDown[Key.GAME_RIGHT] = False

        if (x_axis > -JOY_LIMIT) and (old_x_axis <= -JOY_LIMIT):
            keyDown[Key.LEFT] = keyDown[Key.GAME_LEFT] = False

        # Y

        if y_axis > JOY_LIMIT:
            keyDown[Key.DOWN] = keyDown[Key.GAME_DOWN] = True

        if y_axis < -JOY_LIMIT:
            keyDown[Key.UP] = keyDown[Key.GAME_UP] = True

        if (y_axis < JOY_LIMIT) and (old_y_axis >= JOY_LIMIT):
            keyDown[Key.DOWN] = keyDown[Key.GAME_DOWN] = False

        if (y_axis > -JOY_LIMIT) and (old_y_axis <= -JOY_LIMIT):
            keyDown[Key.UP] = keyDown[Key.GAME_UP] = False

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
                keyDown[Key.SPACE] = buttonIsDown
                keyDown[Key.GAME_PUSH] = buttonIsDown
            if event.button == 1 and gamePhase != Phase.LEVEL:  # B button only used in menus
                keyDown[Key.ESCAPE] = buttonIsDown
            elif event.button == 6:
                keyDown[Key.ESCAPE] = buttonIsDown
            elif event.button == 7:
                keyDown[Key.PAUSE] = buttonIsDown
            else:
                debugPrint('Unhandled JOY button ' + str(event.button))

        if event.type == pygame.KEYUP or event.type == pygame.KEYDOWN:

            if event.type == pygame.KEYDOWN:
                lastKeyDown = event.key

            down = (event.type == pygame.KEYDOWN)

            # MENU KEYS processing
            for keyPair in MENU_KEYS:
                if event.key == keyPair[1]:
                    keyDown[keyPair[0]] = down

            # GAME KEYS processing
            for keyPair in GAME_KEYS:
                if event.key == globals.opt.getValue(keyPair[1]):
                    keyDown[keyPair[0]] = down

            if not down:

                # Cheat
                if event.key == pygame.K_F5:  # Prev level
                    if globals.currLevel > 1:
                        globals.currLevel -= 1
                        globals.loadLevel()

                if event.key == pygame.K_F6:  # Next level
                    if globals.currLevel < LEVELS_NB:
                        globals.currLevel += 1
                        globals.loadLevel()

                if DEBUG_FEATURES:

                    if event.key == pygame.K_F7:  # Prev revenge map
                        if globals.currLevel > 5:
                            globals.currLevel -= 5
                            startRevengeIntroPhase()

                    if event.key == pygame.K_F8:  # Next revenge map
                        if globals.currLevel < LEVELS_NB-5:
                            globals.currLevel += 5
                            startRevengeIntroPhase()

    for i in range(0, len(keyDown)):
        keyPressed[i] = (keyDown[i] and not oldKeyDown[i])

    if keyPressed[Key.PAUSE]:  # Pause game
        if gamePhase == Phase.LEVEL:
            pauseGame = not pauseGame

    if keyPressed[Key.ESCAPE]:
        if gamePhase == Phase.LEVEL:
            startIntroPhase()
        elif gamePhase == Phase.INTRO:
            running = False
        elif gamePhase == Phase.MENU:
            if subMenu == Menu.MAIN:
                startIntroPhase()
            else:
                subMenu = Menu.MAIN  # Return to Main Menu
            globals.playSFX(Sfx.VALID)

    if gamePhase == Phase.INTRO:
        introTimer += 1
        if keyPressed[Key.SPACE] or keyPressed[Key.RETURN]:
            startMenuPhase()
            globals.playSFX(Sfx.VALID)
    elif gamePhase == Phase.MENU:
        menuCounter += 1
        if windowFade < 160:
            windowFade += 16

        # Main Menu navigation
        if subMenu == Menu.MAIN:
            if keyPressed[Key.DOWN] and menuCursor < 6:
                menuCursor += 1
                while isMenuDeactivated(menuCursor):
                    menuCursor += 1
                globals.playSFX(Sfx.VALID)

            if keyPressed[Key.UP] and menuCursor > 0:
                menuCursor -= 1
                while isMenuDeactivated(menuCursor):
                    menuCursor -= 1
                globals.playSFX(Sfx.VALID)

            if keyPressed[Key.SPACE] or keyPressed[Key.RETURN]:
                if menuCursor == Menu.PLAY or menuCursor == Menu.CONTINUE:
                    resetGame()

                    if menuCursor == Menu.CONTINUE:
                        globals.currLevel = globals.maxLevelReached

                    startLevelPhase()
                else:
                    subMenu = menuCursor

                    if subMenu == Menu.OPTIONS:
                        optCursor = 0
                    if subMenu == Menu.CONTROLS:
                        controlsCounter = 0
                        ctrlCursor = 0
                        lastKeyDown = NONE  # To avoid using unwanted SPACE key event
                        tmpKeys = []
                        for i in range(0, len(CTRL_ID)):
                            tmpKeys.append(globals.opt.getValue((CTRL_ID[i])))
                    if subMenu == Menu.TUTORIAL:
                        tutoCounter = 0
                        currTutoPage = 0

                    globals.playSFX(Sfx.VALID)

        elif subMenu == Menu.TUTORIAL:
            if keyPressed[Key.LEFT]:
                currTutoPage = (currTutoPage + TUTO_PAGES - 1) % TUTO_PAGES
                tutoCounter = 0
                globals.playSFX(Sfx.VALID)

            if keyPressed[Key.RIGHT]:
                currTutoPage = (currTutoPage + 1) % TUTO_PAGES
                tutoCounter = 0
                globals.playSFX(Sfx.VALID)

        elif subMenu == Menu.OPTIONS:
            if keyPressed[Key.DOWN] and optCursor < 1:
                optCursor += 1
                globals.playSFX(Sfx.VALID)

            if keyPressed[Key.UP] and optCursor > 0:
                optCursor -= 1
                globals.playSFX(Sfx.VALID)

            if keyPressed[Key.SPACE] or keyPressed[Key.RETURN] or keyPressed[Key.LEFT] or keyPressed[Key.RIGHT]:
                # Invert value
                globals.opt.setValue(OPTIONS_ID[optCursor], not globals.opt.getValue(OPTIONS_ID[optCursor]))
                globals.opt.save()
                globals.applyChannelVolumes()
                globals.playSFX(Sfx.VALID)

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
                    tmpKeys[ctrlCursor] = lastKeyDown
                    ctrlCursor += 1
                    globals.playSFX(Sfx.VALID)
                    if ctrlCursor == len(CTRL_ID):
                        # Setup all keys at once
                        for i in range(0, ctrlCursor):
                            globals.opt.setValue(CTRL_ID[i], tmpKeys[i])
                        globals.opt.save()
                        controlsCounter = 90  # Wait a bit before quitting page
                else:
                    debugPrint('Invalid choice - key already used.')

                lastKeyDown = NONE

    elif gamePhase == Phase.LEVEL and not pauseGame:

        # Fade out
        if windowFade > 0:
            windowFade -= 16
            windowFade = pygame.math.clamp(windowFade, 0, 255)

        # Animate electric border, if pushed
        if globals.electrifyBorder:
            globals.electrifyBorderAnim += 1

        # Update blocs around cyclones
        globals.updateCyclones()

        # Update Penguin
        globals.penguin1.update(keyDown, globals.monsters)

        # Update Monsters
        for m in globals.monsters:
            m.update()

        # Check end of game
        if (globals.gameTimer <= 0.0) or ((globals.toxicBlocsLeft == 0) and not globals.isRevenge):

            if globals.isRevenge:
                if globals.currLevel >= LEVELS_NB:  # End of game reached!
                    startGameWonPhase()
                else:
                    gamePhase = Phase.LEVEL  # Move to next level
                    globals.currLevel += 1  # End of level - display results
                    globals.loadLevel()
            else:
                if globals.toxicBlocsLeft == 0:
                    globals.playSFX(Sfx.WOW)

                startResultPhase()

    elif gamePhase == Phase.RESULT:
        resultTimer += 1
        if resultTimer > 60 * 8:
            percent = globals.getGoalPercent()
            gameOver = (percent < SUCCESS_GOAL)
            globals.penguin1.score += bonus  # Take bonus into account
            globals.penguin1.addPointsToScore()

            debugPrint(f"percent: {percent} gameOver : {gameOver}")

            if gameOver:
                if globals.lb.canEnter(globals.penguin1.score):
                    startEnterNamePhase()
                else:
                    startMenuPhase()
                    globals.playMusic(Music.INTRO, -1)

                # Store level for Continue
                globals.maxLevelReached = max(globals.currLevel, globals.maxLevelReached)

            else:
                startEndLevelPhase()

    elif gamePhase == Phase.REVENGE_INTRO:

        if windowFade < 128:
            windowFade += 16

        introTimer += 1

        if keyPressed[Key.GAME_PUSH] or (introTimer > 60 * 4):
            startRevengeLevelPhase()

    elif gamePhase == Phase.GAME_WON:
        resultTimer += 1
        if resultTimer > 60 * 21:  # Match music duration
            startMenuPhase()
            globals.playMusic(Music.INTRO, -1)

    elif gamePhase == Phase.ENTER_NAME:
        resultTimer += 1
        quitEnterName = False

        if keyPressed[Key.LEFT]:
            cursorTx = (cursorTx + ALPHABET_COLUMNS - 1) % ALPHABET_COLUMNS
        if keyPressed[Key.RIGHT]:
            cursorTx = (cursorTx + 1) % ALPHABET_COLUMNS
        if keyPressed[Key.UP]:
            cursorTy = (cursorTy + ALPHABET_ROWS - 1) % ALPHABET_ROWS
        if keyPressed[Key.DOWN]:
            cursorTy = (cursorTy + 1) % ALPHABET_ROWS
        if keyPressed[Key.SPACE]:
            ch = chr(ord('A') + cursorTx + cursorTy * ALPHABET_COLUMNS)
            if ch == '\\' and len(yourName) > 0:
                quitEnterName = True
            elif len(yourName) < leaderboard.LB_MAX_NAME_LENGTH:
                if ch <= 'Z':
                    yourName += ch
                else:
                    yourName += ' '
                globals.playSFX(Sfx.VALID)

        if keyPressed[Key.BACKSPACE]:
            if len(yourName) > 0:
                yourName = yourName[:-1]
                globals.playSFX(Sfx.VALID)

        if keyPressed[Key.RETURN] or quitEnterName:
            globals.lb.add(globals.penguin1.score, yourName, globals.currLevel)
            globals.lb.save()  # Add new entry and save leaderboard
            startMenuPhase()

    #########
    # DISPLAY
    #########

    # Fill the screen with a color to wipe away anything from last frame
    screen.fill("black")
    screen.blit(globals.border, (0, 0))

    match gamePhase:
        case Phase.INTRO:
            screen.blit(globals.startScreen, (ORIGIN_X, ORIGIN_Y))

            if (introTimer // 16) % 4 != 0:
                displayText(font, "Press START", (215, 235, 125), ORIGIN_X + WINDOW_WIDTH // 2, 230)

        case Phase.MENU:
            screen.blit(globals.startScreen, (ORIGIN_X, ORIGIN_Y))

            applyFade()
            displayMenu()

        case Phase.END_LEVEL:

            displayEndLevel()

            if endOfLevelTimer > 0:
                endOfLevelTimer -= 1
            else:
                if globals.currLevel % 5 == 0:
                    startRevengeIntroPhase()
                else:
                    globals.currLevel += 1
                    startLevelPhase()

        case _:  # other phases where game map is displayed (Phase.LEVEL, Phase.RESULT, Phase.REVENGE_INTRO, etc)

            # Draw Background Map
            displayBGMap(globals.baseX, globals.baseY)

            # Display Penguin
            globals.penguin1.display(screen, globals.baseX, globals.baseY)

            # Display Monsters
            for m in globals.monsters:
                m.display(screen, globals.baseX, globals.baseY)

            # Display moving bloc and bonus, if any
            globals.penguin1.displayBloc(screen, globals.baseX, globals.baseY)

            applyFade()

            # Display in-game menu over game
            displayInGameMenu()

            # Display HUD (in the panel on the right side)
            displayGameHud()

    # Display Player Score
    displayScore(globals.penguin1.score, 256, 45)

    # Display panel (PAUSE)
    displayPanel()

    # flip() the display to put your work on screen
    pygame.display.flip()

    clock.tick(60)  # limits FPS to 60

pygame.quit()
