from constants import *

# Utility functions

def blitGameSprite(screen, sprite, cropSprite):
    screen.blit(sprite, (ORIGIN_X + cropSprite.posX, ORIGIN_Y + cropSprite.posY), cropSprite.getCroppedRegion())


def debugPrint(text):
    if DEBUG_FEATURES:
        print(text)
