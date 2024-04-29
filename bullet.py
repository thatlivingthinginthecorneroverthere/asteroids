# Imports #
import pygame as pg
from settings import *
import util
import math

# Variables #
# None

# Classes #
class Bullet:
    def __init__(self, game, position, velocity):
        self.game = game
        self.x = position[0]
        self.y = position[1]
        self.radius = 3
        self.rotation = 0
        self.velocity = velocity
        self.rot_velocity = 5
        self.life = 0

    def update(self, dt):
        # Add the velocity to the player's x and y
        self.x += self.velocity[0] * dt
        self.y += self.velocity[1] * dt
        
        # If it goes out of bounds, loop around to the other side
        if (self.x <= -self.radius * 2):
            self.x = WIDTH + self.radius
        elif (self.x >= WIDTH + self.radius * 2):
            self.x = -self.radius
            
        if (self.y <= -self.radius * 2):
            self.y = HEIGHT + self.radius
        elif (self.y >= HEIGHT + self.radius * 2):
            self.y = -self.radius

        # Increment alive time
        self.life += dt

        # Check collisions
        for asteroid in self.game.asteroids:
            if (asteroid.distance((self.x, self.y)) <= asteroid.width * 2 and asteroid.intersects((self.x, self.y))):
                self.life = BULLET_LIFETIME # kill it
                asteroid.explode() # explode the asteroid (demote it)
                break

    def draw(self):
        #pg.draw.rect(self.game.screen, 'white', (self.x - self.width / 2, self.y - self.height / 2, self.width, self.height), 2)
        middle = self.x, self.y
        # Draw the "ship"
        #pg.draw.polygon(self.game.screen, 'white', util.rotatePolygon(
        #    ((middle[0] + point[0], middle[1] + point[1]) for point in self.points)
        #    , self.rotation, (self.x, self.y)))
        pg.draw.circle(self.game.screen, 'white', (self.x, self.y), self.radius)

        if self.game.debug: # Draw some debug information like current rotation, velocity, and a line showing the velocity
            self.game.debug_text(str(self.velocity), (self.x, self.y - self.radius * 2))
            self.game.debug_text(str(self.life), (self.x, self.y - self.radius * 2 - 10))
            pg.draw.line(self.game.screen, 'blue', (self.x, self.y), (self.x + self.velocity[0], self.y + self.velocity[1]), 1)