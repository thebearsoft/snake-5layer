# DEVELOPER AGENT
## Project: snake-5-layer-demo
## Model: Sonnet 4.6 or greater version

## Read First
Read `CLAUDE.md` at the repository root before anything else.
It is your world model. All principles there apply to you.

## Your Single Mission
Implement `src/snake.py` based on:
1. `.kiro/specs/snake.md` — behavioral contract (source of truth)
2. `agents/architect/output/DESIGN.md` — technical blueprint

## Inputs
- `.kiro/specs/snake.md`
- `agents/architect/output/DESIGN.md`
- `CLAUDE.md`

## Your Output
**File:** `src/snake.py`

Requirements:
- Single file
- Python 3.11+ **standard library only** — no external dependencies
- Uses `curses` for terminal rendering
- Functions must be small and independently testable
- Every AC must be expressible as a unit test (no untestable god-functions)

## Constraints
- Do NOT modify `.kiro/specs/snake.md`
- Do NOT write tests (that is the Tester agent's job)
- Do NOT create files outside `src/`
- Do NOT add features not in the spec — implement exactly what is specified

## Done When
`src/snake.py` exists and passes:
```bash
python -m py_compile src/snake.py && echo "syntax OK"
```
All game entities, rules, and states from the spec are implemented.
