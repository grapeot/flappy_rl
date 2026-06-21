# RL Concepts, grounded in Flappy Bird

This is the conceptual core of the project. It explains the ideas you came here to
understand — policy, the training loop, the algorithm families, and especially **reward
design and reward hacking** — using this one concrete game so the abstractions stay
attached to something real.

It assumes you don't want to hand-write the algorithms. So it stays at the level of *what
each piece is and why it's shaped that way*, not the gradient math.

---

## 1. The loop: what reinforcement learning actually is

RL is learning by interaction. There is an **agent** and an **environment**. On each step:

1. The environment shows the agent a **state** (here: bird height, velocity, next pipe's
   gap).
2. The agent picks an **action** (flap or don't).
3. The environment moves one tick forward and returns a **reward** (a single number) and
   the next state.

The agent's whole job is to choose actions that maximize **cumulative reward over time**,
not the immediate reward. This "over time" is the heart of it: flapping now might cost a
little but save the bird from a wall three frames later. The agent has to learn to value
future consequences of present actions. That delayed-credit problem — "which of my past
actions caused this reward?" — is what makes RL different from ordinary supervised learning,
where each input has a known correct label. In RL nobody tells the bird the right move;
it only finds out, much later and noisily, whether things went well.

A few terms you'll meet:

- **Episode**: one playthrough from `reset()` to death (or a truncation cap). The bird
  flapping until it hits a pipe is one episode.
- **Return**: the total (usually discounted) reward across an episode. This is the thing
  being maximized.
- **Discount factor (γ, gamma)**: a number near 1 (e.g. 0.99) that makes near-future
  reward worth slightly more than far-future reward. It keeps the math stable and encodes
  "sooner is a bit better." With γ = 0.99, a reward 100 steps away is worth about
  0.99^100 ≈ 0.37 of its face value now.

---

## 2. What a policy *is*, and what it looks like

A **policy** (written π) is the agent's strategy: a function from state to action. It is
the thing being learned. Everything else in RL is machinery for improving the policy.

Concretely in this project the policy is a small neural network (an MLP). Its input is the
observation vector; its output describes what to do:

- In a **policy-gradient** method like PPO, the network outputs a *probability* for each
  action — e.g. "flap with probability 0.2, don't-flap with probability 0.8" — and we
  sample from that. Outputting probabilities (a *stochastic* policy) is what lets the agent
  explore: early on the probabilities are near 50/50 and it tries everything; as it learns,
  they sharpen toward good moves.
- In a **value-based** method like DQN, the network instead outputs a *value* for each
  action — "the long-run payoff of flapping here is 8.3, of not flapping is 9.1" — and the
  policy is the trivial rule "pick the higher one."

So "what does a policy look like" has a very concrete answer here: it's a few small weight
matrices that turn five-ish numbers into two numbers. After training you can save it, load
it, and call it on any state to get a move. That saved file *is* the learned skill.

A useful distinction:

- **Policy** = state → action (what to do).
- **Value function** = state (or state+action) → expected return (how good it is to be
  here, or to do this here). Value is a *prediction*; policy is a *decision*. Some
  algorithms learn only a policy, some only a value function, and some (like PPO,
  "actor-critic") learn both at once — the value function ("critic") is used to judge and
  improve the policy ("actor").

---

## 3. The two algorithm families, and why we pick PPO

You don't need to implement these, but choosing between them and reading their logs
requires knowing what they are.

### Value-based: DQN (Deep Q-Network)

Learns a **Q-function**: Q(state, action) = expected long-run return of taking that action
in that state and behaving well afterward. The policy is "take the action with the highest
Q." It learns by **bootstrapping** — updating its estimate of one state toward the reward
plus its own estimate of the next state (this is the famous Bellman update).

Strengths: sample-efficient, because it uses a **replay buffer** — past experience is stored
and reused many times. Natural fit for small discrete action sets (we have exactly two).

Costs: several moving parts that can be finicky — an **ε-greedy** exploration schedule (act
randomly ε of the time, decay ε over training), a **target network** (a lagged copy used to
stabilize the bootstrap), and the replay buffer. Misconfigure these and it silently fails to
learn.

### Policy-gradient: PPO (Proximal Policy Optimization)

Learns the policy **directly**: it runs the current policy, sees which actions led to
higher-than-expected return, and nudges the network to make those actions more likely —
while *clipping* each update so the policy can't lurch too far in one step (that clipping is
the "proximal" part, and it's what makes PPO stable).

Strengths: robust, forgiving of hyperparameters, the current default across the industry.
Built-in exploration via the stochastic policy — no separate ε schedule to tune.

Costs: **on-policy**, so it cannot reuse old experience the way DQN's replay buffer does;
it needs more environment steps. But Flappy Bird simulates extremely fast headless, so this
cost is irrelevant for us.

### Decision

**PPO by default.** For a project whose point is to understand RL and reward design, PPO's
forgiveness means the bird actually learns without algorithm babysitting, so our attention
goes where it should — to the environment and the reward. DQN stays one line away, and
running both is a good exercise precisely because it makes the value-vs-policy distinction
tangible.

With Stable-Baselines3 the entire algorithm side is roughly:

```python
from stable_baselines3 import PPO
model = PPO("MlpPolicy", env, verbose=1)
model.learn(total_timesteps=500_000)
model.save("flappy_ppo")
```

That brevity is the point: the library is solved infrastructure. The interesting,
project-specific, easy-to-get-wrong work is everything below.

---

## 4. Reward design — the part that actually decides success

The reward function is the only place you tell the agent *what you want*. It is also where
almost all real RL pain lives, because the agent optimizes **exactly what you wrote, not
what you meant**. This section is the heart of the doc.

### The fundamental tension: sparse vs shaped

**Sparse reward**: only signal at meaningful events. For Flappy Bird, e.g. `+1` when the
bird clears a pipe, `0` otherwise, and the episode ends on death.

- *Pro:* it expresses the true objective with no distortion. "Clear pipes" — nothing else.
- *Con:* it's hard to learn from. A fresh, randomly-flapping bird almost never clears a
  pipe, so it almost never sees a reward, so it has almost nothing to learn from. This is
  the **exploration problem** — far-apart reward signals leave long stretches of "no
  feedback," and learning crawls or stalls.

**Shaped reward**: add intermediate hints that point toward the goal. E.g. a small `+0.1`
per frame survived, plus a bonus for being vertically aligned with the next gap.

- *Pro:* dense feedback — every single frame says something — so learning is much faster.
- *Con:* every hint you add is a new surface for the agent to **game**. You are no longer
  rewarding "play the game well"; you are rewarding a *proxy* for it, and proxies leak.

Reward shaping is the craft of adding just enough guidance to make learning tractable
without changing what the optimal behavior actually is. There's even a formal safe version
(*potential-based shaping*) that provably doesn't change the optimal policy — worth knowing
exists, because most naive shaping does *not* have that guarantee.

### A concrete catalog of pitfalls (all real in this game)

These are the failure modes we expect to actually hit, with the mechanism named:

1. **Survival reward with no progress requirement.** Pay `+0.1` per frame alive, and the
   bird may discover that *hovering* — never advancing past a pipe but never dying — racks
   up reward forever. You rewarded "stay alive," and it found a way to stay alive that has
   nothing to do with playing. (Mitigation: tie reward to pipes cleared, or cap episode
   length, or make standing still impossible in the physics.)

2. **Reward scale mismatch.** If "clear a pipe" is worth `+1` but "die" is worth `0` and
   each survived frame is `+0.1`, then surviving 10 idle frames already outweighs the value
   of clearing a pipe. The agent does the arithmetic you actually wrote, not the priorities
   you intended. Relative magnitudes *are* the specification. (Mitigation: make the death
   penalty and pipe reward dominate the per-frame term; sanity-check the numbers by hand.)

3. **Dense bonus that the agent over-optimizes.** Reward "vertical alignment with the gap"
   and the bird may learn to sit perfectly centered while drifting into the pipe wall,
   because at the instant of impact it was beautifully aligned and collected the bonus.
   The proxy (alignment) and the goal (passage) came apart. (Mitigation: only reward
   alignment *and* forward progress jointly, or only reward the actual pipe-clear event.)

4. **Unintended termination incentives.** If dying ends the episode and the per-step reward
   is *negative* (say a small penalty per frame), a naive agent can conclude that the
   fastest way to stop losing points is to **die immediately**. You meant "hurry"; it heard
   "an early death is a good death." (Mitigation: ensure the value of continuing always
   exceeds the value of dying — keep the death penalty larger than any accumulated step
   cost.)

5. **Distributional / boundary exploits.** The agent finds a corner of the state space the
   physics handles oddly — clipping through a pipe edge, exploiting a spawn pattern, riding
   the ceiling. The reward didn't forbid it because you didn't imagine it. (Mitigation:
   harden the physics; randomize spawns and seeds; watch for "too good to be true" scores.)

The throughline: **the agent is a literal-minded optimizer with no common sense and infinite
patience.** Any gap between what you measured and what you wanted, it will find and walk
through. Reward design is the discipline of closing those gaps before the agent finds them
— and of recognizing, when the score looks suspiciously great, that it probably found one
you missed.

### Reward hacking, stated plainly

**Reward hacking** is when the agent achieves high reward *without* achieving the goal you
designed the reward to represent — it optimizes the letter of the reward against its spirit.
Every pitfall above is a flavor of it. It is not the agent being clever or adversarial; it
is the agent doing exactly its job (maximize the number) on a number that imperfectly
encodes your intent.

How to *recognize* it:

- The reward curve goes up but the **behavior you actually care about** doesn't (pipes
  cleared stays flat while reward climbs). This is why you log *task metrics separately
  from reward* — reward is what you optimized, the task metric is what you wanted, and
  watching them diverge is the tell.
- The score is implausibly high, or the policy looks visually degenerate (hovering, wall-
  hugging, suicide).

How to *prevent / reduce* it:

- **Reward the true objective as directly as you can tolerate.** The closer the reward is to
  "cleared a pipe," the less room for proxies to leak. Add shaping only when sparse learning
  genuinely stalls, and add the *least* you can.
- **Keep magnitudes honest.** The relative sizes of survival / progress / death encode your
  priorities; get them wrong and you've mis-specified the goal regardless of intent.
- **Watch behavior, not just curves.** Render episodes periodically. A number can't tell you
  the bird is cheating; your eyes can.
- **Measure the goal metric independently** of the reward, and trust *it* as ground truth.
- **Iterate.** First reward is a hypothesis. You will watch it fail, diagnose which pitfall
  it hit, and revise. That loop is not a detour around the learning — for this project, that
  loop *is* the learning.

This is exactly why the reward function is left unwritten in the code so far: we want to
design it together, deliberately, with these failure modes in view — and very possibly to
watch a first version get hacked, name which pitfall it was, and fix it. That is the most
instructive thing this project can do.

---

## 5. How this lands in practice (the engineering, briefly)

Concepts only become real through a working harness. The practical pieces:

- **The env contract** (`reset` / `step`, observation space, action space, reward) is the
  one interface everything else plugs into. Get it right and you can swap algorithms freely.
- **Headless, faster-than-real-time training**: no rendering, no sleeping. Seconds of
  wall-clock buy thousands of episodes.
- **Evaluation separate from training**: run the frozen policy on fresh seeds and report the
  *task metric* (mean pipes cleared) over a batch — never judge by training reward alone.
- **Logging both reward and task metric**, so reward hacking shows up as a divergence rather
  than hiding as a happy-looking reward curve.
- **Watching with your eyes**: the optional renderer is not a toy — it is a debugging tool.
  Many reward bugs are invisible in metrics and obvious on screen in two seconds.
- **Reproducibility**: seed the env, the algorithm, and the framework so a result can be
  re-run.

The gap between "the reward curve went up" and "the bird plays the game" is precisely where
RL practice lives, and it's the gap this project is built to let you feel directly.

---

## 6. Glossary

- **Agent / Environment** — the learner; the world it acts in.
- **State / Observation** — what the agent sees each step (here: a few numbers).
- **Action** — what it does (flap / noop).
- **Reward** — the scalar feedback signal it maximizes.
- **Return** — discounted sum of rewards over an episode.
- **Policy (π)** — state → action; the learned strategy.
- **Value / Q-function** — predicted return from a state / from a state-action pair.
- **Episode** — one playthrough.
- **γ (discount factor)** — weights near vs far future reward.
- **On-policy / Off-policy** — whether the algorithm can reuse old experience (PPO no, DQN
  yes).
- **Reward shaping** — adding intermediate reward to speed learning.
- **Reward hacking** — high reward without achieving the intended goal.
