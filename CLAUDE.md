# Snake Game — Root Context
## Project: snake-5-layer-demo
## Owner: Jimmy Figueroa Arroyo | Bearsoft Inc.

## What This Project Is
A terminal-based Snake game in Python, built as a vehicle to demonstrate
the Five-Layer LLM Context Architecture. The game is simple. The methodology
is the product.

## Repository Layout
```
snake-5-layer-demo/
├── CLAUDE.md                    ← Layer 1: This file — every agent reads it first
├── HALLUCINATIONS.md            ← Institutional memory of agent drift
├── .kiro/specs/snake.md         ← Layer 5: Behavioral spec — written before any code
├── src/snake.py                 ← Single-file game, stdlib only
├── tests/test_snake.py          ← Layer 5: pytest suite, one test per AC
├── agents/architect/CLAUDE.md   ← Layer 1: Architect agent identity + mission
├── agents/developer/CLAUDE.md   ← Layer 1: Developer agent identity + mission
├── agents/tester/CLAUDE.md      ← Layer 1: Tester agent identity + mission
└── .github/workflows/ci.yml     ← Layer 5: CI — pytest runs on every PR
```

## Five-Layer Architecture (the methodology)
| Layer | What it is | Where it lives |
|-------|-----------|---------------|
| L1 | Initialization — world model agents inherit | CLAUDE.md files |
| L2 | Task context — only committed, reviewed artifacts | Git history |
| L3 | Execution — agents run in scoped tmux panes | agents/ outputs |
| L4 | Verification — PR gate + cherry-pick review | GitHub PRs |
| L5 | Contract — spec before code, tests as truth | .kiro/specs/, tests/, CI |

## Technology Stack
- Python 3.11+ standard library only (no external dependencies)
- pytest for testing (mock curses — no terminal required)
- curses for terminal rendering
- GitHub Actions for CI

## Engineering Principles
1. The spec (`.kiro/specs/snake.md`) is the source of truth.
   Code must conform to spec — never the other way around.
2. Tests are ground truth. A failing test means an agent hallucinated
   behavior that does not conform to spec.
3. No agent writes files outside its declared output scope.
4. Every agent produces output without asking questions.
   If uncertain, document the uncertainty in the output.
5. Human review (Jimmy) is the final gate before any merge.

## Git Workflow
- `develop` — integration branch (all feature branches merge here)
- `main` — production (tagged releases only)
- `feature/*` — branches off develop, opened as PR, CI must pass, human review
- Never push directly to `develop` or `main`
- Use cherry-pick to reject individual hallucinated commits

## Current State
- [ ] Spec authored (Layer 5)
- [ ] Architect agent run (Layer 3)
- [ ] Developer agent run (Layer 3)
- [ ] Tester agent run (Layer 3)
- [ ] CI passing (Layer 5)
- [ ] First PR merged (Layer 4)
