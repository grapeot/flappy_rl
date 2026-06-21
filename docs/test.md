# 测试策略

本文件的目的不是重述 `pytest` 命令，而是定义在每一层上**"已验证"意味着什么**，
这样后续的 agent（或未来的我）才能知道某件事究竟有没有真正做完。

三层架构（参见 [`rfc.md`](rfc.md)）正是让测试变得可处理的原因：每一层都能在信任下一层之前
被单独检验。

## 第 1 层 —— 物理内核（`FlappyBirdGame`）：unit tests

纯粹、确定性的逻辑。没有 RL，没有渲染，除了 seed 之外不引入任何随机性。这是测试最强、
成本最低的一层。

需要覆盖：

- 重力积分正确：在不 flap 的情况下 step，高度单调下降
  （向下速度增大），且幅度符合预期。
- flap 对速度施加符合预期的向上冲量。
- pipes 以配置的间距生成，并以配置的速度向左移动。
- 当 bird 与 pipe 重叠或越出垂直边界时，collision 恰好触发，
  不会早一帧也不会晚一帧。
- pipe-cleared 事件在 bird 经过一根 pipe 时恰好触发一次。
- 确定性：相同 seed + 相同 action 序列 → 完全相同的状态轨迹。

如果第 1 层是扎实的，那么它之上的每一个 bug 都是 RL/reward bug，而不是物理 bug ——
这正是大部分诊断价值所在。

## 第 2 层 —— Env 封装（`FlappyBirdEnv`）：contract + integration tests

验证它遵守 Gymnasium contract，以及 env↔physics 的转换是忠实的。

需要覆盖：

- `reset()` 返回一个落在声明的 `observation_space` 内的 observation，且 `info` 是一个
  dict。
- `step(action)` 返回 `(obs, reward, terminated, truncated, info)`，类型正确；
  `obs` 保持在 `observation_space` 内；`reward` 是一个 float。
- action space 是 `Discrete(2)`，且两个 action 都被接受。
- 一个完整的随机 action episode 能从 `reset()` 跑到 `terminated` 而不报错。
- 设定 seed 的 `reset(seed=k)` 能复现同一个 episode。
- **Reward sanity**（一旦 reward 存在）：有针对性的断言，确认文档中记录的 reward
  事件以文档中记录的符号/量级触发 —— 例如死亡产生 penalty，
  pipe-clear 产生 bonus。这些测试同时充当防护栏，防止意外的 reward
  regression 诱发 hacking。
- 使用 Stable-Baselines3 的 `check_env` 工具，它会对照规范审查 env。

## 第 3 层 —— 训练 / 评估：smoke tests，而非分数测试

我们不去 unit-test "bird 学会了" —— 那既慢又随机。取而代之：

- **Smoke test**：`model.learn(total_timesteps=<small>)` 在真实 env 上端到端运行
  而不报错，并产出一个可保存的 model。这能以低成本捕捉集成层面的破损。
- **Eval harness 检查**：加载一个已保存的 model 并运行 N 个 eval episode，返回一份
  task-metric 摘要（mean / std pipes cleared），且永不抛出异常。

## 手工 / 视觉验证（这是一等步骤，不是事后补充）

本项目中一些最重要的失败 —— 尤其是 reward hacking —— 在
**metrics 里是隐形的，在屏幕上却一目了然。** 因此验证还包括：

- 在一个训练好的 model 上运行 `scripts/play.py --render`，观看若干 episode。
- 确认行为与 metric 相符：如果 mean pipes cleared 很高，bird 就应当肉眼可见地穿过
  pipes —— 而不是悬停、贴着天花板飞或快速死亡。
- "reward 上升"与"task metric / 可见行为"之间的背离，正是 reward hacking 的
  特征，其本身就是一项需要记录到 `working.md` 的发现。

## 什么算"完成"

- 第 1 层和第 2 层在 `pytest` 下通过。
- `check_env` 通过。
- 一个简短的训练 smoke test 完成并保存了一个 model。
- 对于任何真实训练运行：报告 eval task metric *并且* 至少观看了一个渲染的
  episode，同时把观察记录到 `working.md` 中。
