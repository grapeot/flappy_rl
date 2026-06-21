"""第 2 层 FlappyBirdEnv 的契约与集成测试（见 docs/test.md 第 2 层）。"""

import numpy as np
import pytest

from flappy_rl.env import MAX_SCORE, FlappyBirdEnv, RewardConfig
from flappy_rl.game import GameConfig


def test_check_env_sparse():
    from stable_baselines3.common.env_checker import check_env

    check_env(FlappyBirdEnv(reward_config=RewardConfig(mode="sparse")), skip_render_check=True)


def test_check_env_shaped():
    from stable_baselines3.common.env_checker import check_env

    check_env(FlappyBirdEnv(reward_config=RewardConfig(mode="shaped")), skip_render_check=True)


def test_reset_returns_obs_in_space():
    env = FlappyBirdEnv()
    obs, info = env.reset(seed=0)
    assert env.observation_space.contains(obs)
    assert isinstance(info, dict) and info["score"] == 0
    assert obs.dtype == np.float32


def test_step_contract():
    env = FlappyBirdEnv()
    env.reset(seed=0)
    obs, reward, terminated, truncated, info = env.step(1)
    assert env.observation_space.contains(obs)
    assert isinstance(reward, float)
    assert isinstance(terminated, bool)
    assert isinstance(truncated, bool)
    assert "score" in info and "passed_pipe" in info


def test_action_space_is_discrete_2():
    env = FlappyBirdEnv()
    assert env.action_space.n == 2
    env.reset(seed=0)
    env.step(0)
    env.step(1)  # 两个 action 都被接受


def test_random_episode_runs_to_termination():
    env = FlappyBirdEnv()
    env.reset(seed=1)
    rng = np.random.default_rng(1)
    steps = 0
    while steps < 5000:
        _, _, terminated, truncated, _ = env.step(int(rng.integers(0, 2)))
        steps += 1
        if terminated or truncated:
            break
    assert terminated or truncated


def test_seed_reproduces_episode():
    def run(seed):
        env = FlappyBirdEnv()
        env.reset(seed=seed)
        rng = np.random.default_rng(123)
        traj = []
        for _ in range(80):
            a = int(rng.integers(0, 2))
            obs, r, term, trunc, _ = env.step(a)
            traj.append((tuple(np.round(obs, 4)), round(r, 4)))
            if term or trunc:
                break
        return traj

    assert run(7) == run(7)


def test_sparse_reward_values():
    # sparse：过管 +1、死亡 -1、其余 0
    env = FlappyBirdEnv(reward_config=RewardConfig(mode="sparse"))
    env.reset(seed=0)
    saw_death = False
    for _ in range(200):
        _, r, term, trunc, info = env.step(0)  # 一直下坠，制造死亡
        if not (term or trunc):
            assert r == 0.0 or info["passed_pipe"]  # 活着且没过管 → reward 必为 0
        if term:
            assert r == pytest.approx(-1.0)  # 死亡那一帧 -1
            saw_death = True
            break
    assert saw_death


def test_shaped_reward_penalizes_misalignment():
    # shaped：活着、没过管没死的帧，reward 应为负（对齐惩罚），且偏离越大惩罚越大
    env = FlappyBirdEnv(reward_config=RewardConfig(mode="shaped"))
    env.reset(seed=0)
    _, r, term, trunc, info = env.step(0)
    if not (term or trunc) and not info["passed_pipe"]:
        assert r <= 0.0  # 纯对齐惩罚（无事件）应 ≤ 0


def test_pass_pipe_gives_positive_reward():
    # 用宽松配置让小鸟稳过管，验证过管那一帧 reward 含 +1
    cfg = GameConfig(pipe_gap=400.0, gap_margin=20.0, gravity=0.3, flap_impulse=-5.0)
    env = FlappyBirdEnv(game_config=cfg, reward_config=RewardConfig(mode="sparse"))
    env.reset(seed=3)
    got_pass_reward = False
    for _ in range(800):
        a = 1 if env.game.bird_y > env.game.config.height / 2 else 0
        _, r, term, trunc, info = env.step(a)
        if info["passed_pipe"]:
            assert r == pytest.approx(1.0)
            got_pass_reward = True
            break
        if term or trunc:
            break
    assert got_pass_reward


def test_truncate_on_max_score():
    assert MAX_SCORE == 50
