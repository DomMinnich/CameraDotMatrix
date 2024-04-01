# Dominic Minnich | 2024

# Just messing around with the camera an dot matrix displays in python.


# Camera program that uses the webcam to create a retro camera effect.
# The program uses Pygame and OpenCV to capture the webcam feed and render it as a dot matrix display.
# The user can adjust the dot size, spacing, color, frame rate, and visual effect using keyboard controls.
# The program also includes a control panel with instructions and a stats panel to display the current settings.
# The user can take screenshots of the display by pressing the 'S' key.


# Import libraries
# Set variables
# Default settings
# Render visuals
# Functions for adjusting settings
# Handle keyboard events
# Save screenshot
# Render control panel
# Main loop


import os
import cv2
import numpy as np
import pygame
from pygame.locals import *
from datetime import datetime

# Initialize Pygame
pygame.init()

# Set screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Set color
# Greyish white
WHITE = (200, 200, 200)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Set up the display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Dot Matrix Retro Camera")

# Load symbols
symbol_font = pygame.font.SysFont(None, 24)

# Camera setup
camera = cv2.VideoCapture(0)

# Default settings
dot_size = 4
dot_spacing = 5  # Initial dot spacing
show_grid = False
visual_effect = "dots"
dot_color = BLACK
frame_rate = 30
pause_camera = False

# Color cycling variables
color_cycle_speed = 0.1
color_cycle_counter = 0

# Dynamic grid animation variables
grid_animation_counter = 0


def render_visual_effect(frame, dot_size, dot_spacing, show_grid, dot_color):
    global visual_effect
    if visual_effect == "dots":
        render_dots(frame, dot_size, dot_spacing, show_grid, dot_color)
    elif visual_effect == "grid":
        render_grid(frame)


def render_dots(frame, dot_size, dot_spacing, show_grid, dot_color):
    global color_cycle_counter
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    frame_resized = cv2.resize(gray, (SCREEN_WIDTH, SCREEN_HEIGHT))
    _, thresholded = cv2.threshold(frame_resized, 120, 255, cv2.THRESH_BINARY)
    screen.fill(WHITE)

    for y in range(0, SCREEN_HEIGHT, dot_spacing):
        for x in range(0, SCREEN_WIDTH, dot_spacing):
            if thresholded[y, x] == 0:
                color = get_color_with_cycle(dot_color, color_cycle_counter)
                pygame.draw.circle(screen, color, (x, y), dot_size // 2)

    if show_grid:
        draw_grid()


def render_grid(frame):
    global grid_animation_counter
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    frame_resized = cv2.resize(gray, (SCREEN_WIDTH, SCREEN_HEIGHT))
    _, thresholded = cv2.threshold(frame_resized, 120, 255, cv2.THRESH_BINARY)
    screen.fill(WHITE)

    grid_alpha = int(abs(255 * np.sin(grid_animation_counter)))
    grid_color = (0, 0, 0, grid_alpha)

    for y in range(0, SCREEN_HEIGHT, 20):
        pygame.draw.line(screen, grid_color, (0, y), (SCREEN_WIDTH, y))
    for x in range(0, SCREEN_WIDTH, 20):
        pygame.draw.line(screen, grid_color, (x, 0), (x, SCREEN_HEIGHT))


def draw_grid():
    for y in range(0, SCREEN_HEIGHT, dot_spacing):
        pygame.draw.line(screen, BLACK, (0, y), (SCREEN_WIDTH, y))
    for x in range(0, SCREEN_WIDTH, dot_spacing):
        pygame.draw.line(screen, BLACK, (x, 0), (x, SCREEN_HEIGHT))


def get_color_with_cycle(base_color, cycle_counter):
    try:
        base_color = pygame.Color(base_color)
    except ValueError:
        # If base_color is not valid, fallback to default color
        base_color = pygame.Color(0, 0, 0, 0)

    h, s, v, _ = base_color.hsva
    h = (h + cycle_counter) % 360
    rgb_color = pygame.Color(0, 0, 0, 0)
    rgb_color.hsva = (h, s, v, 100)
    return rgb_color


def set_visual_effect(key):
    global visual_effect
    if key == K_1:
        visual_effect = "dots"
    elif key == K_2:
        visual_effect = "grid"


def increase_dot_size():
    global dot_size
    dot_size += 1
    if dot_size > 20:
        dot_size = 20


def decrease_dot_size():
    global dot_size
    dot_size -= 1
    if dot_size < 1:
        dot_size = 1


def change_dot_color(key):
    global dot_color
    if key == K_r:
        dot_color = RED
    elif key == K_g:
        dot_color = GREEN
    elif key == K_b:
        dot_color = BLUE
    elif key == K_k:
        dot_color = BLACK


def increase_frame_rate():
    global frame_rate
    frame_rate += 1
    if frame_rate > 60:
        frame_rate = 60


def decrease_frame_rate():
    global frame_rate
    frame_rate -= 1
    if frame_rate < 1:
        frame_rate = 1


def increase_dot_spacing():
    global dot_spacing
    dot_spacing += 1
    if dot_spacing > 50:
        dot_spacing = 50


def decrease_dot_spacing():
    global dot_spacing
    dot_spacing -= 1
    if dot_spacing < 1:
        dot_spacing = 1


def toggle_pause_camera():
    global pause_camera
    pause_camera = not pause_camera


def auto_adjust():
    global dot_size
    global dot_spacing

    # Capture a frame from the camera
    ret, frame = camera.read()
    if not ret:
        return

    # Convert frame to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Calculate clarity metric using Laplacian operator
    laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()

    # Calculate histogram of oriented gradients (HOG) feature for edge detection
    hog = cv2.HOGDescriptor()
    hog_feature = hog.compute(gray)

    # Determine dot size and spacing based on clarity metric and edge density
    if laplacian_var < 50:
        # Very low clarity: Increase dot size and spacing for better visibility
        dot_size = 7
        dot_spacing = 12
    elif laplacian_var < 150:
        # Low to moderate clarity: Moderate dot size and spacing
        dot_size = 5
        dot_spacing = 10
    elif laplacian_var < 300:
        # Moderate to high clarity: Adjust dot size and spacing based on edge density
        edge_density = np.mean(hog_feature)
        if edge_density < 0.02:
            # Low edge density: Decrease dot size and increase spacing for more detail
            dot_size = 3
            dot_spacing = 15
        elif edge_density < 0.05:
            # Moderate edge density: Moderate dot size and spacing
            dot_size = 2
            dot_spacing = 12
        else:
            # High edge density: Increase dot size and decrease spacing for smoother appearance
            dot_size = 2
            dot_spacing = 8
    else:
        # Very high clarity: Reduce dot size and spacing for more detail
        dot_size = 2
        dot_spacing = 6


def handle_keyboard_events():
    global show_grid
    global dot_size
    global dot_color
    global frame_rate
    global pause_camera
    global dot_spacing

    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            cv2.destroyAllWindows()
            exit()
        elif event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                pygame.quit()
                cv2.destroyAllWindows()
                exit()
            elif event.key == K_SPACE:
                show_grid = not show_grid
            elif event.key == K_1 or event.key == K_2:
                set_visual_effect(event.key)
            elif event.key == K_UP:
                increase_dot_size()
            elif event.key == K_DOWN:
                decrease_dot_size()
            elif event.key in [K_r, K_g, K_b, K_k]:
                change_dot_color(event.key)
            elif event.key == K_f:
                increase_frame_rate()
            elif event.key == K_v:
                decrease_frame_rate()
            elif event.key == K_p:
                toggle_pause_camera()
            elif event.key == K_RIGHT:
                increase_dot_spacing()
            elif event.key == K_LEFT:
                decrease_dot_spacing()
            elif event.key == K_a:
                auto_adjust()
            elif event.key == K_s:
                save_screenshot(screen)


def save_screenshot(screen):
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")  # get current timestamp
    filename = f"screenshot_{timestamp}.png"  # create filename with timestamp

    screenshot = pygame.surfarray.array3d(screen)
    screenshot = cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)  # Convert color format
    screenshot = cv2.transpose(screenshot)  # Transpose the screenshot
    cv2.imwrite(filename, screenshot)
    print(f"Screenshot saved as {filename} at", os.getcwd())


def render_control_panel():
    control_panel_rect = pygame.Rect(10, 10, 300, 300)
    pygame.draw.rect(screen, WHITE, control_panel_rect)

    control_texts = [
        "Controls:",
        "1 - Dots",
        "2 - Grid",
        "UP/DOWN - Adjust Dot Size",
        "R/G/B/K - Change Dot Color",
        "F/V - Adjust Frame Rate",
        "RIGHT/LEFT - Adjust Depth",
        "SPACE - Toggle Grid",
        "P - Pause Camera",
        "ESC - Exit",
        "A - Auto Adjust",
        "S - Save Screenshot",
    ]

    y_offset = 20
    for text in control_texts:
        text_surface = symbol_font.render(text, True, BLACK)
        screen.blit(
            text_surface, (control_panel_rect.x + 10, control_panel_rect.y + y_offset)
        )
        y_offset += 24


def render_stats():
    stats_texts = [
        f"Dot Size: {dot_size}",
        f"Dot Spacing: {dot_spacing}",
        f"Frame Rate: {frame_rate}",
        f"Dot Color: {dot_color}",
        f"Grid: {'ON' if show_grid else 'OFF'}",
    ]
    y_offset = 20
    x_offset = SCREEN_WIDTH - 200  # Adjust x offset
    for text in stats_texts:
        text_surface = symbol_font.render(text, True, BLACK)
        text_rect = text_surface.get_rect()
        text_rect.topleft = (x_offset, y_offset)
        pygame.draw.rect(screen, GREEN, text_rect)  # Draw white rectangle
        screen.blit(text_surface, (x_offset, y_offset))
        y_offset += 24


def main():
    clock = pygame.time.Clock()

    global color_cycle_counter
    global grid_animation_counter

    while True:
        if not pause_camera:
            ret, frame = camera.read()
            if not ret:
                continue

        render_visual_effect(frame, dot_size, dot_spacing, show_grid, dot_color)
        render_control_panel()
        render_stats()

        handle_keyboard_events()

        color_cycle_counter += color_cycle_speed
        grid_animation_counter += 0.1

        pygame.display.flip()

        clock.tick(frame_rate)


# Start the main loop
if __name__ == "__main__":
    try:
        main()
    finally:
        # Release the camera
        camera.release()
