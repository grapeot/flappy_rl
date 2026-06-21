# AGENTS.md — flappy_rl

本项目工作的本地规则。

## 这个项目是什么

一个用于理解 reinforcement learning 的学习载体，做法是教一台计算机玩一个自己编写的
Flappy Bird。优先级是概念清晰和工程整洁，**而非** benchmark 分数，**也非**手写
算法。算法部分我们使用 Stable-Baselines3。在动 reward 代码之前，先读
`docs/concepts.md` 以建立概念框架。

## 结构

- `src/flappy_rl/` —— 这个包：`game.py`（第 1 层 physics）、`env.py`（第 2 层 Gymnasium
  封装 + reward + 可选的 render），以及任何共享的 helper。
- `scripts/` —— 用户入口：`train.py`、`play.py`。这些是稳定的命令；不要把运行逻辑
  只埋在文档里。
- `tests/` —— pytest，按层组织（参见 `docs/test.md`）。
- `docs/` —— `prd.md`、`rfc.md`、`concepts.md`、`test.md`、`working.md`。

## 三层规则

让各层保持解耦：

1. `game.py` 对 RL 或渲染一无所知。
2. `env.py` 拥有 observation、action space、reward 和 `render()`。
3. `scripts/` 拥有算法调用。

Reward 的改动只属于第 2 层。不要把 reward 逻辑泄漏进 physics。

## Reward 是有意推迟的

reward 函数是有意留给一次设计讨论的。在实现它时，遵循 `docs/concepts.md` 中的
陷阱清单：在可容忍的范围内尽可能直接地 reward 真实目标，让量级保持诚实，把 task metric
与 reward 分开记录，并观看渲染的 episode。把第一版 reward 当作一个有待证伪的假设。

## 环境

- Python 3.11+，`uv` + 本地 `.venv`。用 `uv pip install -e '.[dev]'` 安装。
- 使用 `uv pip install`，绝不使用裸的 `pip install`。

## 工作纪律

- 在每一个有意义的步骤更新 `docs/working.md`（Changelog + Lessons Learned）。
- 频繁提交，并按连贯的切片提交（scaffold / implementation / validation），而不是一个
  巨大的 commit。
- 训练会写入 `runs/`、`checkpoints/`、`logs/`、`models/` —— 全部 gitignored。不要
  commit model 二进制文件或视频。
- 验证不仅仅是测试变绿：对于任何真实训练运行，报告 eval task metric 并且观看至少一个
  渲染的 episode（参见 `docs/test.md`）。

## 可发布性

本仓库被构建为可发布的。没有 secret，没有个人数据，没有私有路径。让
`.env.example` 的占位符保持假值。
