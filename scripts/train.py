"""训练一个 policy 来玩 Flappy Bird（默认 PPO，通过 Stable-Baselines3）。

以 headless、快于实时的方式运行——无窗口、无 sleep（见 docs/rfc.md 决策 2）。
尚未实现；脚手架占位符。

意图中的形态：
    from stable_baselines3 import PPO
    from flappy_rl.env import FlappyBirdEnv
    env = FlappyBirdEnv()
    model = PPO("MlpPolicy", env, verbose=1)
    model.learn(total_timesteps=500_000)
    model.save("models/flappy_ppo")
"""


def main() -> None:
    raise SystemExit(
        "train.py 是脚手架占位符。实现（以及 reward 设计）被推迟"
        "——见 docs/concepts.md 和 docs/working.md。"
    )


if __name__ == "__main__":
    main()
