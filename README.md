# 万界 · 行者

**中文** | [English](README.en.md)

---

**万界·行者**是一个由 AI 驱动的文字互动游戏引擎。世界的演化由 15 个学科、85+ 个学术公式驱动——玩家的每个决定通过数学模型处理，世界由此自然涌现剧情，而非预设分支。

检索关键词: `AI文字游戏` `互动小说引擎` `涌现叙事` `认知架构` `因果世界` `双系统理论` `心流` `道德基础` `文化进化` `系统动力学` `PID控制`

---

## 快速开始

### 方式 A：MCP（推荐 —— 给任何 AI Agent 用）

```bash
pip install -e ".[mcp]"
```

在 MCP 客户端（Claude Code / Codex / Cursor / 任意支持 MCP 的 Agent）配置里加：

```json
{ "mcpServers": { "world-walker": { "command": "world-walker-mcp" } } }
```

把设定丢给 Agent 即可开一局（仓库自带 `settings/玄枢界.setting.json`，`load_setting` 一句话开局）。支持 MCP prompt 的客户端还能一键开局：调 `new_game`（参数填设定），
它会生成完整开局指令。流程是：`world_init`（按设定建世界，入参带字段级说明，含 seed）→
玩家每个行动由 `combat` / `trade` / `social` / `karma` 结算 → `narration_context` 取触发的
设定条目、在场角色的卡面文字与编年史 → 文学描写 → `tick` 收回合 → 每 3-5 回合用
`narrative` + `status` 检查涌现事件与心流；Agent 只负责转写 JSON，不得编造数值。

- 生态兼容（不重复造轮子）：直接吃酒馆（SillyTavern）生态的**角色卡**（`.png` 内嵌 / `.json`，
  V1/V2/V3）与**世界书**（world-info / 卡内 `character_book`，含 selective/constant/disable 语义）；
  `character_card_read` 看卡 → `add_character` 入局（卡面文字进叙事层）→ `import_lorebook` 并入设定
- **长局支持（奔着百万回合设计）**：三层记忆，叙事永远只带该带的——
  · `write_summary` 章节摘要（宿主每 20-50 回合写一次，只写"变了什么"）
  · 大事记（突破/击杀/初次抵达/因果升级自动记录，`recap` 与面板都读它）
  · 事件自动归档：状态文件只保留最近 N 条（默认 200，`configure` 可调），
    更旧的追加进 `<状态文件>.log.jsonl`，需要时用 `recall` 按关键词回捞
  · `recap(budget_chars)` 按字符预算给「最新摘要 + 大事记 + 最近事件」
- **成长闭环**：`advance` 突破——引擎按（洞察/心境/业债/气血）判定成败并落数值后果
  （成功涨上限与属性、失败反噬气血并留心伤），杜绝手改等级
- 实况面板：`open_panel` 起一个**只读网页**（气血/内力/心流/世界相位/探索图鉴/大事记/编年史/市场行情，
  状态一变就自动刷新）；玩家记不住的东西——去过哪、见过谁、什么价、发生过什么——都在上面。
  也可单独跑：`python panel.py --state ww_state.json`
- 移动与图鉴：`travel` 是唯一能改玩家位置的工具，首次到达自动进图鉴（地点/人物/物品/已触发设定）
- 回合可回退：`snapshot` / `restore`（引擎状态确定性，回退后重放同种子一致）
- 端到端自检：`python scripts/verify_mcp_stdio.py`（45 项断言，含酒馆生态/图鉴/面板/设定包/长局与确定性）
- 实测：opencode（GLM-5.2）接入后按设定建局、连续结算三个行动，叙事数值与引擎状态文件逐项一致
- 可复现：开局带 `seed`；每次结算的随机数由状态里的 `rng_seed` 与 `rng_counter` 共同决定，并随状态落盘

### 方式 B：CLI（手动结算）

```bash
python init_game.py                                      # 生成示例世界 game_state.json（青云界）
python engine.py world_state --state game_state.json      # Windows 用 python，macOS/Linux 用 python3
```

14 条命令速查（状态文件以 `game_state.json` 为例；注意 `--item` 传的是市场 item_key，不是显示名）：

```bash
python engine.py combat    --state game_state.json --attacker player --defender goblin --action_type heavy
python engine.py trade     --state game_state.json --location bamboo_tea_booth --item an_zhen_san --quantity 3 --direction buy --entity player
python engine.py social    --state game_state.json --actor player --target old_chen --event help
python engine.py karma     --state game_state.json --actor player --karma_type murder_innocent
python engine.py tick      --state game_state.json
python engine.py flow      --state game_state.json
python engine.py identity  --state game_state.json
python engine.py narrative --state game_state.json
python engine.py world_state  --state game_state.json
python engine.py panarchy  --state game_state.json
python engine.py moral_update   --state game_state.json
python engine.py cognition   --state game_state.json --entity player
python engine.py merit     --state game_state.json --aid 0.8 --sincerity 0.9
python engine.py info_weight --state game_state.json --probability 0.05
```

---

## 项目结构

```
game_engine/                      # 仓库根即 game_engine 包（导入别名已放开，目录名任意）
├── engine.py                     # CLI 入口（14 条命令）
├── mcp_server.py                 # MCP 服务器（27 个工具；除 mcp>=2 外无额外依赖）
├── state_schema.py               # 状态结构 + 辅助函数
├── init_game.py                  # 生成示例世界（青云界）
├── pyproject.toml                # pip install -e ".[mcp]"；命令 world-walker / world-walker-mcp
├── scripts/verify_mcp_stdio.py   # MCP 端到端自检（38 项断言，含酒馆生态兼容/图鉴/面板与确定性）
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
