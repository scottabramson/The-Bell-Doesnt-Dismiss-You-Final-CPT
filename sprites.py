
import pygame as pg
from settings import *
from tilemap import *
from random import uniform, choice
import os
from os import path
vec = pg.math.Vector2



#COLLISIONS
def collide_with_walls(sprite, group, dir):
    if dir == 'x':
        hits = pg.sprite.spritecollide(sprite, group, False, collide_hit_rect)
        if hits:
            hit = hits[0]
            if sprite.vel.x > 0:  # Moving right
                sprite.hit_rect.right = hit.rect.left
                sprite.pos.x = sprite.hit_rect.centerx  # Adjust sprite center based on updated hit_rect
            elif sprite.vel.x < 0:  # Moving left
                sprite.hit_rect.left = hit.rect.right
                sprite.pos.x = sprite.hit_rect.centerx
            sprite.vel.x = 0  # Stop horizontal movement

    elif dir == 'y':
        hits = pg.sprite.spritecollide(sprite, group, False, collide_hit_rect)
        if hits:
            hit = hits[0]
            if sprite.vel.y > 0:  # Moving down
                sprite.hit_rect.bottom = hit.rect.top
                sprite.pos.y = sprite.hit_rect.centery
            elif sprite.vel.y < 0:  # Moving up
                sprite.hit_rect.top = hit.rect.bottom
                sprite.pos.y = sprite.hit_rect.centery
            sprite.vel.y = 0  # Stop vertical movement


def check_collisions(player, obstacles):
    for obstacle in obstacles:
        if player.hit_rect.colliderect(obstacle.rect):
            handle_collision(player, obstacle)
def handle_collision(player, obstacle):
    # Example: Stop the player's movement
    player.vel.x = 0
    player.vel.y = 0
    # Optionally, reposition player slightly away from the obstacle
    if player.hit_rect.centerx < obstacle.rect.centerx:
        player.hit_rect.right = obstacle.rect.left
    else:
        player.hit_rect.left = obstacle.rect.right



class Player(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.scale_factor = 0.6  # Define scale factor before loading images
        self.load_images()
        self.image = self.idlesprite_images[0]
        self.rect = self.image.get_rect()
        self.hit_rect = pg.Rect(0, 0, int(self.rect.width * 0.4), int(self.rect.height * 0.4))
        self.hit_rect.center = self.rect.center
        self.vel = vec(0, 0)
        self.pos = vec(x, y)
        self.rot = 0
        self.last_shot = 0
        self.health = PLAYER_HEALTH
        self.current_frame = 0
        self.last_update = pg.time.get_ticks()
        self.action = 'idle'
        self.direction = 's'
        self.direction_frames = {'d': 0, 'w': 6, 'a': 12, 's': 18}
        self.ammo = PLAYER_AMMO  # Start the player with 50 ammo

    def load_images(self):
        frame_width = 48
        frame_height = 73
        scale = self.scale_factor  # Scale factor from the instance variable

        sprite_sheet = pg.image.load('animations/throw.png').convert_alpha()
        sprite_sheet_run = pg.image.load('animations/run.png').convert_alpha()
        sprite_sheet_idle = pg.image.load('animations/idle.png').convert_alpha()

        self.throwsprite_images = [pg.transform.scale(sprite_sheet.subsurface(pg.Rect(i * frame_width, 0, frame_width, frame_height)),
                                      (int(frame_width * scale), int(frame_height * scale))) for i in range(24)]
        self.runsprite_images = [pg.transform.scale(sprite_sheet_run.subsurface(pg.Rect(i * frame_width, 0, frame_width, frame_height)),
                                    (int(frame_width * scale), int(frame_height * scale))) for i in range(24)]
        self.idlesprite_images = [pg.transform.scale(sprite_sheet_idle.subsurface(pg.Rect(i * frame_width, 0, frame_width, frame_height)),
                                     (int(frame_width * scale), int(frame_height * scale))) for i in range(24)]

    def get_keys(self):
        self.vel = vec(0, 0)
        keys = pg.key.get_pressed()
        self.running = False
        self.throwing = False

        if keys[pg.K_LEFT] or keys[pg.K_a]:
            self.vel.x = -PLAYER_SPEED
            self.direction = 'a'
            self.running = True
        if keys[pg.K_RIGHT] or keys[pg.K_d]:
            self.vel.x = PLAYER_SPEED
            self.direction = 'd'
            self.running = True
        if keys[pg.K_UP] or keys[pg.K_w]:
            self.vel.y = -PLAYER_SPEED
            self.direction = 'w'
            self.running = True
        if keys[pg.K_DOWN] or keys[pg.K_s]:
            self.vel.y = PLAYER_SPEED
            self.direction = 's'
            self.running = True
        if keys[pg.K_SPACE] and self.ammo > 0:  # Check ammo is more than 0 before shooting
            self.throwing = True
            now = pg.time.get_ticks()
            if now - self.last_shot > BULLET_RATE:
                self.last_shot = now
                direction_angle = {
                    'd': 0,  # right
                    'a': 180,  # left
                    'w': 270,  # up
                    's': 90  # down
                }.get(self.direction, 0)
                bullet_dir = vec(1, 0).rotate(direction_angle)  # Rotate the bullet vector based on direction
                bullet_pos = self.pos + bullet_dir * 30  # Example offset, adjust as necessary
                Bullet(self.game, bullet_pos, bullet_dir)
                self.vel += vec(-KICKBACK, 0).rotate(direction_angle)
                self.ammo -= 1  # Decrement ammo
                self.game.shoot_sound.play()  # Play shooting sound

        if self.vel.length() > 0:
            self.vel = self.vel.normalize() * PLAYER_SPEED

    def update(self):
        self.get_keys()
        self.animate()

        # Apply horizontal movement
        self.pos.x += self.vel.x * self.game.dt
        self.hit_rect.centerx = self.pos.x
        collide_with_walls(self, self.game.walls, 'x')
        self.rect.centerx = self.hit_rect.centerx

        # Apply vertical movement
        self.pos.y += self.vel.y * self.game.dt
        self.hit_rect.centery = self.pos.y
        collide_with_walls(self, self.game.walls, 'y')
        self.rect.centery = self.hit_rect.centery

    def animate(self):
        now = pg.time.get_ticks()
        if self.running:
            if now - self.last_update > 100:
                self.last_update = now
                self.current_frame = (self.current_frame + 1) % 6
                self.image = self.runsprite_images[self.current_frame + self.direction_frames[self.direction]]
        elif self.throwing:
            if self.current_frame < 6:
                self.image = self.throwsprite_images[self.current_frame + self.direction_frames[self.direction]]
                self.current_frame += 1
            else:
                self.throwing = False
                self.current_frame = 0
        else:
            if now - self.last_update > 100:
                self.last_update = now
                self.current_frame = (self.current_frame + 1) % 4
                self.image = self.idlesprite_images[self.current_frame + self.direction_frames[self.direction]]



#NPC SPRITES


class Mob(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites, game.mobs
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        # Initialize the dictionary to store frames by action and direction
        self.animation_frames = {
            'walk_up': [], 'walk_down': [], 'walk_left': [], 'walk_right': [],
            'idle_up': [], 'idle_down': [], 'idle_left': [], 'idle_right': []
        }
        self.load_images()  # This will populate the above dictionary
        self.image = self.animation_frames['idle_down'][0]  # Default starting image
        self.rect = self.image.get_rect()
        self.hit_rect = pg.Rect(0, 0, int(self.rect.width * 0.8), int(self.rect.height * 0.8))
        self.hit_rect.center = self.rect.center
        self.vel = vec(0, 0)
        self.pos = vec(x, y)
        self.health = MOB_HEALTH
        self.acc = vec(0, 0)
        self.speed = choice(MOB_SPEEDS)
        self.vision_radius = 500
        self.current_frame = 0
        self.last_update = pg.time.get_ticks()
        self.game.debug_mode = False

        # Direction tracking for animation purposes
        self.current_direction = 'down'  # Initial direction

    def load_images(self):
        img_folder = path.join(os.path.dirname(__file__), 'animations')
        sprite_sheet = {
            "walk": "MobRun.png",
            "idle": "MobIdle.png"
        }
        # Update the order to match the sprite sheet: right, up, left, down
        directions = ['right', 'up', 'left', 'down']
        num_directions = len(directions)
        frame_width, frame_height = 32, 50
        scale_factor = 0.9

        new_frame_width = int(frame_width * scale_factor)
        new_frame_height = int(frame_height * scale_factor)

        for key, filename in sprite_sheet.items():
            full_path = path.join(img_folder, filename)
            sprite_sheet_image = pg.image.load(full_path).convert_alpha()
            total_frames = sprite_sheet_image.get_width() // frame_width
            frames_per_direction = total_frames // num_directions

            for index, direction in enumerate(directions):
                frames = []
                for i in range(frames_per_direction):
                    frame_index = i + frames_per_direction * index
                    frame = sprite_sheet_image.subsurface((frame_index * frame_width, 0, frame_width, frame_height))
                    scaled_frame = pg.transform.scale(frame, (new_frame_width, new_frame_height))
                    frames.append(scaled_frame)
                self.animation_frames[f"{key}_{direction}"] = frames

    def animate(self):
        now = pg.time.get_ticks()
        if self.vel.length_squared() > 0:  # Mob has non-zero velocity
            if abs(self.vel.x) > abs(self.vel.y):
                self.current_direction = 'right' if self.vel.x > 0 else 'left'
            else:
                self.current_direction = 'up' if self.vel.y < 0 else 'down'  # Adjust based on your game's coordinate system
            animation_type = f'walk_{self.current_direction}'
        else:
            animation_type = f'idle_{self.current_direction}'

        if now - self.last_update > 100:  # Animation frame rate
            self.last_update = now
            self.current_frame = (self.current_frame + 1) % len(self.animation_frames[animation_type])
            self.image = self.animation_frames[animation_type][self.current_frame]
            self.rect = self.image.get_rect(center=self.rect.center)

    def chase_player(self):
        direction = (self.game.player.pos - self.pos).normalize()
        self.vel = direction * self.speed

    def update(self):
        self.animate()
        self.acc = vec(0, 0)
        can_see = self.can_see_player()
        if can_see:
            self.chase_player()
        else:
            self.idle_behavior()  # Ensure this sets the velocity to zero

        self.vel += self.acc * self.game.dt
        self.pos += self.vel * self.game.dt

        self.hit_rect.centerx = self.pos.x
        collide_with_walls(self, self.game.walls, 'x')
        self.rect.centerx = self.hit_rect.centerx

        self.hit_rect.centery = self.pos.y
        collide_with_walls(self, self.game.walls, 'y')
        self.rect.centery = self.hit_rect.centery

        if self.health <= 0:
            self.kill()

    def idle_behavior(self):
        # Explicitly set velocity to zero when idling
        self.vel = vec(0, 0)

    def avoid_mobs(self):
        for mob in self.game.mobs:
            if mob != self:
                dist = self.pos - mob.pos
                if 0 < dist.length() < AVOID_RADIUS:
                    self.acc += dist.normalize()

    def can_see_player(self):
        if self.pos.distance_to(self.game.player.pos) < self.vision_radius:
            for wall in self.game.walls:
                if wall.rect.clipline(self.pos, self.game.player.pos):
                    return False
            return True
        return False

    def draw_health(self, screen, camera):
        if self.health > 60:
            col = GREEN
        elif self.health > 30:
            col = YELLOW
        else:
            col = RED
        width = int(self.rect.width * self.health / MOB_HEALTH)

        # Calculate the screen position
        screen_pos = camera.apply(self)

        # Create the health bar rectangles
        background_bar = pg.Rect(screen_pos.left, screen_pos.top - 10, self.rect.width, 7)  # Position it above the mob
        health_bar = pg.Rect(screen_pos.left, screen_pos.top - 10, width, 7)

        # Draw the background bar (empty part)
        pg.draw.rect(screen, BLACK, background_bar)

        # Draw the health bar
        pg.draw.rect(screen, col, health_bar)



class Mob2(pg.sprite.Sprite):
    def __init__(self, game, x, y, scale_factor=1.0):
        self.groups = game.all_sprites, game.mobs
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.scale_factor = 0.9  # Add scale factor
        self.load_images()
        self.direction = 'down'  # Default starting direction
        self.image = self.idle_images[self.direction][0]  # Start with the first idle image of the default direction
        self.rect = self.image.get_rect()
        self.pos = vec(x, y)
        self.rect.center = self.pos
        self.last_shot = pg.time.get_ticks()
        self.shoot_delay = MOB2_FIRERATE  # milliseconds
        self.vision_radius = 600
        self.current_frame = 0
        self.last_update = pg.time.get_ticks()
        self.animating_shoot = False
        self.health = MOB2_HEALTH  # Add health attribute

    def load_images(self):
        self.idle_images = {'right': [], 'up': [], 'left': [], 'down': []}
        self.shoot_images = {'right': [], 'up': [], 'left': [], 'down': []}
        sprite_sheet_idle = pg.image.load('animations/MobIdle.png').convert_alpha()
        sprite_sheet_throw = pg.image.load('animations/MobThrow.png').convert_alpha()

        directions = {
            'right': 0,  # Frames 0-5
            'up': 6,     # Frames 6-11
            'left': 12,  # Frames 12-17
            'down': 18   # Frames 18-23
        }

        frame_width, frame_height = 32, 50
        frames_per_direction = 6

        for direction, start_col in directions.items():
            for i in range(frames_per_direction):
                col_index = start_col + i
                frame_rect = pg.Rect(col_index * frame_width, 0, frame_width, frame_height)
                idle_image = sprite_sheet_idle.subsurface(frame_rect)
                shoot_image = sprite_sheet_throw.subsurface(frame_rect)

                # Scale images according to the scale factor
                idle_image = pg.transform.scale(idle_image,
                    (int(frame_width * self.scale_factor), int(frame_height * self.scale_factor)))
                shoot_image = pg.transform.scale(shoot_image,
                    (int(frame_width * self.scale_factor), int(frame_height * self.scale_factor)))

                self.idle_images[direction].append(idle_image)
                self.shoot_images[direction].append(shoot_image)

    def can_see_player(self):
        # Check if the player is within the vision radius
        if self.pos.distance_to(self.game.player.pos) < self.vision_radius:
            # Line-of-sight check
            for wall in self.game.walls:
                if wall.rect.clipline(self.pos, self.game.player.pos):
                    return False
            return True
        return False

    def shoot(self):
        now = pg.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            bullet_dir = (self.game.player.pos - self.pos).normalize()
            Bullet2(self.game, self.pos + bullet_dir * 20, bullet_dir)  # Offset to prevent collision with Mob2 itself
            self.animating_shoot = True

    def update(self):
        now = pg.time.get_ticks()
        if self.can_see_player():
            self.shoot()
            self.update_direction()
        else:
            self.animating_shoot = False

        self.manage_animations(now)

    def update_direction(self):
        player_direction = self.game.player.pos - self.pos
        if abs(player_direction.x) > abs(player_direction.y):
            self.direction = 'right' if player_direction.x > 0 else 'left'
        else:
            self.direction = 'down' if player_direction.y > 0 else 'up'

    def manage_animations(self, now):
        if self.animating_shoot and now - self.last_update > 100:
            self.current_frame = (self.current_frame + 1) % len(self.shoot_images[self.direction])
            self.image = self.shoot_images[self.direction][self.current_frame]
            self.last_update = now
        elif now - self.last_update > 100:
            self.current_frame = (self.current_frame + 1) % len(self.idle_images[self.direction])
            self.image = self.idle_images[self.direction][self.current_frame]
            self.last_update = now

    def draw_health(self, screen, camera):
        if self.health > 35:
            col = GREEN
        elif self.health > 10:
            col = YELLOW
        else:
            col = RED
        width = int(self.rect.width * self.health / MOB2_HEALTH)

        # Calculate the screen position
        screen_pos = camera.apply(self)

        # Create the health bar rectangles
        background_bar = pg.Rect(screen_pos.left, screen_pos.top - 10 * self.scale_factor, self.rect.width, 7)  # Position it above the mob
        health_bar = pg.Rect(screen_pos.left, screen_pos.top - 10 * self.scale_factor, width, 7)

        # Draw the background bar (empty part)
        pg.draw.rect(screen, BLACK, background_bar)

        # Draw the health bar
        pg.draw.rect(screen, col, health_bar)

    def get_hit(self, damage):
        self.health -= damage
        if self.health <= 0:
            self.kill()

class Boss(pg.sprite.Sprite):
    def __init__(self, game, x, y, scale_factor=2):
        self.groups = game.all_sprites, game.mobs
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.scale_factor = scale_factor
        self.load_images()
        self.direction = 'down'
        self.image = self.idle_images[self.direction][0]
        self.rect = self.image.get_rect()
        self.pos = vec(x, y)
        self.rect.center = self.pos
        self.health = BOSS_HEALTH
        self.speed = BOSS_SPEED
        self.last_shot = pg.time.get_ticks()
        self.shoot_delay = BOSS_FIRERATE
        self.vision_radius = 1000
        self.current_frame = 0
        self.last_update = pg.time.get_ticks()
        self.animating_shoot = False
        self.can_see_player = False
        self.attack_cycle = 0
        self.attack_patterns = [self.circle_attack, self.shotgun_attack, self.beam_attack]
        self.attack_delay = 2000  # Time between attacks in milliseconds
        self.last_attack_time = pg.time.get_ticks()
        self.beam_attack_start_time = 0
        self.beam_attack_duration = 8000  # 6 seconds
        self.beam_attack_active = False
        self.boss_name = "Principal Peril"  # Boss name

    def load_images(self):
        self.idle_images = {'right': [], 'up': [], 'left': [], 'down': []}
        self.shoot_images = {'right': [], 'up': [], 'left': [], 'down': []}
        self.walk_images = {'right': [], 'up': [], 'left': [], 'down': []}
        sprite_sheet_idle = pg.image.load('animations/BossIdle.png').convert_alpha()
        sprite_sheet_shoot = pg.image.load('animations/BossThrow.png').convert_alpha()
        sprite_sheet_walk = pg.image.load('animations/BossRun.png').convert_alpha()

        directions = {
            'right': 0,  # Frames 0-5
            'up': 6,     # Frames 6-11
            'left': 12,  # Frames 12-17
            'down': 18   # Frames 18-23
        }

        frame_width, frame_height = 32, 50
        frames_per_direction = 6

        for direction, start_col in directions.items():
            for i in range(frames_per_direction):
                col_index = start_col + i
                frame_rect = pg.Rect(col_index * frame_width, 0, frame_width, frame_height)
                idle_image = sprite_sheet_idle.subsurface(frame_rect)
                shoot_image = sprite_sheet_shoot.subsurface(frame_rect)
                walk_image = sprite_sheet_walk.subsurface(frame_rect)

                idle_image = pg.transform.scale(idle_image,
                    (int(frame_width * self.scale_factor), int(frame_height * self.scale_factor)))
                shoot_image = pg.transform.scale(shoot_image,
                    (int(frame_width * self.scale_factor), int(frame_height * self.scale_factor)))
                walk_image = pg.transform.scale(walk_image,
                    (int(frame_width * self.scale_factor), int(frame_height * self.scale_factor)))

                self.idle_images[direction].append(idle_image)
                self.shoot_images[direction].append(shoot_image)
                self.walk_images[direction].append(walk_image)

    def animate(self):
        now = pg.time.get_ticks()
        if self.vel.length_squared() > 0:
            if abs(self.vel.x) > abs(self.vel.y):
                self.current_direction = 'right' if self.vel.x > 0 else 'left'
            else:
                self.current_direction = 'up' if self.vel.y < 0 else 'down'
            animation_type = f'walk_{self.current_direction}'
        else:
            animation_type = f'idle_{self.current_direction}'

        if now - self.last_update > 100:
            self.last_update = now
            self.current_frame = (self.current_frame + 1) % len(self.walk_images[self.direction])
            self.image = self.walk_images[self.direction][self.current_frame]
            self.rect = self.image.get_rect(center=self.rect.center)

    def shoot(self):
        now = pg.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            bullet_dir = (self.game.player.pos - self.pos).normalize()
            BossBullet(self.game, self.pos + bullet_dir * 20, bullet_dir)
            self.animating_shoot = True

    def circle_attack(self):
        print("Performing circle attack")  # Debugging print
        self.game.boss_attack_sound.play()  # Play the attack sound
        num_bullets = 20
        angle_step = 360 / num_bullets
        for i in range(num_bullets):
            angle = angle_step * i
            direction = vec(1, 0).rotate(angle)
            BossBullet(self.game, self.pos + direction * 20, direction)

    def shotgun_attack(self):
        print("Performing shotgun attack")  # Debugging print
        self.game.boss_attack_sound.play()  # Play the attack sound
        num_bullets = 12
        spread_angle = 45  # Total spread angle for the shotgun attack
        angle_step = spread_angle / (num_bullets - 1)
        base_angle = (self.game.player.pos - self.pos).angle_to(vec(1, 0)) - spread_angle / 2
        for i in range(num_bullets):
            angle = base_angle + angle_step * i
            direction = vec(1, 0).rotate(angle)
            BossBullet(self.game, self.pos + direction * 20, direction)

    def beam_attack(self):
        print("Starting beam attack")  # Debugging print
        self.beam_attack_start_time = pg.time.get_ticks()
        self.beam_attack_active = True
        self.shoot_delay = 100  # Very fast fire rate

    def perform_attack(self):
        now = pg.time.get_ticks()
        if self.beam_attack_active:
            if now - self.beam_attack_start_time <= self.beam_attack_duration:
                self.shoot()  # Continue shooting during beam attack
            else:
                print("Ending beam attack")  # Debugging print
                self.beam_attack_active = False
                self.shoot_delay = BOSS_FIRERATE  # Reset to normal fire rate
                self.last_attack_time = now  # Reset attack timer
        elif now - self.last_attack_time > self.attack_delay:
            print(f"Performing attack cycle {self.attack_cycle}")  # Debugging print
            self.attack_patterns[self.attack_cycle]()
            self.attack_cycle = (self.attack_cycle + 1) % len(self.attack_patterns)
            self.last_attack_time = now

    def update(self):
        now = pg.time.get_ticks()
        self.can_see_player = self.check_visibility()
        if self.can_see_player:
            self.perform_attack()
            self.update_direction()
        else:
            self.animating_shoot = False

        self.manage_animations(now)

    def update_direction(self):
        player_direction = self.game.player.pos - self.pos
        if abs(player_direction.x) > abs(player_direction.y):
            self.direction = 'right' if player_direction.x > 0 else 'left'
        else:
            self.direction = 'down' if player_direction.y > 0 else 'up'

    def manage_animations(self, now):
        if self.animating_shoot and now - self.last_update > 100:
            self.current_frame = (self.current_frame + 1) % len(self.shoot_images[self.direction])
            self.image = self.shoot_images[self.direction][self.current_frame]
            self.last_update = now
        elif now - self.last_update > 100:
            self.current_frame = (self.current_frame + 1) % len(self.idle_images[self.direction])
            self.image = self.idle_images[self.direction][self.current_frame]
            self.last_update = now

    def check_visibility(self):
        if self.pos.distance_to(self.game.player.pos) < self.vision_radius:
            for wall in self.game.walls:
                if wall.rect.clipline(self.pos, self.game.player.pos):
                    return False
            return True
        return False

    def draw_health(self, screen, camera):
        if self.health > 700:
            col = GREEN
        elif self.health > 400:
            col = YELLOW
        else:
            col = RED
        width = int(self.rect.width * self.health / BOSS_HEALTH)

        screen_pos = camera.apply(self)
        background_bar = pg.Rect(screen_pos.left, screen_pos.top - 10 * self.scale_factor, self.rect.width, 7)
        health_bar = pg.Rect(screen_pos.left, screen_pos.top - 10 * self.scale_factor, width, 7)

        pg.draw.rect(screen, BLACK, background_bar)
        pg.draw.rect(screen, col, health_bar)

    def get_hit(self, damage):
        self.health -= damage
        if self.health <= 0:
            self.kill()



class BossBullet(pg.sprite.Sprite):
    def __init__(self, game, pos, dir):
        self.groups = game.all_sprites, game.bullets2
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pg.image.load('img/boss_bullet.png').convert_alpha()
        self.rect = self.image.get_rect()
        self.pos = vec(pos)
        self.vel = dir * BOSS_BULLET_SPEED
        self.rect.center = self.pos
        self.spawn_time = pg.time.get_ticks()

    def update(self):
        self.pos += self.vel * self.game.dt
        self.rect.center = self.pos
        if pg.sprite.spritecollideany(self, self.game.walls) or not self.game.map_rect.contains(self.rect):
            self.kill()



class BossBullet(pg.sprite.Sprite):
    def __init__(self, game, pos, dir):
        self.groups = game.all_sprites, game.bullets2
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pg.image.load('img/boss_bullet.png').convert_alpha()
        self.rect = self.image.get_rect()
        self.pos = vec(pos)
        self.vel = dir * BOSS_BULLET_SPEED
        self.rect.center = self.pos
        self.spawn_time = pg.time.get_ticks()

    def update(self):
        self.pos += self.vel * self.game.dt
        self.rect.center = self.pos
        if pg.sprite.spritecollideany(self, self.game.walls) or not self.game.map_rect.contains(self.rect):
            self.kill()






#OBJECTS AND CONSUMABLE SPRITES

class Bullet(pg.sprite.Sprite):
    def __init__(self, game, pos, dir):
        self.groups = game.all_sprites, game.bullets
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.bullet_img
        self.rect = self.image.get_rect()
        self.hit_rect = self.rect
        self.pos = vec(pos)
        self.rect.center = pos
        spread = uniform(-GUN_SPREAD, GUN_SPREAD)
        self.vel = dir.rotate(spread) * BULLET_SPEED
        self.spawn_time = pg.time.get_ticks()

    def update(self):
        self.pos += self.vel * self.game.dt
        self.rect.center = self.pos
        if pg.sprite.spritecollideany(self, self.game.walls):
            self.kill()
        if pg.time.get_ticks() - self.spawn_time > BULLET_LIFETIME:
            self.kill()

class Bullet2(pg.sprite.Sprite):
    def __init__(self, game, pos, dir):
        self.groups = game.all_sprites, game.bullets2
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        # Load a specific image for Bullet2
        self.image = pg.image.load('img/bullet2.png').convert_alpha()  # Ensure this is the correct path
        self.rect = self.image.get_rect()
        self.pos = vec(pos)
        self.vel = dir * BULLET2_SPEED  # Assuming BULLET_SPEED is defined
        self.rect.center = self.pos
        self.spawn_time = pg.time.get_ticks()

    def update(self):
        self.pos += self.vel * self.game.dt
        self.rect.center = self.pos
        # Check for collision with walls or going out of bounds
        if pg.sprite.spritecollideany(self, self.game.walls) or not self.game.map_rect.contains(self.rect):
            self.kill()



class Wall(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites, game.walls
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.wall_img
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE

class Obstacle(pg.sprite.Sprite):
    def __init__(self, game, x, y, w, h):
        self.groups = game.walls
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.rect = pg.Rect(x, y, w, h)
        self.hit_rect = self.rect
        self.x = x
        self.y = y
        self.rect.x = x
        self.rect.y = y

class Ammo(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites, game.ammo_group
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.ammo_img
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    #def update(self):
        # check for collision with player
       # hits = pg.sprite.spritecollide(self.game.player, self.game.ammo_group, True)  # True to delete ammo on pickup
       # for hit in hits:
            #self.game.player.ammo += 20  # Increase player's ammo by 10 for each pickup
            # You can limit max ammo if necessary
class Medkit(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites, game.medkit
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pg.image.load('img/medkit.png').convert_alpha()  # Update path as necessary
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.heal_amount = 40

    def heal(self, player):
        if player.health + self.heal_amount > PLAYER_MAX_HEALTH:
            player.health = PLAYER_MAX_HEALTH  # Cap health at maximum
        else:
            player.health += self.heal_amount
        self.kill()  # Remove medkit after use



class Door(pg.sprite.Sprite):
    def __init__(self, game, x, y, locked=False):
        self.groups = game.all_sprites, game.doors
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.locked = locked
        self.load_images()  # Load images must be defined before setting the image
        self.image = self.frames[0]
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y
        self.animating = False
        self.current_frame = 0
        self.last_update = pg.time.get_ticks()
        self.frame_rate = 100

    def load_images(self):
        self.frames = []
        sprite_sheet_image = pg.image.load(path.join('animations/door.png')).convert_alpha()
        frame_width = 32  # Width of each frame
        frame_count = 5  # Total number of frames
        for i in range(frame_count):
            frame = sprite_sheet_image.subsurface((i * frame_width, 0, frame_width, frame_width))
            self.frames.append(frame)

    def open(self):
        if not self.locked and not self.animating:
            self.animating = True  # Only start animating if the door is not already animating

    def update(self):
        now = pg.time.get_ticks()
        if self.animating:
            if now - self.last_update > self.frame_rate:
                self.last_update = now
                self.current_frame += 1  # Move to the next frame
                if self.current_frame >= len(self.frames):
                    self.current_frame = len(self.frames) - 1  # Stay on the last frame
                    self.animating = False  # Stop animating
                self.image = self.frames[self.current_frame]
                self.rect = self.image.get_rect(topleft=(self.rect.x, self.rect.y))



class FinishTrigger(pg.sprite.Sprite):
    def __init__(self, game, x, y, w, h):
        self.groups = game.all_sprites, game.finish_triggers
        pg.sprite.Sprite.__init__(self, self.groups)
        self.image = pg.Surface((w, h), pg.SRCALPHA)  # SRCALPHA makes it transparent
        self.rect = self.image.get_rect(topleft=(x, y))
        self.game = game


