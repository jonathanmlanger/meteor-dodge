# Meteor Dodge

![tests](https://github.com/jonathanmlanger/meteor-dodge/actions/workflows/tests.yml/badge.svg)
![Python](https://img.shields.io/badge/MicroPython-Firia%20Labs%20CodeX-blue)
![License: MIT](https://img.shields.io/badge/license-MIT-green)

A tilt-controlled survival game for the [Firia Labs CodeX](https://firialabs.com) handheld, written in Python for my 8th grade computer science class. You steer a ship by tilting the device and dodge meteors falling from the top of the screen. Your score is how many seconds you survive, and every 10 seconds the meteors speed up.

<!-- Add a photo or short GIF of the game running on a CodeX here:
![Meteor Dodge on a CodeX](docs/meteor-dodge.gif) -->

## How to play

| Control | Action |
|---|---|
| **A** | Start / play again |
| **Tilt left / right** | Steer the ship |

You get 3 lives, shown on the four LEDs above the screen. When a meteor hits you, the LEDs flash red and the ship turns red for a moment. The current level is shown in the top right, and your best time is on the title screen.

## Run it on a CodeX

1. Open Firia Labs **CodeSpace** and connect your CodeX by USB.
2. Create a new file and paste in the contents of [`meteor_dodge.py`](meteor_dodge.py).
3. Click **Run**. If the ship moves the wrong way when you tilt, set `FLIP_TILT = True`.

## Settings

The settings block at the top of the file is built for experimenting: change one number, click Run, and explain what changed.

| Setting | Default | What it does |
|---|---|---|
| `START_SPEED` | `3` | Pixels a meteor falls per frame at the start |
| `SPEED_UP` | `1` | Extra speed added each level |
| `LEVEL_TIME` | `10` | Seconds per level |
| `METEOR_COUNT` | `4` | Meteors falling at once |
| `METEOR_SIZE` | `16` | Meteor size in pixels |
| `SHIP_SIZE` | `24` | Ship width in pixels |
| `TILT_POWER` | `10` | How fast the ship moves at full tilt |
| `LIVES` | `3` | Hits before game over (1 to 4) |
| `SHIP_COLOR`, `METEOR_COLOR` | `CYAN`, `ORANGE` | Colors |
| `FLIP_TILT` | `False` | Reverses steering |

## What students learn from it

This is a complete real-time **game loop**: read input, move everything, check for collisions, update the score, repeat. It reads the **accelerometer** for analog input, tracks meteors with **parallel lists** of x and y positions, uses **rectangle overlap** to detect collisions, and redraws only what moved (erasing each object's old position) so the game stays smooth on a small device.

## Testing

The `codex` library only exists on the device, so the tests swap in fake hardware ([`tests/fake_codex.py`](tests/fake_codex.py)): a display that records every draw call, a fake accelerometer a test can tilt, and a clock that jumps forward instantly so a whole game runs in under a second. The endless main loop is skipped, and the game functions are called directly.

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
pytest
```

The 19 tests check the edges of the play area, that new meteors always start above the screen, that full tilt stops the ship at the wall instead of letting it leave the screen, that a meteor lined up with the ship costs exactly one life per hit while one that misses never does, that the score equals seconds survived, and that the level goes up on schedule.

To check that the tests actually catch mistakes, I broke the game on purpose three ways (let the ship drive off the screen, broke the collision math, and reversed the tilt setting). Each change made at least one test fail. GitHub Actions runs the suite on every push.

## Ideas for a next version

The collision check currently lives inside the main `play()` loop. Pulling it out into its own `collides(meteor_x, meteor_y, ship_x)` function would make it easier for students to read and let the tests check it directly.

## How this was built

I designed this game with an AI assistant (Claude) as a pair programmer. I set the requirements (classroom-friendly code, a settings block for experiments, concepts matching the CodeX curriculum), reviewed and tested every version on real devices, and caught a hardware issue along the way: an earlier version used `time.monotonic()`, which I replaced with `time.time()` for the CodeX. The test suite and fake hardware layer were also written with AI help, then checked by deliberately breaking the game to confirm the tests fail when they should.

## License

[MIT](LICENSE) © 2026 Jonathan Langer
