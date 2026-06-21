# PRD — flappy_rl

## Purpose

Build a minimal, well-documented project where a computer learns to play a self-authored
Flappy Bird via reinforcement learning. The project exists primarily as a **learning
vehicle**: the value is in understanding RL's conceptual framework and its practical
engineering, not in pushing a benchmark score or hand-rolling algorithms.

## Who it's for

The author, who wants to understand:

- What a *policy* is and what it concretely looks like.
- The shape of an RL training loop, and why it is the way it is.
- The major algorithm families (value-based vs policy-gradient) at a framework level —
  enough to choose between them and read their output, not to reimplement them.
- **Reward design**: how rewards drive behavior, what the common pitfalls are, and how to
  recognize and prevent *reward hacking*.
- How RL actually gets landed in practice — the environment interface, the training
  harness, evaluation, and the gap between "it trained" and "it works."

## What we are explicitly NOT optimizing for

- Hand-writing DQN/PPO from scratch. We use Stable-Baselines3.
- State-of-the-art sample efficiency or score.
- Learning from raw pixels. We start from a compact numeric state (bird/pipe coordinates),
  which learns in minutes. Pixel-based learning is noted as a possible later extension but
  is out of scope for v0 — it is one to two orders of magnitude slower and brings CNN
  tuning that distracts from the concepts we care about.

## Requirements

### Functional

1. A deterministic, dependency-free Flappy Bird physics core (`FlappyBirdGame`) that
   exposes the full internal state (bird y, bird vy, next-pipe x / gap-top / gap-bottom),
   advances one fixed timestep per call, and reports collisions and pipe-clearing events.
2. A Gymnasium `Env` wrapper that maps the physics core to `reset()` / `step(action)` with
   a defined observation vector, a two-action discrete space, and a reward function.
3. A training entrypoint that runs PPO (default) via Stable-Baselines3 and saves a model.
4. A play/eval entrypoint that loads a saved model and runs episodes, with an optional
   real-time rendered window for human viewing.
5. An optional pygame renderer, fully decoupled from training.

### Non-functional

- Three cleanly separated layers (physics / env / training) so each is independently
  testable and independently readable.
- Training runs headless and faster-than-real-time; rendering is opt-in.
- Reproducible: seeding is supported end to end.
- Public-ready: no secrets, no personal data, fake placeholders only.

## Success criteria

The project succeeds if:

1. **Conceptual**: the docs explain — in plain language, grounded in this concrete game —
   what a policy is, how the loop trains it, the DQN-vs-PPO trade-off, and a catalog of
   reward-design pitfalls and reward-hacking failure modes with concrete examples drawn
   from *this* game.
2. **Working**: a trained policy reliably clears multiple pipes, and we can watch it in a
   rendered window. "Reliably" means clearly above a flap-randomly baseline, demonstrated
   over a batch of eval episodes.
3. **Diagnosable**: when the bird learns something degenerate (e.g. exploits a reward
   loophole), we can see it in the metrics and trace it back to the reward definition — and
   the docs treat that as a first-class expected outcome, not a surprise.

The reward function itself is deliberately deferred to a design discussion; getting it
right (and watching it go wrong) is the core learning experience this project is built
around.
