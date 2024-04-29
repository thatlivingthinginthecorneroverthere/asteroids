# Imports #
import pygame as pg
from settings import *
import util
import math
from bullet import *
from particle import *

# Variables #
# None

# Classes #
class Player:
    def __init__(self, game):
        self.game = game
        self.x = PLAYER_POS[0]
        self.y = PLAYER_POS[1]
        self.width = self.height = 10
        self.width -= 2
        self.rotation = PLAYER_ANGLE
        self.velocity = (0, 0)
        self.drag = (5, 5)
        self.bullets = []
        self.artifical_thrust = (0, 0)
        self.visible = True
        #self.surface = game.screen.subsurface((0, 0, WIDTH, HEIGHT))#pg.Surface(RESOLUTION)
        #print(self.x - self.width / 2, self.y - self.height / 2)

    def shoot(self):
        if not self.visible:
            return # probably dead so, don't shoot
        self.game.play_sound("fire")
        look_vector = self.get_look_vector()
        bullet = Bullet(self.game, (self.x + look_vector[0] * self.height, self.y + look_vector[1] * self.height),
                        (self.velocity[0] + look_vector[0] * BULLET_SPEED, self.velocity[1] + look_vector[1] * BULLET_SPEED))
        self.bullets.append(bullet)

    def get_look_vector(self):
        radians = math.radians(self.rotation)
        return (math.sin(radians), -math.cos(radians))

    def get_right_vector(self):
        radians = math.radians(self.rotation + 90)
        return (math.sin(radians), -math.cos(radians))

    def get_rotation_vector(self): # vector ISN'T the correct word, but not sure what else to use
        # x is rotation (left, right)
        x = ((1 if self.game.keys.get(pg.K_d) else 0) + (-1 if self.game.keys.get(pg.K_a) else 0)) # x move dir, a subtracts, d adds
        return x

    def get_move_vector(self):
        # y is thrust/brakes (up, down)
        look_vector = self.get_look_vector()
        y = ((1 if self.game.keys.get(pg.K_w) else 0) + (-1 if self.game.keys.get(pg.K_s) else 0))
        dir = (y * look_vector[0] + self.artifical_thrust[0], y * look_vector[1] + self.artifical_thrust[1]) # turn the forward/backward (-1, 0, 1) into a vector based on the look vector
        return dir

    def explode(self): # collision detected!
        if (not self.game.is_playing()):
            return
        
        self.game.play_sound("small")
        shrapnel = [Particle(
            self.game,
            (
                self.x + (1 - random.random() * 2) * self.width / 5,
                self.y + (1 - random.random() * 2) * self.height / 5
            ),
            (
                self.velocity[0] * 1.5 + random.random() * 60,
                self.velocity[1] * 1.5 + random.random() * 60
            ), (-10, -10), PLAYER_EXPLOSION_PARTICLE_SIZE, PLAYER_EXPLOSION_PARTICLE_FADE_TIME) for i in range(0, PLAYER_EXPLOSION_PARTICLE_COUNT)]
        for particle in shrapnel:
            self.game.particles.append(particle)
            # we do a little bit of copy and pasting :)

        self.respawn_timer = 0
        self.game.lives -= 1
        if self.game.lives <= 0:
            self.game.gameover()
        else:
            self.visible = False
            self.game.respawn()

    def try_respawn(self, dt):
        self.respawn_timer += dt
        if self.respawn_timer <= PLAYER_RESPAWN_TIME:
            return
        
        valid = False
        respawn_coords = (0, 0)
        while (not valid):
            respawn_coords = (WIDTH / 2 + random.random() * WIDTH / 3, HEIGHT / 2 + random.random() * HEIGHT / 3)
            valid = True
            for asteroid in self.game.asteroids:
                if (asteroid.distance(respawn_coords) <= asteroid.width and asteroid.intersects(respawn_coords)):
                    valid = False
                    break
        self.velocity = (0, 0)
        self.x = respawn_coords[0]
        self.y = respawn_coords[1]
        self.visible = True

        # Respawn particles
        theta = 360 / PLAYER_RESPAWN_PARTICLE_COUNT
        for i in range(0, PLAYER_RESPAWN_PARTICLE_COUNT):
            angle = math.radians(theta * i)
            coords = (math.sin(angle) * 120 + self.x, math.cos(angle) * 120 + self.y)
            #print(i, theta, theta * i, str(coords))
            self.game.particles.append(Particle(self.game, coords, (-coords[0] + self.x, -coords[1] + self.y), (0, 0), 2, 1, (0, 255, 0)))

        self.game.play_sound("extra")
        self.game.respawned()

    def update(self, dt):
        # Update bullets
        for bullet in self.bullets:
            if (bullet.life >= BULLET_LIFETIME):
                self.bullets.remove(bullet)
            else:
                bullet.update(dt)
                
        # Try respawn
        if (self.game.is_respawning()):
            self.try_respawn(dt)
            return
        # Update player's rotation based on left and right input
        self.rotation += self.get_rotation_vector() * dt * PLAYER_ROT_SPEED

        # Lock the rotation from -360 to 360
        if self.rotation > 360:
            self.rotation -= 360
        elif self.rotation < -360:
            self.rotation += 360

        # Get the move vector and update the player's velocity
        look_vector = self.get_look_vector()
        right_vector = self.get_right_vector()
        move_vector = self.get_move_vector()
        self.velocity = (self.velocity[0] + move_vector[0] * dt * PLAYER_ACCELERATION_SPEED, self.velocity[1] + move_vector[1] * dt * PLAYER_ACCELERATION_SPEED)

        if (abs(move_vector[0]) > 0 or abs(move_vector[1]) > 0):
            offsetx = (1 - random.random() * 2) * 15
            offsety = (1 - random.random() * 2) * 15
            offsetz = (1 - random.random() * 2) * self.width / 2 # random width offset
            thrust_particle = Particle(self.game,
                (self.x - look_vector[0] * self.height + right_vector[0] * offsetz, self.y - look_vector[1] * self.height + right_vector[1] * offsetz),
                (
                    self.velocity[0] + -move_vector[0] * PLAYER_PARTICLE_SPEED + offsetx * move_vector[0],
                    self.velocity[1] + -move_vector[1] * PLAYER_PARTICLE_SPEED + offsety * move_vector[1]
                ),
                (20, 20),
                PLAYER_PARTICLE_SIZE, PLAYER_PARTICLE_FADE_TIME, random.choice(PLAYER_PARTICLE_COLORS))
            self.game.particles.append(thrust_particle)

        # Add the velocity to the player's x and y
        self.x += self.velocity[0] * dt
        self.y += self.velocity[1] * dt

        # If you go out of bounds, loop around to the other side
        if (self.x <= -self.height * 2):
            self.x = WIDTH + self.height
        elif (self.x >= WIDTH + self.height * 2):
            self.x = -self.height
            
        if (self.y <= -self.height * 2):
            self.y = HEIGHT + self.height
        elif (self.y >= HEIGHT + self.height * 2):
            self.y = -self.height
        
        # Add drag to the velocity
        drag_vector = (util.clamp(0 - self.velocity[0], -self.drag[0], self.drag[0]), util.clamp(0 - self.velocity[1], -self.drag[1], self.drag[1]))
        self.velocity = (self.velocity[0] + drag_vector[0] * dt, self.velocity[1] + drag_vector[1] * dt)

        # Check collisions
        for asteroid in self.game.asteroids:
            if (asteroid.distance((self.x, self.y)) <= asteroid.width * 2 and asteroid.intersects((self.x, self.y))):
                self.explode() # explode the player (and remove a life)
                break

    def draw(self):
        for bullet in self.bullets:
            bullet.draw()
        #pg.draw.rect(self.game.screen, 'white', (self.x - self.width / 2, self.y - self.height / 2, self.width, self.height), 2)
        middle = self.x, self.y
        # Draw the "ship"
        if self.visible:
            pg.draw.polygon(self.game.screen, 'white', util.rotatePolygon([
                (middle[0] - self.width, middle[1] + self.height),
                (middle[0] + self.width, middle[1] + self.height),
                (middle[0], middle[1] - self.height)
            ], self.rotation, (self.x, self.y)))

        if self.game.debug: # Draw some debug information like current rotation, velocity, and a line showing the velocity
            self.game.debug_text(str(self.velocity), (self.x, self.y - self.height * 2))
            self.game.debug_text(str(self.rotation), (self.x, self.y - self.height * 2 - 10))
            pg.draw.line(self.game.screen, 'green', (self.x, self.y), (self.x + self.velocity[0], self.y + self.velocity[1]), 1)
        """self.surface = pg.Surface((self.width, self.height)) #self.game.screen.subsurface((0, 0, WIDTH, HEIGHT))
        pg.draw.rect(self.surface, 'white', (0, 0, self.width, self.height), 2)
        "" "pg.draw.polygon(self.surface, 'white', [
            (self.width / 2, 0),
            (0, self.height),
            (self.width, self.height)
            #(middle[0] - self.width, middle[1] + self.height),
            #(middle[0] + self.width, middle[1] + self.height),
            #(middle[0], middle[1] - self.height)
        ], 1)"" "
        self.surface = pg.transform.rotate(self.surface, self.rotation)
        self.game.screen.blit(self.surface, (self.x, self.y))"""