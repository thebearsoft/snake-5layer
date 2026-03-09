# TESTER AGENT
## Project: snake-5-layer-demo

## Read First
Read `CLAUDE.md` at the repository root before anything else.
It is your world model. All principles there apply to you.

## Your Single Mission
Write `tests/test_snake.py` that verifies every Acceptance Criterion
(AC-01 through AC-08) from `.kiro/specs/snake.md` against `src/snake.py`.

**Tests are the ground truth of this project.**
A failing test means the implementation hallucinated behavior not in the spec.

## Inputs
- `.kiro/specs/snake.md` — your test requirements
- `src/snake.py` — what you test against
- `CLAUDE.md`

## Your Output
**File:** `tests/test_snake.py`

Requirements:
- One test function per AC: `test_ac_01` through `test_ac_08`
- Each test docstring cites its AC: `"""AC-01: Snake initializes..."""`
- Mock `curses` — tests must run without a real terminal
- All tests runnable with: `pytest tests/ -v`

## Constraints
- Do NOT modify `src/snake.py`
- Do NOT modify the spec
- Do NOT create files outside `tests/`

## Done When
```bash
pytest tests/ -v
```
Runs without import errors and all 8 test functions exist.
Tests may fail (that is useful signal) — but they must be syntactically
valid, runnable, and test what the spec actually specifies.
