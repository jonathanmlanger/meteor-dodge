"""Tests for Meteor Dodge. Run with: pytest -v"""
import pytest

from fake_codex import FakeClock


def record_ship(ns):
    """Wrap draw_ship so a test can see every place the ship was drawn."""
    original = ns["draw_ship"]
    drawn = []

    def spy(x, color):
        drawn.append((x, color))
        original(x, color)

    ns["draw_ship"] = spy
    return drawn


# ---------- helpers ----------

def test_center_text_centers_the_word(game):
    ns, _ = game
    ns["center_text"]("DODGE", 80, ns["ORANGE"], 4)
    # 5 letters x 8 px x scale 4 = 160 px wide, so it starts at (240 - 160) / 2
    assert ns["display"].last_text()[2] == 40


@pytest.mark.parametrize("y, expected", [
    (23, False),    # tucked under the score bar
    (24, True),     # first row below the score bar
    (224, True),    # bottom edge exactly on the last row
    (225, False),   # hanging off the bottom
    (-50, False),   # still above the screen
])
def test_on_screen(game, y, expected):
    ns, _ = game
    assert ns["on_screen"](y) is expected


def test_new_meteors_always_start_above_the_screen(game):
    ns, _ = game
    size = ns["METEOR_SIZE"]
    for _ in range(500):
        y = ns["new_meteor_y"]()
        assert -size - 150 <= y <= -size


@pytest.mark.parametrize("lives", [0, 1, 2, 3, 4])
def test_show_lives_lights_one_green_led_per_life(game, lives):
    ns, _ = game
    ns["show_lives"](lives)
    assert ns["pixels"].leds.count((0, 255, 0)) == lives


def test_ship_is_drawn_inside_its_own_width(game):
    ns, _ = game
    ns["draw_ship"](100, ns["CYAN"])
    for _, x, y, w, h, _ in ns["display"].calls:
        assert 100 <= x and x + w <= 100 + ns["SHIP_SIZE"]


# ---------- steering ----------

def test_full_tilt_right_stops_at_the_right_wall(game):
    ns, _ = game
    ns["accel"].x = ns["TILT_MAX"]
    drawn = record_ship(ns)
    ns["play"]()
    xs = [x for x, _ in drawn]
    assert max(xs) == ns["SCREEN"] - ns["SHIP_SIZE"]
    assert min(xs) >= 0


def test_flip_tilt_reverses_steering(game):
    ns, _ = game
    ns["FLIP_TILT"] = True
    ns["accel"].x = ns["TILT_MAX"]
    drawn = record_ship(ns)
    ns["play"]()
    assert min(x for x, _ in drawn) == 0


# ---------- collisions, lives, scoring ----------

def test_meteor_straight_above_the_ship_costs_a_life_each_time(game):
    ns, _ = game
    ns["METEOR_COUNT"] = 1
    center = (ns["SCREEN"] - ns["SHIP_SIZE"]) // 2
    ns["random"].randint = lambda a, b: center       # meteor lines up with the ship
    ns["new_meteor_y"] = lambda: ns["TOP"]           # and starts at the top
    drawn = record_ship(ns)
    ns["play"]()
    red_flashes = [x for x, color in drawn if color == ns["RED"]]
    assert len(red_flashes) == ns["LIVES"]
    assert ns["pixels"].leds.count((0, 255, 0)) == 0


def test_meteor_that_misses_does_not_end_the_game():
    from conftest import GAME_FILE
    from fake_codex import load_game

    ns, _ = load_game(GAME_FILE, clock=FakeClock(limit_s=30))
    ns["METEOR_COUNT"] = 1
    ns["random"].randint = lambda a, b: 0            # meteor always falls on the far left
    ns["new_meteor_y"] = lambda: ns["TOP"]
    with pytest.raises(TimeoutError):                # still alive after 30 seconds
        ns["play"]()


def test_score_is_seconds_survived(game):
    ns, clock = game
    score = ns["play"]()
    assert int(clock.now) - 1 <= score <= int(clock.now)


def test_level_goes_up_every_level_time(game):
    ns, clock = game
    ns["LIVES"] = 40                                 # survive long enough to level up
    ns["play"]()
    levels = [t for t in ns["display"].texts() if t.startswith("Lv")]
    expected_top_level = 1 + int(clock.now // ns["LEVEL_TIME"])
    assert "Lv2" in levels
    assert levels[-1] in ("Lv" + str(expected_top_level), "Lv" + str(expected_top_level - 1))
