import pygame as pg
import sys
from os import path
from settings import *
from sprites import *
from random import uniform
from tilemap import *
from button import *

def get_font(size):  # Make sure this is accessible
    return pg.font.Font("assets/font.ttf", size)

# HUD functions
def draw_player_health(surf, x, y, pct):
    if pct < 0:
        pct = 0
    BAR_LENGTH = 200
    BAR_HEIGHT = 20
    fill = pct * BAR_LENGTH
    outline_rect = pg.Rect(x, y, BAR_LENGTH, BAR_HEIGHT)
    fill_rect = pg.Rect(x, y, fill, BAR_HEIGHT)
    if pct > 0.6:
        col = GREEN
    elif pct > 0.3:
        col = YELLOW
    else:
        col = RED
    pg.draw.rect(surf, col, fill_rect)
    pg.draw.rect(surf, WHITE, outline_rect, 2)

def draw_ammo(surf, ammo):
    font = pg.font.Font(None, 36)  # You can adjust the font size as needed
    text = font.render(f'Ammo: {ammo}', True, pg.Color('white'))
    surf.blit(text, (10, 50))  # Position the ammo count on the screen

def show_end_game_menu(self):
    while True:
        END_GAME_MOUSE_POS = pg.mouse.get_pos()
        self.screen.fill("black")

        END_GAME_TEXT = get_font(85).render("Game Over", True, "Red")
        END_GAME_RECT = END_GAME_TEXT.get_rect(center=(WIDTH / 2, HEIGHT / 3.5))
        self.screen.blit(END_GAME_TEXT, END_GAME_RECT)

        RESTART_BUTTON = Button(image=None, pos=(WIDTH / 2, HEIGHT / 2),
                                text_input="RESTART", font=get_font(55), base_color="White", hovering_color="Green")
        MAIN_MENU_BUTTON = Button(image=None, pos=(WIDTH / 2, HEIGHT / 2 + 100),
                                  text_input="MAIN MENU", font=get_font(55), base_color="White", hovering_color="Green")
        QUIT_BUTTON = Button(image=None, pos=(WIDTH / 2, HEIGHT / 2 + 200),
                             text_input="QUIT", font=get_font(55), base_color="White", hovering_color="Green")

        for button in [RESTART_BUTTON, MAIN_MENU_BUTTON, QUIT_BUTTON]:
            button.changeColor(END_GAME_MOUSE_POS)
            button.update(self.screen)

        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            if event.type == pg.MOUSEBUTTONDOWN:
                self.button_click_sound.play()  # Play button click sound
                if RESTART_BUTTON.checkForInput(END_GAME_MOUSE_POS):
                    self.reset_game(full_reset=True)  # Full reset on restart
                    self.load_level(self.current_level)  # Restart from current level
                    self.run()  # Ensure the game starts running after restart
                    return
                elif MAIN_MENU_BUTTON.checkForInput(END_GAME_MOUSE_POS):
                    self.reset_game(full_reset=True)  # Full reset when returning to the main menu
                    self.main_menu(self)
                elif QUIT_BUTTON.checkForInput(END_GAME_MOUSE_POS):
                    pg.quit()
                    sys.exit()

            pg.display.update()

def show_opening_crawl(screen, text_lines):
    clock = pg.time.Clock()
    crawl_speed = 1  # Slower crawl speed
    font = get_font(30)  # Adjust font size as needed

    # Create a surface for the text
    text_surface = pg.Surface((WIDTH, HEIGHT * 2))
    text_surface.fill((0, 0, 0))

    # Render the text lines onto the surface
    y = HEIGHT
    for line in text_lines:
        rendered_text = font.render(line, True, (255, 255, 0))  # Yellow text
        text_rect = rendered_text.get_rect(center=(WIDTH / 2, y))
        text_surface.blit(rendered_text, text_rect)
        y += 40  # Adjust line spacing as needed

    # Scroll the text surface upwards
    y_offset = 0
    while y_offset < text_surface.get_height() - HEIGHT:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()

        screen.fill((0, 0, 0))
        screen.blit(text_surface, (0, -y_offset))
        pg.display.flip()
        y_offset += crawl_speed
        clock.tick(60)

    # After the crawl is done, wait for a key press to continue
    waiting = True
    while waiting:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            if event.type == pg.KEYDOWN:
                waiting = False

class Game:
    def __init__(self, play_callback=None, main_menu_callback=None):
        self.play = play_callback if play_callback else self.default_play
        self.main_menu = main_menu_callback if play_callback else self.default_main_menu
        self.end_game_font = get_font(45)
        self.restart_button = Button(image=None, pos=(WIDTH / 2, HEIGHT / 2),
                                     text_input="RESTART", font=get_font(75), base_color="White",
                                     hovering_color="Green")
        pg.init()
        pg.mixer.init()  # Initialize the mixer
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption(TITLE)
        self.clock = pg.time.Clock()
        self.current_level = 'level1.tmx'  # Initialize current level

        # Load sounds
        self.load_sounds()

        # Sprite groups
        self.all_sprites = pg.sprite.Group()
        self.doors = pg.sprite.Group()
        self.walls = pg.sprite.Group()
        self.mobs = pg.sprite.Group()  # Initialize the mobs group
        self.bullets = pg.sprite.Group()
        self.bullets2 = pg.sprite.Group()
        self.ammo_group = pg.sprite.Group()
        self.medkit = pg.sprite.Group()
        self.finish_triggers = pg.sprite.Group()
        self.load_data()
        self.score = 0
        self.high_score = self.load_high_score()  # Load the high score

        # Play background music
        pg.mixer.music.play(-1)

    def load_sounds(self):
        self.shoot_sound = pg.mixer.Sound(path.join('sounds', 'shoot.mp3'))
        self.death_sound = pg.mixer.Sound(path.join('sounds', 'dead.mp3'))
        self.collect_sound = pg.mixer.Sound(path.join('sounds', 'collect.mp3'))
        self.button_click_sound = pg.mixer.Sound(path.join('sounds', 'click.mp3'))
        self.boss_attack_sound = pg.mixer.Sound(path.join('sounds', 'BossAttack.mp3'))
        pg.mixer.music.load(path.join('sounds', 'song.mp3'))

    def load_data(self):
        game_folder = path.dirname(__file__)
        self.img_folder = path.join(game_folder, 'img')
        self.map_folder = path.join(game_folder, 'maps')
        self.completed_img = pg.image.load(path.join(self.img_folder, 'completed.png')).convert_alpha()
        self.map = TiledMap(path.join(self.map_folder, self.current_level))
        self.map_img = self.map.make_map()
        self.map_rect = self.map_img.get_rect()
        self.bullet_img = pg.image.load(path.join(self.img_folder, BULLET_IMG)).convert_alpha()
        self.mob_img = pg.image.load(path.join(self.img_folder, MOB_IMG)).convert_alpha()
        self.ammo_img = pg.image.load(path.join(self.img_folder, 'ammo.png')).convert_alpha()
        self.medkit_img = pg.image.load(path.join(self.img_folder, 'medkit.png')).convert_alpha()

    def load_level(self, level_name):
        self.current_level = level_name  # Set the current level
        if level_name == 'level3.tmx':
            pg.mixer.music.load(path.join('sounds', 'bossmusic.mp3'))
            pg.mixer.music.play(-1)
        else:
            pg.mixer.music.load(path.join('sounds', 'song.mp3'))
            pg.mixer.music.play(-1)
        self.map = TiledMap(path.join(self.map_folder, level_name))
        self.map_img = self.map.make_map()
        self.map_rect = self.map_img.get_rect()
        self.new()

    def show_crawl_and_load_level(self, level_name):
        if level_name == 'level1.tmx':
            crawl_text = [
                "A long time ago in a school far, far away...",
                "",
                "",
                "",
                "Inky, a student who recently got detention,",
                "must escape the school to play the newest",
                "version of his favorite game.",
                "",
                "With the clock ticking and obstacles in his way,",
                "Inky must navigate through the school, avoid",
                "teachers, and find his way to freedom.",
                "",
                "The adventure begins now...",
                "",
                "",
                "",
                "Click Space to continue."
            ]
            show_opening_crawl(self.screen, crawl_text)
        self.load_level(level_name)

    def new(self):
        # initialize all variables and do all the setup for a new game
        self.all_sprites.empty()
        self.doors.empty()
        self.walls.empty()
        self.mobs.empty()
        self.bullets.empty()
        self.bullets2.empty()
        self.ammo_group.empty()
        self.medkit.empty()
        self.finish_triggers.empty()

        for tile_object in self.map.tmxdata.objects:
            if tile_object.name == 'player':
                self.player = Player(self, tile_object.x, tile_object.y)
            elif tile_object.name == 'zombie':
                Mob(self, tile_object.x, tile_object.y)
            elif tile_object.name == 'zombie2':
                Mob2(self, tile_object.x, tile_object.y)
            elif tile_object.name == 'boss':
                Boss(self, tile_object.x, tile_object.y)
            elif tile_object.name == 'wall':
                Obstacle(self, tile_object.x, tile_object.y, tile_object.width, tile_object.height)
            elif tile_object.name == 'door':
                locked = tile_object.properties.get('locked', False)  # Assume there's a 'locked' property
                Door(self, tile_object.x, tile_object.y, locked)
            elif tile_object.name == 'finish':
                FinishTrigger(self, tile_object.x, tile_object.y, tile_object.width, tile_object.height)
            elif tile_object.name == 'ammo':
                Ammo(self, tile_object.x, tile_object.y)
            elif tile_object.name == 'medkit':
                Medkit(self, tile_object.x, tile_object.y)

        self.camera = Camera(self.map.width, self.map.height)
        self.draw_debug = False

    def run(self):
        self.playing = True
        self.start_timer()  # Start the timer when the game starts
        while self.playing:
            self.dt = self.clock.tick(FPS) / 1000.0
            self.events()
            self.update()
            self.draw()
            pg.display.flip()  # Ensure that display updates are being called

    def quit(self):
        pg.quit()
        sys.exit()

    def update(self):
        # Update all sprites
        self.all_sprites.update()
        self.camera.update(self.player)

        # Mobs hit player
        hits = pg.sprite.spritecollide(self.player, self.mobs, False, collide_hit_rect)
        for mob in hits:
            self.player.health -= MOB_DAMAGE
            if self.player.health <= 0:
                self.playing = False
                self.update_high_score()  # Update high score if player dies
                self.death_sound.play()  # Play death sound

        # Handling Bullet2 hits in the Game.update() method
        hits = pg.sprite.spritecollide(self.player, self.bullets2, True, pg.sprite.collide_mask)
        for hit in hits:
            self.player.health -= 10  # Adjust based on damage defined
            if self.player.health <= 0:
                self.playing = False  # Or handle game over
                self.update_high_score()  # Update high score if player dies
                self.death_sound.play()  # Play death sound

        # Regular bullets hit mobs
        hits = pg.sprite.groupcollide(self.mobs, self.bullets, False, True)
        for mob, bullets in hits.items():
            for bullet in bullets:
                if isinstance(mob, Mob2):
                    mob.get_hit(BULLET_DAMAGE)
                else:
                    mob.health -= BULLET_DAMAGE
                if mob.health <= 0:
                    mob.kill()
                    if isinstance(mob, Boss):
                        self.score += 2500  # Award 2500 points for killing the boss
                    else:
                        self.score += 100

        # Handle ammo pickups
        ammo_hits = pg.sprite.spritecollide(self.player, self.ammo_group, True)
        for ammo in ammo_hits:
            self.collect_sound.play()  # Play collect sound
            self.player.ammo += 20  # Assuming you want to increase ammo by 20 per pickup
            self.score += 50  # Add points for picking up ammo

        # Handle medkit pickups
        medkit_hits = pg.sprite.spritecollide(self.player, self.medkit, True)
        for medkit in medkit_hits:
            self.collect_sound.play()  # Play collect sound
            medkit.heal(self.player)
            self.score += 50  # Add points for picking up medkits

        # Check for level completion
        if pg.sprite.spritecollide(self.player, self.finish_triggers, False):
            self.handle_level_complete()

        # Door interactions
        door_hits = pg.sprite.spritecollide(self.player, self.doors, False)
        for door in door_hits:
            if not door.animating:
                door.open()

        # Check if player dies
        if self.player.health <= 0:
            self.playing = False
            self.update_high_score()  # Update high score if player dies
            show_end_game_menu(self)

    def handle_level_complete(self):
        if self.current_level == 'level3.tmx':
            self.show_game_completed_menu()
        else:
            self.show_level_complete_menu()

    def show_game_completed_menu(self):
        while True:
            GAME_COMPLETED_MOUSE_POS = pg.mouse.get_pos()
            self.screen.blit(self.completed_img, (0, 0))  # Blit the completed image as the background

            GAME_COMPLETED_TEXT = get_font(85).render("Game Completed!", True, "Green")
            GAME_COMPLETED_RECT = GAME_COMPLETED_TEXT.get_rect(center=(WIDTH / 2, HEIGHT / 3.5))
            self.screen.blit(GAME_COMPLETED_TEXT, GAME_COMPLETED_RECT)

            RESTART_BUTTON = Button(image=None, pos=(WIDTH / 2, HEIGHT / 2),
                                    text_input="RESTART", font=get_font(55), base_color="Yellow", hovering_color="Green")
            MAIN_MENU_BUTTON = Button(image=None, pos=(WIDTH / 2, HEIGHT / 2 + 100),
                                      text_input="MAIN MENU", font=get_font(55), base_color="Yellow", hovering_color="Green")
            QUIT_BUTTON = Button(image=None, pos=(WIDTH / 2, HEIGHT / 2 + 200),
                                 text_input="QUIT", font=get_font(55), base_color="Red", hovering_color="Green")

            for button in [RESTART_BUTTON, MAIN_MENU_BUTTON, QUIT_BUTTON]:
                button.changeColor(GAME_COMPLETED_MOUSE_POS)
                button.update(self.screen)

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()
                if event.type == pg.MOUSEBUTTONDOWN:
                    self.button_click_sound.play()  # Play button click sound
                    if RESTART_BUTTON.checkForInput(GAME_COMPLETED_MOUSE_POS):
                        self.reset_game(full_reset=False)  # Restart level 3
                        self.load_level('level3.tmx')
                        self.run()
                        return
                    elif MAIN_MENU_BUTTON.checkForInput(GAME_COMPLETED_MOUSE_POS):
                        self.reset_game(full_reset=True)  # Full reset when returning to the main menu
                        self.main_menu(self)
                        return
                    elif QUIT_BUTTON.checkForInput(GAME_COMPLETED_MOUSE_POS):
                        pg.quit()
                        sys.exit()

            pg.display.update()

    def show_level_complete_menu(self):
        while True:
            LEVEL_COMPLETE_MOUSE_POS = pg.mouse.get_pos()
            self.screen.fill("black")

            LEVEL_COMPLETE_TEXT = get_font(85).render("Level Complete", True, "White")
            LEVEL_COMPLETE_RECT = LEVEL_COMPLETE_TEXT.get_rect(center=(WIDTH / 2, HEIGHT / 3.5))
            self.screen.blit(LEVEL_COMPLETE_TEXT, LEVEL_COMPLETE_RECT)

            CONTINUE_BUTTON = Button(image=None, pos=(WIDTH / 2, HEIGHT / 2),
                                     text_input="CONTINUE", font=get_font(55), base_color="White", hovering_color="Green")
            MAIN_MENU_BUTTON = Button(image=None, pos=(WIDTH / 2, HEIGHT / 2 + 100),
                                      text_input="MAIN MENU", font=get_font(55), base_color="White", hovering_color="Green")
            QUIT_BUTTON = Button(image=None, pos=(WIDTH / 2, HEIGHT / 2 + 200),
                                 text_input="QUIT", font=get_font(55), base_color="White", hovering_color="Green")

            for button in [CONTINUE_BUTTON, MAIN_MENU_BUTTON, QUIT_BUTTON]:
                button.changeColor(LEVEL_COMPLETE_MOUSE_POS)
                button.update(self.screen)

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()
                if event.type == pg.MOUSEBUTTONDOWN:
                    self.button_click_sound.play()  # Play button click sound
                    if CONTINUE_BUTTON.checkForInput(LEVEL_COMPLETE_MOUSE_POS):
                        next_level = 'level2.tmx' if self.current_level == 'level1.tmx' else 'level3.tmx'
                        self.load_level(next_level)  # Load the next level dynamically
                        return
                    elif MAIN_MENU_BUTTON.checkForInput(LEVEL_COMPLETE_MOUSE_POS):
                        self.reset_game()  # Reset the game when returning to the main menu
                        self.main_menu(self)
                    elif QUIT_BUTTON.checkForInput(LEVEL_COMPLETE_MOUSE_POS):
                        pg.quit()
                        sys.exit()

            pg.display.update()

    def draw_score(self):
        font = pg.font.Font(None, 36)  # Adjust the font size as needed
        text = font.render(f'Score: {self.score}', True, pg.Color('white'))
        self.screen.blit(text, (WIDTH - 10 - text.get_width(), 10))  # Top right corner

    def draw_high_score(self):
        font = pg.font.Font(None, 36)  # Adjust the font size as needed
        text = font.render(f'High Score: {self.high_score}', True, pg.Color('gold'))
        self.screen.blit(text, (WIDTH - 10 - text.get_width(), HEIGHT - 40))  # Bottom right corner

    def draw_boss_health_bar(self):
        boss = next((sprite for sprite in self.mobs if isinstance(sprite, Boss) and sprite.can_see_player), None)
        if boss:
            BAR_LENGTH = 400
            BAR_HEIGHT = 30
            fill = boss.health / BOSS_HEALTH * BAR_LENGTH
            outline_rect = pg.Rect(WIDTH // 2 - BAR_LENGTH // 2, HEIGHT - BAR_HEIGHT - 10, BAR_LENGTH, BAR_HEIGHT)
            fill_rect = pg.Rect(WIDTH // 2 - BAR_LENGTH // 2, HEIGHT - BAR_HEIGHT - 10, fill, BAR_HEIGHT)
            col = RED if fill < BAR_LENGTH / 3 else GREEN
            pg.draw.rect(self.screen, col, fill_rect)
            pg.draw.rect(self.screen, WHITE, outline_rect, 2)
            boss_name_text = get_font(30).render("Principal Gorlock, The Punisher", True, pg.Color('white'))
            self.screen.blit(boss_name_text, (WIDTH // 2 - boss_name_text.get_width() // 2, HEIGHT - BAR_HEIGHT - 60))

    def draw(self):
        pg.display.set_caption("{:.2f}".format(self.clock.get_fps()))
        self.screen.blit(self.map_img, self.camera.apply_rect(self.map_rect))

        for sprite in self.all_sprites:
            if not isinstance(sprite, FinishTrigger):
                self.screen.blit(sprite.image, self.camera.apply(sprite))
                if isinstance(sprite, Mob) or isinstance(sprite, Mob2) or isinstance(sprite, Boss):
                    sprite.draw_health(self.screen, self.camera)  # Draw health bar for Mob, Mob2, and Boss

            if self.draw_debug:
                pg.draw.rect(self.screen, CYAN, self.camera.apply_rect(sprite.hit_rect), 1)

        if self.draw_debug:
            for wall in self.walls:
                pg.draw.rect(self.screen, CYAN, self.camera.apply_rect(wall.rect), 1)

        # HUD functions
        draw_player_health(self.screen, 10, 10, self.player.health / PLAYER_HEALTH)
        draw_ammo(self.screen, self.player.ammo)  # Draw the ammo count
        self.draw_score()
        self.draw_high_score()
        self.draw_timer()
        if any(isinstance(sprite, Boss) and sprite.can_see_player for sprite in self.mobs):
            self.draw_boss_health_bar()

        pg.display.flip()

    def events(self):
        # catch all events here
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.quit()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    self.pause_timer()  # Pause the timer when game is paused
                    self.show_pause_menu()
                if event.key == pg.K_h:
                    self.draw_debug = not self.draw_debug

    def show_pause_menu(self):
        paused = True
        while paused:
            PAUSE_MOUSE_POS = pg.mouse.get_pos()
            self.screen.fill("black")

            PAUSE_TEXT = get_font(85).render("Paused", True, "White")
            PAUSE_RECT = PAUSE_TEXT.get_rect(center=(WIDTH / 2, HEIGHT / 3.5))
            self.screen.blit(PAUSE_TEXT, PAUSE_RECT)

            RESUME_BUTTON = Button(image=None, pos=(WIDTH / 2, HEIGHT / 2),
                                   text_input="RESUME", font=get_font(55), base_color="White", hovering_color="Green")
            RESTART_BUTTON = Button(image=None, pos=(WIDTH / 2, HEIGHT / 2 + 100),
                                    text_input="RESTART", font=get_font(55), base_color="White", hovering_color="Green")
            MAIN_MENU_BUTTON = Button(image=None, pos=(WIDTH / 2, HEIGHT / 2 + 200),
                                      text_input="MAIN MENU", font=get_font(55), base_color="White", hovering_color="Green")
            QUIT_BUTTON = Button(image=None, pos=(WIDTH / 2, HEIGHT / 2 + 300),
                                 text_input="QUIT", font=get_font(55), base_color="White", hovering_color="Green")

            for button in [RESUME_BUTTON, RESTART_BUTTON, MAIN_MENU_BUTTON, QUIT_BUTTON]:
                button.changeColor(PAUSE_MOUSE_POS)
                button.update(self.screen)

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()
                if event.type == pg.MOUSEBUTTONDOWN:
                    self.button_click_sound.play()  # Play button click sound
                    if RESUME_BUTTON.checkForInput(PAUSE_MOUSE_POS):
                        self.resume_timer()  # Resume the timer when the game is resumed
                        paused = False
                    elif RESTART_BUTTON.checkForInput(PAUSE_MOUSE_POS):
                        self.reset_game(full_reset=True)  # Full reset on restart
                        self.load_level(self.current_level)
                        self.run()
                        return
                    elif MAIN_MENU_BUTTON.checkForInput(PAUSE_MOUSE_POS):
                        self.reset_game(full_reset=True)  # Full reset when returning to the main menu
                        self.main_menu(self)
                        return
                    elif QUIT_BUTTON.checkForInput(PAUSE_MOUSE_POS):
                        pg.quit()
                        sys.exit()

            pg.display.update()

    def show_start_screen(self):
        pass

    def show_go_screen(self):
        pass

    def default_play(self):
        # Default play behavior if no callback is provided
        pass

    def default_main_menu(self):
        # Default main menu behavior if no callback is provided
        pass

    def start_timer(self):
        self.start_time = pg.time.get_ticks()
        self.paused_time = 0

    def pause_timer(self):
        self.paused_time = pg.time.get_ticks()

    def resume_timer(self):
        if self.paused_time:
            self.start_time += pg.time.get_ticks() - self.paused_time
            self.paused_time = 0

    def reset_game(self, full_reset=False):
        self.score = 0 if full_reset else self.score
        self.start_timer()  # Restart the timer

    def draw_timer(self):
        if self.paused_time:
            elapsed_time = self.paused_time - self.start_time
        else:
            elapsed_time = pg.time.get_ticks() - self.start_time
        seconds = elapsed_time // 1000
        minutes = seconds // 60
        seconds = seconds % 60
        timer_text = get_font(30).render(f'{minutes:02}:{seconds:02}', True, pg.Color('white'))
        self.screen.blit(timer_text, (WIDTH // 2 - timer_text.get_width() // 2, 10))

    def update_high_score(self):
        if self.score > self.high_score:
            self.high_score = self.score
            self.save_high_score()

    def save_high_score(self):
        with open('highscore.txt', 'w') as file:
            file.write(str(self.high_score))

    def load_high_score(self):
        try:
            with open('highscore.txt', 'r') as file:
                return int(file.read())
        except FileNotFoundError:
            return 0
