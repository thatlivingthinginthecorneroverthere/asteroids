# Imports #
import pygame as pg
from settings import *
import util
import math
import random
from shapely.geometry import Point, Polygon

# Variables #
# None

# Classes #
class Particle:
    def __init__(self, game, coordinate, velocity, drag, radius=2, fade_time=3, color=(255, 255, 255)):
        self.game = game
        self.x = coordinate[0]
        self.y = coordinate[1]
        self.radius = radius
        self.rotation = 0
        self.velocity = velocity
        self.drag = drag
        self.fade_time = fade_time
        self.life = 0
        self.start_color = color
        self.color = self.start_color

    def intersects(self, coordinates): # turn x, y tuple into point [--NVMand turn it into object space--], then check if it's within the polygon
       raise NotImplementedError() #return Point((self.x - coordinates[0], self.y - coordinates[1])).within(self.polygon) # Point((self.x, self.y)).within(self.polygon) #

    def get_look_vector(self):
        radians = math.radians(self.rotation)
        return (math.sin(radians), -math.cos(radians))

    def get_move_vector(self):
        # (x, y)
        dir = (0, 0) # just use base velocity
        return dir

    def update(self, dt):
        # Get the move vector and update the entity's velocity
        move_vector = self.get_move_vector()
        self.velocity = (self.velocity[0] + move_vector[0] * dt, self.velocity[1] + move_vector[1] * dt)

        # Add the velocity to the entity's x and y
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
        
        # Add drag to the velocity
        drag_vector = (util.clamp(0 - self.velocity[0], -self.drag[0], self.drag[0]), util.clamp(0 - self.velocity[1], -self.drag[1], self.drag[1]))
        self.velocity = (self.velocity[0] + drag_vector[0] * dt, self.velocity[1] + drag_vector[1] * dt)

        # Increment alive time
        self.life += dt

        # Change color based on life and lifetime
        color_delta = util.clamp(self.life / self.fade_time * 255, 0, 255)
        self.color = (
            util.clamp(self.start_color[0] - color_delta, 0, 255),
            util.clamp(self.start_color[1] - color_delta, 0, 255),
            util.clamp(self.start_color[2] - color_delta, 0, 255))

    def draw(self):
        #pg.draw.rect(self.game.screen, 'white', (self.x - self.width / 2, self.y - self.height / 2, self.width, self.height), 2)
        middle = self.x, self.y
        # Draw the "particle"
        pg.draw.circle(self.game.screen, self.color, (self.x, self.y), self.radius) # don't animate size because it just rounds the float to an integer ):
            #- (util.clamp(self.life / self.fade_time, 0, 1) * self.radius))

        if self.game.debug: # Draw some debug information like current rotation, velocity, and a line showing the velocity
            #self.game.debug_text(str(self.velocity), (self.x, self.y - self.radius * 2))
            #self.game.debug_text(str(self.rotation), (self.x, self.y - self.radius * 2 - 10))
            pg.draw.line(self.game.screen, 'red', (self.x, self.y), (self.x + self.velocity[0], self.y + self.velocity[1]), 1)