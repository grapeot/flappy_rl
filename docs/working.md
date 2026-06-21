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
- 实现 JSON 录制器 `recorder.py`（schema version 1，是网页播放器的 contract）和录制脚本
  `scripts/record_episode.py`（random/heuristic/still 三种无需训练的策略）。录了一局启发式
  回放存为 `docs/sample_episode.json`（925 帧 / 过 20 管 / 240KB）。
- 实现网页 Canvas 播放器 `docs/player.js` + GitHub Pages 首页骨架 `docs/index.html`
  （思路简介 + 可播放回放 + 训练结果占位区）。数据与播放解耦：一份固定播放器播任意
  episode JSON。
- 训练前打通整条"录制→JSON→网页播放"链路并用 playwright 截图视觉验证通过（第 301 帧
  得分 6、HUD/outcome 正确、无 console 报错、管道与小鸟渲染正确）。早期风险点排除，
  可安全进入训练阶段。
- 实现 Gymnasium env `env.py`（Layer 2）：5 维相对坐标 observation、Discrete(2)、
  terminate（撞/出界）+ truncate（过 50 管）、两版 reward 由 `RewardConfig.mode` 切换。
  装好 gymnasium 1.3 / SB3 2.9 / torch 2.12。配 `tests/test_env.py`（含 SB3 check_env
  对两版均通过、reward 值语义断言），全部测试 23 个全绿，ruff lint 通过。
- 实现训练（`scripts/train.py` + `metrics.py` + `record_policy.py`）和泛化评估
  （`scripts/evaluate.py`）。两版各训练 50 万步（PPO, γ=0.99）。
- 训练结果（印证文档核心论点）：v1_sparse 首次打满 50 在 55,312 步、末50局平均 49.5；
  v2_shaped 首次打满在 42,511 步、末50局平均 50.0。**shaped 学得更早更稳**，正是 sparse
  vs shaped 张力的真实体现。两版 reward 与 task metric 同步上升，无 reward hacking。
- 泛化测试（30 个全新 seed）：v1_sparse 打满率 100%，v2_shaped 96.7%。两版都真学会玩
  （非记忆关卡），验证相对坐标 observation。有趣反转：sparse 泛化反略胜 shaped——shaped
  的对齐项是代理目标，把策略轻微拉离"纯过管"。
- 网页填充：`docs/index.html` 整合两版可切换回放、训练曲线（`curves.js`，reward+score
  双线）、泛化表。playwright（networkidle 等待）截图视觉验证全部正确。删除不再引用的
  `sample_episode.json`。

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
- 回放管线先于训练打通。JSON schema（recorder.py version 1）是 `docs/player.js` 的
  contract，改 schema 必须同步改播放器。`docs/sample_episode.json` 是进 git 的示例数据，
  别被 `.gitignore` 的 `runs/` 规则误伤——示例放 `docs/` 下。
- 本地 `file://` 直接打开 index.html 会因浏览器 CORS 拦截 fetch 而加载不出回放；必须用
  `python -m http.server` 起本地服务访问。GitHub Pages 上无此问题。
- env.py 的两版 reward 由 `RewardConfig.mode` 切换（"sparse"/"shaped"），不要复制两份
  env 类。observation 全部归一化（除以 height/width/max_fall_speed），改物理常量不影响
  observation 尺度。`info` 里同时带 score 和 passed_pipe，训练时 reward 与 task metric
  必须分开记录才能看出 reward hacking。
