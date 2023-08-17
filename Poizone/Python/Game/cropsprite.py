from constants import BLOC_SIZE, BLOCS_RANGE

class CropSprite():
    def __init__(self, posX, posY, widthRegion = BLOC_SIZE, heightRegion = BLOC_SIZE):
        self.posX = posX
        self.posY = posY
        self.xRegion = 0
        self.yRegion = 0
        self.widthRegion = widthRegion
        self.heightRegion = heightRegion

        # Clip sprite on game window

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
