"""
经济结算规则 (Economy)

价格 = base_price × (demand_base / supply_current) × market_events_multiplier

大宗交易后价格回归: 每回合 base_price 缓慢复位
"""

import math

DEFAULT_BASE_PRICES = {
    "回灵丹": 50,
    "金疮药": 30,
    "辟谷丹": 20,
    "灵石": 100,
    "凝气丸": 80,
    "辟尘符": 40,
}

def init_market(location_id, items=None):
    """初始化一个市场"""
    if items is None:
        items = ["回灵丹", "金疮药", "辟谷丹"]
    market = {}
    for item in items:
        market[item] = {
            "price": DEFAULT_BASE_PRICES.get(item, 50),
            "supply": 20,
            "base_price": DEFAULT_BASE_PRICES.get(item, 50)
        }
    return market

def resolve_trade(state, location_id, item, quantity, is_buyer, entity_id):
    """
    结算一次交易
    
    参数:
        is_buyer: True=玩家购买, False=玩家卖出
        entity_id: 交易方 entity id
    
    返回: {
        "success": true,
        "price_per_unit": 50,
        "total_cost": 100,
        "price_after": 52,    # 交易后新价格
        "supply_after": 18,
        "events": ["玩家购买回灵丹×2，花费100灵石"]
    }
    """
    cur = state.get("currency", "灵石")   # 世界观无关：货币名由状态给出（玄晶/灵石/信用点…）
    loc_market = state.get("market", {}).get(location_id)
    result = {
        "success": False,
        "price_per_unit": 0,
        "total_cost": 0,
        "price_after": 0,
        "supply_after": 0,
        "events": []
    }
    
    if quantity <= 0:
        result["events"].append("交易数量必须为正")
        return result

    if not loc_market or item not in loc_market:
        result["events"].append(f"此地没有{item}")
        return result
    
    ent = state["entities"].get(entity_id)
    if not ent:
        result["events"].append("交易方不存在")
        return result
    
    item_data = loc_market[item]
    
    # 大宗交易引起的价格波动
    supply_ratio = quantity / max(1, item_data["supply"])
    
    if is_buyer:
        if item_data["supply"] < quantity:
            result["events"].append(f"库存不足(只剩{item_data['supply']}个)")
            return result
        
        # 价格随购买量上升
        price_multiplier = 1.0 + supply_ratio * 0.2
        price = int(item_data["price"] * min(price_multiplier, 1.5))
        total = price * quantity
        
        if ent.get("gold", 0) < total:
            result["events"].append(f"{cur}不足(需要{total}，只有{ent.get('gold', 0)})")
            return result
        
        # 执行交易
        ent["gold"] -= total
        item_data["supply"] -= quantity
        # 价格更新
        item_data["price"] = int(item_data["price"] * (1 + supply_ratio * 0.05))
        
        result["success"] = True
        result["price_per_unit"] = price
        result["total_cost"] = total
        result["price_after"] = item_data["price"]
        result["supply_after"] = item_data["supply"]
        result["events"].append(
            f"{ent['name']}购买{item}×{quantity}，花费{total}{cur}"
        )
        
        # 大宗交易影响关系 (坊主印象)
        if quantity >= 5:
            result["events"].append(f"坊主注意到了{ent['name']}的大额购买")
            result["relation_hint"] = "merchant"
    else:
        # 卖出
        price_multiplier = max(0.5, 1.0 - supply_ratio * 0.15)
        price = int(item_data["price"] * price_multiplier)
        total = price * quantity
        
        ent["gold"] = ent.get("gold", 0) + total
        item_data["supply"] += quantity
        item_data["price"] = int(item_data["price"] * (1 - supply_ratio * 0.03))
        item_data["price"] = max(item_data["base_price"] // 2, item_data["price"])
        
        result["success"] = True
        result["price_per_unit"] = price
        result["total_cost"] = total
        result["price_after"] = item_data["price"]
        result["supply_after"] = item_data["supply"]
        result["events"].append(
            f"{ent['name']}出售{item}×{quantity}，获得{total}{cur}"
        )
    
    return result

def tick_market(state):
    """每回合结束时价格缓慢回归 base_price"""
    for loc_id, loc_market in state.get("market", {}).items():
        for item, data in loc_market.items():
            if data["price"] > data["base_price"]:
                data["price"] = max(data["base_price"], int(data["price"] * 0.95))
            elif data["price"] < data["base_price"]:
                data["price"] = min(data["base_price"], int(data["price"] * 1.05))
            # 供给缓慢恢复
            if data["supply"] < 20:
                data["supply"] += 1
