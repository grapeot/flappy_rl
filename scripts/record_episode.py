"""录一局 JSON 回放 artifact —— 在训练前打通"录制→JSON→网页播放"链路。

支持三种无需训练的策略，用于验证整条管线：
    random    : 每帧以 50% 概率拍翅（瞎拍，通常过不了首管）
    heuristic : 低于下一根缝隙中心就拍（简单可解策略，能过不少管）
    still     : 从不拍（直接下坠，最短回放）

用法：
    python scripts/record_episode.py --policy heuristic --seed 0 --out docs/sample_episode.json
"""

from __future__ import annotations

import argparse
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from flappy_rl.game import FlappyBirdGame  # noqa: E402
from flappy_rl.recorder import EpisodeRecorder  # noqa: E402

MAX_SCORE = 50  # 与决策三一致：过满 50 管 truncate 算赢


def pick_action(policy: str, game: FlappyBirdGame, rng: random.Random) -> int:
    if policy == "random":
        return 1 if rng.random() < 0.5 else 0
    if policy == "still":
        return 0
    if policy == "heuristic":
        vals = game.observation_values()
        return 1 if game.bird_y > vals["gap_center"] else 0
    raise ValueError(f"未知策略: {policy}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--policy", default="heuristic", choices=["random", "heuristic", "still"])
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", default="docs/sample_episode.json")
    args = ap.parse_args()

    game = FlappyBirdGame()
    game.reset(seed=args.seed)
    rng = random.Random(args.seed)
    rec = EpisodeRecorder(game, label=f"{args.policy}_demo", seed=args.seed, policy=args.policy)
    rec.start()

    outcome = "crash"
    while game.alive:
        action = pick_action(args.policy, game, rng)
        game.step(flap=bool(action))
        rec.capture(action)
        if game.score >= MAX_SCORE:
            outcome = "win"
            break

    saved = rec.finish(outcome=outcome).save(args.out)
    print(f"已录制 {args.policy} 策略 seed={args.seed}: "
          f"得分={game.score} 帧数={game.frame} 结局={outcome}")
    print(f"写入 {saved}")


if __name__ == "__main__":
    main()
