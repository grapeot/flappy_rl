# Test Strategy

The point of this file is not to restate `pytest` commands but to define **what "verified"
means** at each layer, so a later agent (or future me) knows when something is actually done.

The three-layer architecture (see [`rfc.md`](rfc.md)) is what makes testing tractable: each
layer is checkable on its own before the next is trusted.

## Layer 1 — Physics core (`FlappyBirdGame`): unit tests

Pure, deterministic logic. No RL, no rendering, no randomness beyond a seed. This is the
layer with the strongest, cheapest tests.

Cover:

- Gravity integrates correctly: stepping with no flap monotonically decreases height
  (increases downward velocity) by the expected amount.
- Flap applies the expected upward impulse to velocity.
- Pipes spawn at the configured spacing and move left at the configured speed.
- Collision fires exactly when the bird overlaps a pipe or leaves the vertical bounds, and
  not a frame early or late.
- A pipe-cleared event fires exactly once as the bird passes a pipe.
- Determinism: same seed + same action sequence → identical state trajectory.

If Layer 1 is solid, every bug above it is an RL/reward bug, not a physics bug — which is
most of the diagnostic value.

## Layer 2 — Env wrapper (`FlappyBirdEnv`): contract + integration tests

Verify it honors the Gymnasium contract and that the env↔physics translation is faithful.

Cover:

- `reset()` returns an observation inside the declared `observation_space`, and `info` is a
  dict.
- `step(action)` returns `(obs, reward, terminated, truncated, info)` with correct types;
  `obs` stays inside `observation_space`; `reward` is a float.
- The action space is `Discrete(2)` and both actions are accepted.
- A full random-action episode runs from `reset()` to `terminated` without error.
- Seeding `reset(seed=k)` reproduces the same episode.
- **Reward sanity** (once the reward exists): targeted assertions that the documented reward
  events fire with the documented signs/magnitudes — e.g. death yields the penalty,
  pipe-clear yields the bonus. These tests double as guardrails against accidental reward
  regressions that invite hacking.
- Use Stable-Baselines3's `check_env` utility, which audits the env against the spec.

## Layer 3 — Training / eval: smoke tests, not score tests

We do not unit-test "the bird learns" — that's slow and stochastic. Instead:

- **Smoke test**: `model.learn(total_timesteps=<small>)` runs end to end without error on
  the real env, and produces a saveable model. This catches integration breakage cheaply.
- **Eval harness check**: loading a saved model and running N eval episodes returns a
  task-metric summary (mean / std pipes cleared) and never throws.

## Manual / visual verification (a first-class step, not an afterthought)

Some of the most important failures in this project — reward hacking especially — are
**invisible in metrics and obvious on screen.** Verification therefore includes:

- Run `scripts/play.py --render` on a trained model and watch several episodes.
- Confirm the behavior matches the metric: if mean pipes cleared is high, the bird should
  visibly clear pipes — not hover, hug the ceiling, or die fast.
- A divergence between "reward went up" and "task metric / visible behavior" is the
  signature of reward hacking and is itself a finding to record in `working.md`.

## What counts as "done"

- Layers 1 and 2 green under `pytest`.
- `check_env` passes.
- A short training smoke test completes and saves a model.
- For any real training run: the eval task metric is reported *and* at least one rendered
  episode was watched, with the observation logged in `working.md`.
