"""
Test stand-ins for the Firia Labs CodeX hardware.

The real `codex` module only exists on the device. These fakes let the game
code run on a regular computer so pytest can check the logic:

* FakeClock    - replaces sleep/time/ticks_ms so tests run instantly
* FakeDisplay  - records everything the game draws
* FakePixels   - the four LEDs (used to show lives)
* FakeButtons  - lets a test "press" a button at a chosen moment
* FakeAccel    - lets a test tilt the device
"""
import ast
import random
from pathlib import Path

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)
CYAN = (0, 255, 255)


class FakeClock:
    def __init__(self, limit_s=3600):
        self.now = 0.0
        self.limit_s = limit_s  # stops a runaway game from hanging the test run

    def sleep(self, seconds):
        self.now += seconds
        if self.now > self.limit_s:
            raise TimeoutError("game ran longer than the test allows")

    def time(self):
        return self.now

    def ticks_ms(self):
        return int(self.now * 1000)

    @staticmethod
    def ticks_diff(new, old):
        return new - old


class FakeDisplay:
    def __init__(self):
        self.calls = []

    def fill(self, color):
        self.calls.append(("fill", color))

    def fill_rect(self, x, y, w, h, color):
        self.calls.append(("fill_rect", x, y, w, h, color))

    def draw_text(self, text, x=0, y=0, color=None, scale=1, background=None):
        self.calls.append(("text", text, x, y, color, scale))

    def texts(self):
        return [c[1] for c in self.calls if c[0] == "text"]

    def last_text(self):
        return [c for c in self.calls if c[0] == "text"][-1]


class FakePixels:
    def __init__(self):
        self.leds = [BLACK] * 4

    def set(self, i, color):
        self.leds[i] = tuple(color)

    def fill(self, color):
        self.leds = [tuple(color)] * 4

    def off(self):
        self.leds = [BLACK] * 4


class FakeButtons:
    def __init__(self, clock):
        self.clock = clock
        self.scheduled = []  # [time_in_seconds, button]

    def press(self, button, at):
        """Schedule a press. It counts once the clock reaches `at` seconds."""
        self.scheduled.append([at, button])

    def was_pressed(self, button):
        for item in self.scheduled:
            if item[1] == button and item[0] <= self.clock.now:
                self.scheduled.remove(item)
                return True
        return False


class FakeAccel:
    def __init__(self):
        self.x = 0

    def read(self):
        return (self.x, 0, 0)


def load_game(path, clock=None, seed=0):
    """
    Load a game file with fake hardware plugged in.

    The endless `while True` main loop at the bottom of each game is skipped,
    along with the device-only imports, so every function can be called
    directly from a test.
    """
    clock = clock or FakeClock()
    tree = ast.parse(Path(path).read_text())
    tree.body = [
        node for node in tree.body
        if not (isinstance(node, ast.ImportFrom) and node.module in ("codex", "time"))
        and not isinstance(node, ast.While)
    ]
    ns = {
        "display": FakeDisplay(),
        "pixels": FakePixels(),
        "buttons": FakeButtons(clock),
        "accel": FakeAccel(),
        "BTN_U": "U", "BTN_D": "D", "BTN_L": "L", "BTN_R": "R",
        "BTN_A": "A", "BTN_B": "B",
        "BLACK": BLACK, "WHITE": WHITE, "RED": RED, "GREEN": GREEN,
        "BLUE": BLUE, "YELLOW": YELLOW, "ORANGE": ORANGE,
        "PURPLE": PURPLE, "CYAN": CYAN,
        "sleep": clock.sleep, "time": clock.time,
        "ticks_ms": clock.ticks_ms, "ticks_diff": clock.ticks_diff,
        "__name__": "game_under_test",
    }
    exec(compile(tree, str(path), "exec"), ns)
    ns["random"] = random.Random(seed)  # repeatable "random" numbers
    return ns, clock
