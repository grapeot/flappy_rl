"""脚手架阶段的测试。

这些测试只断言两件事：包结构可以被 import，以及被推迟的组件会把自己声明为占位符。
真正的分层测试（physics 单元测试、env 契约测试、训练 smoke test）在 docs/test.md 中
有规格说明，会随实现一起落地。
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
        raise AssertionError(f"{cls.__name__} 应当是一个 NotImplementedError 占位符")
