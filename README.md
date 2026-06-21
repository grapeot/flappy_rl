# flappy_rl

A small, readable project for **understanding reinforcement learning** by teaching a
computer to play Flappy Bird. The goal here is not to hand-write algorithms — we lean on
mature libraries for that. The goal is to understand the *concepts and the engineering of
landing RL in practice*: what a policy is, how the training loop is shaped, how to design a
reward, and how to avoid reward hacking.

If you want the conceptual tour, read the docs in this order:

1. [`docs/prd.md`](docs/prd.md) — what we're building and why; the success criteria.
2. [`docs/rfc.md`](docs/rfc.md) — the architecture and the key design decisions, including
   *why this is a synchronous fixed-timestep loop and not "control a real window."*
3. [`docs/concepts.md`](docs/concepts.md) — the RL primer: policy, value, the loop, DQN vs
   PPO, and **reward design + reward hacking** (the part you actually came for).
4. [`docs/test.md`](docs/test.md) — what "verified" means at each layer.

The `docs/working.md` file is the running changelog and lessons-learned log.

## Design in one paragraph

Flappy Bird is one of the friendliest RL problems there is: two actions (flap / don't),
a state describable by a handful of numbers (bird height, vertical velocity, the gap of the
next pipe), and a clear notion of progress (stay alive, clear pipes). We write the game as a
plain Python object, wrap it in the standard [Gymnasium](https://gymnasium.farama.org/) `Env`
interface (`reset()` / `step()`), and let [Stable-Baselines3](https://stable-baselines3.readthedocs.io/)
do the learning. Rendering a window is an optional, human-only side path that is fully
decoupled from training — during training there is no window and no real-time clock.

## Status

Scaffold + documentation stage. The reward function is intentionally **left for a follow-up
discussion** — designing it well is the most interesting part of the project, and
[`docs/concepts.md`](docs/concepts.md) sets up the trade-offs we'll decide on together.

## Privacy

This repository is designed to be publishable with only fake examples. It contains no
secrets, no personal data, and no private paths. `.env.example` documents an optional
experiment-tracking integration with a placeholder key.

## Quick start (once implemented)

```bash
# Create the environment with uv
uv venv .venv && source .venv/bin/activate
uv pip install -e '.[dev]'

# Train
python scripts/train.py

# Watch the trained bird play (opens a window)
python scripts/play.py --render
```
