import pygame
from constants import *
import globals
from utility import *

# Sound/Music
def init():

    global music, sfx

    music = [None] * Music.NB
    sfx = [None] * Sfx.NB

    # Load musics recorded from SoundTracker

    musicList = [
        [Music.INTRO,   'intro.wav'],   # Patterns 0-15
        [Music.REVENGE, 'revenge.wav'], # Patterns 16-20
        [Music.WIN,     'win.wav'],     # Patterns 21-26
        [Music.WIN_GAME,'winGame.wav'], # Patterns 27-29
        [Music.END,     'endLand.wav'], # Pattern 29
        [Music.PLAY_0,  'play1.wav'],   # Patterns 30-35
        [Music.PLAY_1,  'play2.wav'],   # Patterns 36-44
        [Music.PLAY_2,  'play3.wav'],   # Patterns 45-50
        [Music.PLAY_3,  'play4.wav'],   # Patterns 51-56
        [Music.PLAY_4,  'play5.wav']    # Patterns 57-62
    ]

    for m in musicList:
        music[m[0]] = pygame.mixer.Sound('Data/musics/' + m[1])

    # Load sounds recorded from SoundTracker: samples indexes from 23 to 35

    sfxList = [
        [ Sfx.READY,    'READY.wav'],           # 23 (sample N) - START OF LEVEL
        [ Sfx.LAUNCH,   'LAUNCHBLCK.wav'],      # 24 (sample O)
        [ Sfx.CRASH,    'CRASHblock.wav'],      # 25 (sample P)
        [ Sfx.BOOM,     'BOOM.wav'],            # 26 (sample Q) - bomb
        [ Sfx.ELEC,     'ELECTRIC.wav'],        # 27 (sample R) - border
        [ Sfx.MAGIC,    'MAGIC.wav'],           # 28 (sample S)
        [ Sfx.DIAMOND,  'DIAMOND.wav'],         # 29 (sample T) - when 4 diamonds assembled
        # soundFun  = 'Fun.wav')                # 30 (sample U) - (not used in 1-player mode)
        [ Sfx.OH_NO,    'OH_NO.wav'],           # 31 (sample V) - wrong move / death
        [ Sfx.ALCOOL,   'BEER_BLOCK.wav'],      # 32 (sample W)
        [ Sfx.COLL,     'COLLISION.wav'],       # 33 (sample X) - penguin or monster death
        [ Sfx.SPLATCH,  'SPLATCH.wav'],         # 34 (sample Y) - green glass breaking
        [ Sfx.WOW,      'WOW.wav'],             # 35 (sample Z) - END OF LEVEL
        [ Sfx.TICK,     'TICK.wav'],            # New sample (same as R but with higher pitch)
        [ Sfx.VALID,    'VALIDATE.wav'],        # New sample for menus
        [ Sfx.TELEPORT, 'TELEPORT.wav']         # New sample (same as S, with lower pitch)
    ]

    for s in sfxList:
        sfx[s[0]] = pygame.mixer.Sound('Data/bruitages/' + s[1])

    # Set volumes

    sfx[Sfx.CRASH].set_volume(0.5)
    sfx[Sfx.ELEC].set_volume(0.8)
    sfx[Sfx.LAUNCH].set_volume(0.3)
    sfx[Sfx.MAGIC].set_volume(0.2)
    sfx[Sfx.SPLATCH].set_volume(0.5)
    sfx[Sfx.TICK].set_volume(0.7)
    sfx[Sfx.VALID].set_volume(0.3)
    sfx[Sfx.TELEPORT].set_volume(0.5)

    applyChannelVolumes()


def playSFX(sfxId, loop=0):
    if globals.opt.getValue(OPTIONS_ID[0]):
        sfx[sfxId].play(loop)


def stopSFX(sfxId):
    sfx[sfxId].stop()


def playMusic(musicId, loop=0):
    debugPrint('playMusic loop=' + str(loop))
    musicChannel = pygame.mixer.Channel(1)
    pygame.mixer.stop()
    musicChannel.play(music[musicId], loop)


def applyChannelVolumes():
    musicChannel = pygame.mixer.Channel(1)
    musicChannel.set_volume(1 if globals.opt.getValue(OPTIONS_ID[1]) else 0)
