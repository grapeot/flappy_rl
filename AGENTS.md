# AGENTS.md — flappy_rl

Local rules for working in this project.

## What this project is

A learning vehicle for understanding reinforcement learning by teaching a computer to play a
self-authored Flappy Bird. The priority is conceptual clarity and clean engineering, **not**
benchmark score and **not** hand-rolled algorithms. We use Stable-Baselines3 for the
algorithm. Read `docs/concepts.md` for the conceptual frame before touching reward code.

## Structure

- `src/flappy_rl/` — the package: `game.py` (Layer 1 physics), `env.py` (Layer 2 Gymnasium
  wrapper + reward + optional render), and any shared helpers.
- `scripts/` — user entrypoints: `train.py`, `play.py`. These are the stable commands; don't
  bury run logic only in docs.
- `tests/` — pytest, organized by layer (see `docs/test.md`).
- `docs/` — `prd.md`, `rfc.md`, `concepts.md`, `test.md`, `working.md`.

## The three-layer rule

Keep the layers decoupled:

1. `game.py` knows nothing about RL or rendering.
2. `env.py` owns the observation, the action space, the reward, and `render()`.
3. `scripts/` own the algorithm calls.

Reward changes belong in Layer 2 only. Don't leak reward logic into the physics.

## Reward is deferred on purpose

The reward function is intentionally left for a design discussion. When implementing it,
follow the pitfalls catalog in `docs/concepts.md`: reward the true objective as directly as
tolerable, keep magnitudes honest, log the task metric separately from reward, and watch
rendered episodes. Treat the first reward as a hypothesis to be falsified.

## Environment

- Python 3.11+, `uv` + local `.venv`. Install with `uv pip install -e '.[dev]'`.
- Use `uv pip install`, never bare `pip install`.

## Working discipline

- Update `docs/working.md` (Changelog + Lessons Learned) at every meaningful step.
- Commit frequently and in coherent slices (scaffold / implementation / validation), not one
  giant commit.
- Training writes to `runs/`, `checkpoints/`, `logs/`, `models/` — all gitignored. Don't
  commit model binaries or videos.
- Verification is not just green tests: for any real training run, report the eval task
  metric AND watch at least one rendered episode (see `docs/test.md`).

## Publishability

This repo is built to be publishable. No secrets, no personal data, no private paths. Keep
`.env.example` placeholders fake.
