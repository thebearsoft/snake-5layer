# Snake Game — Technical Design
## Version: 1.0.0
## Agent: Architect
## Input: `.kiro/specs/snake.md` v1.0.0
## Output: `src/snake.py`

## Configuration
- All hardcoded values must be externalized into a `config.yaml` file
- Code must never contain magic numbers or magic strings
- No hard coded values ever, all must go to config.yaml file
---

## 1. Module Structure

Single file: `src/snake.py`

All logic lives in one module (stdlib only). No submodules.

### Functions / Classes

```
Direction (Enum)
    UP, DOWN, LEFT, RIGHT
    property: opposite → Direction

GameState (Enum)
    RUNNING, GAME_OVER, QUIT

Snake (dataclass)
    body: list[tuple[int, int]]   # [(row, col), ...]  head = body[0]
    direction: Direction

    move(new_direction: Direction | None) → tuple[int, int]
        # Returns new head position; does NOT mutate body yet
        # Ignores new_direction if it equals self.direction.opposite

    grow(new_head: tuple[int, int]) → None
        # Prepend new_head; keep tail

    step(new_head: tuple[int, int]) → None
        # Prepend new_head; remove tail

Board (dataclass)
    rows: int
    cols: int

    in_bounds(pos: tuple[int, int]) → bool

Game
    snake: Snake
    board: Board
    food: tuple[int, int]
    score: int
    state: GameState
    tick_interval_ms: int          # starts at 150, decreases with score

    __init__(rows=20, cols=40) → None
    _spawn_food() → tuple[int, int]
    tick(input_direction: Direction | None) → GameState
        # Single game step: move → check collision → check food → render data
    handle_input(key: int) → Direction | None | "QUIT"
    run(stdscr) → None             # main curses loop

render(stdscr, game: Game) → None
    # Draws board border, snake, food, score, game-over overlay

main() → None
    # Entry point: curses.wrapper(lambda stdscr: Game().run(stdscr))
```

---

## 2. Data Structures

### Snake body
```python
body: list[tuple[int, int]]
# body[0] = head, body[-1] = tail
# Example (length 3, center of 20×40 board):
# [(10, 20), (10, 19), (10, 18)]
```
- **Rationale:** List gives O(1) prepend via `[new_head] + body` (body is short;
  deque would also work but adds complexity for negligible gain at game scale).
- Head-first ordering makes collision checks direct: `new_head in body[1:]`.

### Food
```python
food: tuple[int, int]   # (row, col)
```
Single tuple; exactly one item always present (AC-05, §1.2).

### Board
```python
rows: int = 20
cols: int = 40
```
Boundary check: `0 <= row < rows and 0 <= col < cols`.

### Direction
```python
class Direction(Enum):
    UP    = (-1,  0)
    DOWN  = ( 1,  0)
    LEFT  = ( 0, -1)
    RIGHT = ( 0,  1)

    @property
    def opposite(self) -> "Direction":
        r, c = self.value
        return Direction((-r, -c))
```
Value encodes the delta, so `new_head = (head_row + dr, head_col + dc)` without
a lookup table.

### Score
```python
score: int = 0   # starts at 0 (AC-08); +10 per food (AC-04)
```

### Tick interval
```python
tick_interval_ms: int = 150
```
Decreases as score increases (AC-09). Speed schedule (see §3).

---

## 3. Game Loop Design

### Tick rate & speed schedule (AC-09)

Base interval: **150 ms**.

| Score threshold | Interval |
|----------------|----------|
| 0              | 150 ms   |
| 50             | 130 ms   |
| 100            | 110 ms   |
| 150            | 90 ms    |
| 200            | 70 ms    |
| 250+           | 50 ms    |

`tick_interval_ms` is recomputed after every food consumption event inside
`tick()`. Floor is 50 ms to keep the game playable.

### Input handling

`curses.halfdelay(n)` is used so `stdscr.getch()` blocks for at most
`tick_interval_ms / 100` tenths of a second (curses unit), then returns -1 if
no key was pressed. This gives a non-blocking poll without a busy loop.

Key mapping:
```
curses.KEY_UP  / ord('w')  → Direction.UP
curses.KEY_DOWN / ord('s') → Direction.DOWN
curses.KEY_LEFT / ord('a') → Direction.LEFT
curses.KEY_RIGHT / ord('d') → Direction.RIGHT
ord('q')                   → QUIT signal
-1 (timeout)               → None (keep current direction)
```

### Render order (inside `run` loop)

1. Clear screen (or selective erase — implementation detail).
2. Draw board border.
3. Draw food character (`*`).
4. Draw snake body (head: `@`, body segments: `o`).
5. Draw score line (`Score: N`).
6. If state == GAME_OVER: draw centered overlay (`GAME OVER — press q to quit`).
7. `stdscr.refresh()`.

### Single iteration pseudocode

```
loop:
    key = stdscr.getch()           # blocks up to tick_interval_ms
    direction = handle_input(key)
    if direction == QUIT:
        game.state = QUIT
        break
    game.tick(direction)
    render(stdscr, game)
    if game.state == GAME_OVER:
        wait for 'q' then break
```

---

## 4. State Machine

```
          ┌─────────────────────────────────────┐
          │              RUNNING                │
          │  (normal tick loop, input accepted) │
          └──────────────┬──────────────────────┘
                         │
          ┌──────────────┴──────────────┐
          │ boundary hit OR self-collision│  (AC-06, AC-07)
          ▼                             │
   ┌─────────────┐        ┌─────────────┴──────┐
   │  GAME_OVER  │        │  q pressed          │
   │ (show score)│        │  (any time in RUNNING│
   └──────┬──────┘        │   or GAME_OVER)     │
          │ q pressed      └────────┬────────────┘
          │                         │
          ▼                         ▼
       ┌──────┐                 ┌──────┐
       │ QUIT │                 │ QUIT │
       └──────┘                 └──────┘
```

### Transition table

| Current state | Event                        | Next state |
|--------------|------------------------------|------------|
| RUNNING      | tick — boundary collision     | GAME_OVER  |
| RUNNING      | tick — self-collision         | GAME_OVER  |
| RUNNING      | key `q`                      | QUIT       |
| GAME_OVER    | key `q`                      | QUIT       |
| QUIT         | —                            | (exit)     |

- `game.tick()` sets `game.state` to `GAME_OVER` on collision; the run loop
  checks state after every tick.
- `q` is checked in `handle_input` before `tick()` executes, so it works in
  both RUNNING and GAME_OVER phases.

### AC traceability

| AC    | Design decision |
|-------|----------------|
| AC-01 | `Snake.__init__`: body = [(rows//2, cols//2)], direction = RIGHT |
| AC-02 | `game.tick()` always calls `snake.step()` or `snake.grow()` once |
| AC-03 | `Direction.opposite` property; ignored in `snake.move()` |
| AC-04 | `tick()`: if new_head == food → `snake.grow()`, score += 10, `_spawn_food()` |
| AC-05 | `_spawn_food()`: random sample from `all_cells - set(snake.body)` |
| AC-06 | `tick()`: if new_head in snake.body[1:] → state = GAME_OVER |
| AC-07 | `tick()`: if not board.in_bounds(new_head) → state = GAME_OVER |
| AC-08 | `score` initialized to 0; incremented by 10 on food only |
| AC-09 | `tick_interval_ms` recomputed from score after each food event |

---

## 5. Ambiguities & Interpretations

### 5.1 Initial food position
**Spec gap:** §1.2 says food spawns at a random position not occupied by the
snake, but does not specify the initial food spawn timing.

**Interpretation:** Food is spawned during `Game.__init__` immediately after
the snake is placed, using the same `_spawn_food()` logic. This guarantees
exactly one food item exists from the first frame.

### 5.2 Speed schedule granularity (AC-09)
**Spec gap:** AC-09 says "speed increases incrementally every N points scored"
but does not define N or the magnitude.

**Interpretation:** N = 50 points per step, interval decreases by 20 ms per
step, floor at 50 ms (see §3 table). This is documented as a design decision;
the spec author may override.

### 5.3 Collision check order
**Spec gap:** §2.3 lists two game-over conditions without specifying priority
when both occur simultaneously (e.g., diagonal-impossible in 4-directional
movement, but boundary + body could both be true in theory if body presses
against wall).

**Interpretation:** Boundary check precedes self-collision check inside
`tick()`. Both set the same GAME_OVER state so the order has no observable
effect.

### 5.4 `q` during GAME_OVER
**Spec gap:** §4 shows QUIT as a state but does not explicitly state whether
`q` is accepted during GAME_OVER.

**Interpretation:** `q` transitions to QUIT from any state. The game-over
overlay instructs the player to press `q` to exit, making this the natural UX.

### 5.5 Board border rendering
**Spec gap:** §1.3 defines board dimensions but does not specify whether a
border character is rendered.

**Interpretation:** A single-character border (`#`) is drawn inside the curses
window, reducing the playable area by 1 cell on each edge. The snake's valid
coordinate space is `[0, rows)` × `[0, cols)` in logical coordinates; the
renderer maps these to `[1, rows+1)` × `[1, cols+1)` in screen coordinates to
leave room for the border.

### 5.6 Minimum terminal size
**Spec gap:** Spec does not specify behavior when the terminal is smaller than
`board.rows + 2` × `board.cols + 2`.

**Interpretation:** `Game.run()` checks terminal size at startup and raises a
`RuntimeError` with a descriptive message if the terminal is too small. Per
project principle §6, no silent fallbacks.
