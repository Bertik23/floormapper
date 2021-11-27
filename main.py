import pygame as pg
from pygame.locals import RESIZABLE
import math
from math import cos, sin
import numpy as np

from pygame.transform import threshold

pg.init()

ONE = (1, 1, 1, 255)
# COLORS
WHITE = (255, 255, 255, 255)
BLACK = (0, 0, 0, 255)
GREEN = (0, 255, 0, 255)
PINK = (255, 0, 255, 255)
# COLORS END

window = pg.display.set_mode((800, 600), RESIZABLE)


class Floor:
    def __init__(
            self,
            size: tuple[int, int],
            objects: dict[str, list[tuple[int, int]]]
            ):
        self.size = size
        self.objects = objects
        self.mask = None
        for object, value in objects.items():
            if getattr(self, object, None) is None:
                setattr(self, object, value)

    def render(self, surface: pg.Surface):
        surface.fill(BLACK)
        for object in self.objects.values():
            pg.draw.lines(surface, WHITE, True, object)

        self.mask = pg.mask.from_threshold(surface, WHITE, (1, 1, 1, 255))


class Bot:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.rotation = math.pi
        self.proximitySensorLen = 50
        self.proximitySensor = None
        self.surface = None
        self.mask = None
        self.maxSpeed = 0.5
        self.colSpeed = 0.1
        self.speed = 0.1
        self.size = 10
        self.reversingTimer = 0

    def render(self, surface: pg.Surface):
        sensorEdges = [
            (self.x+self.size*cos(self.rotation),
             self.y-self.size*sin(self.rotation)),
            (self.x
             + self.size*cos(self.rotation)
             + self.proximitySensorLen*sin(self.rotation),
             self.y
             - self.size*sin(self.rotation)
             + self.proximitySensorLen*cos(self.rotation)),
            (self.x
             - self.size*cos(self.rotation)
             + self.proximitySensorLen*sin(self.rotation),
             self.y
             + self.size*sin(self.rotation)
             + self.proximitySensorLen*cos(self.rotation)),
            (self.x-self.size*cos(self.rotation),
             self.y+self.size*sin(self.rotation))
        ]
        self.sensorRect = pg.draw.lines(surface, PINK, True, sensorEdges)

        self.proximitySensor = pg.mask.from_threshold(surface, PINK, ONE)

        self.surface = surface.subsurface(
            pg.Rect(
                self.x-self.size,
                self.y-self.size,
                2*self.size,
                2*self.size
                )
            )
        pg.draw.circle(self.surface, GREEN, (self.size, self.size), self.size)

        # print(sensorEdges, self.sensorRect.topleft)

        self.mask = pg.mask.from_threshold(self.surface, GREEN, (1, 1, 1, 255))

    def checkCollision(self, floor):
        r = [False, False]
        colisionPoints = floor.mask.overlap(
            self.mask,
            (int(self.x-self.size), int(self.y-self.size))
        )
        sensorTrigger = floor.mask.overlap(
            self.proximitySensor,
            (0, 0)  # self.sensorRect.topleft
        )
        if sensorTrigger is not None:
            r[1] = True
            # self.speed = self.colSpeed
            # print(sensorTrigger)
        # else:
        #     self.speed = self.maxSpeed
        if colisionPoints is None:
            pass
            # print("No colision")
        else:
            r[0] = True
        return r[0], r[1]
        # self.mask.to_surface(surface, dest=(int(self.x-10), int(self.y-10)))

    def move(self):
        self.x += math.sin(self.rotation)*self.speed
        self.y += math.cos(self.rotation)*self.speed
        # print(self.x, self.y)

    def algorithm(self, collisions):
        botCol, sensorCol = collisions
        self.speed = self.colSpeed if sensorCol else self.maxSpeed
        if botCol:
            self.reversingTimer = 100
        if self.reversingTimer > 0:
            self.speed = -self.colSpeed
            self.reversingTimer -= 1
            if self.reversingTimer == 0:
                self.rotation += math.pi/36


floor = Floor(
    (600, 600),
    {"table": [(10, 10), (10, 200), (500, 200), (500, 10)],
     "wall": [(0, 0), (0, 600-1), (800-1, 600-1), (800-1, 0)]})

bot = Bot(250, 550)

running = True
while running:
    for u in pg.event.get():
        if u.type == pg.QUIT:
            running = False

    floor.render(window)
    bot.render(window)
    cols = bot.checkCollision(floor)
    bot.algorithm(cols)
    bot.move()
    # pg.mask.from_threshold(window, WHITE, (1, 1, 1, 255)).to_surface(window)
    pg.display.update()
    # break
