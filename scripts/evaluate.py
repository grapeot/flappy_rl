"""泛化评估 —— 在一批没训练过的 seed 上跑训练好的 policy，看它是否真学会玩。

RL 的一个常见陷阱：policy 可能只是记住了训练时遇到的特定管道序列，换个 seed 就崩。
本脚本在一批全新 seed 上评估，报告过管数分布，判断泛化能力。

用法：
    python scripts/evaluate.py --label v1_sparse --reward sparse --episodes 30
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from stable_baselines3 import PPO  # noqa: E402

from flappy_rl.env import MAX_SCORE, FlappyBirdEnv, RewardConfig  # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--label", required=True)
    ap.add_argument("--reward", required=True, choices=["sparse", "shaped"])
    ap.add_argument("--episodes", type=int, default=30)
    ap.add_argument("--seed-base", type=int, default=10_000, help="评估 seed 起点，远离训练用的小 seed")
    args = ap.parse_args()

    model = PPO.load(f"runs/{args.label}/model")
    env = FlappyBirdEnv(reward_config=RewardConfig(mode=args.reward))

    scores = []
    wins = 0
    for i in range(args.episodes):
        seed = args.seed_base + i  # 全新 seed，训练时没见过
        obs, _ = env.reset(seed=seed)
        while True:
            action, _ = model.predict(obs, deterministic=True)
            obs, _, terminated, truncated, _ = env.step(int(action))
            if env.game.score >= MAX_SCORE:
                truncated = True
            if terminated or truncated:
                break
        scores.append(env.game.score)
        if env.game.score >= MAX_SCORE:
            wins += 1

    summary = {
        "label": args.label,
        "episodes": args.episodes,
        "seed_range": [args.seed_base, args.seed_base + args.episodes - 1],
        "mean": round(statistics.mean(scores), 2),
        "median": statistics.median(scores),
        "min": min(scores),
        "max": max(scores),
        "win_rate": round(wins / args.episodes, 3),  # 打满 50 管的比例
        "scores": scores,
    }
    out = Path(f"runs/{args.label}/generalization.json")
    out.write_text(json.dumps(summary), encoding="utf-8")
    print(f"=== {args.label} 泛化评估（{args.episodes} 个全新 seed）===")
    print(f"  过管数 mean={summary['mean']} median={summary['median']} "
          f"min={summary['min']} max={summary['max']}")
    print(f"  打满率(win_rate)={summary['win_rate']}")
    print(f"  写入 {out}")


if __name__ == "__main__":
    main()
