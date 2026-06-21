"""逐帧 JSON 录制器 —— 回放 artifact 的来源。

一局游戏被录成一个 JSON 文件：包含物理常量（播放器据此换算坐标）、逐帧快照、以及结局
摘要。网页 Canvas 播放器（docs/player.js）加载这个 JSON 就能重演该局。

JSON schema（version 1）是播放器的 contract，改动它要同步改播放器：

    {
      "version": 1,
      "meta": {                      # 这一局的标识与背景
        "label": "v1_sparse",        # 哪个 reward 版本 / 实验
        "seed": 0,
        "policy": "ppo" | "random" | "heuristic",
        "score": 7,                  # 最终过管数
        "frames": 412,               # 总帧数
        "outcome": "crash" | "win"   # 撞死 / 过满上限算赢
      },
      "config": {                    # 物理常量（像素），播放器画布据此布局
        "width": 288, "height": 512, "bird_x": 72, "bird_radius": 12,
        "pipe_width": 52
      },
      "frames": [                    # 逐帧，每帧一个快照
        {
          "frame": 1,
          "bird_y": 250.5, "bird_vy": -10.5,
          "score": 0,
          "action": 1,               # 这一帧的动作：0=noop, 1=flap
          "pipes": [{"x": 288.0, "gap_top": 180.0, "gap_bottom": 340.0}, ...]
        },
        ...
      ]
    }
"""

from __future__ import annotations

import json
from pathlib import Path

from .game import FlappyBirdGame

SCHEMA_VERSION = 1


class EpisodeRecorder:
    """累积一局的逐帧快照，结束后写成一个 JSON 文件。

    用法：
        rec = EpisodeRecorder(game, label="v1_sparse", seed=0, policy="random")
        game.reset(seed=0)
        rec.start()
        while game.alive and game.score < MAX_SCORE:
            action = pick_action(...)
            game.step(flap=bool(action))
            rec.capture(action)
        rec.finish(outcome="crash").save("runs/v1_sparse/ep_0.json")
    """

    def __init__(
        self,
        game: FlappyBirdGame,
        *,
        label: str,
        seed: int,
        policy: str,
    ) -> None:
        self.game = game
        self.label = label
        self.seed = seed
        self.policy = policy
        self._frames: list[dict] = []
        self._outcome: str | None = None

    def start(self) -> None:
        """记录初始帧（reset 之后、第一次 step 之前的状态）。"""
        snap = self.game.frame_state()
        snap["action"] = 0
        self._frames.append(snap)

    def capture(self, action: int) -> None:
        """在一次 game.step(...) 之后调用，记录该帧及导致它的动作。"""
        snap = self.game.frame_state()
        snap["action"] = int(action)
        self._frames.append(snap)

    def finish(self, outcome: str) -> "EpisodeRecorder":
        """标记结局（"crash" 或 "win"）。返回 self 便于链式 save()。"""
        self._outcome = outcome
        return self

    def to_dict(self) -> dict:
        c = self.game.config
        return {
            "version": SCHEMA_VERSION,
            "meta": {
                "label": self.label,
                "seed": self.seed,
                "policy": self.policy,
                "score": self.game.score,
                "frames": len(self._frames),
                "outcome": self._outcome or ("win" if self.game.alive else "crash"),
            },
            "config": {
                "width": c.width,
                "height": c.height,
                "bird_x": c.bird_x,
                "bird_radius": c.bird_radius,
                "pipe_width": c.pipe_width,
            },
            "frames": self._frames,
        }

    def save(self, path: str | Path) -> Path:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self.to_dict()), encoding="utf-8")
        return path
