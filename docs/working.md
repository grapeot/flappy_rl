# Working Log

## Changelog

### 2026-06-20

- Scaffolded the project: `docs/`, `src/flappy_rl/`, `scripts/`, `tests/`, `AGENTS.md`,
  `.gitignore`, `.env.example`, `pyproject.toml`, `README.md`.
- Wrote the documentation set: `prd.md` (goals + success criteria), `rfc.md` (architecture
  and the four key decisions), `concepts.md` (the RL primer + reward design / reward hacking
  catalog), `test.md` (per-layer verification meaning).
- Recorded the central design decisions: internal-state Gymnasium env (not window control),
  synchronous fixed-timestep loop (not async real-time), three decoupled layers, PPO by
  default via Stable-Baselines3.
- Left the reward function and the implementation deliberately unwritten — the reward design
  is the next discussion, by design.

## Lessons Learned

- The original framing ("a game window + a programmatic control interface") is the wrong
  path for an RL on a self-authored game: it forces pixels + input injection, the hardest
  setting. Because we own the game, the correct interface is `reset()`/`step()` over the
  internal numeric state. Don't reintroduce a window-control layer.
- "Real-time vs turn-based" is a false binary. The loop is synchronous fixed-timestep; the
  game is frozen between `step()` calls, so the agent never races the clock. Real-time is
  only the rendering layer, opt-in and decoupled.
- Reward is the whole specification. Log the *task metric* (pipes cleared) separately from
  reward so reward hacking shows up as a divergence rather than hiding inside a nice-looking
  reward curve. Watching rendered episodes is a debugging tool, not a demo.
