# Game Master 协议 (AI → 引擎调用约定 v2)

> 核心原则:**所有确定性计算交给引擎,Agent 只负责文学叙事**。

---

## 1. 引擎命令总览

| 命令 | 用途 | 关键参数 |
|------|------|---------|
| `combat` | 战斗结算 | --attacker --defender --action_type |
| `trade` | 交易结算 | --location --item --quantity --direction |
| `social` | 关系更新 | --actor --target --event --intensity |
| `karma` | 因果债分录 | --actor --victim --karma_type |
| `tick` | 回合结束 | (无额外参数) |
| `cognition` | 双系统判定 | --entity |
| `flow` | 心流状态检查 | (无) |
| `identity` | 玩家身份画像 | (无) |
| `narrative` | 涌现叙事+Panarchy | (无) |
| `panarchy` | 世界相位判定 | (无) |
| `moral_update` | 道德向量更新 | (无) |
| `merit` | 功德计算 | --aid --sincerity |
| `info_weight` | 叙事信息权重 | --probability |
| `world_state` | 世界状态快照 | (无) |

---

## 2. 每回合强制流程

```
玩家输入行动
      │
      ▼
  [1] Agent 读取状态  ← cat game_state.json
  [2] 判断行动是否涉及数值变化
  [3] 调用引擎结算    ← python3 engine.py <action> --state game_state.json ...
  [4] 读取引擎输出 JSON
  [5] 生成文学描写    ← 仅展示给玩家
  [6] 必要时机tick    ← python3 engine.py tick --state game_state.json
```

---

## 3. 强制规则

1. ❌ **不能跳过引擎** — 所有数值结算必须经 engine.py
2. ❌ **不能让玩家看到结构化数值** — JSON 只在 Agent 内部使用
3. ✅ **必须**将道德向量、心流状态、Panarchy 融入叙事节奏
4. ✅ **必须**在每 3-5 回合检查一次 flow/narrative 命令
5. ❌ **不能**手写修改 state JSON (必须通过引擎)

---

## 4. 世界观无关

引擎是通用的。Agent 根据当前"叙事素材库"选择描写词汇:

| 世界观 | str 描写 | 境界体系 |
|--------|---------|---------|
| 修真 | 灵气/内力 | 练气→筑基→金丹→元婴 |
| 武侠 | 内力/后劲 | 三流→二流→一流→绝顶 |
| 奇幻 | 法力/精神 | 1st→9th circle |
| 科幻 | 能量/神经同步 | C-class→S-class |

引擎公式不变,描写词汇切换。

---

## 5. 调用示例

\```bash
# 战斗
python3 engine.py combat --state g.json --attacker player --defender bandit --action_type heavy

# 检查玩家心理状态
python3 engine.py flow --state g.json
# 输出: {"state": "anxiety", "adjustment": -0.15, "trigger_luck": true}
# Agent: 描写一场"否极泰来"的奇遇作为缓冲

# 检查涌现事件
python3 engine.py narrative --state g.json
# 输出: {"emergent_events": [{"type":"calamity_omen", ...}]}
# Agent: 植入大劫将至的伏笔

# 业债积累触发后果
python3 engine.py karma --state g.json --actor player --victim villager --karma_type murder_innocent
# 输出: {"risk_level": "high", "karma_consequence": {"triggered": true, "effects": ["突破成功率-30%"]}}
# Agent: 描写玩家心中隐约的不安感,突破时心魔威力增大
\```
