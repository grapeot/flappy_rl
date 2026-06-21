"""Scaffold-stage tests.

These assert only that the package structure is importable and that the deferred components
announce themselves as placeholders. Real per-layer tests (physics unit tests, env contract
tests, training smoke test) are specified in docs/test.md and land with the implementation.
"""

import flappy_rl


def test_package_imports():
    assert flappy_rl.__version__ == "0.1.0"


def test_components_are_deferred_placeholders():
    from flappy_rl.env import FlappyBirdEnv
    from flappy_rl.game import FlappyBirdGame

    for cls in (FlappyBirdGame, FlappyBirdEnv):
        try:
            cls()
        except NotImplementedError:
            continue
        raise AssertionError(f"{cls.__name__} should be a NotImplementedError placeholder")
