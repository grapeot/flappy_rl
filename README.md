# flappy_rl

一个小巧、易读的项目，通过教计算机玩 Flappy Bird 来**理解 reinforcement learning（强化学习）**。
这里的目标不是手写算法 —— 那部分我们依靠成熟的库。目标是理解
*RL 在实践中落地的概念与工程*：policy 是什么、训练循环如何成形、如何设计
reward，以及如何避免 reward hacking。

如果你想要一次概念性的导览，请按以下顺序阅读文档：

1. [`docs/prd.md`](docs/prd.md) —— 我们在构建什么、为什么构建；成功标准。
2. [`docs/rfc.md`](docs/rfc.md) —— 架构与关键设计决策，包括
   *为什么这是一个同步的固定 timestep 循环，而不是"控制一个真实窗口"*。
3. [`docs/concepts.md`](docs/concepts.md) —— RL 入门：policy、value、循环、DQN 与
   PPO，以及 **reward 设计 + reward hacking**（你真正为之而来的那部分）。
4. [`docs/test.md`](docs/test.md) —— 每一层的"已验证"意味着什么。

`docs/working.md` 文件是持续的 changelog 和经验教训记录。

## 一段话设计

Flappy Bird 是现存最友好的 RL 问题之一：两个动作（flap / 不 flap）、
一个用少数几个数字就能描述的 state（bird 高度、垂直速度、下一个 pipe 的 gap），
以及一个清晰的进展概念（活着、过 pipe）。我们把游戏写成一个
普通的 Python 对象，用标准的 [Gymnasium](https://gymnasium.farama.org/) `Env`
接口（`reset()` / `step()`）包装它，并让 [Stable-Baselines3](https://stable-baselines3.readthedocs.io/)
负责学习。渲染窗口是一条可选的、仅供人观看的旁路，与训练完全
解耦 —— 训练期间没有窗口，也没有实时时钟。

## 状态

脚手架 + 文档阶段。reward 函数被刻意**留给后续
讨论** —— 把它设计好是这个项目最有意思的部分，而
[`docs/concepts.md`](docs/concepts.md) 铺设了我们将一起决定的那些取舍。

## 隐私

本仓库被设计为可发布的，且只含假示例。它不包含任何
密钥、个人数据或私有路径。`.env.example` 用一个占位密钥记录了一个
可选的实验追踪（experiment-tracking）集成。

## 快速开始（实现之后）

```bash
# 用 uv 创建环境
uv venv .venv && source .venv/bin/activate
uv pip install -e '.[dev]'

# 训练
python scripts/train.py

# 观看训练好的小鸟游玩（会打开一个窗口）
python scripts/play.py --render
```
