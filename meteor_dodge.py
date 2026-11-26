# ============================================
#               METEOR DODGE
# Tilt your CodeX left and right to steer.
# Dodge the falling meteors. Survive as long as you can!
# Your score = seconds alive. Beat your best!
# ============================================

from codex import *
from time import sleep, time
import random

# ==================== SETTINGS ====================
# Change ONE number. Click Run. What changed?
START_SPEED = 3      # how fast meteors fall at the start
SPEED_UP = 1         # how much faster they get each level
LEVEL_TIME = 10      # seconds until the next level
METEOR_COUNT = 4     # how many meteors fall at once
METEOR_SIZE = 16     # size of each meteor (pixels)
SHIP_SIZE = 24       # width of your ship (pixels)
TILT_POWER = 10      # how fast your ship moves when you tilt
LIVES = 3            # hits before GAME OVER (1 to 4)
SHIP_COLOR = CYAN
METEOR_COLOR = ORANGE
FLIP_TILT = False    # ship goes the wrong way? Change to True
# ==================================================

# Game numbers (no need to change these)
SCREEN = 240         # the screen is 240 x 240 pixels
TOP = 24             # space at the top for score and lives
SHIP_Y = 208         # how far down the ship sits
SHIP_H = 16          # ship height
TILT_MAX = 16384     # accelerometer reading for a big tilt


def center_text(text, y, color, scale):
    # Draw text in the middle of the screen
    x = (SCREEN - len(text) * 8 * scale) // 2
    display.draw_text(text, x, y, color, scale)


def wait_for_a():
    buttons.was_pressed(BTN_A)          # forget old presses
    while not buttons.was_pressed(BTN_A):
        sleep(0.05)


def show_lives(lives):
    # The 4 lights on top show your lives
    for i in range(4):
        if i < lives:
            pixels.set(i, (0, 255, 0))
        else:
            pixels.set(i, (0, 0, 0))


def draw_top_bar(score, level):
    display.draw_text("Score " + str(score), 4, 4, WHITE, 2, BLACK)
    display.draw_text("Lv" + str(level), 160, 4, YELLOW, 2, BLACK)


def draw_ship(x, color):
    nose = SHIP_SIZE // 3
    display.fill_rect(x + nose, SHIP_Y, nose, 6, color)          # nose
    display.fill_rect(x, SHIP_Y + 6, SHIP_SIZE, SHIP_H - 6, color)  # body


def on_screen(y):
    # Only draw meteors that are fully on the screen
    return y >= TOP and y + METEOR_SIZE <= SCREEN


def new_meteor_y():
    # Start above the screen at a random height
    return -METEOR_SIZE - random.randint(0, 150)


def play():
    display.fill(BLACK)
    ship_x = (SCREEN - SHIP_SIZE) // 2
    lives = LIVES
    speed = START_SPEED
    level = 1

    # Two lists: one for each meteor's x, one for each meteor's y
    meteor_x = []
    meteor_y = []
    for i in range(METEOR_COUNT):
        meteor_x.append(random.randint(0, SCREEN - METEOR_SIZE))
        meteor_y.append(new_meteor_y())

    start = time()
    next_level = start + LEVEL_TIME
    score = 0
    show_lives(lives)
    draw_top_bar(score, level)
    draw_ship(ship_x, SHIP_COLOR)

    while lives > 0:
        # 1. Tilt to move the ship
        x, y, z = accel.read()
        move = int(TILT_POWER * x / TILT_MAX)
        if FLIP_TILT:
            move = -move
        old_x = ship_x
        ship_x = ship_x + move
        if ship_x < 0:
            ship_x = 0
        if ship_x > SCREEN - SHIP_SIZE:
            ship_x = SCREEN - SHIP_SIZE
        if ship_x != old_x:
            display.fill_rect(old_x, SHIP_Y, SHIP_SIZE, SHIP_H, BLACK)
            draw_ship(ship_x, SHIP_COLOR)

        # 2. Move every meteor down
        for i in range(len(meteor_x)):
            if on_screen(meteor_y[i]):
                display.fill_rect(meteor_x[i], meteor_y[i], METEOR_SIZE, METEOR_SIZE, BLACK)
            meteor_y[i] = meteor_y[i] + speed

            # Fell off the bottom? Send it back to the top
            if meteor_y[i] > SCREEN:
                meteor_x[i] = random.randint(0, SCREEN - METEOR_SIZE)
                meteor_y[i] = new_meteor_y()

            # 3. Did it hit the ship?
            hit = (meteor_x[i] < ship_x + SHIP_SIZE and
                   meteor_x[i] + METEOR_SIZE > ship_x and
                   meteor_y[i] < SHIP_Y + SHIP_H and
                   meteor_y[i] + METEOR_SIZE > SHIP_Y)
            if hit:
                lives = lives - 1
                show_lives(lives)
                pixels.fill((255, 0, 0))
                draw_ship(ship_x, RED)
                sleep(0.3)
                show_lives(lives)
                draw_ship(ship_x, SHIP_COLOR)
                meteor_x[i] = random.randint(0, SCREEN - METEOR_SIZE)
                meteor_y[i] = new_meteor_y()
            elif on_screen(meteor_y[i]):
                display.fill_rect(meteor_x[i], meteor_y[i], METEOR_SIZE, METEOR_SIZE, METEOR_COLOR)

        # 4. Score and level
        new_score = int(time() - start)
        level_up = time() >= next_level
        if level_up:
            speed = speed + SPEED_UP
            level = level + 1
            next_level = next_level + LEVEL_TIME
        if new_score != score or level_up:
            score = new_score
            draw_top_bar(score, level)

        sleep(0.02)

    return score


def game_over(score, best, new_best):
    pixels.off()
    display.fill(BLACK)
    center_text("GAME OVER", 30, RED, 3)
    center_text("Score: " + str(score), 85, WHITE, 2)
    center_text("Best: " + str(best), 115, CYAN, 2)
    if new_best:
        center_text("NEW BEST!", 145, YELLOW, 2)
    center_text("A = Play again", 200, WHITE, 2)


# ============ MAIN PROGRAM ============
best = 0
while True:
    display.fill(BLACK)
    center_text("METEOR", 40, ORANGE, 4)
    center_text("DODGE", 80, ORANGE, 4)
    center_text("Tilt to steer", 140, WHITE, 2)
    center_text("A = Start", 170, YELLOW, 2)
    center_text("Best: " + str(best), 205, CYAN, 2)
    wait_for_a()

    score = play()
    new_best = score > best
    if new_best:
        best = score
    game_over(score, best, new_best)
    sleep(1)
    wait_for_a()
