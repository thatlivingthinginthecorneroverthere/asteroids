# Libraries #
import pygame as pg
import sys
from settings import *
from player import *
from asteroid import *
from map import *

# Classes #
def enum(**enums):
    return type('Enum', (), enums);
GAME_STATE = enum(Title=0, Play=1, Respawn=2, GameOver=3)

class Game:
    def __init__(self):
        pg.init()
        self.screen = pg.display.set_mode(RESOLUTION, pg.SRCALPHA)
        self.clock = pg.time.Clock()
        self.asteroids = []
        self.particles = []
        self.keys = {}
        self.player = Player(self)
        self.debug = DEBUG # start debug?

        self.debug_font = pg.font.SysFont('monospace', 10)
        self.debug_panel_font = pg.font.SysFont('monospace', 20)
        self.title_font = pg.font.SysFont('monospace', 100)
        self.title_font.set_bold(True)
        self.title_sub_font = pg.font.SysFont('monospace', 20)
        self.title_sub_font.set_italic(True)

        self.sounds = {
            "large": "assets/exp-large.mp3",
            "medium": "assets/exp-medium.mp3",
            "small": "assets/exp-small.mp3",
            "extra": "assets/extra-ship.mp3",
            "fire": "assets/fire.mp3",
        }

        self.enemy_timer = 0
        self.state = GAME_STATE.Title
        self.reset() # show title

    def play_sound(self, name):
        sound = pg.mixer.Sound(self.sounds[name])
        sound.set_volume(.05)
        sound.play()

    def is_playing(self):
        return self.state == GAME_STATE.Play
    
    def is_respawning(self):
        return self.state == GAME_STATE.Respawn

    def respawned(self): # the player tells the game "hey i respawned", terrible in practice but it works :)
        self.state = GAME_STATE.Play

    def respawn(self): # the player tells the game "hey im respawning", again, terrible but it works
        self.state = GAME_STATE.Respawn

    def new_game(self):
        #self.map = Map(self)
        self.state = GAME_STATE.Play
        self.player.artifical_thrust = (0, 0)
        self.player.velocity = (0, 0)
        self.player.x = PLAYER_POS[0]
        self.player.y = PLAYER_POS[1]
        self.player.rotation = 0
        self.player.update(1)
        self.particles.clear()
        self.asteroids.clear()
        self.lives = 3
        self.level = 1
        self.create_asteroids()

    def reset(self): # Show title screen
        self.state = GAME_STATE.Title
        self.level = 2
        self.create_asteroids()
        self.player.x = WIDTH / 2 + (1 - random.random() * 2) * (WIDTH / 3)
        self.player.y = HEIGHT / 2
        self.particles.clear()
        self.start_timer = START_WAIT_TIME # how much time to wait for allowing start (seconds)

    def gameover(self):
        self.reset()

    def create_asteroids(self):
        asteroid_count = util.clamp(self.level * 6, 0, MAX_ASTEROIDS)
        
        for i in range(0, asteroid_count):
            self.asteroids.append(Asteroid(self))
        if self.level > 1:
            for i in range(0, random.randint(0, asteroid_count - 3)):
                self.asteroids[i].explode(False)
                if (random.random() > .5):
                    self.asteroids[i].explode(False) # triplets!

    def spawn_enemy(self):
        pass

    def update(self): # Update all (clock, entities)
        pg.display.flip()
        self.clock.tick(FPS)
        self.delta = self.clock.get_time() / 1000 # ms to seconds
        pg.display.set_caption(f'Asteroids - {self.clock.get_fps() :.1f}fps :: {self.clock.get_time()}dt ({self.delta}dt s) :: {self.clock.get_rawtime()}rdt')

        if self.start_timer > -1:
            self.start_timer -= self.delta

        if self.state == GAME_STATE.Title:
            self.update_title()
        else:
            self.update_logic()
        self.update_entities()

    def update_logic(self): # Handle enemy spawn timer and level completion
        self.enemy_timer += self.delta
        if (len(self.asteroids) <= 0):
            self.level += 1
            self.create_asteroids()
        if (self.enemy_timer >= ENEMY_TIMER_MAX):
            self.spawn_enemy()
            self.enemy_timer = 0

    def update_entities(self): # Update all entities
        self.player.update(self.delta)
        for entity in self.asteroids:
            entity.update(self.delta)
        for entity in self.particles:
            if (entity.life >= entity.fade_time):
                self.particles.remove(entity)
            else:
                entity.update(self.delta)

    def update_title(self):
        look_vector = self.player.get_look_vector()
        target = PLAYER_TITLE_TARGET
        target_rotation = math.atan2(target[1] - self.player.y, target[0] - self.player.x) * 180 / math.pi + 90
        target_direction = target_rotation - self.player.rotation
        if (target_direction < 0): # it was really that simple? really?? (context: prevent it turning all the way around instead of taking the shortest route)
            target_direction += 360
        if (target_direction > 180):
            target_direction -= 180
        self.player.artifical_thrust = (look_vector[0], look_vector[1])
        self.player.rotation += util.clamp(target_direction, -PLAYER_ROT_SPEED * self.delta, PLAYER_ROT_SPEED * self.delta)

    def draw_title(self): # Draw title screen
        text = self.title_font.render("Asteroids", True, 'white')
        rect = text.get_rect()
        rect.center = (WIDTH / 2, HEIGHT / 2 - HEIGHT / 6)
        self.screen.blit(text, rect)

        if self.start_timer <= 0:
            r = g = b = util.clamp((1 - (self.start_timer + 1)) * 255, 0, 255)
            #print(r, self.start_timer)
            text = self.title_sub_font.render("Press any key to play", True, (r, g, b))
            rect = text.get_rect()
            rect.center = (WIDTH / 2, HEIGHT / 2 + HEIGHT / 6)
            self.screen.blit(text, rect)

    def draw(self): # Draw all entities and other game related features
        self.screen.fill('black')
        if (self.state == GAME_STATE.Title):
            self.draw_title()
        #self.map.draw()
        #pg.draw.rect(self.screen, 'white', (0, 0, 50, 50), 2)
        self.draw_entities()
        self.draw_debug()

    def draw_entities(self): # Draws all entities (asteroids, player, )
        for entity in self.particles:
            entity.draw()
        self.player.draw()
        for entity in self.asteroids:
            entity.draw()

    def draw_debug(self): # Draws debug information (if enabled, f2 to toggle)
        if not self.debug:
            return
        def draw(text, y): # nesting functions :0 so unperformant but like lazy :) and not even supposed to be used in normal gameplay so
            text = self.debug_panel_font.render(text, True, 'white')
            rect = text.get_rect()
            rect.left = 0
            rect.top = y
            self.screen.blit(text, rect)
            return y + self.debug_panel_font.get_height()
        y = 0
        y = draw(f'Total Asteroid(s) left: {len(self.asteroids)}', y)
        y = draw(f'Total Active Particle(s): {len(self.particles)}', y)
        y = draw(f'Total Active Bullet(s): {len(self.player.bullets)}', y)
        keys = ""
        for key in self.keys:
            keys += pg.key.name(key) + " "
        y = draw(f'Pressed Keys(s): {keys}', y)
        y = draw(f'Game State: {self.state}', y)
        y = draw(f'Level: {self.level}', y)
        y = draw(f'Lives: {self.lives}', y)

    def debug_text(self, text, coordinates): # Utility function for other classes to draw debug text (ex: above entities)
        #if not self.debug:
        #    return
        text = self.debug_font.render(text, True, 'white', 'black')
        rect = text.get_rect()
        rect.center = coordinates
        self.screen.blit(text, rect)

    def handle_inputs_down(self, key): # Handle key down events
        if (key == pg.K_F2):
            self.debug = not self.debug
        elif (self.state == GAME_STATE.Title):
            if self.start_timer <= 0:
                self.new_game()
        elif (key == pg.K_SPACE):
            self.player.shoot()
        elif (key == pg.K_ESCAPE):
            self.reset()
        elif (key == pg.K_t):
            self.player.explode()
        self.keys[key] = True

    def handle_inputs_up(self, key): # Handle key up events
        del self.keys[key]

    def check_events(self): # Check pygame events
        for event in pg.event.get():
            if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE and self.state == GAME_STATE.Title):
                pg.quit()
                sys.exit()
            elif event.type == pg.KEYDOWN:
                self.handle_inputs_down(event.key)
            elif event.type == pg.KEYUP:
                self.handle_inputs_up(event.key)
    
    def run(self): # Main loop
        while True:
            self.check_events()
            self.update()
            self.draw()