# Imports #
import pygame as pg
from settings import *
from particle import *
import util
import math
import random
from shapely.geometry import Point, Polygon

# Variables #
# None

# Classes #
class Asteroid:
    def __init__(self, game):
        self.game = game
        self.width = self.height = ASTEROID_STARTING_SIZE
        self.rotation = 0
        self.velocity = (20 * (1 if random.random() > .5 else -1), 20 * (1 if random.random() > .5 else -1) * (random.random() * 2 - 1))
        self.rot_velocity = 5
        self.points = []#[(-30, 0), (0, 30), (30, 0), (0, -30)]
        self.stage = ASTEROID_TOTAL_STAGES
        self.generate_points()

        self.x = WIDTH * random.random()
        self.y = HEIGHT * random.random()
        if (random.random() > .5): # spawn on the left or right
            if (self.velocity[0] > 0):
                self.x = -self.width
            else:
                self.x = WIDTH + self.width
        else: # spawn on the top or bottom
            if (self.velocity[1] > 0):
                self.y = -self.height
            else:
                self.y = HEIGHT + self.height

    def generate_points(self): # TODO: randomly generate BETTER
        point_count = 17 + ((self.stage - 5) * 2)
        theta = 360 // point_count
        self.points.clear()
        for i in range(0, point_count):
            angle = theta * i + (random.random() * theta / 2)
            distance = random.random() + .5 * (15 if i % 2 == 0 else -30 * (random.random() * 2 - 1))
            angler = math.radians(angle)
            x = (self.width + distance) * math.cos(angler)
            y = (self.height + distance) * math.sin(angler)
            self.points.append((x, y))
        self.polygon = Polygon([Point(point[0], point[1]) for point in self.points])

    def intersects(self, coordinates): # turn x, y tuple into point [--NVMand turn it into object space--], then check if it's within the polygon
        return Point((self.x - coordinates[0], self.y - coordinates[1])).within(self.polygon) # Point((self.x, self.y)).within(self.polygon) #

    def distance(self, coordinates):
        return Point((self.x, self.y)).distance(Point(coordinates))

    def explode(self, play_sound=True):
        self.game.asteroids.remove(self)
        if (self.stage <= 1): # Shrapnel (fireworks) and no more babies! (or children, offspring, whatever)
            if play_sound:
                self.game.play_sound("small")
            # this looks horrendous, but it works :)
            shrapnel = [Particle(
                self.game,
                (
                    self.x + (1 - random.random() * 2) * self.width / 5,
                    self.y + (1 - random.random() * 2) * self.height / 5
                ),
                (
                    self.velocity[0] * 1.5 + random.random() * 60,
                    self.velocity[1] * 1.5 + random.random() * 60
                ), (-10, -10), ASTEROID_PARTICLE_SIZE, ASTEROID_PARTICLE_FADE_TIME) for i in range(0, ASTEROID_EXPLOSION_PARTICLE_COUNT)]
            for particle in shrapnel:
                self.game.particles.append(particle)
            return
        if play_sound:
            self.game.play_sound("medium")
        baby_count = util.clamp((ASTEROID_TOTAL_STAGES - self.stage) + 2, 0, 4) # doesn't need to be a variable, but it looks nicer so... shoot me
        for i in range(0, baby_count): # make baby_count babies
            baby = Asteroid(self.game)
            baby.x = self.x
            baby.y = self.y
            baby.velocity = ((self.velocity[0] + (random.random() * 2 - 1) * ((ASTEROID_TOTAL_STAGES - self.stage) * 5 + 20)) * 1.5,
                             (self.velocity[1] + (random.random() * 2 - 1) * ((ASTEROID_TOTAL_STAGES - self.stage) * 5 + 20)) * 1.5)
            baby.stage = self.stage - 1
            baby.width = baby.height = self.width - ASTEROID_SIZE_DECREMENT
            baby.generate_points()
            self.game.asteroids.append(baby)

    def get_look_vector(self):
        radians = math.radians(self.rotation)
        return (math.sin(radians), -math.cos(radians))

    def get_rotation_vector(self): # vector ISN'T the correct word, but not sure what else to use
        # x is rotation (left, right)
        x = self.rot_velocity
        return x

    def get_move_vector(self):
        # (x, y)
        dir = (0, 0) # just use base velocity
        return dir

    def update(self, dt):
        # Update entity's rotation based on left and right input
        self.rotation += self.get_rotation_vector() * dt

        # Lock the rotation from -360 to 360
        if self.rotation > 360:
            self.rotation -= 360
        elif self.rotation < -360:
            self.rotation += 360

        # Get the move vector and update the entity's velocity
        move_vector = self.get_move_vector()
        self.velocity = (self.velocity[0] + move_vector[0] * dt, self.velocity[1] + move_vector[1] * dt)

        # Add the velocity to the entity's x and y
        self.x += self.velocity[0] * dt
        self.y += self.velocity[1] * dt

        # If it goes out of bounds, loop around to the other side
        if (self.x <= -self.height * 2):
            self.x = WIDTH + self.height
        elif (self.x >= WIDTH + self.height * 2):
            self.x = -self.height
            
        if (self.y <= -self.height * 2):
            self.y = HEIGHT + self.height
        elif (self.y >= HEIGHT + self.height * 2):
            self.y = -self.height
        
        # Add drag to the velocity
        #drag_vector = (util.clamp(0 - self.velocity[0], -self.drag[0], self.drag[0]), util.clamp(0 - self.velocity[1], -self.drag[1], self.drag[1]))
        #self.velocity = (self.velocity[0] + drag_vector[0] * dt, self.velocity[1] + drag_vector[1] * dt)

    def draw(self):
        #pg.draw.rect(self.game.screen, 'white', (self.x - self.width / 2, self.y - self.height / 2, self.width, self.height), 2)
        middle = self.x, self.y
        # Draw the "ship"
        points = util.rotatePolygon(
            ((middle[0] + point[0], middle[1] + point[1]) for point in self.points), self.rotation, (self.x, self.y))
        self.polygon = Polygon([Point(point[0] - middle[0], point[1] - middle[1]) for point in points])
        pg.draw.polygon(self.game.screen, 'white', points, 1)

        if self.game.debug: # Draw some debug information like current rotation, velocity, and a line showing the velocity
            self.game.debug_text(str(self.velocity), (self.x, self.y - self.height * 2))
            self.game.debug_text(str(self.rotation), (self.x, self.y - self.height * 2 - 10))
            pg.draw.line(self.game.screen, 'green', (self.x, self.y), (self.x + self.velocity[0], self.y + self.velocity[1]), 1)