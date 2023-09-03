import pygame
import random

# In pixels
GROUND = 242
FX_WIDTH = 16

# A particle FX customized for rocket propulsion
class Particles(object):

    particles = []

    def createNewParticle(self):
        px = self.originX + random.randrange(-FX_WIDTH, +FX_WIDTH)
        py = self.originY
        vx = random.randrange(-150, +150) / 10.0
        vy = random.randrange(0, +300) / 10.0
        life = 20 + random.randrange(0, 30)

        t = 0.5 - (px - self.originX) / (2*FX_WIDTH)                # Interpolator
        color = (int(235 + 20 * t), int(255 * t), int(255 * t))     # Between red and white

        return [px, py, vx, vy, life, color]

    def __init__(self, originX, originY, particlesNumber):

        self.originX = originX
        self.originY = originY
        self.particles = []

        for i in range(0, particlesNumber):
            self.particles.append(self.createNewParticle())

    def update(self, dt):
        for p in self.particles:
            if p[4] <= 0:
                self.particles.remove(p)
                self.particles.append(self.createNewParticle())
            else:
                p[0] += p[2] * dt
                p[1] += p[3] * dt
                p[4] -= 1
                if p[1] > GROUND:     # Bounce on ground (vy = -vy)
                    p[3] = -p[3] * 0.8
                p[3] += 0.05            # Gravity

    def display(self, surface, minX, minY, width, height):
        for p in self.particles:
            x = int(p[0])
            y = int(p[1])
            if (x >= minX and x < minX + width) and (y >= minY and y < minY + height):
                surface.set_at((x, y), p[5])
