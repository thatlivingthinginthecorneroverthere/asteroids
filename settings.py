# Game Configuration / Settings #

# Other
DEBUG = False # F2 to toggle

START_WAIT_TIME = 3 # seconds

# Rendering
RESOLUTION = WIDTH, HEIGHT = 1920, 1080 #1600, 900 # 16:9 ratio 1920, 1080
FPS = 60

# Player
PLAYER_POS = WIDTH / 2, HEIGHT / 2 # starting position
PLAYER_TITLE_TARGET = PLAYER_POS # what the title screen player trys to orient to
PLAYER_ANGLE = 0 # starting angle
PLAYER_ACCELERATION_SPEED = 40 # x (pixels) per second
PLAYER_ROT_SPEED = 90 # x degrees per second

PLAYER_RESPAWN_TIME = 3 # seconds
PLAYER_RESPAWN_PARTICLE_COUNT = 6

PLAYER_EXPLOSION_PARTICLE_SIZE = 1
PLAYER_EXPLOSION_PARTICLE_FADE_TIME = 3
PLAYER_EXPLOSION_PARTICLE_COUNT = 30

PLAYER_PARTICLE_COLORS = [
    (235, 40, 19), # red
    (235, 66, 19), # red-orange
    (235, 95, 19), # orange
    #(235, 183, 52), # orange
    #(173, 133, 29), # orange
    #(227, 235, 19), # yellow
    #(203, 209, 46), # yellow
]
PLAYER_PARTICLE_SIZE = 2
PLAYER_PARTICLE_FADE_TIME = 2
PLAYER_PARTICLE_SPEED = 150

# Enemy
ENEMY_TIMER_MAX = 3 # seconds

# Asteroids
ASTEROID_TOTAL_STAGES = 6#3
ASTEROID_STARTING_SIZE = 60
ASTEROID_SIZE_DECREMENT = 20 # 20 40 60

ASTEROID_PARTICLE_SIZE = 1
ASTEROID_PARTICLE_FADE_TIME = 3
ASTEROID_EXPLOSION_PARTICLE_COUNT = 4

MAX_ASTEROIDS = 32 # max big asteroids on generation

# Bullet
BULLET_SPEED = 100 # x (pixels) per second
BULLET_LIFETIME = 4 # seconds