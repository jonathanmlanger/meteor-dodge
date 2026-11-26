from pathlib import Path

import pytest

from fake_codex import load_game

GAME_FILE = Path(__file__).resolve().parent.parent / "meteor_dodge.py"


@pytest.fixture
def game():
    """A fresh copy of the game with fake hardware and a fresh clock."""
    return load_game(GAME_FILE)
