# 工作日志

## Changelog

### 2026-06-20

- 搭好项目脚手架：`docs/`、`src/flappy_rl/`、`scripts/`、`tests/`、`AGENTS.md`、
  `.gitignore`、`.env.example`、`pyproject.toml`、`README.md`。
- 写好文档集：`prd.md`（目标 + 成功标准）、`rfc.md`（架构与四个关键决策）、
  `concepts.md`（RL 入门 + reward 设计 / reward hacking 清单）、`test.md`（每一层
  "已验证"的含义）。
- 记录核心设计决策：内部状态的 Gymnasium env（而非窗口操控）、同步 fixed-timestep
  循环（而非异步实时）、三个解耦的层、默认走 Stable-Baselines3 的 PPO。
- 刻意把 reward 函数和实现留空——reward 设计是下一场讨论的内容，本就如此安排。
- 把项目工作语言定为中文，并把已有的全部文档（concepts/prd/rfc/test/README/AGENTS/
  working）和源码注释从英文改写为中文。技术术语（RL、policy、reward、PPO、DQN、
  Gymnasium 等）保留英文。
- 一轮聊天敲定全部设计决策，存档进 `docs/decisions.md`：observation 用相对坐标看一根
  管道；两个 reward baseline（版本一真 sparse `0/+1/-1`、版本二 dy 垂直距离 shaping），
  版本三考虑重力的思路只记不实现；episode 撞/出界终止、过 50 管 truncate；γ=0.99、起手
  3-5M timesteps。新增决策：回放走 JSON artifact + 网页 Canvas 播放器，GitHub Pages 从
  `docs/` 发布（rfc.md 决策 6/7）。
- 实现物理内核 `game.py`（Layer 1）：重力/拍翅/管道/碰撞/计分，全确定性，参数为命名
  常量。配 12 个单元测试（`tests/test_game.py`），全绿。删掉过时的 `test_scaffold.py`
  （game 已实现，不再是占位符）。
- 物理手感验证：随机策略约 27 帧死、得分 0（瞎拍的鸟过不了第一根管——印证 sparse 之痛）；
  "对准缝隙中心"启发式 seed0 过 20 管、撑 924 帧（游戏可解，RL 有东西可学）。难度合适。

## Lessons Learned

- 最初的设想（"一个游戏窗口 + 一套 programmatic 控制接口"）对于在自己编写的游戏上
  做 RL 是错误的路线：它逼着你走 pixels + 输入注入，那是最难的设定。因为游戏是我们
  自己的，正确的接口是对内部数值 state 做 `reset()`/`step()`。不要再把窗口操控这一层
  加回来。
- "实时 vs 回合制"是伪二分。这个循环是同步 fixed-timestep 的；游戏在两次 `step()`
  之间是冻结的，所以 agent 永远不会和时钟赛跑。实时只属于渲染层，opt-in 且解耦。
- reward 就是整份规格说明。把 task metric（过管数）与 reward 分开记录，这样 reward
  hacking 会以背离的形式显现出来，而不是藏在一条好看的 reward 曲线里。观看渲染的
  episode 是调试工具，不是演示。
- 项目工作语言为中文。后续所有文档、注释、commit message 默认用中文；技术术语和代码
  标识符保留英文。
