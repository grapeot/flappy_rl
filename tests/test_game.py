"""第 1 层物理内核 FlappyBirdGame 的单元测试。

覆盖 docs/test.md 第 1 层要求：重力、拍翅、管道移动、碰撞时机、计分、确定性。
"""

import pytest

from flappy_rl.game import FlappyBirdGame, GameConfig


@pytest.fixture
def game():
    g = FlappyBirdGame()
    g.reset(seed=0)
    return g


def test_reset_alive_and_centered(game):
    assert game.alive
    assert game.score == 0
    assert game.frame == 0
    assert game.bird_y == pytest.approx(game.config.height / 2.0)
    assert len(game.pipes) >= 3


def test_gravity_pulls_down_without_flap(game):
    y0 = game.bird_y
    game.step(flap=False)
    assert game.bird_vy > 0          # 向下（y 向下为正）
    assert game.bird_y > y0          # 高度数值变大 = 往下掉
    # 连续不拍，下落速度单调增大直至封顶
    prev_vy = game.bird_vy
    for _ in range(5):
        game.step(flap=False)
        assert game.bird_vy >= prev_vy
        prev_vy = game.bird_vy


def test_flap_sets_upward_velocity(game):
    for _ in range(3):
        game.step(flap=False)       # 先让它有个向下速度
    assert game.bird_vy > 0
    game.step(flap=True)
    assert game.bird_vy == pytest.approx(game.config.flap_impulse)
    assert game.bird_vy < 0          # 向上


def test_fall_speed_is_capped(game):
    for _ in range(100):
        game.step(flap=False)
        if not game.alive:
            break
    # 即便撞了，撞之前任何一帧 vy 都不应超过封顶
    assert game.bird_vy <= game.config.max_fall_speed + 1e-9


def test_pipes_move_left(game):
    x0 = game.pipes[0].x
    game.step(flap=True)
    assert game.pipes[0].x == pytest.approx(x0 - game.config.pipe_speed)


def test_hits_ceiling_dies():
    g = FlappyBirdGame()
    g.reset(seed=1)
    # 一直拍翅膀冲顶，最终撞顶死亡
    died_flag_on_death_frame = False
    for _ in range(200):
        g.step(flap=True)
        if not g.alive:
            died_flag_on_death_frame = g.just_died  # 死亡那一帧 just_died 应为 True
            break
    assert not g.alive
    assert died_flag_on_death_frame
    # 死亡后再 step 是 no-op，且 just_died 复位
    frame_before = g.frame
    g.step(flap=True)
    assert g.frame == frame_before
    assert g.just_died is False


def test_hits_floor_dies():
    g = FlappyBirdGame()
    g.reset(seed=2)
    for _ in range(500):
        g.step(flap=False)          # 一直下落
        if not g.alive:
            break
    assert not g.alive


def test_scoring_fires_once_per_pipe():
    # 用一个宽缝、慢速的配置，让小鸟能稳过几根管道
    cfg = GameConfig(pipe_gap=400.0, gap_margin=20.0, gravity=0.3, flap_impulse=-5.0)
    g = FlappyBirdGame(cfg)
    g.reset(seed=3)
    score_events = 0
    # 简单悬浮策略：低于中线就拍，制造大致水平的飞行
    for _ in range(600):
        flap = g.bird_y > cfg.height / 2
        g.step(flap=flap)
        if g.just_scored:
            score_events += 1
        if not g.alive:
            break
    # score 属性应与 just_scored 事件次数一致
    assert g.score == score_events
    assert g.score >= 1             # 这套宽松配置至少能过一根


def test_determinism_same_seed_same_trajectory():
    def run(seed):
        g = FlappyBirdGame()
        g.reset(seed=seed)
        traj = []
        for i in range(120):
            g.step(flap=(i % 7 == 0))
            traj.append((g.bird_y, g.bird_vy, g.score, g.alive))
        return traj

    assert run(42) == run(42)
    # 注意：小鸟在碰到管道前的运动不依赖 seed，所以短窗口轨迹可能相同。
    # 真正受 seed 控制的是管道缝隙位置——用它来验证不同 seed 确实产生不同世界。
    def gaps(seed):
        g = FlappyBirdGame()
        g.reset(seed=seed)
        return [(round(p.gap_top, 3)) for p in g.pipes]

    assert gaps(42) == gaps(42)
    assert gaps(42) != gaps(7)


def test_next_pipe_is_ahead():
    g = FlappyBirdGame()
    g.reset(seed=5)
    g.step(flap=False)
    p = g.next_pipe()
    # 下一根管道的右沿应在小鸟前方或正对
    assert (p.x + g.config.pipe_width) >= g.config.bird_x


def test_observation_values_keys(game):
    vals = game.observation_values()
    for k in ("bird_y", "bird_vy", "next_pipe_dx", "gap_top", "gap_bottom", "gap_center"):
        assert k in vals
        assert isinstance(vals[k], float)


def test_frame_state_serializable(game):
    import json

    game.step(flap=True)
    snap = game.frame_state()
    json.dumps(snap)                # 不抛异常即为可序列化
    assert "bird_y" in snap and "pipes" in snap
    assert isinstance(snap["pipes"], list)
