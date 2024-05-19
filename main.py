import pygame as pg
import sys
from settings import *
from tilemap import *
from os import path
from button import *
from splashscreen import *
from game import *
from tilemap import *

pg.init()
pg.mixer.init()

# Load and play background music once
pg.mixer.music.load(path.join('sounds', 'song.mp3'))
pg.mixer.music.play(-1)

# Background Animation
frames = []
for i in range(1, 23):  # Adjust the range based on your frame count
    # Load each frame image
    frame = pg.image.load(f"schoolbusgif/schoolbus{i}.jpg")
    # Scale the frame to fill the screen
    scaled_frame = pg.transform.scale(frame, (WIDTH, HEIGHT))
    # Append the scaled frame to the frames list
    frames.append(scaled_frame)

# Frame settings
current_frame = 0  # Start with the first frame
frame_count = len(frames)  # Total number of frames

fullscreen = False  # Global fullscreen variable

def get_font(size):  # Returns Press-Start-2P in the desired size
    return pg.font.Font("assets/font.ttf", size)

def set_screen_mode():
    global SCREEN, fullscreen
    if fullscreen:
        SCREEN = pg.display.set_mode((WIDTH, HEIGHT), pg.FULLSCREEN)
    else:
        SCREEN = pg.display.set_mode((WIDTH, HEIGHT))

def play(level, g):
    g.show_crawl_and_load_level(level)
    g.run()

def level_select(g):
    global current_frame, fullscreen
    clock = pg.time.Clock()
    set_screen_mode()

    while True:
        LEVEL_SELECT_MOUSE_POS = pg.mouse.get_pos()
        SCREEN.blit(frames[current_frame], (0, 0))

        # Create a semi-transparent box
        box_surface = pg.Surface((400, 500), pg.SRCALPHA)  # Width, Height
        box_surface.fill((0, 0, 0, 128))  # RGBA

        # Blit the semi-transparent box to the screen
        SCREEN.blit(box_surface, (WIDTH / 2 - 200, HEIGHT / 2 - 200))  # Position it at the center

        LEVEL_SELECT_TEXT = get_font(70).render("Select Level", True, "White")
        LEVEL_SELECT_RECT = LEVEL_SELECT_TEXT.get_rect(center=(WIDTH / 2, HEIGHT / 6 - 50))
        SCREEN.blit(LEVEL_SELECT_TEXT, LEVEL_SELECT_RECT)

        LEVEL_1_BUTTON = Button(image=None, pos=(WIDTH / 2, HEIGHT / 2 - 100),
                                text_input="LEVEL 1", font=get_font(55), base_color="White", hovering_color="Green")
        LEVEL_2_BUTTON = Button(image=None, pos=(WIDTH / 2, HEIGHT / 2),
                                text_input="LEVEL 2", font=get_font(55), base_color="White", hovering_color="Green")
        LEVEL_3_BUTTON = Button(image=None, pos=(WIDTH / 2, HEIGHT / 2 + 100),
                                text_input="LEVEL 3", font=get_font(55), base_color="White", hovering_color="Green")
        BACK_BUTTON = Button(image=None, pos=(WIDTH / 2, HEIGHT / 2 + 200),
                             text_input="BACK", font=get_font(55), base_color="White", hovering_color="Red")

        for button in [LEVEL_1_BUTTON, LEVEL_2_BUTTON, LEVEL_3_BUTTON, BACK_BUTTON]:
            button.changeColor(LEVEL_SELECT_MOUSE_POS)
            button.update(SCREEN)

        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            if event.type == pg.MOUSEBUTTONDOWN:
                g.button_click_sound.play()  # Play button click sound
                if LEVEL_1_BUTTON.checkForInput(LEVEL_SELECT_MOUSE_POS):
                    play('level1.tmx', g)
                if LEVEL_2_BUTTON.checkForInput(LEVEL_SELECT_MOUSE_POS):
                    play('level2.tmx', g)
                if LEVEL_3_BUTTON.checkForInput(LEVEL_SELECT_MOUSE_POS):
                    play('level3.tmx', g)
                if BACK_BUTTON.checkForInput(LEVEL_SELECT_MOUSE_POS):
                    main_menu(g)

        # Display the high score
        font = pg.font.Font(None, 36)  # Adjust the font size as needed
        text = font.render(f'High Score: {g.high_score}', True, pg.Color('gold'))
        SCREEN.blit(text, (WIDTH - 10 - text.get_width(), HEIGHT - 40))  # Bottom right corner

        current_frame = (current_frame + 1) % frame_count
        clock.tick(10)
        pg.display.update()

def options(g):
    while True:
        OPTIONS_MOUSE_POS = pg.mouse.get_pos()
        SCREEN.blit(frames[current_frame], (0, 0))  # Blit the background animation

        # Create a semi-transparent box
        box_surface = pg.Surface((400, 300), pg.SRCALPHA)
        box_surface.fill((0, 0, 0, 128))
        SCREEN.blit(box_surface, (WIDTH / 2 - 200, HEIGHT / 2 - 150))

        OPTIONS_TEXT = get_font(75).render("OPTIONS", True, "White")
        OPTIONS_RECT = OPTIONS_TEXT.get_rect(center=(WIDTH / 2, HEIGHT / 7))
        SCREEN.blit(OPTIONS_TEXT, OPTIONS_RECT)

        TUTORIAL_BUTTON = Button(image=None, pos=(WIDTH / 2, HEIGHT / 2.2 - 50),
                                 text_input="TUTORIAL", font=get_font(40), base_color="White", hovering_color="Green")
        SETTINGS_BUTTON = Button(image=None, pos=(WIDTH / 2, HEIGHT / 2.2 + 50),
                                 text_input="SETTINGS", font=get_font(40), base_color="White", hovering_color="Green")
        BACK_BUTTON = Button(image=None, pos=(WIDTH / 2, HEIGHT / 2.2 + 150),
                             text_input="BACK", font=get_font(40), base_color="White", hovering_color="Red")

        for button in [TUTORIAL_BUTTON, SETTINGS_BUTTON, BACK_BUTTON]:
            button.changeColor(OPTIONS_MOUSE_POS)
            button.update(SCREEN)

        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            if event.type == pg.MOUSEBUTTONDOWN:
                g.button_click_sound.play()  # Play button click sound
                if TUTORIAL_BUTTON.checkForInput(OPTIONS_MOUSE_POS):
                    tutorial(g)  # Display the tutorial image
                if SETTINGS_BUTTON.checkForInput(OPTIONS_MOUSE_POS):
                    settings(g)
                if BACK_BUTTON.checkForInput(OPTIONS_MOUSE_POS):
                    main_menu(g)

        pg.display.update()

def settings(g):
    global current_frame, SCREEN, fullscreen  # Declare SCREEN and fullscreen as global
    clock = pg.time.Clock()
    volume = pg.mixer.music.get_volume()  # Get current volume
    set_screen_mode()

    while True:
        SETTINGS_MOUSE_POS = pg.mouse.get_pos()
        SCREEN.blit(frames[current_frame], (0, 0))  # Blit the background animation

        # Create a semi-transparent box
        box_surface = pg.Surface((400, 300), pg.SRCALPHA)
        box_surface.fill((0, 0, 0, 128))
        SCREEN.blit(box_surface, (WIDTH / 2 - 200, HEIGHT / 2 - 150))

        SETTINGS_TEXT = get_font(45).render("SETTINGS", True, "White")
        SETTINGS_RECT = SETTINGS_TEXT.get_rect(center=(WIDTH / 2, HEIGHT / 4))
        SCREEN.blit(SETTINGS_TEXT, SETTINGS_RECT)

        VOLUME_TEXT = get_font(30).render("Volume", True, "White")
        VOLUME_RECT = VOLUME_TEXT.get_rect(center=(WIDTH / 2, HEIGHT / 2 - 50))
        SCREEN.blit(VOLUME_TEXT, VOLUME_RECT)

        # Draw volume slider
        pg.draw.rect(SCREEN, "White", (WIDTH / 2 - 100, HEIGHT / 2, 200, 10))
        pg.draw.circle(SCREEN, "Green", (int(WIDTH / 2 - 100 + volume * 200), HEIGHT / 2), 10)

        FULLSCREEN_BUTTON = Button(image=None, pos=(WIDTH / 2, HEIGHT / 2 + 50),
                                   text_input="FULLSCREEN", font=get_font(30), base_color="White", hovering_color="Green")
        BACK_BUTTON = Button(image=None, pos=(WIDTH / 2, HEIGHT / 2 + 150),
                             text_input="BACK", font=get_font(55), base_color="White", hovering_color="Red")

        for button in [FULLSCREEN_BUTTON, BACK_BUTTON]:
            button.changeColor(SETTINGS_MOUSE_POS)
            button.update(SCREEN)

        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            if event.type == pg.MOUSEBUTTONDOWN:
                g.button_click_sound.play()  # Play button click sound
                if event.button == 1:
                    if BACK_BUTTON.checkForInput(SETTINGS_MOUSE_POS):
                        options(g)
                    if FULLSCREEN_BUTTON.checkForInput(SETTINGS_MOUSE_POS):
                        fullscreen = not fullscreen
                        set_screen_mode()
                    # Check if the volume slider is being adjusted
                    if WIDTH / 2 - 100 <= SETTINGS_MOUSE_POS[0] <= WIDTH / 2 + 100 and HEIGHT / 2 - 10 <= SETTINGS_MOUSE_POS[1] <= HEIGHT / 2 + 10:
                        volume = (SETTINGS_MOUSE_POS[0] - (WIDTH / 2 - 100)) / 200
                        pg.mixer.music.set_volume(volume)  # Set the volume for the music
                        g.shoot_sound.set_volume(volume)  # Set the volume for the shoot sound
                        g.death_sound.set_volume(volume)  # Set the volume for the death sound
                        g.collect_sound.set_volume(volume)  # Set the volume for the collect sound
                        g.button_click_sound.set_volume(volume)  # Set the volume for the button click sound

        current_frame = (current_frame + 1) % frame_count
        clock.tick(10)
        pg.display.update()

def tutorial(g):
    global current_frame
    clock = pg.time.Clock()
    set_screen_mode()

    while True:
        TUTORIAL_MOUSE_POS = pg.mouse.get_pos()
        SCREEN.fill((0, 0, 0))  # Fill the screen with black

        # Load and display the tutorial image
        tutorial_img = pg.image.load('img/tutorial.jpg').convert_alpha()
        tutorial_img = pg.transform.scale(tutorial_img, (WIDTH, HEIGHT))  # Scale the image to fit the screen
        SCREEN.blit(tutorial_img, (0, 0))

        BACK_BUTTON = Button(image=None, pos=(WIDTH - 100, HEIGHT - 50),
                             text_input="BACK", font=get_font(55), base_color="White", hovering_color="Red")

        BACK_BUTTON.changeColor(TUTORIAL_MOUSE_POS)
        BACK_BUTTON.update(SCREEN)

        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            if event.type == pg.MOUSEBUTTONDOWN:
                g.button_click_sound.play()  # Play button click sound
                if BACK_BUTTON.checkForInput(TUTORIAL_MOUSE_POS):
                    options(g)

        current_frame = (current_frame + 1) % frame_count
        clock.tick(10)
        pg.display.update()

def main_menu(g):
    global current_frame

    clock = pg.time.Clock()
    set_screen_mode()
    pg.mixer.music.load(path.join('sounds', 'song.mp3'))
    pg.mixer.music.play(-1)

    while True:
        SCREEN.blit(frames[current_frame], (0, 0))
        MENU_MOUSE_POS = pg.mouse.get_pos()


        MENU_TEXT = get_font(50).render("The Bell Doesn't Dismiss You!", True, "Yellow")
        MENU_RECT = MENU_TEXT.get_rect(center=(640, 100))

        PLAY_BUTTON = Button(image=pg.image.load("menubuttons/Play Rect.png"), pos=(640, 250),
                             text_input="PLAY", font=get_font(55), base_color="White", hovering_color="Green")
        OPTIONS_BUTTON = Button(image=pg.image.load("menubuttons/Options Rect.png"), pos=(640, 400),
                                text_input="OPTIONS", font=get_font(55), base_color="White", hovering_color="Green")
        QUIT_BUTTON = Button(image=pg.image.load("menubuttons/Quit Rect.png"), pos=(640, 550),
                             text_input="QUIT", font=get_font(55), base_color="White", hovering_color="Red")

        SCREEN.blit(MENU_TEXT, MENU_RECT)

        for button in [PLAY_BUTTON, OPTIONS_BUTTON, QUIT_BUTTON]:
            button.changeColor(MENU_MOUSE_POS)
            button.update(SCREEN)

        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            if event.type == pg.MOUSEBUTTONDOWN:
                g.button_click_sound.play()  # Play button click sound
                if PLAY_BUTTON.checkForInput(MENU_MOUSE_POS):
                    level_select(g)  # Go to level select screen

                if OPTIONS_BUTTON.checkForInput(MENU_MOUSE_POS):
                    options(g)
                if QUIT_BUTTON.checkForInput(MENU_MOUSE_POS):
                    pg.quit()
                    sys.exit()

        # Update the frame index for the next loop iteration
        current_frame = (current_frame + 1) % frame_count

        # Control the frame rate
        clock.tick(10)

        pg.display.update()

splash = splashscreen()
splash.show_start_screen()
g = Game(play, main_menu)
main_menu(g)
