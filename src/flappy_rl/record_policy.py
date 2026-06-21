"""用训练好的 policy 玩一局并录成回放 JSON。

复用 EpisodeRecorder（recorder.py）。注意：policy 接收的是 env 的归一化 observation，
但回放录的是 game 的原始物理状态——两者来自同一个 game 实例，天然一致。
"""

from __future__ import annotations

from pathlib import Path

from .env import MAX_SCORE, FlappyBirdEnv, RewardConfig
from .recorder import EpisodeRecorder


def record_policy_episode(
    model,
    *,
    reward_mode: str,
    seed: int,
    label: str,
    out_path: str | Path,
    deterministic: bool = True,
) -> dict:
    """让 model 在指定 seed 上玩一局，录成回放 JSON。返回 meta 摘要。"""
    env = FlappyBirdEnv(reward_config=RewardConfig(mode=reward_mode))
    obs, _ = env.reset(seed=seed)
    game = env.game

    rec = EpisodeRecorder(game, label=label, seed=seed, policy="ppo")
    rec.start()

    outcome = "crash"
    while True:
        action, _ = model.predict(obs, deterministic=deterministic)
        action = int(action)
        obs, _, terminated, truncated, _ = env.step(action)
        rec.capture(action)
        if game.score >= MAX_SCORE:
            outcome = "win"
            break
        if terminated or truncated:
            outcome = "win" if truncated else "crash"
            break

    rec.finish(outcome=outcome).save(out_path)
    return {"score": game.score, "frames": game.frame, "outcome": outcome}
