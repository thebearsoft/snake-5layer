"""
Snake game test suite.
Tests AC-01 through AC-09 from .kiro/specs/snake.md.
All tests mock curses — no terminal required.
Run with: pytest tests/ -v
"""
import sys
import types
import unittest.mock as mock
from unittest.mock import MagicMock, patch

# ---------------------------------------------------------------------------
# Stub the curses module before importing src.snake so the module-level
# import of curses does not require a real terminal.
# ---------------------------------------------------------------------------
curses_stub = types.ModuleType("curses")
curses_stub.KEY_UP = 259
curses_stub.KEY_DOWN = 258
curses_stub.KEY_LEFT = 260
curses_stub.KEY_RIGHT = 261
curses_stub.color_pair = lambda n: n
curses_stub.init_pair = lambda *a: None
curses_stub.start_color = lambda: None
curses_stub.curs_set = lambda n: None
curses_stub.wrapper = lambda fn: fn(MagicMock())
curses_stub.error = Exception
sys.modules.setdefault("curses", curses_stub)

from src.snake import Direction, GameState, Snake, Board, Game  # noqa: E402


# ---------------------------------------------------------------------------
# AC-01
# ---------------------------------------------------------------------------

def test_ac_01():
    """AC-01: Snake initializes at center with length 1, direction RIGHT."""
    game = Game(rows=20, cols=40)
    snake = game.snake

    expected_head = (20 // 2, 40 // 2)  # (10, 20)
    assert len(snake.body) == 1, "Snake must start with length 1"
    assert snake.body[0] == expected_head, (
        f"Head must be at board center {expected_head}, got {snake.body[0]}"
    )
    assert snake.direction == Direction.RIGHT, (
        f"Initial direction must be RIGHT, got {snake.direction}"
    )


# ---------------------------------------------------------------------------
# AC-02
# ---------------------------------------------------------------------------

def test_ac_02():
    """AC-02: Snake moves one cell per tick in current direction."""
    game = Game(rows=20, cols=40)
    head_before = game.snake.body[0]

    # Default direction is RIGHT → col should increase by 1
    game.tick(None)

    head_after = game.snake.body[0]
    dr, dc = Direction.RIGHT.value
    expected = (head_before[0] + dr, head_before[1] + dc)
    assert head_after == expected, (
        f"After one tick moving RIGHT, head should be at {expected}, got {head_after}"
    )


# ---------------------------------------------------------------------------
# AC-03
# ---------------------------------------------------------------------------

def test_ac_03():
    """AC-03: Opposite direction input is ignored."""
    game = Game(rows=20, cols=40)
    # Snake starts moving RIGHT — LEFT is the opposite and must be ignored
    head_before = game.snake.body[0]

    game.tick(Direction.LEFT)

    head_after = game.snake.body[0]
    dr, dc = Direction.RIGHT.value
    expected = (head_before[0] + dr, head_before[1] + dc)
    assert head_after == expected, (
        "Opposite direction (LEFT while moving RIGHT) must be ignored; "
        f"expected head at {expected}, got {head_after}"
    )


# ---------------------------------------------------------------------------
# AC-04
# ---------------------------------------------------------------------------

def test_ac_04():
    """AC-04: Food consumption increases length by 1 and score by 10."""
    game = Game(rows=20, cols=40)
    head = game.snake.body[0]
    dr, dc = game.snake.direction.value
    # Place food one step ahead of the snake head
    game.food = (head[0] + dr, head[1] + dc)

    length_before = len(game.snake.body)
    score_before = game.score

    game.tick(None)

    assert len(game.snake.body) == length_before + 1, (
        "Snake length must increase by 1 after eating food"
    )
    assert game.score == score_before + 10, (
        f"Score must increase by 10 after eating food; "
        f"expected {score_before + 10}, got {game.score}"
    )


# ---------------------------------------------------------------------------
# AC-05
# ---------------------------------------------------------------------------

def test_ac_05():
    """AC-05: New food never spawns on snake body."""
    game = Game(rows=20, cols=40)

    for _ in range(50):
        new_food = game._spawn_food()
        assert new_food not in game.snake.body, (
            f"Food spawned at {new_food} which overlaps snake body {game.snake.body}"
        )


# ---------------------------------------------------------------------------
# AC-06
# ---------------------------------------------------------------------------

def test_ac_06():
    """AC-06: Self-collision triggers GAME_OVER."""
    game = Game(rows=20, cols=40)
    # Build a snake body that wraps so the next step hits itself.
    # Shape (moving RIGHT, head at col 5):
    #   head→(5,5) body: (5,4),(5,3),(5,2),(4,2),(4,3),(4,4),(4,5),(4,6),(5,6)
    # After one RIGHT tick head would be at (5,6) which is already in the body.
    # Simpler: manually craft a collision scenario.
    game.snake.body = [
        (10, 20),  # head
        (10, 21),  # body — one step to the right
        (11, 21),
        (11, 20),
        (11, 19),
        (10, 19),
        (9, 19),
        (9, 20),
        (9, 21),
        (9, 22),
        (10, 22),
        (11, 22),
        (12, 22),
        (12, 21),
        (12, 20),
        (12, 19),
        (12, 18),
        (11, 18),
        (10, 18),
        (10, 19),  # not in body[1:] yet after prepend? let's use a direct approach
    ]
    # Simplest direct approach: set head one step away from a body cell,
    # ensuring next tick head == a body segment.
    game.snake.body = [(10, 20), (10, 19), (10, 18)]
    game.snake.direction = Direction.DOWN
    # Place a body segment at (11, 20) — where head will land
    game.snake.body = [(10, 20), (11, 20), (12, 20), (12, 19), (11, 19), (10, 19)]
    game.snake.direction = Direction.DOWN
    # After tick DOWN head would be at (11, 20) which is body[1] → self-collision
    # Move food away so eating doesn't interfere
    game.food = (0, 0)

    game.tick(None)

    assert game.state == GameState.GAME_OVER, (
        f"Self-collision must trigger GAME_OVER, got state={game.state}"
    )


# ---------------------------------------------------------------------------
# AC-07
# ---------------------------------------------------------------------------

def test_ac_07():
    """AC-07: Boundary collision triggers GAME_OVER."""
    game = Game(rows=20, cols=40)
    # Place snake head at the right boundary, moving RIGHT
    game.snake.body = [(10, 39)]
    game.snake.direction = Direction.RIGHT
    game.food = (0, 0)

    game.tick(None)

    assert game.state == GameState.GAME_OVER, (
        f"Moving outside board boundary must trigger GAME_OVER, got state={game.state}"
    )


# ---------------------------------------------------------------------------
# AC-08
# ---------------------------------------------------------------------------

def test_ac_08():
    """AC-08: Score starts at 0 and increments correctly."""
    game = Game(rows=20, cols=40)
    assert game.score == 0, f"Initial score must be 0, got {game.score}"

    # Eat three pieces of food
    for expected_score in (10, 20, 30):
        head = game.snake.body[0]
        dr, dc = game.snake.direction.value
        game.food = (head[0] + dr, head[1] + dc)
        game.tick(None)
        assert game.score == expected_score, (
            f"Score after eating food should be {expected_score}, got {game.score}"
        )


# ---------------------------------------------------------------------------
# AC-09
# ---------------------------------------------------------------------------

def test_ac_09():
    """AC-09: Tick interval starts at 150ms and decreases incrementally with score."""
    game = Game(rows=20, cols=40)

    assert game.tick_interval_ms == 150, (
        f"Initial tick interval must be 150ms, got {game.tick_interval_ms}"
    )

    # Speed schedule from DESIGN.md §3 (thresholds are post-eat scores):
    # score ≥ 50  → 130ms  (pre-eat score must be ≥ 40 so post-eat ≥ 50)
    # score ≥ 100 → 110ms
    # score ≥ 150 → 90ms
    # score ≥ 200 → 70ms
    # score ≥ 250 → 50ms (floor)
    #
    # Each row: (pre_eat_score, expected_interval_after_eating)
    # Post-eat score = pre_eat_score + 10
    schedule = [
        (0,   150),  # post-eat  10 < 50  → 150ms
        (30,  150),  # post-eat  40 < 50  → 150ms
        (39,  150),  # post-eat  49 < 50  → 150ms
        (40,  130),  # post-eat  50 ≥ 50  → 130ms
        (89,  130),  # post-eat  99 < 100 → 130ms
        (90,  110),  # post-eat 100 ≥ 100 → 110ms
        (139, 110),  # post-eat 149 < 150 → 110ms
        (140,  90),  # post-eat 150 ≥ 150 → 90ms
        (189,  90),  # post-eat 199 < 200 → 90ms
        (190,  70),  # post-eat 200 ≥ 200 → 70ms
        (239,  70),  # post-eat 249 < 250 → 70ms
        (240,  50),  # post-eat 250 ≥ 250 → 50ms (floor)
        (990,  50),  # post-eat 1000       → 50ms (floor never exceeded)
    ]

    for score_val, expected_interval in schedule:
        g = Game(rows=20, cols=40)
        g.score = score_val
        # Eat food to trigger interval recomputation inside tick()
        head = g.snake.body[0]
        dr, dc = g.snake.direction.value
        g.food = (head[0] + dr, head[1] + dc)
        g.tick(None)
        assert g.tick_interval_ms == expected_interval, (
            f"Pre-eat score={score_val}, post-eat score={g.score}: "
            f"tick_interval_ms should be {expected_interval}ms, got {g.tick_interval_ms}ms"
        )
