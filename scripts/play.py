"""加载一个训练好的 policy 并游玩若干 episode；可选地渲染一个实时窗口。

使用与训练*相同*的同步循环，但在传入 --render 时 sleep 到约 30 FPS 并绘制
（见 docs/rfc.md 决策 2）。每个 episode 报告 task metric（过管数）。观看渲染的
episode 是发现 reward hacking 的调试工具（docs/test.md）。

尚未实现；脚手架占位符。
"""


def main() -> None:
    raise SystemExit(
        "play.py 是脚手架占位符。实现被推迟——见 docs/working.md。"
    )


if __name__ == "__main__":
    main()
