"""Train a policy to play Flappy Bird (PPO by default, via Stable-Baselines3).

Runs headless and faster-than-real-time — no window, no sleeping (see docs/rfc.md
Decision 2). NOT YET IMPLEMENTED; scaffold placeholder.

Intended shape:
    from stable_baselines3 import PPO
    from flappy_rl.env import FlappyBirdEnv
    env = FlappyBirdEnv()
    model = PPO("MlpPolicy", env, verbose=1)
    model.learn(total_timesteps=500_000)
    model.save("models/flappy_ppo")
"""


def main() -> None:
    raise SystemExit(
        "train.py is a scaffold placeholder. Implementation (and reward design) is deferred "
        "— see docs/concepts.md and docs/working.md."
    )


if __name__ == "__main__":
    main()
