"""
状态结构定义 (State Schema)

游戏状态是一个 JSON 对象,Agent 通过 read/write 与引擎交换。
引擎本身不持有状态——它每次调用都接收完整状态 JSON，返回更新后的完整状态 JSON。
这样 Agent 只需要在游戏开始时 load_state()，每回合通过 engine 结算后 save_state()。

状态结构:
{
  "tick": 123,                    # 回合数
  "entities": {
    "player": {
      "name": "玩家",
      "faction": "散修",
      "attrs": {"str": 12, "dex": 14, "int": 10, "con": 11, "cha": 9},
      "hp": 80, "hp_max": 80,     # 生命值
      "mp": 30, "mp_max": 30,     # 法力/内力
      "level": "练气三层",
      "gold": 500,
      "location": "bamboo_tea_booth"
    },
    "old_chen": { ... }
  },
  "relations": {
    "player:old_chen": {"affinity": 10, "respect": -5},
    ...
  },
  "market": {
    "bamboo_tea_booth": {
      "回灵丹": {"price": 50, "supply": 20, "base_price": 50},
      ...
    }
  },
  "karma_ledger": [
    {"from": "player", "to": "old_chen", "type": "赊欠", "amount": 50, "tick": 120, "settled": false}
  ],
  "world_flags": ["innkeeper_dead"],   # 触发过的世界事件
  "event_log": [...]                     # 最近 N 条事件
}
"""

import json, sys

def new_game():
    """返回一个初始状态"""
    return {
        "tick": 0,
        "entities": {},
        "relations": {},
        "market": {},
        "karma_ledger": [],
        "world_flags": [],
        "event_log": []
    }

def load_state(path):
    """从路径加载状态 JSON"""
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_state(state, path):
    """保存状态 JSON 到路径"""
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

def entity_key(a, b):
    """生成关系键——保证对称性，始终按字母顺序"""
    return f"{min(a,b)}:{max(a,b)}"

def get_relation(state, a, b):
    """安全获取关系，不存在返回默认值（返回副本，避免原地修改污染）"""
    key = entity_key(a, b)
    r = state.get("relations", {}).get(key, {"affinity": 0, "respect": 0})
    return dict(r)

def _clamp(value, lo=-100, hi=100):
    """将值限制在 [lo, hi] 范围内"""
    return max(lo, min(hi, value))

def set_relation(state, a, b, affinity_delta=0, respect_delta=0):
    """更新关系值 (affinity/respect clamp 到 -100~100)"""
    key = entity_key(a, b)
    if "relations" not in state:
        state["relations"] = {}
    if key not in state["relations"]:
        state["relations"][key] = {"affinity": 0, "respect": 0}
    state["relations"][key]["affinity"] = _clamp(state["relations"][key]["affinity"] + affinity_delta)
    state["relations"][key]["respect"] = _clamp(state["relations"][key]["respect"] + respect_delta)

def add_karma(state, debtor, creditor, ktype, amount):
    """添加因果债记录"""
    entry = {
        "from": debtor,
        "to": creditor,
        "type": ktype,
        "amount": amount,
        "tick": state["tick"],
        "settled": False
    }
    state["karma_ledger"].append(entry)
    return entry

def get_unsettled_karma(state, entity):
    """获取某实体未偿还的因果债总额"""
    return sum(
        e["amount"] for e in state["karma_ledger"]
        if e["from"] == entity and not e["settled"]
    )

def log_event(state, etype, desc):
    """记录事件到日志"""
    state["event_log"].append({
        "tick": state["tick"],
        "type": etype,
        "desc": desc
    })
    # 只保留最近 50 条
    if len(state["event_log"]) > 50:
        state["event_log"] = state["event_log"][-50:]
