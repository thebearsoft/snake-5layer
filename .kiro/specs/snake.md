# Snake Game — Behavioral Specification
## Version: 1.0.0
## Status: Active
## Maintained by: Jimmy Figueroa Arroyo | Bearsoft Inc.

> **This spec is the contract. It is written before any code.
> Code is fixed to match the spec — the spec is never changed to match code.**

---

## 1. Game Entities

### 1.1 Snake
- Represented as a list of `(row, col)` coordinate tuples
- Head is always index `0`
- Minimum length: 1 segment at game start
- Initial position: center of the board
- Initial direction: RIGHT

### 1.2 Food
- Represented as a single `(row, col)` coordinate tuple
- Spawns at a random position not occupied by the snake
- Exactly one food item exists at all times

### 1.3 Board
- Dimensions: configurable, default 20 rows × 40 cols
- Bounded: snake cannot move outside board boundaries
- Collision with boundary → game over

---

## 2. Game Rules

### 2.1 Movement
- Snake moves one cell per tick in its current direction
- Direction can be changed by player input
- A direction change to the exact opposite of the current direction is **ignored**
  (cannot reverse into itself)

### 2.2 Growth
When the snake head occupies the same cell as food:
- Snake length increases by 1
- Score increases by 10
- New food spawns immediately at a valid position

### 2.3 Collision
Game over conditions:
- Head collides with any body segment (self-collision)
- Head moves outside board boundaries

### 2.4 Scoring
- Initial score: 0
- Score increment per food: 10
- Score displayed during gameplay and at game over

---

## 3. Controls
| Input | Action |
|-------|--------|
| `↑` or `w` | Move up |
| `↓` or `s` | Move down |
| `←` or `a` | Move left |
| `→` or `d` | Move right |
| `q` | Quit game |

---

## 4. Game States
| State | Meaning |
|-------|---------|
| `RUNNING` | Normal gameplay |
| `GAME_OVER` | Collision detected — show final score |
| `QUIT` | Player pressed `q` — clean exit |

---

## 5. Acceptance Criteria
> One-to-one mapping with test functions in `tests/test_snake.py`.

| AC | Description |
|----|-------------|
| AC-01 | Snake initializes at center with length 1, direction RIGHT |
| AC-02 | Snake moves one cell per tick in current direction |
| AC-03 | Opposite direction input is ignored |
| AC-04 | Food consumption increases length by 1 and score by 10 |
| AC-05 | New food never spawns on snake body |
| AC-06 | Self-collision triggers GAME_OVER |
| AC-07 | Boundary collision triggers GAME_OVER |
| AC-08 | Score starts at 0 and increments correctly |
| AC-09 | Game renders at a consistent tick rate (e.g. 150ms), and speed increases incrementally every N points scored |
