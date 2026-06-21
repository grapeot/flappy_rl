"""Layer 2 —— 封装物理内核的 Gymnasium environment。

把 FlappyBirdGame（game.py）翻译成 Stable-Baselines3 消费的标准 RL 契约：reset()/step()、
一个 5 维相对坐标 observation、一个 Discrete(2) 的 action space，以及 reward 函数。

reward 有两个 baseline，由 RewardConfig.mode 切换（决策见 docs/decisions.md）：

- "sparse"（版本一）：过管 +1、死亡 -1、其余每帧 0。最纯，暴露 sparse 学得慢。
- "shaped"（版本二）：在 sparse 事件之上，每帧叠加一个连续的对齐引导——离下一根缝隙
  中心的垂直偏差 dy 越大，扣得越多（dy 归一化后平方，乘一个小系数）。

版本三（考虑重力/动量）只在 docs/decisions.md 记思路，不在此实现。
"""

from __future__ import annotations

from dataclasses import dataclass

import gymnasium as gym
import numpy as np
from gymnasium import spaces

from .game import FlappyBirdGame, GameConfig

MAX_SCORE = 50  # 决策三：过满 50 管 truncate 算赢


@dataclass
class RewardConfig:
    """reward 形态。mode 决定走哪个 baseline。"""

    mode: str = "sparse"          # "sparse" | "shaped"
    pass_pipe: float = 1.0        # 过一根管道
    death: float = -1.0           # 死亡（撞/出界）
    alignment_coef: float = 0.1   # 仅 shaped：对齐惩罚系数（作用在归一化 dy² 上）


class FlappyBirdEnv(gym.Env):
    """围绕 FlappyBirdGame 的 gymnasium.Env。

    observation（5 维 float32，全部相对/归一化，让 policy 在屏幕各处泛化）：
        [0] 小鸟高度          bird_y / height           ∈ [0,1]
        [1] 小鸟垂直速度      bird_vy / max_fall_speed  约 ∈ [-1,1]
        [2] 到下一根管道水平距离  dx / width            约 ∈ [0,~2]
        [3] 缝隙上沿相对小鸟   (gap_top - bird_y) / height
        [4] 缝隙下沿相对小鸟   (gap_bottom - bird_y) / height

    action: Discrete(2)  # 0 = 不拍, 1 = 拍

    每步把 info 里带上 task metric（score、过管事件），让训练时 reward 与任务指标分开记录，
    这样 reward hacking 会以背离形式显现（见 docs/concepts.md）。
    """

    metadata = {"render_modes": []}

    def __init__(
        self,
        game_config: GameConfig | None = None,
        reward_config: RewardConfig | None = None,
    ) -> None:
        super().__init__()
        self.game = FlappyBirdGame(game_config)
        self.reward_config = reward_config or RewardConfig()

        # observation 各分量理论范围较宽，留足边界避免裁剪；用 float32 配合 SB3。
        high = np.array([2.0, 4.0, 4.0, 4.0, 4.0], dtype=np.float32)
        self.observation_space = spaces.Box(low=-high, high=high, dtype=np.float32)
        self.action_space = spaces.Discrete(2)

    # ------------------------------------------------------------------ #
    def _obs(self) -> np.ndarray:
        c = self.game.config
        v = self.game.observation_values()
        return np.array(
            [
                v["bird_y"] / c.height,
                v["bird_vy"] / c.max_fall_speed,
                v["next_pipe_dx"] / c.width,
                (v["gap_top"] - v["bird_y"]) / c.height,
                (v["gap_bottom"] - v["bird_y"]) / c.height,
            ],
            dtype=np.float32,
        )

    def reset(self, *, seed: int | None = None, options: dict | None = None):
        super().reset(seed=seed)
        self.game.reset(seed=seed)
        return self._obs(), {"score": 0}

    def step(self, action: int):
        self.game.step(flap=bool(action))

        terminated = self.game.just_died
        truncated = self.game.score >= MAX_SCORE
        reward = self._reward()

        info = {
            "score": self.game.score,
            "passed_pipe": self.game.just_scored,  # 本帧是否过管（task metric 事件）
        }
        return self._obs(), reward, terminated, truncated, info

    def _reward(self) -> float:
        rc = self.reward_config
        r = 0.0

        # 事件项（两版共用）
        if self.game.just_scored:
            r += rc.pass_pipe
        if self.game.just_died:
            r += rc.death

        # 塑形项（仅 shaped）：离下一根缝隙中心的归一化垂直偏差，平方惩罚
        if rc.mode == "shaped" and self.game.alive:
            c = self.game.config
            v = self.game.observation_values()
            dy = (v["bird_y"] - v["gap_center"]) / c.height  # 归一化
            r -= rc.alignment_coef * (dy * dy)

        return float(r)

    def render(self):
        # 网页回放走 JSON + Canvas 播放器（见 docs/player.js），不在此渲染。
        # 逐帧快照通过 recorder.py 在训练/评估循环外录制。
        return None
