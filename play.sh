#!/bin/bash
# 万界 · 行者 — 快速启动脚本
# ./play.sh           运行所有命令演示
# ./play.sh --state F  指定状态文件 (默认 game_state.json)

STATE="${2:-game_state.json}"
export PYTHONPATH=.

echo "=== 万界 · 行者 | 第 $(python3 -c "import json;print(json.load(open('$STATE')).get('tick',0))") 回合 ==="
echo ""

case "$1" in
  combat)
    python3 engine.py combat --state "$STATE" --attacker player --defender "${3:-goblin}"
    ;;
  trade)
    python3 engine.py trade --state "$STATE" --location "${3:-bamboo_tea_booth}" --item "${4:-an_zhen_san}" --quantity "${5:-1}" --direction "${6:-buy}" --entity player
    ;;
  social)
    python3 engine.py social --state "$STATE" --actor player --target "${3:-old_chen}" --event "${4:-help}"
    ;;
  karma)
    python3 engine.py karma --state "$STATE" --actor player --karma_type "${3:-help_innocent}"
    ;;
  tick)
    python3 engine.py tick --state "$STATE"
    ;;
  world)
    python3 engine.py world_state --state "$STATE"
    ;;
  narrative)
    python3 engine.py narrative --state "$STATE"
    ;;
  flow)
    python3 engine.py flow --state "$STATE"
    ;;
  panarchy)
    python3 engine.py panarchy --state "$STATE"
    ;;
  identity)
    python3 engine.py identity --state "$STATE"
    ;;
  moral)
    python3 engine.py moral_update --state "$STATE"
    ;;
  cognition)
    python3 engine.py cognition --state "$STATE" --entity player
    ;;
  merit)
    python3 engine.py merit --state "$STATE" --aid "${3:-1.0}" --sincerity "${4:-1.0}"
    ;;
  info)
    python3 engine.py info_weight --state "$STATE" --probability "${3:-0.1}"
    ;;
  init)
    python3 init_game.py
    ;;
  *)
    echo "用法: ./play.sh <command> [--state FILE] [args]"
    echo ""
    echo "可用命令:"
    echo "  combat    trade    social    karma     tick"
    echo "  world     narrative  flow    panarchy  identity"
    echo "  moral     cognition  merit   info      init"
    ;;
esac
