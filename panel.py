#!/usr/bin/env python3
"""
万界·行者 · 实况面板 (World Walker Live Panel)

一个**只读**的小型 HTTP 服务：把状态文件渲染成可以长期挂着的游戏面板
（玩家血量/心流/图鉴/编年史/市场行情实时更新）。

单独用:
    python panel.py --state ww_state.json --port 8765
由 MCP 拉起: 调工具 open_panel（会自动指向当前对局的状态文件）

端点:
    GET /        面板页面（panel.html）
    GET /state   视图模型 JSON（状态 + 引擎推导的心流/相位/身份 + 图鉴）
    GET /events  SSE：状态文件一变就推送
"""

import argparse
import json
import os
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if "game_engine" not in sys.modules:
    import importlib.util

    _spec = importlib.util.spec_from_file_location(
        "game_engine", os.path.join(_SCRIPT_DIR, "__init__.py"),
        submodule_search_locations=[_SCRIPT_DIR])
    _pkg = importlib.util.module_from_spec(_spec)
    _pkg.__path__ = [_SCRIPT_DIR]
    sys.modules["game_engine"] = _pkg

from game_engine.rules.narrative_engine import (  # noqa: E402
    flow_channel_status, panarchy_phase_check, player_identity_vector)
from game_engine.state_schema import load_state  # noqa: E402

HTML_FILE = os.path.join(_SCRIPT_DIR, "panel.html")
MORAL_DIMS = ("关怀", "公平", "忠诚", "权威", "圣洁", "自由")


def view_model(state_path):
    """把状态文件转成面板要用的视图模型（只读，不改状态）。"""
    s = load_state(state_path)
    player = s.get("entities", {}).get("player", {})
    loc = player.get("location", "")
    try:
        insights = {
            "flow": flow_channel_status(s),
            "phase": panarchy_phase_check(s),
            "identity": player_identity_vector(s),
        }
    except Exception as e:
        insights = {"error": str(e)[:120]}

    market = []
    for mLoc, items in sorted(s.get("market", {}).items()):
        rows = []
        for key, it in sorted(items.items()):
            base = it.get("base_price") or it.get("price") or 0
            price = it.get("price", 0)
            rows.append({
                "key": key, "name": it.get("name", key), "price": price,
                "base_price": base, "supply": it.get("supply", 0),
                "delta": price - base, "type": it.get("type", ""),
            })
        market.append({"location": mLoc, "items": rows})

    codex = s.get("codex", {})
    return {
        "updated_at": time.strftime("%H:%M:%S"),
        "world": s.get("world_info", {}) or {},
        "tick": s.get("tick", 0),
        "seed": s.get("rng_seed"),
        "player": {
            "name": player.get("name", "玩家"), "level": player.get("level", ""),
            "hp": player.get("hp", 0), "hp_max": player.get("hp_max", 1),
            "mp": player.get("mp", 0), "mp_max": player.get("mp_max", 0),
            "gold": player.get("gold", 0), "location": loc,
            "attrs": player.get("attrs", {}),
        },
        "insights": insights,
        "moral": {
            "dims": MORAL_DIMS,
            "values": (player.get("morality") or [0, 0, 0, 0, 0, 0])[:6],
        },
        "karma": sum(e.get("amount", 0) for e in s.get("karma_ledger", [])
                     if e.get("from") == "player" and not e.get("settled")),
        "present": [{"id": k, "name": e.get("name", k), "level": e.get("level", ""),
                     "hp": e.get("hp"), "hp_max": e.get("hp_max"),
                     "desc": (e.get("desc") or "")[:90]}
                    for k, e in s.get("entities", {}).items()
                    if k != "player" and (not loc or e.get("location") == loc)],
        "others": [{"id": k, "name": e.get("name", k), "location": e.get("location", "")}
                   for k, e in s.get("entities", {}).items() if k != "player" and e.get("location") != loc],
        "codex": {
            "locations": codex.get("locations", []),
            "people": codex.get("people", []),
            "items": codex.get("items", []),
            "lore": codex.get("lore", []),
        },
        "lore_total": len(s.get("lore", [])),
        "market": market,
        "chronicle": [e for e in s.get("event_log", [])[-24:]][::-1],
        "milestones": ["第%d回合·%s" % (m.get("tick", 0), m.get("desc", ""))
                       for m in s.get("milestones", [])[-10:]][::-1],
        "summaries": len(s.get("summaries", [])),
        "archived_events": int(s.get("archived_events", 0)),
        "flags": s.get("world_flags", []),
    }


class Handler(BaseHTTPRequestHandler):
    state_path = None

    def log_message(self, *args):  # 静音访问日志
        pass

    def _send(self, code, ctype, body):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = self.path.split("?")[0]
        if path == "/state":
            try:
                vm = json.dumps(view_model(self.state_path), ensure_ascii=False).encode("utf-8")
            except Exception as e:
                vm = json.dumps({"error": str(e)[:200]}).encode("utf-8")
            self._send(200, "application/json; charset=utf-8", vm)
        elif path == "/events":
            self._sse()
        else:
            try:
                with open(HTML_FILE, "rb") as f:
                    self._send(200, "text/html; charset=utf-8", f.read())
            except OSError:
                self._send(500, "text/plain; charset=utf-8", b"panel.html missing")

    def _sse(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream; charset=utf-8")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Connection", "keep-alive")
        self.end_headers()
        last = object()
        try:
            while True:
                try:
                    st = os.stat(self.state_path)
                    sig = (st.st_mtime_ns, st.st_size)
                except OSError:
                    sig = None
                if sig != last:
                    last = sig
                    body = json.dumps(view_model(self.state_path), ensure_ascii=False)
                    self.wfile.write(("event: state\ndata: %s\n\n" % body).encode("utf-8"))
                else:
                    self.wfile.write(b": ping\n\n")
                self.wfile.flush()
                time.sleep(0.5)
        except (BrokenPipeError, ConnectionResetError, OSError, ValueError):
            return


def start(state_path, port=8765, host="127.0.0.1"):
    """启动面板服务（后台线程），返回 (server, 实际端口)。端口被占则自动顺延。"""
    Handler.state_path = os.path.abspath(state_path)
    srv = None
    for p in range(int(port), int(port) + 10):
        try:
            srv = ThreadingHTTPServer((host, p), Handler)
            break
        except OSError:
            continue
    if srv is None:
        raise RuntimeError("端口 %s~%s 都被占用" % (port, int(port) + 9))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv, srv.server_address[1]


def main():
    ap = argparse.ArgumentParser(description="万界·行者 实况面板")
    ap.add_argument("--state", default="ww_state.json", help="状态文件路径")
    ap.add_argument("--port", type=int, default=8765)
    ap.add_argument("--host", default="127.0.0.1")
    args = ap.parse_args()
    if not os.path.exists(args.state):
        print("状态文件不存在: %s" % args.state)
        return 1
    srv, port = start(args.state, args.port, args.host)
    print("面板已启动: http://%s:%d/   （盯住 %s，Ctrl+C 退出）" % (args.host, port, args.state))
    try:
        while True:
            time.sleep(3600)
    except KeyboardInterrupt:
        srv.shutdown()
    return 0


if __name__ == "__main__":
    sys.exit(main())
