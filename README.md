# 万界 · 行者 · World Walker

## 检索关键词 / Keywords

`AI文字游戏` `互动小说引擎` `涌现叙事` `认知架构` `Prospect Theory` `ACT-R` `Panarchy`
`因果世界` `双系统理论` `道德基础` `文化进化` `系统动力学` `PID控制` `Moral Psychology`

`AI text adventure` `interactive fiction engine` `emergent narrative` `cognitive architecture`
`game AI` `world simulation` `behavioral economics` `evolutionary dynamics` `systems thinking`

---

## 简介 / Introduction

> **中文**: "万界·行者"是一个由 AI 驱动的**文字互动游戏引擎**。它不是一个预设剧情的视觉小说，而是一个**由数学驱动的因果宇宙**——玩家的每一个决定都通过 15 个学科的 85+ 个学术公式进行处理，结果是**世界自己在讲故事**。于是，同样的引擎可以模拟一个修真大陆的宗门兴衰、一个赛博朋克城市的帮派暗战、或一个奇幻王国的王位争夺——不靠分支剧本，靠**涌现**。
>
> **EN**: *World Walker* is an AI-driven **text interaction engine**. It isn't a branching visual novel with pre-written storylines — it's a **mathematically grounded causal universe**. Every player decision is processed through 85+ academic formulas spanning 15 disciplines, and the result is that **the world tells its own story**. The same engine simulates a cultivation sect's rise and fall, a cyberpunk city's gang warfare, or a fantasy kingdom's succession crisis — all without pre-written branches, through **emergence**.

---

## 精简描述 / TL;DR (用于仓库描述 / Repo Description)

**中**: AI 文字互动游戏引擎 — 85+ 数学模型驱动的涌现叙事系统，世界观无关（修真/武侠/奇幻/科幻通用），Agent 通过 CLI 调用引擎，引擎返回 JSON 世界状态。

**EN**: AI text-interaction engine — 85+ mathematical models drive emergent, worldview-agnostic narratives. Agent calls engine via CLI; engine returns structured JSON world state.

---

## 项目结构 / Project Structure

```
game_engine/
├── engine.py               CLI 入口 / CLI entry (14 commands)
├── state_schema.py         状态结构 / State schema + helpers
├── demo_state.json         演示状态 / Example game state
├── GAME_MASTER_PROTOCOL.md AI↔引擎调用协议 / Agent↔Engine protocol
└── rules/                  85+ 学术公式的 Python 实现 / Academic formulas as Python
    ├── combat.py           战斗 / Combat (hit/crit/skill/mp)
    ├── economy.py          经济 / Economy (supply/demand/bulk-price)
    ├── social.py           社交基础 / Social 2D (affinity/respect)
    ├── karma.py            因果债 / Causal debt (karma ledger)
    ├── cognition.py        认知 / Cognition (dual-system/Prospect/ACT-R/flow)
    ├── world_dynamics.py   世界演化 / World dynamics (chaos/evolution/PID/Panarchy)
    ├── social_extended.py  扩展社会 / Extended social (moral/Milgram/Bandura/Cialdini)
    ├── cultural_evolution.py 文化进化 / Cultural evolution (memetics/ratchet/DIT)
    ├── systems_feedback.py  系统控制 / Systems feedback (Meadows 12 leverage/NAT)
    └── narrative_engine.py  涌现叙事 / Emergent narrative (identity/events/phase)
```

---

## 14 条引擎命令 / 14 Engine Commands

```bash
PYTHONPATH=. python3 engine.py <command> --state game.json [options]

combat       战斗结算: 命中/暴击/伤害/击杀 / hit, crit, dmg, kill
trade        经济结算: 大宗购买推高价格 / buy/sell with price impact
social       社交事件: 10 种事件→2D 关系变化 / 10 events → affinity+respect
karma        因果债: 杀生+50/助人-10, 风险等级 / karma ledger, risk assessment
tick         世界步进: 市场回归均值 / market mean-reversion per turn
flow         心流检测: 基于最近 5 场胜率 / Csikszentmihalyi flow state
identity     玩家画像: Bartle 四维身份向量 / player identity vector
narrative    涌现事件: 阈值触发大世界事件 / threshold-driven emergent events
world_state  世界快照: 实体/关系/市场/因果 / full world state summary
panarchy     相位判定: r-K-Ω-α 四相位 / adaptive cycle phase detection
moral_update 道德更新: 六维身份指数衰减 / Haidt 6-dim moral identity
cognition    认知审计: 双系统切换判定 / Kahneman System 1/2 switching
merit        功德计算: aid × (0.4+0.6×sincerity) / merit weighted by sincerity
info_weight  信息权重: 基于概率的叙事重要性 / Shannon-based event weight
```

---

## 学术覆盖 / Academic Coverage

共编码 **85+ 学术公式**来自 15 个学科分支：

*85+ academic formulas, 15 discipline branches:*

| 学科/Discipline | 核心理论 / Core Theories | 行数 |
|-----------------|------------------------|------|
| 认知科学 Cognitive Science | Kahneman 双系统, Prospect Theory λ=2.25, ACT-R 记忆激活, Csikszentmihalyi 心流 | 235 |
| 混沌/复杂系统 Chaos/Complex | Lorenz 吸引子, Lyapunov 指数, Logistic 映射 (r=3.57 混沌阈值), Panarchy r-K-Ω-α, PID 控制 | 275 |
| 道德心理学 Moral Psychology | Haidt 六维道德基础, Tajfel 社会认同, Bandura 道德推脱, Milgram 服从 65%, Cialdini 影响力 | 202 |
| 进化动力学 Evolutionary | Price 方程 Δz̄=Cov+E(Δz), Hamilton rb>c, ESS 混合策略, Red Queen | 275 |
| 文化进化 Cultural Evolution | 双继承理论 DIT, 模因适应度, 累积文化棘轮, 保真度 n 次衰减 | 92 |
| 系统理论 Systems Theory | Donella Meadows 12 杠杆点 (对数缩放), NAT 级联故障, ANT 行动者网络 | 141 |
| 叙事学 Narrative Studies |涌现而非分支, Bartle 四维玩家类型, 叙事传输理论, 空间叙事 | 141 |
| 信息论 Information Theory | Shannon 熵, KL 散度, 事件信息量 (小概率=高权重), 信道容量 | — |

---

## 设计原则 / Design Principles

| # | 原则 / Principle | 含义 / Meaning |
|---|-----------------|----------------|
| 1 | **世界观无关** / *Worldview-agnostic* | 同一套公式，换叙事词汇即可模拟修真/武侠/奇幻/科幻 |
| 2 | **涌现而非分支** / *Emergence > Branching* | 世界从数学机制中自然产生剧情，不预写分支树 |
| 3 | **Agent→引擎→文学** / *Agent→Engine→Prose* | 引擎返回 JSON，AI Agent 负责将其转为文学描写 |
| 4 | **完全响应式** / *Fully responsive* | 玩家想做的一切，引擎都能给一个有数学依据的结果 |

---

## 与人协作 / How to collaborate

对玩家: 你告诉 Agent 你想做什么 → Agent 调用引擎 → 引擎返回 JSON → Agent 用文字告诉你发生了什么。

*To players: tell the Agent what you want → Agent calls engine → engine returns JSON → Agent renders it as prose.*

对 AI Agent: 详见 `GAME_MASTER_PROTOCOL.md` — 完整的调用协议、参数说明、响应格式。

*For AI Agents: see `GAME_MASTER_PROTOCOL.md` for the complete call protocol, parameters, and response schemas.*

---

## License / 许可证

MIT
