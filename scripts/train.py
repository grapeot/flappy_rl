"""训练一个 PPO policy 玩 Flappy Bird，记录指标曲线，并录几局回放。

以 headless、快于实时的方式训练（无窗口、无 sleep）。训练时把 reward 与 task metric
（过管数）分开记录，便于事后看 reward hacking（见 docs/concepts.md）。

用法：
    python scripts/train.py --reward sparse  --timesteps 3000000 --label v1_sparse
    python scripts/train.py --reward shaped  --timesteps 3000000 --label v2_shaped

产出（runs/<label>/，已 gitignore）：
    model.zip            训练好的 policy
    metrics.json         逐 episode 的 reward / score 曲线
    ep_seed*.json        几局回放 artifact（最终拷到 docs/ 供网页展示）
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from stable_baselines3 import PPO  # noqa: E402
from stable_baselines3.common.monitor import Monitor  # noqa: E402

from flappy_rl.env import FlappyBirdEnv, RewardConfig  # noqa: E402
from flappy_rl.metrics import EpisodeMetricsCallback  # noqa: E402
from flappy_rl.record_policy import record_policy_episode  # noqa: E402


def make_env(reward_mode: str) -> Monitor:
    # Monitor 包装让 info["episode"] 带上 r/l；再把 env 的 score 透传给 callback。
    env = FlappyBirdEnv(reward_config=RewardConfig(mode=reward_mode))
    return Monitor(env, info_keywords=("score",))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--reward", required=True, choices=["sparse", "shaped"])
    ap.add_argument("--timesteps", type=int, default=3_000_000)
    ap.add_argument("--label", required=True, help="实验标签，如 v1_sparse")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--record-seeds", type=int, nargs="*", default=[0, 1, 2])
    args = ap.parse_args()

    out_dir = Path("runs") / args.label
    out_dir.mkdir(parents=True, exist_ok=True)

    env = make_env(args.reward)
    model = PPO("MlpPolicy", env, verbose=1, seed=args.seed, gamma=0.99)

    cb = EpisodeMetricsCallback(label=args.label, out_path=out_dir / "metrics.json")
    print(f"开始训练 {args.label}（reward={args.reward}, timesteps={args.timesteps:,}）")
    model.learn(total_timesteps=args.timesteps, callback=cb, progress_bar=False)

    model.save(out_dir / "model")
    print(f"模型已保存到 {out_dir / 'model.zip'}")

    # 用训练好的 policy 录几局回放
    for s in args.record_seeds:
        info = record_policy_episode(
            model, reward_mode=args.reward, seed=s,
            label=args.label, out_path=out_dir / f"ep_seed{s}.json",
        )
        print(f"  录制 seed={s}: 得分={info['score']} 帧={info['frames']} 结局={info['outcome']}")

    print(f"完成。指标曲线：{out_dir / 'metrics.json'}")


if __name__ == "__main__":
    main()
