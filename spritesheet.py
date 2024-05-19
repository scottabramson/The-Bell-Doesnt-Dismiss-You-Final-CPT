import pygame
from settings import *

# Initialize Pygame
pygame.init()


# Clock for controlling frame rate
clock = pygame.time.Clock()

# Load the sprite sheets
sprite_sheet = pygame.image.load('animations/throw.png').convert_alpha()
sprite_sheet_run = pygame.image.load('animations/run.png').convert_alpha()
sprite_sheet_idle = pygame.image.load('animations/idle.png').convert_alpha()  # Load idle sprites

frame_width = 48  # Width of each frame in the sprite sheet
frame_height = 73  # Height of each frame in the sprite sheet

# Slicing sprite sheets into frames
throwsprite_images = [sprite_sheet.subsurface(pygame.Rect(i * frame_width, 0, frame_width, frame_height))
                      for i in range(24)]  # 24 frames, assuming all throws are in one row

runsprite_images = [sprite_sheet_run.subsurface(pygame.Rect(i * frame_width, 0, frame_width, frame_height))
                    for i in range(24)]  # 24 frames for running, assuming each direction has 6 frames

idlesprite_images = [sprite_sheet_idle.subsurface(pygame.Rect(i * frame_width, 0, frame_width, frame_height))
                     for i in range(24)]  # 4 idle frames, one for each direction

current_image = throwsprite_images[0]

# Animation frames by direction
direction_frames = {'d': 0, 'w': 6, 'a': 12, 's': 18}


def changeSpriteImage(sprite, frame):
    global current_image
    current_image = sprite[frame]


def throw_loop():
    frame_run = 0
    frame_throw = 0
    frame_idle = 0  # Initialize idle frame count
    direction = 's'
    last_direction = 's'  # Initially set to 's', will update as the player moves
    running = False
    throwing = False
    key_list = []

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_d, pygame.K_w, pygame.K_a, pygame.K_s):
                    if chr(event.key) not in key_list:
                        key_list.append(chr(event.key))
                    direction = key_list[-1]
                    last_direction = direction  # Update last_direction whenever direction changes
                    running = True
                if event.key == pygame.K_SPACE and not throwing:
                    throwing = True
                    frame_throw = 0  # Reset frame for throw animation

            if event.type == pygame.KEYUP:
                if event.key in (pygame.K_d, pygame.K_w, pygame.K_a, pygame.K_s):
                    if chr(event.key) in key_list:
                        key_list.remove(chr(event.key))
                    if key_list:
                        direction = key_list[-1]
                        last_direction = direction  # Update last_direction on key release
                    else:
                        running = False
                        frame_run = 0  # Reset frame when stopping
                        last_direction = direction  # Ensure last_direction holds the stopped direction

        # Determine which animation to play
        if throwing:
            if frame_throw < 6:  # Assuming 6 frames per direction for throwing
                sprite_index = direction_frames[direction] + frame_throw
                if sprite_index < len(throwsprite_images):
                    changeSpriteImage(throwsprite_images, sprite_index)
                frame_throw += 1
            else:
                throwing = False
                frame_throw = 0  # Reset frame count after animation completes

        elif running:
            run_frame_count = 6  # Each direction has 6 frames
            sprite_index = direction_frames[direction] + (frame_run % run_frame_count)
            changeSpriteImage(runsprite_images, sprite_index)
            frame_run += 1

        else:
            # Play idle animation when not running or throwing
            idle_frame_count = 6  # Correct number of frames per direction
            if last_direction in direction_frames:
                base_index = direction_frames[last_direction]  # Base index depending on the direction
                sprite_index = base_index + (frame_idle % idle_frame_count)
            else:
                sprite_index = frame_idle % idle_frame_count  # Fallback to a default if direction is undefined
            changeSpriteImage(idlesprite_images, sprite_index)
            frame_idle += 1

        # Update screen
        SCREEN.fill((0, 0, 0))  # You might still need to clear if there's lots of movement
        rect = SCREEN.blit(current_image, (375, 275))
        pygame.display.update(rect)  # Update only the rectangle area of the sprite
        clock.tick(10)  # Consider increasing frame rate for smoother animation

throw_loop()
