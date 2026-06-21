"""Layer 2 —— 封装物理内核的 Gymnasium environment。

本模块把 FlappyBirdGame（game.py）翻译成 Stable-Baselines3 所消费的标准 RL 契约：
reset()/step()、一个 observation space、一个 Discrete(2) 的 action space，以及——
至关重要的——REWARD 函数。

尚未实现。reward 函数被刻意推迟到一次设计讨论；其中的取舍见 docs/concepts.md 第 4 节
（reward design + reward hacking），我们会在写它之前先把这些定下来。本文件是脚手架占位符。
"""

from __future__ import annotations


class FlappyBirdEnv:
    """围绕 FlappyBirdGame 的 gymnasium.Env 封装。

    意图中的接口（待实现）：
        - observation_space : 归一化的 [bird_y, bird_vy, dx_to_pipe, gap_top,
                              gap_bottom] 的 Box（确切设计是一个待解问题——见 rfc.md）
        - action_space      : Discrete(2)  # 0 = noop, 1 = flap
        - reset(seed) -> (obs, info)
        - step(action) -> (obs, reward, terminated, truncated, info)
        - render()          : 可选的 pygame 窗口——仅供人类观看，与训练解耦

    DESIGN HOLD（设计悬置）：step() 内部的 reward 计算被刻意留空。设计它是下一场对话。
    实现时，把 task metric（过管数）和 reward 分开记进 `info`，让 reward hacking 可见
    （见 docs/concepts.md）。
    """

    def __init__(self) -> None:
        raise NotImplementedError(
            "FlappyBirdEnv 是脚手架占位符；reward 设计被推迟。"
            "见 docs/concepts.md 第 4 节。"
        )
