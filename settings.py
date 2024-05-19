import pygame as pg
vec = pg.math.Vector2


# define some colors (R, G, B)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DARKGREY = (40, 40, 40)
LIGHTGREY = (100, 100, 100)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
BROWN = (106, 55, 5)
CYAN = (0, 255, 255)

# game settings
WIDTH = 1280
HEIGHT = 720
FPS = 60
SCREEN = pg.display.set_mode((WIDTH, HEIGHT))
pg.display.set_caption("The Bell Doesn't Dismiss You!")
TITLE = "Made By Scott and Cooper"
BGCOLOR = BLACK

TILESIZE = 64
GRIDWIDTH = WIDTH / TILESIZE
GRIDHEIGHT = HEIGHT / TILESIZE

#WALL_IMG = 'tileGreen_39.png'

# Player settings
PLAYER_HEALTH = 100
PLAYER_MAX_HEALTH = 100
PLAYER_SPEED = 225
PLAYER_ROT_SPEED = 150
PLAYER_HIT_RECT = pg.Rect(0, 0, 35, 35)
BARREL_OFFSET = vec(30, 10)


# Gun settings
BULLET_IMG = 'bullet.png'
BULLET_SPEED = 240
BULLET_LIFETIME = 2000
BULLET_RATE = 300
KICKBACK = 0
GUN_SPREAD = 0
BULLET_DAMAGE = 35
PLAYER_AMMO = 100


# Mob settings
MOB_IMG = 'zombie1_hold.png'
MOB_SPEEDS = [70, 85, 75, 90]
MOB_HIT_RECT = pg.Rect(0, 0, 30, 30)
MOB_HEALTH = 100
MOB_DAMAGE = 0.5
MOB_KNOCKBACK = 0
AVOID_RADIUS = 50

#MOB2 settings
BULLET2_SPEED = 300
MOB2_HEALTH = 70
MOB2_FIRERATE = 2000 #milliseconds



# Add constants to settings.py
BOSS_HEALTH = 1300  # Adjust as needed
BOSS_SPEED = 100  # Adjust as needed
BOSS_FIRERATE = 2000  # Boss shooting delay in milliseconds
BOSS_BULLET_SPEED = 300  # Speed of the boss's bullets






