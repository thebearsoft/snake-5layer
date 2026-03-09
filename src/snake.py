"""Snake game — single-file implementation.

Spec:   .kiro/specs/snake.md v1.0.0
Design: agents/architect/output/DESIGN.md v1.0.0

Note on config: DESIGN.md calls for a config.yaml file, but Python's stdlib
has no YAML parser (PyYAML is external). All configuration lives in CONFIG
below — the spirit (no magic numbers) is preserved, stdlib-only constraint met.
"""
from __future__ import annotations

import curses
import random
from dataclasses import dataclass
from enum import Enum

# ---------------------------------------------------------------------------
# Configuration — every tunable value lives here; no magic numbers elsewhere
# ---------------------------------------------------------------------------
CONFIG: dict = {
    "board_rows": 20,
    "board_cols": 40,
    "tick_interval_ms": 150,
    "score_per_food": 10,
    # (score_threshold, interval_ms) — evaluated in order; last match wins
    "speed_schedule": [
        (0,   150),
        (50,  130),
        (100, 110),
        (150,  90),
        (200,  70),
        (250,  50),
    ],
    "min_tick_interval_ms": 50,
    "char_border": "#",
    "char_food":   "*",
    "char_head":   "@",
    "char_body":   "o",
    "game_over_msg":  "GAME OVER — press q to quit",
    "score_label":    "Score: ",
}


# ---------------------------------------------------------------------------
# Direction
# ---------------------------------------------------------------------------
class Direction(Enum):
    UP    = (-1,  0)
    DOWN  = ( 1,  0)
    LEFT  = ( 0, -1)
    RIGHT = ( 0,  1)

    @property
    def opposite(self) -> "Direction":
        r, c = self.value
        return Direction((-r, -c))


# ---------------------------------------------------------------------------
# GameState
# ---------------------------------------------------------------------------
class GameState(Enum):
    RUNNING   = "RUNNING"
    GAME_OVER = "GAME_OVER"
    QUIT      = "QUIT"


# ---------------------------------------------------------------------------
# Snake
# ---------------------------------------------------------------------------
@dataclass
class Snake:
    body: list[tuple[int, int]]   # body[0] = head, body[-1] = tail
    direction: Direction

    def move(self, new_direction: Direction | None) -> tuple[int, int]:
        """Return new head position without mutating body.

        Ignores new_direction if it equals the opposite of the current
        direction (AC-03).
        """
        if new_direction is not None and new_direction != self.direction.opposite:
            self.direction = new_direction
        dr, dc = self.direction.value
        head_r, head_c = self.body[0]
        return (head_r + dr, head_c + dc)

    def grow(self, new_head: tuple[int, int]) -> None:
        """Prepend new_head; keep tail — snake grows by 1 (AC-04)."""
        self.body.insert(0, new_head)

    def step(self, new_head: tuple[int, int]) -> None:
        """Prepend new_head; remove tail — snake moves without growing."""
        self.body.insert(0, new_head)
        self.body.pop()


# ---------------------------------------------------------------------------
# Board
# ---------------------------------------------------------------------------
@dataclass
class Board:
    rows: int
    cols: int

    def in_bounds(self, pos: tuple[int, int]) -> bool:
        r, c = pos
        return 0 <= r < self.rows and 0 <= c < self.cols


# ---------------------------------------------------------------------------
# Game
# ---------------------------------------------------------------------------
class Game:
    def __init__(
        self,
        rows: int = CONFIG["board_rows"],
        cols: int = CONFIG["board_cols"],
    ) -> None:
        self.board = Board(rows=rows, cols=cols)
        start = (rows // 2, cols // 2)
        self.snake = Snake(body=[start], direction=Direction.RIGHT)  # AC-01
        self.score: int = 0                                          # AC-08
        self.state: GameState = GameState.RUNNING
        self.tick_interval_ms: int = CONFIG["tick_interval_ms"]
        self.food: tuple[int, int] = self._spawn_food()             # AC-05

    def _spawn_food(self) -> tuple[int, int]:
        """Return a random cell not occupied by the snake (AC-05)."""
        all_cells = {
            (r, c)
            for r in range(self.board.rows)
            for c in range(self.board.cols)
        }
        available = list(all_cells - set(self.snake.body))
        if not available:
            raise RuntimeError(
                "No available cells to spawn food — board is completely full"
            )
        return random.choice(available)

    def _update_tick_interval(self) -> None:
        """Recompute tick interval from score using the speed schedule (AC-09)."""
        interval = CONFIG["tick_interval_ms"]
        for threshold, ms in CONFIG["speed_schedule"]:
            if self.score >= threshold:
                interval = ms
        self.tick_interval_ms = max(CONFIG["min_tick_interval_ms"], interval)

    def tick(self, input_direction: Direction | None) -> GameState:
        """Advance one game step; return the new state (AC-02)."""
        if self.state != GameState.RUNNING:
            return self.state

        new_head = self.snake.move(input_direction)

        # Boundary collision — checked first (AC-07)
        if not self.board.in_bounds(new_head):
            self.state = GameState.GAME_OVER
            return self.state

        # Self-collision (AC-06)
        if new_head in self.snake.body[1:]:
            self.state = GameState.GAME_OVER
            return self.state

        # Food consumption (AC-04)
        if new_head == self.food:
            self.snake.grow(new_head)
            self.score += CONFIG["score_per_food"]
            self.food = self._spawn_food()
            self._update_tick_interval()
        else:
            self.snake.step(new_head)

        return self.state

    def handle_input(self, key: int) -> Direction | None | str:
        """Map a curses key code to Direction, 'QUIT', or None (no-op)."""
        if key == ord("q"):
            return "QUIT"
        mapping: dict[int, Direction] = {
            curses.KEY_UP:    Direction.UP,
            ord("w"):         Direction.UP,
            curses.KEY_DOWN:  Direction.DOWN,
            ord("s"):         Direction.DOWN,
            curses.KEY_LEFT:  Direction.LEFT,
            ord("a"):         Direction.LEFT,
            curses.KEY_RIGHT: Direction.RIGHT,
            ord("d"):         Direction.RIGHT,
        }
        return mapping.get(key)

    def run(self, stdscr: "curses.window") -> None:
        """Main curses game loop."""
        # Screen layout (all rows are 0-indexed):
        #   row 0          : score line
        #   row 1          : top border
        #   rows 2..rows+1 : play area  (game coord r → screen row r+2)
        #   row rows+2     : bottom border
        # Minimum terminal: rows+3 tall, cols+2 wide
        min_rows = self.board.rows + 3
        min_cols = self.board.cols + 2
        actual_rows, actual_cols = stdscr.getmaxyx()
        if actual_rows < min_rows or actual_cols < min_cols:
            raise RuntimeError(
                f"Terminal too small: need at least {min_rows} rows × {min_cols} cols, "
                f"got {actual_rows} × {actual_cols}"
            )

        curses.curs_set(0)
        stdscr.timeout(self.tick_interval_ms)

        while self.state != GameState.QUIT:
            key = stdscr.getch()
            direction = self.handle_input(key)

            if direction == "QUIT":
                self.state = GameState.QUIT
                break

            if self.state == GameState.RUNNING:
                self.tick(direction)  # type: ignore[arg-type]
                stdscr.timeout(self.tick_interval_ms)

            render(stdscr, self)

            if self.state == GameState.GAME_OVER:
                # Block until player presses q
                stdscr.timeout(-1)
                while True:
                    k = stdscr.getch()
                    if k == ord("q"):
                        self.state = GameState.QUIT
                        break


# ---------------------------------------------------------------------------
# Renderer
# ---------------------------------------------------------------------------
def _safe_addch(stdscr: "curses.window", row: int, col: int, ch: str) -> None:
    """addch wrapper that tolerates the curses bottom-right-corner scroll quirk.

    curses raises curses.error when writing to the absolute last cell of the
    terminal because it would trigger an unwanted scroll. This is a known
    curses limitation, not an application error; we skip that one cell.
    """
    try:
        stdscr.addch(row, col, ch)
    except curses.error:
        pass  # bottom-right terminal cell only — not an application error


def render(stdscr: "curses.window", game: Game) -> None:
    """Draw score, board border, food, snake, and optional game-over overlay."""
    stdscr.erase()

    rows = game.board.rows
    cols = game.board.cols
    border = CONFIG["char_border"]

    # Score line (row 0)
    score_str = f"{CONFIG['score_label']}{game.score}"
    stdscr.addstr(0, 0, score_str)

    # Top border (row 1)
    for c in range(cols + 2):
        _safe_addch(stdscr, 1, c, border)

    # Bottom border (row rows+2)
    for c in range(cols + 2):
        _safe_addch(stdscr, rows + 2, c, border)

    # Side borders (rows 2..rows+1)
    for r in range(2, rows + 2):
        _safe_addch(stdscr, r, 0, border)
        _safe_addch(stdscr, r, cols + 1, border)

    # Food — game coord (fr, fc) → screen (fr+2, fc+1)
    fr, fc = game.food
    _safe_addch(stdscr, fr + 2, fc + 1, CONFIG["char_food"])

    # Snake — head is index 0
    for i, (sr, sc) in enumerate(game.snake.body):
        ch = CONFIG["char_head"] if i == 0 else CONFIG["char_body"]
        _safe_addch(stdscr, sr + 2, sc + 1, ch)

    # Game-over overlay
    if game.state == GameState.GAME_OVER:
        msg = CONFIG["game_over_msg"]
        overlay_row = (rows + 3) // 2
        overlay_col = max(0, (cols + 2 - len(msg)) // 2)
        stdscr.addstr(overlay_row, overlay_col, msg)

    stdscr.refresh()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
def main() -> None:
    curses.wrapper(lambda stdscr: Game().run(stdscr))


if __name__ == "__main__":
    main()
