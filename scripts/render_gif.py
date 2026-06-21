"""把一局回放 JSON 渲染成 GIF（用于 README，GitHub 能直接播放）。

画法与网页播放器 docs/player.js 保持一致：天蓝背景、绿色管道带缝隙、黄色小鸟、
顶部得分、拍翅那一帧描红圈。纯 PIL，不依赖浏览器。

用法：
    python scripts/render_gif.py docs/results/v1_sparse_ep0.json docs/assets/demo.gif --fps 30 --max-frames 600
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

SKY = (78, 192, 202)
PIPE = (90, 160, 44)
PIPE_EDGE = (63, 122, 30)
BIRD = (246, 211, 60)
BIRD_EDGE = (211, 158, 0)
FLAP_EDGE = (232, 118, 90)
TEXT = (255, 255, 255)


def render(episode: dict, scale: float = 1.0) -> list[Image.Image]:
    cfg = episode["config"]
    W, H = int(cfg["width"] * scale), int(cfg["height"] * scale)
    bx = cfg["bird_x"] * scale
    r = cfg["bird_radius"] * scale
    pw = cfg["pipe_width"] * scale

    try:
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", int(28 * scale))
    except Exception:
        font = ImageFont.load_default()

    frames = []
    for f in episode["frames"]:
        img = Image.new("RGB", (W, H), SKY)
        d = ImageDraw.Draw(img)
        for p in f["pipes"]:
            x = p["x"] * scale
            gt = p["gap_top"] * scale
            gb = p["gap_bottom"] * scale
            d.rectangle([x, 0, x + pw, gt], fill=PIPE, outline=PIPE_EDGE, width=2)
            d.rectangle([x, gb, x + pw, H], fill=PIPE, outline=PIPE_EDGE, width=2)
        by = f["bird_y"] * scale
        edge = FLAP_EDGE if f["action"] == 1 else BIRD_EDGE
        ew = 3 if f["action"] == 1 else 2
        d.ellipse([bx - r, by - r, bx + r, by + r], fill=BIRD, outline=edge, width=int(ew))
        score = str(f["score"])
        tb = d.textbbox((0, 0), score, font=font)
        d.text(((W - (tb[2] - tb[0])) / 2, 12 * scale), score, fill=TEXT, font=font)
        frames.append(img)
    return frames


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("episode_json")
    ap.add_argument("out_gif")
    ap.add_argument("--fps", type=int, default=30)
    ap.add_argument("--max-frames", type=int, default=600)
    ap.add_argument("--scale", type=float, default=1.0)
    ap.add_argument("--frame-step", type=int, default=2, help="每隔几帧取一帧（减小体积）")
    args = ap.parse_args()

    episode = json.loads(Path(args.episode_json).read_text(encoding="utf-8"))
    episode["frames"] = episode["frames"][: args.max_frames : args.frame_step]
    frames = render(episode, scale=args.scale)

    out = Path(args.out_gif)
    out.parent.mkdir(parents=True, exist_ok=True)
    # 抽帧后实际帧率 = fps / frame_step，duration 据此换算
    duration = int(1000 / (args.fps / args.frame_step))
    frames[0].save(
        out, save_all=True, append_images=frames[1:],
        duration=duration, loop=0, optimize=True,
    )
    size_kb = out.stat().st_size / 1024
    print(f"已生成 {out}：{len(frames)} 帧，{size_kb:.0f} KB")


if __name__ == "__main__":
    main()
