# RFC — Architecture & Key Decisions

This document records the architecture and the design decisions that shaped it. The
conceptual RL background lives in [`concepts.md`](concepts.md); this file is about *how the
code is structured and why*.

## The architecture in one diagram

```
┌─────────────────────────────────────────────────────────────┐
│  scripts/train.py · scripts/play.py   (user entrypoints)     │
└───────────────┬─────────────────────────────────────────────┘
                │ uses
┌───────────────▼─────────────────────────────────────────────┐
│  Stable-Baselines3  (PPO / DQN — the algorithm, off the shelf)│
└───────────────┬─────────────────────────────────────────────┘
                │ drives via reset()/step()
┌───────────────▼─────────────────────────────────────────────┐
│  Layer 2:  FlappyBirdEnv  (gymnasium.Env wrapper)            │
│    - observation vector, action space, REWARD function       │
│    - optional render() → pygame  (human-only side path)      │
└───────────────┬─────────────────────────────────────────────┘
                │ wraps
┌───────────────▼─────────────────────────────────────────────┐
│  Layer 1:  FlappyBirdGame  (pure physics, no RL, no render)  │
│    - bird y / vy, gravity, pipe spawning, collision          │
└─────────────────────────────────────────────────────────────┘
```

Everything runs in **one Python process**. There is no game window to "control," no
screen-scraping, no simulated keypresses, no inter-process communication.

## Decision 1 — Internal state, not a window + control interface

The instinctive design is "make a real game window, give it an API, and have the program
control it like a player." For RL on a game *you wrote yourself*, this is the wrong path.

Driving a window means screen-capture, image recognition, and OS-level input injection —
the hardest RL setting (learn from pixels under real input latency). That setting only
makes sense when you *cannot* reach the game's internal state, e.g. playing someone else's
closed game.

Here the game is ours, so the bird's height, velocity, and the next pipe's gap are just
variables we can read. The RL algorithm doesn't want a picture of the window; it wants
those numbers. So the right interface is not "control a window" but "expose a function you
can `step()`" — which is exactly the Gymnasium contract:

```python
obs, info = env.reset(seed=0)
obs, reward, terminated, truncated, info = env.step(action)  # action ∈ {0: noop, 1: flap}
```

Rendering a window is then a pure, optional, human-only output path — decoupled from
learning, off during training, on when we want to watch.

**Consequence:** the "Python backend vs real-time window" tension in the original framing
dissolves. There is no second process and no real-time control channel to coordinate.

## Decision 2 — Synchronous fixed-timestep loop, not async real-time

"Real-time vs turn-based" is a false binary here. The game is *conceptually* real-time (the
bird falls whether or not you act), but every real-time game is, inside the machine, a
sequence of discrete frames. We treat one frame as one decision point: flap this frame or
not? So from the algorithm's view it is step-based — but a "step" is a fixed slice of
physics time, not a turn that waits for an opponent.

The key property: **the game is frozen between steps.** `env.step()` advances physics
exactly one tick and returns; nothing moves until the agent calls again. The agent never
"falls behind" the game — the game waits for the agent. (The latency worry — "the algorithm
is too slow, the bird crashes before it decides" — only exists in the screen-control path,
which is another reason we rejected it.)

Therefore:

- **Training:** run the loop with no `sleep` and no window, as fast as the CPU allows —
  potentially tens of thousands of frames per second. Wall-clock realtime would just waste
  cycles.
- **Playing for humans:** run the *same* loop, but `sleep` to ~30 FPS and render. It looks
  like a live game; the core is identical synchronous stepping.

Same loop; the only difference is whether we sleep and draw.

## Decision 3 — Three decoupled layers

- **Layer 1 `FlappyBirdGame` (physics):** owns bird position/velocity, gravity, flap
  impulse, pipe spawning and motion, collision and scoring. Knows nothing about RL or
  rendering. Deterministic given a seed. Independently testable by stepping it by hand and
  asserting on coordinates.
- **Layer 2 `FlappyBirdEnv` (gymnasium.Env):** translates physics into the RL contract —
  defines the observation vector, the discrete action space, and **the reward function**
  (the one piece we are deliberately deferring to a design discussion). Owns the optional
  `render()`.
- **Layer 3 training/eval:** thin scripts that hand the env to Stable-Baselines3.

This separation is what makes the project a good teaching artifact: reward design changes
touch only Layer 2; algorithm changes touch only Layer 3; physics stays put and trusted.

## Decision 4 — Algorithm: PPO by default, DQN available

Both fit a two-action, low-dimensional, dense-reward problem. We default to **PPO** because
it is robust to hyperparameters and is the current industry default — it lets us spend our
attention on the environment and reward rather than on babysitting exploration schedules.
**DQN** stays available as a one-line swap, partly because contrasting the two (value-based
vs policy-gradient) is itself instructive. We do not implement either; Stable-Baselines3
provides both. Rationale and trade-offs are in [`concepts.md`](concepts.md).

## Decision 5 — Compact numeric observation, not pixels (for v0)

The observation is a small vector — bird height, vertical velocity, horizontal distance to
the next pipe, and that pipe's gap edges. Relative/normalized coordinates are preferred over
raw ones so the policy generalizes across the screen. This learns in minutes with an MLP
policy. Pixel input (CNN policy) is a documented future extension, deliberately out of v0
scope for cost and focus reasons.

## Tech stack

- Python 3.11+, managed with `uv` in a local `.venv`.
- `gymnasium` for the env contract.
- `stable-baselines3` (+ `torch`) for PPO/DQN.
- `pygame` for the optional renderer only.
- `pytest` for tests; `ruff` for lint.

## Open questions (for the upcoming reward discussion)

1. Reward shape: sparse (only on pipe-clear / death) vs shaped (per-frame survival, gap
   proximity bonus). Trade-off: learning speed vs reward-hacking surface.
2. Observation design: raw vs relative coordinates; how many pipes ahead to expose.
3. Episode termination and any truncation cap (to stop a "perfect" bird from running
   forever during eval).

These are intentionally unresolved here — they are the substance of the next conversation.
