# Five-Layer LLM Context Architecture
## Operationalization Guide — Snake Game Pet Project
**Author:** Ing. Jimmy Figueroa jimmy@thebearsoft.com | Bearsoft Inc.
**Stack:** Warp · tmux · Claude Code · Kiro · GitHub · lazygit

---

## Prerequisites

```bash
# Verify your stack is ready
claude --version          # Claude Code CLI
tmux -V                   # tmux
lazygit --version         # lazygit (cherry-pick UI)
gh --version              # GitHub CLI
kiro --version            # Kiro SDD tool
```

---

## Project Overview

We will build a **terminal Snake game in Python** as a vehicle to
demonstrate all five layers in a real, observable workflow.

The game is simple enough to hold in your head but complex enough
to show: spec drift, hallucination in game logic, multi-agent
coordination, and the value of a test suite as ground truth.

```
snake-game/
├── CLAUDE.md               ← Layer 1: Agent initialization
├── .kiro/
│   └── specs/
│       └── snake.md        ← Layer 5: Spec (maintained artifact)
├── src/
│   └── snake.py
├── tests/
│   └── test_snake.py       ← Layer 5: Test suite (hallucination detector)
├── agents/
│   ├── architect/
│   │   └── CLAUDE.md
│   ├── developer/
│   │   └── CLAUDE.md
│   └── tester/
│       └── CLAUDE.md
└── .github/
    └── workflows/
        └── ci.yml          ← Layer 5: Auto-runs tests on every PR
```

---

## STEP 1 — Repository Bootstrap

```bash
# Create and clone repo
gh repo create snake-game --private --clone
cd snake-game

# Create branch structure manually
git checkout -b develop
git push -u origin develop

# Verify branch structure
git branch -a
# * develop
#   main

# Create initial project structure
mkdir -p src tests agents/architect agents/developer agents/tester .kiro/specs .github/workflows

# Commit skeleton
git add .
git commit -m "chore: project skeleton — five-layer architecture"
git push origin develop
```

---

## STEP 2 — Layer 1: Root CLAUDE.md (Initialization Context)

This is the **world model** every agent inherits. Write it once,
update it as the project evolves. It is the most important file
in the repository.

```bash
cat > CLAUDE.md << 'EOF'
# Snake Game — Root Context
## Project: snake-game
## Owner: Jimmy Figueroa Arroyo | Bearsoft Inc.

## What This Project Is
A terminal-based Snake game in Python, built as a demonstration
of the Five-Layer LLM Context Architecture. The game is the vehicle.
The methodology is the product.

## Repository Layout
- src/snake.py         — single-file game implementation
- tests/test_snake.py  — pytest test suite (ground truth)
- .kiro/specs/snake.md — Kiro spec (source of truth for behavior)
- agents/              — per-agent CLAUDE.md files
- .github/workflows/   — CI pipeline (runs tests on every PR)

## Technology Stack
- Python 3.11+
- pytest for testing
- curses for terminal rendering
- GitHub Actions for CI

## Engineering Principles
1. The spec (.kiro/specs/snake.md) is the source of truth.
   Code must conform to spec. Not the other way around.
2. Tests are ground truth. A failing test means the agent
   hallucinated behavior that does not conform to spec.
3. No agent modifies files outside its declared output scope.
4. Every agent must produce output without asking questions.
   If uncertain, document the uncertainty in the output file.
5. Human review (Jimmy) is the final gate before any merge.

## Git Workflow
- Branch: feature/* off develop
- PR: open against develop immediately (nothing merged yet)
- Cherry-pick: selectively pick commits from feature branch onto develop via lazygit
- Merge: gh pr merge --squash --delete-branch (develop already has the picks)
- Never push directly to main or develop

## Current State
Track in this section as the project evolves:
- [ ] Spec authored (Layer 5)
- [ ] Architect agent run (Layer 3)
- [ ] Developer agent run (Layer 3)
- [ ] Tester agent run (Layer 3)
- [ ] CI passing (Layer 5)
- [ ] First PR merged (Layer 4)
EOF

git add CLAUDE.md
git commit -m "docs: root CLAUDE.md — layer 1 initialization context"
git push origin develop
```

---

## STEP 3 — Layer 5a: Kiro Spec (Contract First)

**Critical:** The spec is authored BEFORE any code is written.
This is what makes it a contract, not documentation.

```bash
cat > .kiro/specs/snake.md << 'EOF'
# Snake Game — Behavioral Specification
## Version: 1.0.0
## Status: Active
## Maintained by: Jimmy Figueroa Arroyo

---

## 1. Game Entities

### 1.1 Snake
- Represented as a list of (row, col) coordinate tuples
- Head is always index 0
- Minimum length: 1 segment at game start
- Initial position: center of the board
- Initial direction: RIGHT

### 1.2 Food
- Represented as a single (row, col) coordinate tuple
- Spawns at a random position not occupied by the snake
- Exactly one food item exists at all times

### 1.3 Board
- Dimensions: configurable, default 20 rows x 40 cols
- Bounded: snake cannot move outside board boundaries
- Collision with boundary results in game over

---

## 2. Game Rules

### 2.1 Movement
- Snake moves one cell per tick in its current direction
- Direction can be changed by player input
- A direction change to the exact opposite current direction
  is IGNORED (cannot reverse into itself)

### 2.2 Growth
- When the snake head occupies the same cell as food:
  - Snake length increases by 1
  - Score increases by 10
  - New food spawns immediately at a valid position

### 2.3 Collision
- Game over conditions:
  - Head collides with any body segment (self-collision)
  - Head moves outside board boundaries

### 2.4 Scoring
- Initial score: 0
- Score increment per food: 10
- Score is displayed during gameplay and at game over

---

## 3. Controls
- UP arrow or 'w': move up
- DOWN arrow or 's': move down
- LEFT arrow or 'a': move left
- RIGHT arrow or 'd': move right
- 'q': quit game

---

## 4. Game States
- RUNNING: normal gameplay
- GAME_OVER: collision detected, show final score
- QUIT: player pressed q, clean exit

---

## 5. Acceptance Criteria (maps 1:1 to test cases)
- AC-01: Snake initializes at center with length 1, direction RIGHT
- AC-02: Snake moves one cell per tick in current direction
- AC-03: Opposite direction input is ignored
- AC-04: Food consumption increases length by 1 and score by 10
- AC-05: New food never spawns on snake body
- AC-06: Self-collision triggers GAME_OVER
- AC-07: Boundary collision triggers GAME_OVER
- AC-08: Score starts at 0 and increments correctly
EOF

git add .kiro/
git commit -m "spec: snake game behavioral specification v1.0.0 — layer 5 contract"
git push origin develop
```

---

## STEP 4 — Agent CLAUDE.md Files (Layer 1 per agent)

Each agent gets its own identity. Three agents, three missions.

```bash
# --- ARCHITECT AGENT ---
cat > agents/architect/CLAUDE.md << 'EOF'
# ARCHITECT AGENT
## snake-game project

## Your Single Mission
Read the Kiro spec at .kiro/specs/snake.md and produce a
complete technical design document at agents/architect/output/DESIGN.md.
You do not write code. You design.

## Context You Must Carry
- Root CLAUDE.md defines all project principles (read it first)
- The Kiro spec is your only input — design must satisfy every AC
- The Developer agent will implement from your DESIGN.md
- The Tester agent will write tests from both spec and DESIGN.md

## Your Output
File: agents/architect/output/DESIGN.md

Required sections:
1. Module structure (what classes/functions, their responsibilities)
2. Data structures (how snake, food, board are represented)
3. Game loop design (tick rate, input handling, render order)
4. State machine (RUNNING → GAME_OVER → QUIT transitions)
5. Anything ambiguous in the spec — document your interpretation

## What You Must NOT Do
- Do not write Python code
- Do not create any files outside agents/architect/output/
- Do not ask questions — if the spec is ambiguous, state your
  interpretation in section 5 and proceed

## Definition of Done
agents/architect/output/DESIGN.md exists and covers all 5 sections.
Every AC in the spec (AC-01 through AC-08) is traceable to a
design decision in your document.
EOF

# --- DEVELOPER AGENT ---
cat > agents/developer/CLAUDE.md << 'EOF'
# DEVELOPER AGENT
## snake-game project

## Your Single Mission
Implement src/snake.py based on:
1. .kiro/specs/snake.md (behavioral contract)
2. agents/architect/output/DESIGN.md (technical design)

## Context You Must Carry
- Root CLAUDE.md defines all project principles (read it first)
- The spec is the source of truth — code must satisfy every AC
- The design document is your implementation blueprint
- Do not gold-plate: implement exactly what the spec requires,
  nothing more

## Your Output
File: src/snake.py

Requirements:
- Single file implementation
- Python 3.11+ standard library only (no external dependencies)
- Uses curses for terminal rendering
- Every AC in the spec must be implementable as a unit test
- Functions must be small and testable (no 100-line god functions)

## What You Must NOT Do
- Do not modify .kiro/specs/snake.md
- Do not write tests (that is the Tester agent's job)
- Do not create files outside src/
- Do not add features not in the spec

## Definition of Done
src/snake.py exists, is syntactically valid (python -m py_compile src/snake.py
exits 0), and implements all game entities, rules, and states from the spec.
EOF

# --- TESTER AGENT ---
cat > agents/tester/CLAUDE.md << 'EOF'
# TESTER AGENT
## snake-game project

## Your Single Mission
Write tests/test_snake.py that verifies every Acceptance Criterion
(AC-01 through AC-08) from .kiro/specs/snake.md against the
implementation in src/snake.py.

## Context You Must Carry
- Root CLAUDE.md defines all project principles (read it first)
- The spec ACs are your test requirements — one test per AC minimum
- Tests are the ground truth of this project: if a test fails,
  the implementation hallucinated behavior not in the spec
- Use pytest. Mock curses — do not require a real terminal to test

## Your Output
File: tests/test_snake.py

Requirements:
- One test function per AC, named test_ac_01 through test_ac_08
- Each test docstring cites its AC: """AC-01: Snake initializes..."""
- All tests must be runnable with: pytest tests/ -v
- No test should require a display or terminal (mock curses)

## What You Must NOT Do
- Do not modify src/snake.py
- Do not modify the spec
- Do not create files outside tests/

## Definition of Done
pytest tests/ -v runs without import errors and all 8 test
functions exist. Tests may fail (that is useful signal) but
they must be syntactically valid and runnable.
EOF

mkdir -p agents/architect/output agents/developer/output agents/tester/output

git add agents/
git commit -m "docs: per-agent CLAUDE.md files — layer 1 agent initialization"
git push origin develop
```

---

## STEP 5 — tmux Session Layout (Layer 3: Execution)

This is your Warp terminal setup. One window, four panes.
Three agents running in parallel, you coordinating in pane 4.

```bash
# Launch the multi-agent session from your project root
tmux new-session -d -s snake-agents -x 220 -y 50

# Pane layout: 3 agents top, coordinator bottom
tmux split-window -h -t snake-agents        # Split: left | right
tmux split-window -v -t snake-agents:0.0    # Split left: top | bottom
tmux split-window -v -t snake-agents:0.2    # Split right: top | bottom

# Label each pane
tmux select-pane -t snake-agents:0.0 -T "ARCHITECT"
tmux select-pane -t snake-agents:0.1 -T "COORDINATOR"
tmux select-pane -t snake-agents:0.2 -T "DEVELOPER"
tmux select-pane -t snake-agents:0.3 -T "TESTER"

# Attach to session
tmux attach -t snake-agents

# Visual layout in Warp:
# ┌─────────────────────┬─────────────────────┐
# │   ARCHITECT         │   DEVELOPER         │
# │   pane 0.0          │   pane 0.2          │
# ├─────────────────────┼─────────────────────┤
# │   COORDINATOR       │   TESTER            │
# │   pane 0.1 (you)    │   pane 0.3          │
# └─────────────────────┴─────────────────────┘
```

---

## STEP 6 — Feature Branch + Run Agents (Layers 2, 3, 4)

```bash
# COORDINATOR PANE (0.1) — you run this
git checkout develop
git checkout -b feature/snake-v1
# Creates: feature/snake-v1 off develop

# Verify you're on the feature branch
git branch
# * feature/snake-v1

# --- PHASE 1: Run Architect agent (pane 0.0) ---
# Switch to pane 0.0 in tmux: Ctrl+b then arrow key
cd /path/to/snake-game
claude --context agents/architect/CLAUDE.md \
       "Read the Kiro spec and produce your design document."

# Wait for DESIGN.md to appear, then review it
# from COORDINATOR pane:
cat agents/architect/output/DESIGN.md

# If design looks correct — cherry-pick ONLY the design commit:
git add agents/architect/output/DESIGN.md
git commit -m "design: architect output — snake game technical design"
# Note the commit hash
git log --oneline -1
# e.g.: a1b2c3d design: architect output

# --- PHASE 2: Run Developer and Tester in parallel (panes 0.2, 0.3) ---

# DEVELOPER PANE (0.2):
claude --context agents/developer/CLAUDE.md \
       "Implement src/snake.py per spec and design."

# TESTER PANE (0.3) — runs simultaneously:
claude --context agents/tester/CLAUDE.md \
       "Write tests/test_snake.py covering all 8 ACs."

# While agents run — watch output in real time:
# COORDINATOR: watch both panes, do not intervene unless
# an agent is clearly hallucinating (going off-spec)
```

---

## STEP 7 — Layer 5b: Run Tests (Hallucination Detection)

```bash
# COORDINATOR PANE — after both developer and tester finish

# First: syntax check (fast fail)
python -m py_compile src/snake.py && echo "OK" || echo "SYNTAX ERROR"

# Install pytest if needed
pip install pytest -q

# Run the test suite — this is your hallucination detector
pytest tests/ -v

# Expected output pattern:
# tests/test_snake.py::test_ac_01 PASSED   ← snake init
# tests/test_snake.py::test_ac_02 PASSED   ← movement
# tests/test_snake.py::test_ac_03 PASSED   ← direction lock
# tests/test_snake.py::test_ac_04 PASSED   ← food consumption
# tests/test_snake.py::test_ac_05 PASSED   ← food spawn valid
# tests/test_snake.py::test_ac_06 PASSED   ← self collision
# tests/test_snake.py::test_ac_07 PASSED   ← boundary collision
# tests/test_snake.py::test_ac_08 PASSED   ← scoring

# If a test FAILS:
# 1. Read the failure message
# 2. Check: does the spec say what the test expects? (check .kiro/specs/snake.md)
# 3. If YES → implementation hallucinated. Send back to developer agent.
# 4. If NO  → test hallucinated. Send back to tester agent.
# Never manually fix agent output without documenting why.

# If all tests PASS — stage for cherry-pick review:
git add src/snake.py tests/test_snake.py
git commit -m "feat: snake game implementation + test suite (all ACs passing)"
git log --oneline -3
```

---

## STEP 8 — Layer 4: GitHub PR + Cherry-Pick Review

```bash
# Set up CI first (runs tests automatically on every PR)
cat > .github/workflows/ci.yml << 'EOF'
name: CI — Snake Game

on:
  pull_request:
    branches: [develop, main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install pytest
      - run: pytest tests/ -v
      - run: python -m py_compile src/snake.py
EOF

git add .github/
git commit -m "ci: github actions — pytest on every PR (layer 5 automation)"

# Push feature branch and open PR (PR is now open — nothing merged yet)
git push origin feature/snake-v1

gh pr create \
  --base develop \
  --head feature/snake-v1 \
  --title "feat: snake game v1 — five layer architecture demo" \
  --body "## What this PR does
Implements Snake game demonstrating the Five-Layer LLM Context Architecture.

## Layer verification
- [x] L1: CLAUDE.md initialized all agents
- [x] L2: Agents consumed only verified repo artifacts
- [x] L3: 3 agents ran in parallel tmux session
- [x] L4: This PR + cherry-pick review is the verification gate
- [x] L5: Kiro spec authored before code, pytest suite covers all 8 ACs

## Hallucination check
All 8 ACs pass in CI. Any failing test = hallucinated behavior.

## Human review checklist
- [ ] DESIGN.md faithfully reflects the spec
- [ ] src/snake.py matches design intent
- [ ] test_snake.py tests what the spec actually says
- [ ] No features added outside spec scope"

# GitHub Actions runs pytest automatically on the open PR.
# While CI runs — cherry-pick SELECTIVELY onto develop:

git checkout develop

# Open lazygit to cherry-pick from feature/snake-v1
lazygit
# Log panel [0]: find feature/snake-v1 commits
# space = select commits you want
# C     = cherry-pick selected commits onto develop

# Push develop with your cherry-picked selection
git push origin develop

# Squash-merge closes the PR cleanly (develop already has your picks)
gh pr merge --squash --delete-branch

# Sync local develop
git pull origin develop
```

---

## STEP 9 — Tag a Release

```bash
# Verify develop is clean and tests still pass
pytest tests/ -v

# When ready for a production release — tag from develop, merge to main via PR
git checkout develop
git tag v1.0.0
git push origin v1.0.0

gh pr create \
  --base main \
  --head develop \
  --title "release: v1.0.0 — snake game five-layer demo"

# Review, cherry-pick any final cleanup commits if needed, then squash-merge
gh pr merge --squash --delete-branch

git pull origin main
```

---

## STEP 10 — Update Root CLAUDE.md (Close the Loop)

Every completed iteration should update the root context.
This is what makes the next agent generation better than the last.

```bash
# Update the Current State section in CLAUDE.md:
# - [x] Spec authored (Layer 5)
# - [x] Architect agent run (Layer 3)
# - [x] Developer agent run (Layer 3)
# - [x] Tester agent run (Layer 3)
# - [x] CI passing (Layer 5)
# - [x] First PR merged (Layer 4)
# Add: Known patterns, known gotchas, decisions made

git add CLAUDE.md
git commit -m "docs: update root context — v1.0.0 complete, lessons learned"
git push origin develop
```

---

## Five-Layer Verification Checklist

Use this after every iteration to confirm all layers fired:

```
Layer 1 — Initialization
  □ Root CLAUDE.md was the first file read by every agent
  □ Each agent had its own scoped CLAUDE.md
  □ No agent was launched without a CLAUDE.md

Layer 2 — Task Context
  □ Agents consumed only files already committed to the repo
  □ No agent was given uncommitted or unreviewed context
  □ Gitingest or equivalent used for large codebase context

Layer 3 — Execution
  □ Agents ran in separate tmux panes with clear role separation
  □ No agent did work outside its declared mission
  □ Coordinator (Jimmy) observed but did not intervene in generation

Layer 4 — Verification
  □ Every agent output was reviewed before committing
  □ PR opened against develop (feature branch, nothing merged yet)
  □ Cherry-picked only trusted commits onto develop via lazygit
  □ gh pr merge --squash --delete-branch used to close the PR cleanly
  □ No direct push to develop or main

Layer 5 — Contract
  □ Kiro spec existed before any code was written
  □ Spec was not modified to match code (code was fixed to match spec)
  □ All ACs have corresponding test functions
  □ CI ran tests automatically on the PR
  □ No test was deleted or disabled to make CI pass
```

---

## Agent Hallucination Log (template)

Keep this in your repo as `HALLUCINATIONS.md`. It is your
institutional memory of where agents drift.

```markdown
# Hallucination Log — snake-game

| Date | Agent | AC | What it hallucinated | How caught | Fix |
|------|-------|----|----------------------|------------|-----|
| YYYY-MM-DD | developer | AC-03 | Allowed reverse direction | test_ac_03 failed | Sent back to developer with spec quote |
```

---

*"Agents generate code. Humans validate meaning. This is the way."*
*— Bearsoft Inc. AI Engineering Methodology*
