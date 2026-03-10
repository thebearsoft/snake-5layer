# Snake — Five-Layer LLM Context Architecture Demo

**Author:** Ing. Jimmy Figueroa · [jimmy@thebearsoft.com](mailto:jimmy@thebearsoft.com) · Bearsoft Inc.

A terminal Snake game in Python — simple enough to hold in your head,
purposeful enough to demonstrate a complete AI engineering methodology.

> The game is the vehicle. The methodology is the product.

---

## What This Is

This repository is a working demonstration of the **Five-Layer LLM Context Architecture** —
a structured approach to multi-agent AI development that eliminates hallucination drift,
enforces spec-first contracts, and keeps humans as the final verification gate.

Every file, every directory, every workflow step exists to prove a layer of the architecture
in a real, observable system.

---

## The Five Layers

| Layer | Name | Purpose | Lives in |
|-------|------|---------|----------|
| **L1** | Initialization | World model every agent inherits | `CLAUDE.md` files |
| **L2** | Task Context | Only committed, reviewed artifacts as agent input | Git history |
| **L3** | Execution | Agents run in scoped tmux panes with clear role separation | `agents/` outputs |
| **L4** | Verification | PR gate + selective cherry-pick review before anything lands | GitHub PRs, lazygit |
| **L5** | Contract | Spec written before code — tests are ground truth | `.kiro/specs/`, `tests/`, CI |

---

## Repository Layout

```
snake-5-layer-demo/
│
├── CLAUDE.md                        ← L1: Root initialization context (every agent reads this first)
├── HALLUCINATIONS.md                ← Institutional memory of agent drift
│
├── .kiro/
│   └── specs/
│       └── snake.md                 ← L5: Behavioral spec — the contract, written before any code
│
├── agents/
│   ├── architect/
│   │   ├── CLAUDE.md                ← L1: Architect agent identity and mission
│   │   └── output/
│   │       └── DESIGN.md            ← L3: Architect agent output
│   ├── developer/
│   │   └── CLAUDE.md                ← L1: Developer agent identity and mission
│   └── tester/
│       └── CLAUDE.md                ← L1: Tester agent identity and mission
│
├── src/
│   └── snake.py                     ← Game implementation (stdlib only)
│
├── tests/
│   └── test_snake.py                ← L5: One test per AC — the hallucination detector
│
├── docs/
│   └── five-layer-guide.md          ← Full operationalization guide (step-by-step)
│
└── .github/
    └── workflows/
        └── ci.yml                   ← L5: pytest runs automatically on every PR
```

---

## Key Resources

| File | What it is |
|------|-----------|
| [`CLAUDE.md`](CLAUDE.md) | The root world model — start here |
| [`.kiro/specs/snake.md`](.kiro/specs/snake.md) | Behavioral spec: 8 Acceptance Criteria, written before code |
| [`docs/five-layer-guide.md`](docs/five-layer-guide.md) | Step-by-step operationalization guide |
| [`agents/architect/output/DESIGN.md`](agents/architect/output/DESIGN.md) | Architect agent technical design |
| [`HALLUCINATIONS.md`](HALLUCINATIONS.md) | Log of every agent drift caught and corrected |

---

## Stack

| Tool | Role |
|------|------|
| **Claude Code** | Agent execution environment |
| **Kiro** | Spec-driven development (SDD) — spec before code |
| **tmux + Warp** | Multi-agent pane layout (L3 execution) |
| **lazygit** | Selective cherry-pick review (L4 verification) |
| **GitHub CLI (`gh`)** | PR lifecycle — open, review, squash-merge |
| **pytest** | Test suite as ground truth (L5 contract) |
| **GitHub Actions** | CI — auto-runs tests on every PR |

---

## Git Workflow

```
feature/snake-v1  ──●──●──●──●──
                              ↑
                     gh pr create (PR open, nothing merged)
                              ↓
develop           ────────────●──●── (cherry-picked commits via lazygit)
                              ↓
                     gh pr merge --squash --delete-branch
```

1. Branch off `develop` → do work on `feature/*`
2. Open PR immediately (`gh pr create --base develop`) — CI runs
3. `git checkout develop` → open lazygit → cherry-pick only trusted commits
4. `git push origin develop`
5. `gh pr merge --squash --delete-branch` — closes the PR cleanly
6. `git pull origin develop`

> **Never push directly to `develop` or `main`.**
> Cherry-pick is the human review mechanism — it is the gate between agent output and the integration branch.

---

## Engineering Principles

1. **Spec is the source of truth.** Code is fixed to match the spec. The spec is never changed to match code.
2. **Tests are ground truth.** A failing test means an agent hallucinated behavior outside the spec.
3. **No agent writes outside its declared scope.** Role separation is enforced by directory boundaries.
4. **Every agent produces output without asking questions.** If uncertain, it documents the uncertainty.
5. **Human review is the final gate.** No agent output reaches `develop` without deliberate cherry-pick selection.
6. **Errors degrade gracefully — never silently.** No swallowed exceptions, no silent fallbacks.

---

## Project Status

- [x] Spec authored (Layer 5)
- [ ] Architect agent run (Layer 3)
- [ ] Developer agent run (Layer 3)
- [ ] Tester agent run (Layer 3)
- [ ] CI passing (Layer 5)
- [ ] First PR merged (Layer 4)

---

*"Agents generate code. Humans validate meaning. This is the way."*
*— Bearsoft Inc. AI Engineering Methodology*
