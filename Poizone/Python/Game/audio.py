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
    music[Music.INTRO]      = pygame.mixer.Sound('Data/musics/intro.wav')   # Patterns 0-15
    music[Music.REVENGE]    = pygame.mixer.Sound('Data/musics/revenge.wav') # Patterns 16-20
    music[Music.WIN]        = pygame.mixer.Sound('Data/musics/win.wav')     # Patterns 21-26
    music[Music.WIN_GAME]   = pygame.mixer.Sound('Data/musics/winGame.wav') # Patterns 27-29
    music[Music.END]        = pygame.mixer.Sound('Data/musics/endLand.wav') # Pattern 29
    music[Music.PLAY_0]     = pygame.mixer.Sound('Data/musics/play1.wav')   # Patterns 30-35
    music[Music.PLAY_1]     = pygame.mixer.Sound('Data/musics/play2.wav')   # Patterns 36-44
    music[Music.PLAY_2]     = pygame.mixer.Sound('Data/musics/play3.wav')   # Patterns 45-50
    music[Music.PLAY_3]     = pygame.mixer.Sound('Data/musics/play4.wav')   # Patterns 51-56
    music[Music.PLAY_4]     = pygame.mixer.Sound('Data/musics/play5.wav')   # Patterns 57-62

    # Load sounds recorded from SoundTracker: samples indexes from 23 to 35
    sfx[Sfx.READY]    = pygame.mixer.Sound('Data/bruitages/READY.wav')          # 23 (sample N) - START OF LEVEL
    sfx[Sfx.LAUNCH]   = pygame.mixer.Sound('Data/bruitages/LAUNCHBLCK.wav')     # 24 (sample O)
    sfx[Sfx.CRASH]    = pygame.mixer.Sound('Data/bruitages/CRASHblock.wav')     # 25 (sample P)
    sfx[Sfx.BOOM]     = pygame.mixer.Sound('Data/bruitages/BOOM.wav')           # 26 (sample Q) - bomb
    sfx[Sfx.ELEC]     = pygame.mixer.Sound('Data/bruitages/ELECTRIC.wav')       # 27 (sample R) - border
    sfx[Sfx.MAGIC]    = pygame.mixer.Sound('Data/bruitages/MAGIC.wav')          # 28 (sample S)
    sfx[Sfx.DIAMOND]  = pygame.mixer.Sound('Data/bruitages/DIAMOND.wav')   # 29 (sample T) - when 4 diamonds assembled
    # soundFun  = pygame.mixer.Sound('Data/bruitages/Fun.wav')          # 30 (sample U) - (not used in 1-player mode)
    sfx[Sfx.OH_NO]    = pygame.mixer.Sound('Data/bruitages/OH_NO.wav')  # 31 (sample V) - wrong move / death
    sfx[Sfx.ALCOOL]   = pygame.mixer.Sound('Data/bruitages/BEER_BLOCK.wav')  # 32 (sample W)
    sfx[Sfx.COLL]     = pygame.mixer.Sound('Data/bruitages/COLLISION.wav')  # 33 (sample X) - penguin or monster death
    sfx[Sfx.SPLATCH]  = pygame.mixer.Sound('Data/bruitages/SPLATCH.wav')  # 34 (sample Y) - green glass breaking
    sfx[Sfx.WOW]      = pygame.mixer.Sound('Data/bruitages/WOW.wav')    # 35 (sample Z) - END OF LEVEL
    sfx[Sfx.TICK]     = pygame.mixer.Sound('Data/bruitages/TICK.wav')  # New sample (same as R but with higher pitch)
    sfx[Sfx.VALID]    = pygame.mixer.Sound('Data/bruitages/VALIDATE.wav')  # New sample for menus
    sfx[Sfx.TELEPORT] = pygame.mixer.Sound('Data/bruitages/TELEPORT.wav')  # New sample (same as S, with lower pitch)

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


def playMusic(musicId, loop=0):
    debugPrint('playMusic loop=' + str(loop))
    musicChannel = pygame.mixer.Channel(1)
    pygame.mixer.stop()
    musicChannel.play(music[musicId], loop)


def applyChannelVolumes():
    musicChannel = pygame.mixer.Channel(1)
    musicChannel.set_volume(1 if globals.opt.getValue(OPTIONS_ID[1]) else 0)
