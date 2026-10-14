#!/usr/bin/env python3
"""
万界·行者 · MCP 服务器 (World Walker MCP Server)

把规则引擎包装成 MCP 工具，供任意 MCP 客户端（Claude Code / Codex / Cursor / 自建 Agent）
驱动一局文字对话互动游戏：读设定 → world_init 建世界 → 玩家每步行动都经引擎结算 →
Agent 只负责把引擎返回的 JSON 转写成文学描写。

设计约束（与 GAME_MASTER_PROTOCOL.md 一致）:
- 所有数值结算必须走引擎工具，Agent 不得手写 state JSON
- state 落盘为 JSON 文件，对局可中断续跑；服务器另记"当前对局"路径
- 可选种子: 同一 state + 同一 tick + 同一行动 → 同一结果（rng_seed）

World Walker rule engine exposed over MCP. The host agent narrates; the engine decides.
"""

import json
import os
import random
import sys

# 引擎内部用 `import game_engine.*`，要求仓库目录名恰好是 game_engine。
# 这里注册包别名，使任意克隆目录名 / pip 安装方式都能工作。
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if "game_engine" not in sys.modules:
    import importlib.util

    _spec = importlib.util.spec_from_file_location(
        "game_engine",
        os.path.join(_SCRIPT_DIR, "__init__.py"),
        submodule_search_locations=[_SCRIPT_DIR],
    )
    _engine_pkg = importlib.util.module_from_spec(_spec)
    _engine_pkg.__path__ = [_SCRIPT_DIR]
    sys.modules["game_engine"] = _engine_pkg

from mcp.server.mcpserver import MCPServer

from game_engine.rules.cognition import daily_cognitive_budget, should_use_system2
from game_engine.rules.combat import resolve_combat
from game_engine.rules.economy import resolve_trade, tick_market
from game_engine.rules.karma import get_karma_consequence, resolve_karma
from game_engine.rules.narrative_engine import (
    check_world_emergent_events,
    flow_channel_status,
    panarchy_phase_check,
    player_identity_vector,
    update_player_moral_identity,
)
from game_engine.rules.social import resolve_social_event
from game_engine.rules.social_extended import merit_quality
from game_engine.rules.world_dynamics import event_information
from game_engine.state_schema import entity_key, load_state, log_event, save_state

from pydantic import BaseModel, Field


class WorldInfo(BaseModel):
    """世界基本盘（设定里的世界观信息）。"""
    name: str = Field(description="世界名，如「临江渡口」「青云界」")
    era: str = Field(default="", description="纪元/时代，如「江湖历三年」")
    location_desc: str = Field(default="", description="开场地点描写（两三句，用于开局叙事）")


class EntityIn(BaseModel):
    """一个角色。主角用 player 参数传入；NPC 放进 entities 数组并给 id。"""
    id: str | None = Field(default=None, description="实体 id（NPC 必填；player 不用填）")
    name: str = Field(description="显示名")
    faction: str = Field(default="", description="阵营/势力")
    attrs: dict[str, int] = Field(default_factory=dict,
                                 description="五维属性 str/dex/int/con/cha，缺省按 10")
    hp: int | None = Field(default=None, description="当前生命，缺省等于 hp_max")
    hp_max: int = Field(default=100, description="生命上限")
    mp: int = Field(default=0, description="当前内力/法力")
    mp_max: int = Field(default=0, description="内力上限")
    level: str = Field(default="凡人", description="境界/等级，如「练气三层」「一流高手」「C-class」")
    gold: int = Field(default=0, description="钱财")
    location: str = Field(default="", description="所在地（要与 market 的 location 一致才可交易）")
    skills: list[str] = Field(default_factory=list, description="技能名（可选）")
    morality: list[int] = Field(default_factory=list, description="六维道德向量（可选，默认全 0）")


class MarketItemIn(BaseModel):
    """市场里的一件商品。交易工具用 key 定位它（不是显示名）。"""
    key: str = Field(description="商品 key，交易时传它，如 chen_jiu")
    name: str = Field(description="显示名，如「陈酒」")
    price: int = Field(default=50, description="当前价")
    supply: int = Field(default=20, description="库存")
    base_price: int | None = Field(default=None, description="基准价（价格会回归它），缺省等于 price")
    type: str = Field(default="", description="类别（丹药/武器/情报…）")
    desc: str = Field(default="", description="一句话描述")


class MarketIn(BaseModel):
    """一个地点的市场。"""
    location: str = Field(description="地点（与角色的 location 一致）")
    items: list[MarketItemIn] = Field(default_factory=list, description="该地点的商品")


class RelationIn(BaseModel):
    """一条关系（键由引擎按字母序生成，不用你操心顺序）。"""
    a: str = Field(description="实体 id 之一")
    b: str = Field(description="实体 id 之二")
    affinity: int = Field(default=0, description="亲密度 -100~100")
    respect: int = Field(default=0, description="敬重/畏惧 -100~100")


server = MCPServer(
    name="world-walker",
    version="0.3.0",
    instructions=(
        "万界·行者规则引擎：世界观无关的因果推演内核。主持文字互动游戏时："
        "先 world_schema 了解状态结构，按玩家设定调用 world_init 建世界；"
        "玩家的每个行动都交给对应工具结算，你只把返回的 JSON 转写成文学描写，"
        "不得自行编造数值结果；回合结束调用 tick；每 3-5 回合调用 narrative 与 status 一次。"
    ),
)

NEW_GAME_BRIEF = """你在主持一局文字互动游戏，数值结算必须全部通过 world-walker 的工具完成。

## 铁律
1. 所有数值（命中/伤害/价格/关系/因果）必须由工具结算，不许自行编造或心算。
2. 玩家只该看到你的文学描写；JSON 与字段名不要让玩家看到，数值要自然融进叙事。
3. 不要手改状态文件，一切变更都经工具落盘。

## 回合流程
- 开局：`world_init`（设定与状态文件路径见下）→ 写两三百字开场（可用 world_info.location_desc）。
- 每个玩家行动：需要时 `read_state` 看现状 → 选对应工具结算（combat / trade / social / karma）
  → 把返回 JSON 转写成文学描写。
- 回合收尾：`tick`。
- 每 3-5 回合：`narrative`（涌现事件与相位）与 `status`（心流/身份/道德/认知）各一次，
  把结果织进叙事节奏（例如心流偏低就安排一段缓冲剧情）。
- 字段不清楚时先 `world_schema` 查（world_init 的入参 schema 已带字段说明，通常不必查）。

## 本次设定
{setting}

## 状态文件
{state_path}（seed={seed}，同种子可复现）

现在开始：先 `world_init` 开起这局，然后写开场。"""


@server.prompt(name="new_game", title="开一局新游戏",
               description="把设定交给规则引擎，开始一局文字互动游戏。参数 setting 填你的设定（世界观/主角/NPC/地点/商品表）")
def new_game(setting: str, state_path: str = "ww_state.json", seed: int = 20261014) -> str:
    """生成「开局指令」：协议 + 你的设定 + 状态文件，客户端把它作为一条用户消息发给 Agent。"""
    return (NEW_GAME_BRIEF.replace("{setting}", setting.strip())
                         .replace("{state_path}", state_path)
                         .replace("{seed}", str(seed)))


_active = {"path": None}
ATTR_KEYS = ("str", "dex", "int", "con", "cha")
SOCIAL_EVENTS = ("help", "harm", "threaten", "intimidate", "gift", "betray",
                 "cooperate", "insult", "praise", "murder")
KARMA_TYPES = ("murder_innocent", "murder_evil", "theft", "lie", "betray",
               "help_innocent", "help_evil", "repay_debt", "oath_broken")


def _state_path() -> str:
    if not _active["path"]:
        raise ValueError("当前没有进行中的对局：先调用 world_init（新建）或 world_open（续跑）")
    return _active["path"]


def _load() -> dict:
    return load_state(_state_path())


def _finish(state: dict, result: dict) -> dict:
    """状态落盘，并在返回给 Agent 的结果上标注当前 tick。"""
    save_state(state, _state_path())
    result["_tick"] = state.get("tick", 0)
    return result


def _seed_rng(state: dict) -> None:
    """带种子可复现：同一 state、同一计数器、同一行动 → 同一结果。

    计数器随每次结算递增并落盘，保证同一回合内的多次行动不会复用同一段随机序列。
    """
    seed = state.get("rng_seed")
    if seed is None:
        return
    counter = int(state.get("rng_counter", 0)) + 1
    state["rng_counter"] = counter
    mixed = (int(seed) * 1000003 + int(state.get("tick", 0)) * 7919 + counter) % (2 ** 32)
    random.seed(mixed)
    try:
        import numpy as np
        np.random.seed(mixed)
    except Exception:
        pass


def _require_entity(state: dict, entity_id: str, role: str) -> dict:
    ent = state.get("entities", {}).get(entity_id)
    if not ent:
        raise ValueError("%s不存在: %s（当前实体: %s）" % (role, entity_id, ", ".join(state.get("entities", {}))))
    return ent


def _normalize_entity(entity_id: str, raw: dict) -> dict:
    if not isinstance(raw, dict) or not raw.get("name"):
        raise ValueError("实体 %s 缺少 name" % entity_id)
    attrs = dict(raw.get("attrs") or {})
    for k in ATTR_KEYS:
        v = attrs.get(k, 10)
        if not isinstance(v, (int, float)):
            raise ValueError("实体 %s 的属性 %s 必须是数字" % (entity_id, k))
        attrs[k] = int(v)
    hp_max = int(raw.get("hp_max", 100))
    mp_max = int(raw.get("mp_max", 0))
    ent = {
        "name": str(raw["name"]),
        "faction": str(raw.get("faction", "")),
        "attrs": attrs,
        "hp": int(raw.get("hp", hp_max)),
        "hp_max": hp_max,
        "mp": int(raw.get("mp", mp_max)),
        "mp_max": mp_max,
        "level": str(raw.get("level", "凡人")),
        "gold": int(raw.get("gold", 0)),
        "location": str(raw.get("location", "")),
    }
    if raw.get("skills"):
        ent["skills"] = list(raw["skills"])
    if raw.get("morality"):
        ent["morality"] = list(raw["morality"])[:6]
    return ent


@server.tool()
def world_schema() -> dict:
    """返回世界状态的数据结构说明（Chinese: 供 Agent 按玩家设定构造 world_init 入参）。
    Schema reference for building world_init arguments."""

    return {
        "state_fields": {
            "tick": "回合数（整数，引擎维护）",
            "rng_seed": "随机种子（整数，决定可复现性）",
            "world_info": {"name": "世界名", "era": "纪元", "location_desc": "开场地点描写"},
            "entities": "entity_id -> 实体对象（见 entity_shape）",
            "relations": "关系表，键为 'a:b'（字母序，引擎自动生成），值为 {affinity, respect}（-100~100）",
            "market": "location -> {item_key -> item_shape}；交易工具用 item_key 而非 name",
            "karma_ledger": "因果债流水（引擎维护）",
            "world_flags": "已触发的世界事件标记（字符串数组）",
            "event_log": "最近事件（引擎维护，最多 50 条）",
        },
        "entity_shape": {
            "name": "显示名（必填）",
            "faction": "阵营/势力",
            "attrs": {"str": "力量", "dex": "敏捷", "int": "悟性/智力", "con": "体质", "cha": "魅力"},
            "hp": "当前生命", "hp_max": "生命上限",
            "mp": "当前内力/法力", "mp_max": "内力上限",
            "level": "境界/等级（如 '练气三层'、'一流高手'、'C-class'）",
            "gold": "钱财",
            "location": "所在地（需与 market 的 location 键一致才可交易）",
            "skills": "技能名数组（可选）",
            "morality": "六维道德向量（可选，默认 [0,0,0,0,0,0]）",
        },
        "market_item_shape": {
            "name": "显示名（如 '安神丹'）", "price": "当前价", "supply": "库存",
            "base_price": "基准价（价格会回归它）", "type": "类别", "desc": "描述",
        },
        "world_init_args": {
            "state_path": "状态文件路径，默认 ww_state.json",
            "world": "{name, era, location_desc}",
            "player": "entity_shape（id 固定为 'player'）",
            "entities": "[{id, ...entity_shape}]，NPC 列表",
            "market": "[{location, items: [{key, ...market_item_shape}]}]",
            "relations": "[{a, b, affinity, respect}]（键由引擎按字母序生成）",
            "world_flags": "字符串数组（可选）",
            "seed": "整数种子（可选，默认 20261014）",
        },
        "action_tools": {
            "combat": "attacker/defender/action_type(attack|heavy|flee)/skill",
            "trade": "location/item_key/quantity/direction(buy|sell)/entity",
            "social": "actor/target/event(%s)/intensity" % "|".join(SOCIAL_EVENTS),
            "karma": "actor/victim(可空)/karma_type(%s)" % "|".join(KARMA_TYPES),
            "tick": "回合结束（市场演化 + tick+1）",
            "narrative": "涌现事件 + 世界相位（每 3-5 回合查一次）",
            "status": "心流/身份/相位/道德/认知 聚合（每 3-5 回合查一次）",
            "merit": "功德值（纯函数：aid 救助 0~1, sincerity 诚心 0~1）",
            "narrative_weight": "事件叙事权重 = -log P(事件)（纯函数）",
        },
    }


@server.tool()
def world_init(state_path: str, world: WorldInfo, player: EntityIn,
               entities: list[EntityIn] | None = None, market: list[MarketIn] | None = None,
               relations: list[RelationIn] | None = None, world_flags: list[str] | None = None,
               seed: int = 20261014) -> dict:
    """按玩家设定创建一局新游戏并写盘（Chinese: 设定 → 世界状态；创建后即成为当前对局）。
    Create a new game from the player's setting bible and make it the active session."""

    state_entities = {"player": _normalize_entity("player", player.model_dump(exclude_none=True))}
    for npc in entities or []:
        raw = npc.model_dump(exclude_none=True)
        eid = str(raw.get("id") or "").strip()
        if not eid:
            raise ValueError("entities 里每个 NPC 都必须有 id")
        if eid == "player":
            raise ValueError("entities 里不要重复定义 player")
        state_entities[eid] = _normalize_entity(eid, raw)

    state_market = {}
    for loc in market or []:
        items = {}
        for item in loc.items:
            d = item.model_dump(exclude_none=True)
            items[item.key] = {
                "name": d.get("name", item.key),
                "price": int(d.get("price", 50)),
                "supply": int(d.get("supply", 20)),
                "base_price": int(d.get("base_price", d.get("price", 50))),
                "type": str(d.get("type", "")),
                "desc": str(d.get("desc", "")),
            }
        state_market[loc.location] = items

    state_relations = {}
    for rel in relations or []:
        for eid in (rel.a, rel.b):
            if eid not in state_entities:
                raise ValueError("关系引用了不存在的实体: %s" % eid)
        state_relations[entity_key(rel.a, rel.b)] = {
            "affinity": int(rel.affinity),
            "respect": int(rel.respect),
        }

    state = {
        "tick": 0,
        "rng_seed": int(seed),
        "entities": state_entities,
        "relations": state_relations,
        "market": state_market,
        "karma_ledger": [],
        "world_flags": list(world_flags or []),
        "event_log": [],
        "world_info": {
            "name": world.name,
            "era": world.era,
            "location_desc": world.location_desc,
        },
    }
    log_event(state, "system", "世界「%s」开局：%s" % (state["world_info"]["name"],
                                                  state["world_info"]["location_desc"] or "旅程开始"))

    _active["path"] = os.path.abspath(state_path)
    save_state(state, _active["path"])
    return {
        "state_path": _active["path"],
        "world": state["world_info"]["name"],
        "entities": len(state["entities"]),
        "market_locations": sorted(state_market),
        "relations": len(state_relations),
        "seed": int(seed),
        "message": "世界已创建。玩家所在位置: %s" % state_entities["player"].get("location", ""),
    }


@server.tool()
def world_open(state_path: str) -> dict:
    """打开已有状态文件继续对局（Chinese: 断点续跑）。Resume a saved game state."""

    if not os.path.exists(state_path):
        raise ValueError("状态文件不存在: %s" % state_path)
    state = load_state(state_path)
    _active["path"] = os.path.abspath(state_path)
    return {
        "state_path": _active["path"],
        "tick": state.get("tick", 0),
        "world": (state.get("world_info") or {}).get("name", ""),
        "entities": sorted(state.get("entities", {})),
    }


@server.tool()
def read_state() -> dict:
    """返回当前对局的完整状态 JSON（Chinese: Agent 读它来决定调用哪个行动工具）。
    Full state of the active game."""

    return _load()


@server.tool()
def combat(attacker: str, defender: str, action_type: str = "attack",
           skill: dict | None = None) -> dict:
    """结算一次战斗（Chinese: action_type 取 attack|heavy|flee；skill 形如 {name, power, mp_cost}）。
    Resolve one combat exchange."""

    if action_type not in ("attack", "heavy", "flee"):
        raise ValueError("action_type 只能是 attack / heavy / flee")
    state = _load()
    _seed_rng(state)
    _require_entity(state, attacker, "攻击方")
    _require_entity(state, defender, "防守方")
    result = resolve_combat(state, attacker, defender, action_type, skill)
    for e in result.get("events", []):
        log_event(state, "combat", e)
    return _finish(state, result)


@server.tool()
def trade(location: str, item: str, direction: str, quantity: int = 1,
          entity: str = "player") -> dict:
    """结算一次交易（Chinese: item 传市场里的 item_key，不是显示名；direction 取 buy|sell）。
    Settle one trade at a market location."""

    if direction not in ("buy", "sell"):
        raise ValueError("direction 只能是 buy / sell")
    state = _load()
    _seed_rng(state)
    _require_entity(state, entity, "交易方")
    if location not in state.get("market", {}):
        raise ValueError("此地没有市场: %s（可用: %s）" % (location, ", ".join(state.get("market", {}))))
    result = resolve_trade(state, location, item, int(quantity), direction == "buy", entity)
    for e in result.get("events", []):
        log_event(state, "trade", e)
    return _finish(state, result)


@server.tool(description="结算一次社交事件并更新关系：event 取 "
                       + "|".join(SOCIAL_EVENTS) + "，intensity 为强度倍率。Settle a social event.")
def social(actor: str, target: str, event: str, intensity: float = 1.0) -> dict:

    if event not in SOCIAL_EVENTS:
        raise ValueError("event 只能是: %s" % ", ".join(SOCIAL_EVENTS))
    state = _load()
    _seed_rng(state)
    _require_entity(state, actor, "发起方")
    _require_entity(state, target, "目标")
    result = resolve_social_event(state, actor, target, event, float(intensity))
    for e in result.get("events", []):
        log_event(state, "social", e)
    return _finish(state, result)


@server.tool(description="记录一次因果债：karma_type 取 " + "|".join(KARMA_TYPES)
                       + "，victim 可为空（无具体受害者时）。Record causal debt.")
def karma(actor: str, karma_type: str, victim: str | None = None) -> dict:

    if karma_type not in KARMA_TYPES:
        raise ValueError("karma_type 只能是: %s" % ", ".join(KARMA_TYPES))
    state = _load()
    _seed_rng(state)
    _require_entity(state, actor, "行动者")
    if victim:
        _require_entity(state, victim, "受害方")
    result = resolve_karma(state, actor, victim, karma_type)
    for e in result.get("events", []):
        log_event(state, "karma", e)
    consequence = get_karma_consequence(state, actor)
    if consequence["triggered"]:
        result["karma_consequence"] = consequence
    return _finish(state, result)


@server.tool()
def tick() -> dict:
    """推进一个回合：市场演化 + tick+1（Chinese: 每回合结束时调用一次）。Advance one turn."""

    state = _load()
    _seed_rng(state)
    tick_market(state)
    state["tick"] = state.get("tick", 0) + 1
    log_event(state, "tick", "回合%d结束" % state["tick"])
    return _finish(state, {"events": ["回合%d结束" % state["tick"]]})


@server.tool()
def narrative() -> dict:
    """检查世界的涌现事件与相位（Chinese: 每 3-5 回合调用一次，用于埋设伏笔）。
    Emergent world events and the current world phase."""

    state = _load()
    _seed_rng(state)
    events = check_world_emergent_events(state)
    phase = panarchy_phase_check(state)
    for e in events:
        desc = e.get("desc") or e.get("type", "")
        log_event(state, "emergent", str(desc))
    return _finish(state, {"emergent_events": events, "panarchy_phase": phase})


@server.tool()
def status() -> dict:
    """聚合玩家的心理/身份/道德与世界相位（Chinese: 心流、Bartle 身份、六维道德、认知预算）。
    Aggregated insights: flow, identity, morality, world phase, cognition."""

    state = _load()
    _seed_rng(state)
    player = state.get("entities", {}).get("player", {})
    attrs = player.get("attrs", {})
    realm_level = int(attrs.get("int", 10) // 5)
    budget = daily_cognitive_budget(realm_level, "正常")
    return _finish(state, {
        "flow": flow_channel_status(state),
        "identity": player_identity_vector(state),
        "panarchy_phase": panarchy_phase_check(state),
        "moral_vector": update_player_moral_identity(state),
        "cognition": {
            "cognitive_budget": budget,
            "system2_likely": should_use_system2(budget, max(0.1, float(attrs.get("int", 10)) / 20)),
        },
        "unsettled_karma": sum(e["amount"] for e in state.get("karma_ledger", [])
                               if e["from"] == "player" and not e["settled"]),
    })


@server.tool()
def merit(aid: float = 0.5, sincerity: float = 0.5) -> dict:
    """功德值（Chinese: 纯函数，aid=救助程度 0~1，sincerity=诚心 0~1）。
    Merit quality of an act (pure function)."""

    return {"merit_value": merit_quality(float(aid), float(sincerity))}


@server.tool()
def narrative_weight(probability: float) -> dict:
    """事件叙事权重 = 自信息量 -log P（Chinese: 纯函数；概率越低越值得浓墨重彩）。
    Narrative weight of an event (pure function)."""

    if not (0.0 < probability <= 1.0):
        raise ValueError("probability 必须在 (0, 1] 区间")
    return {"info_weight": event_information(float(probability))}


def main() -> None:
    server.run("stdio")


if __name__ == "__main__":
    main()
