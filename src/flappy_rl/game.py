"""Layer 1 —— 纯 Flappy Bird 物理。

本模块只拥有游戏的力学机制，别无其他：没有 RL、没有渲染、没有 reward。
给定 seed 即为确定性，是 Gymnasium env（env.py）所封装的基础。

尚未实现。这是一个脚手架占位符，描述意图中的形态，让项目结构保持连贯。
见 docs/rfc.md（决策 3）和 docs/test.md（第 1 层）。
"""

from __future__ import annotations


class FlappyBirdGame:
    """确定性的 fixed-timestep Flappy Bird 物理。

    意图中的接口（待实现）：
        - reset(seed) -> None         : 开始一局全新的游戏
        - step(flap: bool) -> None    : 精确推进一个物理 tick
        - state                        : bird y、bird vy、next pipe x / gap_top / gap_bottom
        - alive: bool                  : 一旦发生碰撞或越界即为 False
        - score: int                   : 目前已过的管道数

    这个类对 observation、把 action 当成 int、reward 一无所知。那些是 env 的职责。
    保持这一层纯粹，正是物理可以被独立测试的原因。
    """

    def __init__(self) -> None:
        raise NotImplementedError(
            "FlappyBirdGame 是脚手架占位符。见 docs/rfc.md 和 docs/test.md。"
        )
