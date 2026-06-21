"""Layer 1 —— 纯 Flappy Bird 物理。

本模块只拥有游戏的力学机制：重力、拍翅、管道、碰撞、计分。没有 RL、没有渲染、没有
reward。给定 seed 即为确定性，是 Gymnasium env（env.py）所封装的基础。

坐标系：x 向右、y 向下（屏幕坐标，y=0 在顶部）。小鸟 x 固定，世界向左流动——等价于
小鸟向右匀速前进。所有可调参数都是 GameConfig 上的命名常量，便于调难度。
"""

from __future__ import annotations

import random
from dataclasses import dataclass


@dataclass
class GameConfig:
    """物理参数。默认值按"对人略难、对 RL 友好"挑选；改这里即可调难度。"""

    # 画面尺寸（逻辑像素；渲染器据此换算）
    width: float = 288.0
    height: float = 512.0

    # 小鸟
    bird_x: float = 72.0          # 小鸟水平位置，固定
    bird_radius: float = 12.0     # 碰撞用半径（小鸟近似为圆）
    gravity: float = 0.9          # 每帧给 vy 的向下增量
    flap_impulse: float = -10.5   # 拍翅时把 vy 设为该值（负=向上），能反超几帧重力
    max_fall_speed: float = 14.0  # vy 下限（封顶下落速度，防止穿模）

    # 管道
    pipe_gap: float = 160.0       # 缝隙高度（约小鸟直径的 6-7 倍，留足余量）
    pipe_spacing: float = 180.0   # 相邻两根管道的水平间距
    pipe_speed: float = 4.0       # 管道每帧向左移动的像素；间距/速度 ≈ 45 帧过一根
    pipe_width: float = 52.0      # 管道宽度（碰撞用）
    gap_margin: float = 60.0      # 缝隙中心离上下边界的最小距离（限制缝隙生成范围）


@dataclass
class Pipe:
    """一根管道：x 是左沿，gap_top/gap_bottom 是缝隙的上下沿（y 坐标）。"""

    x: float
    gap_top: float
    gap_bottom: float
    scored: bool = False  # 小鸟是否已越过这根管道并计过分


class FlappyBirdGame:
    """确定性的 fixed-timestep Flappy Bird 物理。

    用法：
        game = FlappyBirdGame()
        game.reset(seed=0)
        while game.alive:
            game.step(flap=...)
            obs_source = game.observation_values()  # env 据此构造 observation

    本类对 observation 向量、把 action 当成 int、reward 一无所知——那是 env 的职责。
    保持这一层纯粹，正是物理可以被独立测试的原因。
    """

    def __init__(self, config: GameConfig | None = None) -> None:
        self.config = config or GameConfig()
        self._rng = random.Random()
        self.bird_y: float = 0.0
        self.bird_vy: float = 0.0
        self.pipes: list[Pipe] = []
        self.score: int = 0          # 已过管道数
        self.alive: bool = False
        self.frame: int = 0          # 已推进的帧数
        self._just_scored: bool = False     # 本帧是否刚过了一根管道
        self._just_died: bool = False       # 本帧是否刚死

    # ------------------------------------------------------------------ #
    # 生命周期
    # ------------------------------------------------------------------ #
    def reset(self, seed: int | None = None) -> None:
        """开始一局全新的游戏。给定 seed 则确定性。"""
        if seed is not None:
            self._rng.seed(seed)
        c = self.config
        self.bird_y = c.height / 2.0
        self.bird_vy = 0.0
        self.score = 0
        self.frame = 0
        self.alive = True
        self._just_scored = False
        self._just_died = False
        # 预先铺几根管道，第一根留出一点缓冲距离
        self.pipes = []
        first_x = c.width + 0.0
        for i in range(3):
            self.pipes.append(self._spawn_pipe(first_x + i * c.pipe_spacing))

    def _spawn_pipe(self, x: float) -> Pipe:
        """在水平位置 x 生成一根缝隙位置随机的管道。"""
        c = self.config
        lo = c.gap_margin
        hi = c.height - c.gap_margin - c.pipe_gap
        gap_top = self._rng.uniform(lo, hi)
        return Pipe(x=x, gap_top=gap_top, gap_bottom=gap_top + c.pipe_gap)

    # ------------------------------------------------------------------ #
    # 推进一帧
    # ------------------------------------------------------------------ #
    def step(self, flap: bool) -> None:
        """精确推进一个物理 tick。flap=True 时拍一下翅膀。

        死亡后再调用是 no-op。用 just_scored / just_died 查询本帧发生的事件。
        """
        self._just_scored = False
        self._just_died = False
        if not self.alive:
            return

        c = self.config
        self.frame += 1

        # 垂直运动
        if flap:
            self.bird_vy = c.flap_impulse
        else:
            self.bird_vy = min(self.bird_vy + c.gravity, c.max_fall_speed)
        self.bird_y += self.bird_vy

        # 管道左移
        for p in self.pipes:
            p.x -= c.pipe_speed

        # 计分：小鸟 x 越过管道右沿且未计过分 → +1
        for p in self.pipes:
            if not p.scored and (p.x + c.pipe_width) < c.bird_x:
                p.scored = True
                self.score += 1
                self._just_scored = True

        # 回收离屏管道，按间距补新管道，始终保持队列充足
        self.pipes = [p for p in self.pipes if p.x + c.pipe_width > 0]
        while len(self.pipes) < 3:
            last_x = max(p.x for p in self.pipes)
            self.pipes.append(self._spawn_pipe(last_x + c.pipe_spacing))

        # 碰撞检测
        if self._check_collision():
            self.alive = False
            self._just_died = True

    def _check_collision(self) -> bool:
        """撞地、撞顶，或与任一管道实体部分重叠则为碰撞。"""
        c = self.config
        r = c.bird_radius
        # 上下边界
        if self.bird_y - r <= 0 or self.bird_y + r >= c.height:
            return True
        # 管道：小鸟近似为以 (bird_x, bird_y) 为心、半径 r 的圆
        bx = c.bird_x
        for p in self.pipes:
            # 水平重叠？
            if p.x - r < bx < p.x + c.pipe_width + r:
                # 在缝隙内（上沿之下且下沿之上）才安全
                if not (self.bird_y - r > p.gap_top and self.bird_y + r < p.gap_bottom):
                    return True
        return False

    # ------------------------------------------------------------------ #
    # 查询（供 env 构造 observation / reward）
    # ------------------------------------------------------------------ #
    @property
    def just_scored(self) -> bool:
        """本帧是否刚过了一根管道。"""
        return self._just_scored

    @property
    def just_died(self) -> bool:
        """本帧是否刚死。"""
        return self._just_died

    def next_pipe(self) -> Pipe:
        """小鸟前方（含正对）最近的、尚未完全越过的那根管道。"""
        c = self.config
        candidates = [p for p in self.pipes if (p.x + c.pipe_width) >= c.bird_x]
        if not candidates:
            return self.pipes[0]
        return min(candidates, key=lambda p: p.x)

    def observation_values(self) -> dict[str, float]:
        """返回构造 observation 所需的原始量（绝对值；env 负责转相对/归一化）。"""
        p = self.next_pipe()
        return {
            "bird_y": self.bird_y,
            "bird_vy": self.bird_vy,
            "next_pipe_dx": p.x - self.config.bird_x,
            "gap_top": p.gap_top,
            "gap_bottom": p.gap_bottom,
            "gap_center": (p.gap_top + p.gap_bottom) / 2.0,
        }

    def frame_state(self) -> dict:
        """返回这一帧的完整可序列化快照，供 JSON 录制器逐帧记录。"""
        return {
            "frame": self.frame,
            "bird_y": round(self.bird_y, 2),
            "bird_vy": round(self.bird_vy, 2),
            "score": self.score,
            "alive": self.alive,
            "pipes": [
                {
                    "x": round(p.x, 2),
                    "gap_top": round(p.gap_top, 2),
                    "gap_bottom": round(p.gap_bottom, 2),
                }
                for p in self.pipes
            ],
        }
