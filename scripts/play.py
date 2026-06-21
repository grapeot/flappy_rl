"""Load a trained policy and play episodes; optionally render a real-time window.

Uses the SAME synchronous loop as training, but sleeps to ~30 FPS and draws when --render
is passed (see docs/rfc.md Decision 2). Reports the task metric (pipes cleared) per episode.
Watching rendered episodes is a debugging tool for spotting reward hacking (docs/test.md).

NOT YET IMPLEMENTED; scaffold placeholder.
"""


def main() -> None:
    raise SystemExit(
        "play.py is a scaffold placeholder. Implementation is deferred — see docs/working.md."
    )


if __name__ == "__main__":
    main()
