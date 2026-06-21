"""训练管线的 smoke test（docs/test.md 第 3 层）。

不验证"学会了"（那慢且随机），只验证整条训练管线端到端能跑：PPO 在真实 env 上训练
极少步数、产出可保存可加载的模型、并能用它录一局回放。这能在 CI 里低成本捕捉集成破损。
"""

from stable_baselines3 import PPO
from stable_baselines3.common.monitor import Monitor

from flappy_rl.env import FlappyBirdEnv, RewardConfig
from flappy_rl.metrics import EpisodeMetricsCallback
from flappy_rl.record_policy import record_policy_episode


def test_ppo_trains_saves_loads_and_records(tmp_path):
    env = Monitor(
        FlappyBirdEnv(reward_config=RewardConfig(mode="sparse")),
        info_keywords=("score",),
    )
    model = PPO("MlpPolicy", env, seed=0, gamma=0.99, n_steps=256, batch_size=64, verbose=0)

    cb = EpisodeMetricsCallback(label="smoke", out_path=tmp_path / "metrics.json")
    model.learn(total_timesteps=1024, callback=cb)

    # 模型可保存可加载
    model.save(tmp_path / "model")
    loaded = PPO.load(tmp_path / "model")

    # metrics 落盘且结构正确
    cb.flush()
    assert (tmp_path / "metrics.json").exists()

    # 能用训练好的 model 录一局回放
    info = record_policy_episode(
        loaded, reward_mode="sparse", seed=0, label="smoke",
        out_path=tmp_path / "ep.json",
    )
    assert (tmp_path / "ep.json").exists()
    assert "score" in info and "outcome" in info


def test_metrics_callback_records_episodes(tmp_path):
    env = Monitor(FlappyBirdEnv(), info_keywords=("score",))
    model = PPO("MlpPolicy", env, seed=1, n_steps=256, batch_size=64, verbose=0)
    cb = EpisodeMetricsCallback(label="m", out_path=tmp_path / "m.json", flush_every=1)
    # 随机短 env 的 episode 很短（约 25 帧），1024 步内必然结束多个 episode
    model.learn(total_timesteps=1024, callback=cb)
    assert len(cb.episodes) >= 1
    for e in cb.episodes:
        for k in ("t", "ep", "reward", "score", "length"):
            assert k in e
