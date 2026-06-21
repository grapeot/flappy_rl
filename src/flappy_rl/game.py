"""Layer 1 — pure Flappy Bird physics.

This module owns the game's mechanics and nothing else: no RL, no rendering, no reward.
It is deterministic given a seed, and is the foundation the Gymnasium env (env.py) wraps.

NOT YET IMPLEMENTED. This is a scaffold placeholder describing the intended shape so the
project structure is coherent. See docs/rfc.md (Decision 3) and docs/test.md (Layer 1).
"""

from __future__ import annotations


class FlappyBirdGame:
    """Deterministic fixed-timestep Flappy Bird physics.

    Intended interface (to be implemented):
        - reset(seed) -> None         : start a fresh game
        - step(flap: bool) -> None    : advance exactly one physics tick
        - state                        : bird y, bird vy, next pipe x / gap_top / gap_bottom
        - alive: bool                  : False once a collision or out-of-bounds occurs
        - score: int                   : pipes cleared so far

    The class knows nothing about observations, actions-as-ints, or reward. Those are the
    env's job. Keeping this layer pure is what makes physics independently testable.
    """

    def __init__(self) -> None:
        raise NotImplementedError(
            "FlappyBirdGame is a scaffold placeholder. See docs/rfc.md and docs/test.md."
        )
