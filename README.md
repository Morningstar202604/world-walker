# 万界·行者 · World Walker

> **EN**: A world-class AI-driven text interactive fiction engine — where player choices drive world evolution through systematic mathematical models and deep academic theories across 15+ disciplines.

> **中**: 世界级 AI 文字互动游戏引擎 —— 基于 15+ 学科、85+ 学术模型的因果世界推演系统。玩家的选择通过系统性数学模型驱动世界演化。

---

## 核心理念 / Core Concept

玩家自由决定一切。在合理范围内想做就做。引擎不做选择题，只回答"如果这样做会发生什么"。

*Player freedom is absolute. Within logical constraints, do whatever you want. The engine doesn't give multiple choices — it answers "What happens if you do this?".*

---

## 项目结构 / Project Structure

```
game_engine/
├── engine.py              # 统一 CLI 入口 / Unified CLI entry point
├── state_schema.py        # 状态 JSON 结构 / Game state schema
├── demo_state.json        # 演示状态示例 / Demo state
├── GAME_MASTER_PROTOCOL.md # AI↔引擎协议 / AI↔Engine protocol
└── rules/
    ├── combat.py          # 战斗系统 (命中/暴击/技能)
    ├── economy.py         # 经济系统 (供需/大宗交易)
    ├── social.py          # 基础社交 (2D关系)
    ├── karma.py           # 因果债系统 (业/清算)
    ├── cognition.py       # 认知科学 (双系统/前景论/心流)
    ├── world_dynamics.py  # 世界推演 (混沌/进化/Panarchy)
    ├── social_extended.py # 扩展社会 (道德/服从/影响)
    ├── cultural_evolution.py # 文化进化 (模因/棘轮)
    ├── systems_feedback.py   # 控制论 (杠杆点/级联)
    └── narrative_engine.py   # 叙事涌现 (身份/相位)
```

## 学术覆盖 / Academic Coverage

共编码 **85+ 学术公式**来自 11 个参考文献：

*85+ academic formulas encoded from 11 reference documents:*

| 学科/Discipline | 理论/Theory | Lines |
|-----------------|-------------|-------|
| Cognitive Science | Kahneman 双系统 / Prospect Theory λ=2.25 / ACT-R / Flow | 235 |
| Chaos/Complex Systems | Lorenz / Lyapunov / Logistic Map / Panarchy r-K-Ω-α / PID | 275 |
| Moral Psychology | Haidt 6-dim / Tajfel / Bandura / Milgram / Cialdini | 202 |
| Evolutionary Dynamics | Price Equation / Hamilton rb>c / ESS / Red Queen | 275 |
| Cultural Evolution | Dual Inheritance / Memetics / Cumulative Culture | 92 |
| Systems Theory | Meadows 12 Leverage Points / NAT Cascade / ANT | 141 |
| Narrative Studies | Emergence / Bartle Types / Player Identity | 141 |
| Information Theory | Shannon Entropy / KL Divergence / Event Weight | — |

## 使用方法 / Usage

```bash
# 战斗结算 / Combat resolution
python3 engine.py combat --state game.json --attacker player --defender npc_001

# 心流检测 / Flow check
python3 engine.py flow --state game.json

# 世界涌现事件 / World emergent events
python3 engine.py narrative --state game.json

# 认知双-system check / Cognitive dual-system
python3 engine.py cognition --state game.json --entity player

# 全境 tick / End of turn
python3 engine.py tick --state game.json
```

## 设计原则 / Design Principles

1. **世界观无关** / *Worldview-agnostic* — 同一公式用于修真/奇幻/武侠/科幻
2. **涌现而非分支** / *Emergence over branching* — 世界从机制中自然涌现
3. **Agent→引擎→文学** / *Agent→Engine→Literature* — 引擎返回结构化 JSON，Agent 将其文学化
4. **完全自由** / *Absolute freedom* — 玩家能做的一切，引擎都能响应

---

*License: MIT*
