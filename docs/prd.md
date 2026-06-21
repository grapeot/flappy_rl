# PRD — flappy_rl

## 目的

构建一个最小化、文档完善的项目，让计算机通过 reinforcement learning（强化学习，RL）学会玩一个自行编写的
Flappy Bird。这个项目首先是一个**学习载体**：价值在于理解 RL 的概念框架及其工程实践，
而不在于刷高某个基准分数或手写算法。

## 面向谁

项目作者，他想理解：

- *policy*（策略）是什么，它具体长什么样。
- RL 训练循环的形态，以及它为什么是现在这个样子。
- 主要的算法家族（value-based 与 policy-gradient）在框架层面的差异 ——
  足以在两者间做出选择并读懂它们的输出，而不必去重新实现它们。
- **reward design**（奖励设计）：reward 如何驱动行为，常见的陷阱有哪些，以及如何
  识别并防止 *reward hacking*。
- RL 在实践中究竟如何落地 —— environment 接口、训练框架、评估，以及
  "它训练完了"和"它真能用"之间的差距。

## 我们明确不去优化什么

- 从零手写 DQN/PPO。我们使用 Stable-Baselines3。
- 最前沿的 sample efficiency（样本效率）或分数。
- 从原始像素学习。我们从一个紧凑的数值 state（bird/pipe 坐标）出发，
  这样能在几分钟内学会。基于像素的学习被列为一个可能的后续扩展，但
  不在 v0 范围之内 —— 它要慢上一到两个数量级，并带来 CNN
  调参，会分散我们关注的概念。

## 需求

### 功能性

1. 一个确定性的、零依赖的 Flappy Bird 物理内核（`FlappyBirdGame`），它
   暴露完整的内部 state（bird y、bird vy、next-pipe x / gap-top / gap-bottom），
   每次调用推进一个固定的 timestep，并报告碰撞和过 pipe 事件。
2. 一个 Gymnasium `Env` wrapper，把物理内核映射为 `reset()` / `step(action)`，
   带有一个定义好的 observation 向量、一个两动作的 discrete 空间，以及一个 reward 函数。
3. 一个训练入口，通过 Stable-Baselines3 运行 PPO（默认）并保存模型。
4. 一个 play/eval 入口，加载已保存的模型并运行 episode，可选地附带一个
   实时渲染的窗口供人观看。
5. 一个可选的 pygame renderer，与训练完全解耦。

### 非功能性

- 三个干净分离的层（physics / env / training），使每一层都可以独立
  测试、独立阅读。
- 训练以 headless 方式运行且快于实时；渲染是 opt-in 的。
- 可复现：端到端支持 seeding。
- 可公开：无密钥、无个人数据，仅用假占位符。

## 成功标准

项目成功的标志是：

1. **概念上**：文档用平实的语言、扎根于这个具体游戏，解释了 ——
   policy 是什么、循环如何训练它、DQN-vs-PPO 的取舍，以及一份
   reward 设计陷阱和 reward-hacking 失效模式的清单，配以取自*这个*游戏的具体例子。
2. **可工作**：一个训练好的 policy 能可靠地通过多个 pipe，且我们能在一个
   渲染窗口里看到它。"可靠"意味着明显优于随机扇翅膀的 baseline，并在
   一批 eval episode 上得到验证。
3. **可诊断**：当 bird 学到某种退化行为（例如钻了某个 reward 漏洞）时，我们能
   在 metrics 中看到它，并把它追溯回 reward 定义 —— 而且
   文档把这种情况当作一等的、预期内的结果，而非意外。

reward 函数本身被刻意推迟到一次设计讨论；把它设计对（以及看着它出错）
正是这个项目所围绕构建的核心学习体验。
