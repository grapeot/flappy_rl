"""训练过程指标记录 —— 把 reward 和 task metric 分开记，这样 reward hacking 可见。

核心理念（见 docs/concepts.md）：reward 是被优化的东西，task metric（过管数）是我们
真正想要的东西。两者分开记录，才能看出"reward 涨但过管数不涨"这种 reward hacking 的
signature。本模块提供一个 SB3 callback，按 episode 累计两者并周期性落盘成 JSON。
"""

from __future__ import annotations

import json
from pathlib import Path

from stable_baselines3.common.callbacks import BaseCallback


class EpisodeMetricsCallback(BaseCallback):
    """逐 episode 记录 reward 总和与最终 score（过管数），周期性写盘。

    产出 JSON（供网页画曲线）：
        {
          "label": "v1_sparse",
          "episodes": [
            {"t": 1234, "ep": 1, "reward": -1.0, "score": 0, "length": 27},
            ...
          ]
        }
    其中 t 是该 episode 结束时的累计 timestep，便于把曲线画在 timestep 轴上。
    """

    def __init__(self, label: str, out_path: str | Path, flush_every: int = 50):
        super().__init__()
        self.label = label
        self.out_path = Path(out_path)
        self.flush_every = flush_every
        self.episodes: list[dict] = []
        self._ep_count = 0

    def _on_step(self) -> bool:
        # SB3 在 info["episode"] 里给出每个结束 episode 的 r/l（由 Monitor 包装提供）
        for info in self.locals.get("infos", []):
            ep = info.get("episode")
            if ep is None:
                continue
            self._ep_count += 1
            self.episodes.append(
                {
                    "t": int(self.num_timesteps),
                    "ep": self._ep_count,
                    "reward": round(float(ep["r"]), 3),
                    "score": int(info.get("score", 0)),  # 最终过管数 = task metric
                    "length": int(ep["l"]),
                }
            )
            if self._ep_count % self.flush_every == 0:
                self.flush()
        return True

    def flush(self) -> None:
        self.out_path.parent.mkdir(parents=True, exist_ok=True)
        self.out_path.write_text(
            json.dumps({"label": self.label, "episodes": self.episodes}),
            encoding="utf-8",
        )

    def _on_training_end(self) -> None:
        self.flush()
