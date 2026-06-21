"""录制器与 JSON schema 的测试。

JSON schema（recorder.py version 1）是网页播放器 docs/player.js 的 contract，这些测试把
schema 的形状钉住——schema 一旦改动而这些测试没同步更新，说明播放器可能已经对不上。
"""

import json

from flappy_rl.game import FlappyBirdGame
from flappy_rl.recorder import SCHEMA_VERSION, EpisodeRecorder


def _play_episode(policy="still", seed=0, max_frames=100):
    game = FlappyBirdGame()
    game.reset(seed=seed)
    rec = EpisodeRecorder(game, label="test", seed=seed, policy=policy)
    rec.start()
    while game.alive and game.frame < max_frames:
        flap = policy == "heuristic" and game.bird_y > game.config.height / 2
        game.step(flap=flap)
        rec.capture(1 if flap else 0)
    return game, rec


def test_recorded_dict_has_required_schema():
    game, rec = _play_episode()
    rec.finish(outcome="crash")
    d = rec.to_dict()

    assert d["version"] == SCHEMA_VERSION
    # meta 必含字段（播放器 HUD 依赖）
    for k in ("label", "seed", "policy", "score", "frames", "outcome"):
        assert k in d["meta"], f"meta 缺字段 {k}"
    # config 必含字段（播放器布局依赖）
    for k in ("width", "height", "bird_x", "bird_radius", "pipe_width"):
        assert k in d["config"], f"config 缺字段 {k}"
    # 每帧必含字段（播放器逐帧绘制依赖）
    assert len(d["frames"]) >= 1
    for f in d["frames"]:
        for k in ("frame", "bird_y", "bird_vy", "score", "action", "pipes"):
            assert k in f, f"frame 缺字段 {k}"
        for p in f["pipes"]:
            for k in ("x", "gap_top", "gap_bottom"):
                assert k in p, f"pipe 缺字段 {k}"


def test_frames_count_matches_meta():
    game, rec = _play_episode()
    d = rec.finish(outcome="crash").to_dict()
    assert d["meta"]["frames"] == len(d["frames"])


def test_action_is_recorded_per_frame():
    game, rec = _play_episode(policy="heuristic", seed=2)
    d = rec.finish(outcome="crash").to_dict()
    actions = {f["action"] for f in d["frames"]}
    assert actions <= {0, 1}  # action 只能是 0/1


def test_save_writes_valid_json(tmp_path):
    game, rec = _play_episode()
    path = rec.finish(outcome="crash").save(tmp_path / "sub" / "ep.json")
    assert path.exists()
    loaded = json.loads(path.read_text(encoding="utf-8"))
    assert loaded["version"] == SCHEMA_VERSION
    assert isinstance(loaded["frames"], list)


def test_outcome_defaults_to_crash_when_dead():
    game = FlappyBirdGame()
    game.reset(seed=0)
    rec = EpisodeRecorder(game, label="t", seed=0, policy="still")
    rec.start()
    while game.alive:
        game.step(flap=False)  # 直接坠落致死
        rec.capture(0)
    # 没显式 finish，to_dict 应根据 alive 推断为 crash
    d = rec.to_dict()
    assert d["meta"]["outcome"] == "crash"
