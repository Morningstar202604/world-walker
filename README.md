# 万界 · 行者

**中文** | [English](README.en.md)

---

**万界·行者**是一个由 AI 驱动的文字互动游戏引擎。世界的演化由 15 个学科、85+ 个学术公式驱动——玩家的每个决定通过数学模型处理，世界由此自然涌现剧情，而非预设分支。

检索关键词: `AI文字游戏` `互动小说引擎` `涌现叙事` `认知架构` `因果世界` `双系统理论` `心流` `道德基础` `文化进化` `系统动力学` `PID控制`

---

## 快速开始

```bash
# 查看命令列表
PYTHONPATH=. python3 engine.py --help

# 14 条命令速查
PYTHONPATH=. python3 engine.py combat    --state game.json --attacker player --defender goblin
PYTHONPATH=. python3 engine.py trade     --state game.json --location market --item 丹药 --quantity 3 --direction buy --entity player
PYTHONPATH=. python3 engine.py social    --state game.json --actor player --target npc --event help
PYTHONPATH=. python3 engine.py karma     --state game.json --actor player --karma_type murder_innocent
PYTHONPATH=. python3 engine.py tick      --state game.json
PYTHONPATH=. python3 engine.py flow      --state game.json
PYTHONPATH=. python3 engine.py identity  --state game.json
PYTHONPATH=. python3 engine.py narrative --state game.json
PYTHONPATH=. python3 engine.py world_state  --state game.json
PYTHONPATH=. python3 engine.py panarchy  --state game.json
PYTHONPATH=. python3 engine.py moral_update   --state game.json
PYTHONPATH=. python3 engine.py cognition   --state game.json --entity player
PYTHONPATH=. python3 engine.py merit     --state game.json --aid 0.8 --sincerity 0.9
PYTHONPATH=. python3 engine.py info_weight --state game.json --probability 0.05
```

---

## 项目结构

```
game_engine/
├── engine.py                     # CLI 入口（14 条命令）
├── state_schema.py               # 状态结构 + 辅助函数
├── demo_state.json               # 演示状态
├── GAME_MASTER_PROTOCOL.md       # AI Agent 调用协议
└── rules/                        # 85+ 学术公式（Python 实现）
    ├── combat.py                 #    战斗 / 命中 / 暴击
    ├── economy.py                #    经济 / 供需 / 价格波动
    ├── social.py                 #    社交二维关系
    ├── karma.py                  #    因果债
    ├── cognition.py              #    认知科学（双系统、前景理论、ACT-R、心流）
    ├── world_dynamics.py         #    世界演化（混沌、进化、Panarchy、PID）
    ├── social_extended.py        #    扩展社交（Haidt、Milgram、Bandura）
    ├── cultural_evolution.py     #    文化进化（DIT、模因、文化棘轮）
    ├── systems_feedback.py       #    系统反馈（Meadows 12 杠杆点、NAT）
    └── narrative_engine.py       #    涌现叙事（Bartle、事件、相位）
```

---

## 学术覆盖

85+ 公式，15 个学科分支：

| 学科 | 核心理论 | 文件 | 行数 |
|------|---------|------|------|
| 认知科学 | Kahneman 双系统, Prospect Theory, ACT-R 记忆, Csikszentmihalyi 心流 | cognition.py | 235 |
| 混沌 / 复杂系统 | Lorenz, Lyapunov 指数, Logistic 映射, Panarchy, PID 控制 | world_dynamics.py | 275 |
| 道德心理学 | Haidt 六维, Tajfel, Bandura, Milgram, Cialdini | social_extended.py | 202 |
| 进化动力学 | Price 方程, Hamilton, ESS, Red Queen | world_dynamics.py | — |
| 文化进化 | DIT, 模因, 文化棘轮, 保真度衰减 | cultural_evolution.py | 92 |
| 系统理论 | Meadows 12 杠杆点, NAT 级联, ANT 行动者网络 | systems_feedback.py | 141 |
| 叙事学 | 涌现叙事, Bartle, 叙事传输, 空间叙事 | narrative_engine.py | 141 |
| 信息论 | Shannon 熵, KL 散度, 事件信息量 | world_dynamics.py | — |

---

## 设计原则

1. **世界观无关** —— 同一套数学，换叙事词汇即可模拟修真/武侠/奇幻/科幻
2. **涌现而非分支** —— 世界从机制中自然产生剧情，不预写分支树
3. **Agent → 引擎 → 文学** —— 引擎返回 JSON，AI Agent 负责转为文学描写
4. **完全响应式** —— 玩家想做的一切，引擎都能给一个有数学依据的结果

---

## 与他人协作

- **对玩家**: 你告诉 AI Agent 你想做什么 → Agent 调用引擎 → 引擎返回 JSON → Agent 用文字告诉你发生了什么
- **对 AI Agent**: 详见 [`GAME_MASTER_PROTOCOL.md`](GAME_MASTER_PROTOCOL.md) —— 完整的调用协议、参数说明、响应格式

---

## 许可

MIT
