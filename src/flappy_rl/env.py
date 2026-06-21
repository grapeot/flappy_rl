"""Layer 2 — Gymnasium environment wrapping the physics core.

This module translates FlappyBirdGame (game.py) into the standard RL contract that
Stable-Baselines3 consumes: reset()/step(), an observation space, a Discrete(2) action
space, and — crucially — the REWARD function.

NOT YET IMPLEMENTED. The reward function is deliberately deferred to a design discussion;
see docs/concepts.md section 4 (reward design + reward hacking) for the trade-offs we will
decide on before writing it. This file is a scaffold placeholder.
"""

from __future__ import annotations


class FlappyBirdEnv:
    """gymnasium.Env wrapper around FlappyBirdGame.

    Intended interface (to be implemented):
        - observation_space : Box of normalized [bird_y, bird_vy, dx_to_pipe, gap_top,
                              gap_bottom] (exact design is an open question — see rfc.md)
        - action_space      : Discrete(2)  # 0 = noop, 1 = flap
        - reset(seed) -> (obs, info)
        - step(action) -> (obs, reward, terminated, truncated, info)
        - render()          : optional pygame window — human-only, decoupled from training

    DESIGN HOLD: the reward computation inside step() is intentionally unwritten. Designing
    it is the next conversation. When implemented, log the task metric (pipes cleared) into
    `info` separately from reward so reward hacking is visible (see docs/concepts.md).
    """

    def __init__(self) -> None:
        raise NotImplementedError(
            "FlappyBirdEnv is a scaffold placeholder; reward design is deferred. "
            "See docs/concepts.md section 4."
        )
