#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
码译 · VibeCode —— 零依赖 MCP Server（Model Context Protocol）
===========================================================
让 Cursor / Claude / 任意支持 MCP 的客户端，直接查询本仓库的前端组件术语库。

特性
----
- 纯 Python 标准库，无需 pip install（Python 3.8+）。
- 读取仓库内的 data/terms.json，URL slug 复刻 gen_vibecode.py 算法，与线上一致。
- 提供两个工具：search_vibecode_terms（检索）、get_vibecode_term（取详情）。

运行
----
    python mcp/vibecode_mcp.py
（作为 MCP server 由客户端以 stdio 方式拉起，无需手动运行）

调试（手动发一条 JSON-RPC 看返回）
    echo '{"jsonrpc":"2.0","id":1,"method":"tools/list"}' | python mcp/vibecode_mcp.py
"""
import sys
import os
import io
import re
import json
import ast

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TERMS_PATH = os.path.join(ROOT, "data", "terms.json")
SITE_BASE = os.environ.get("VIBECODE_SITE_BASE", "https://mayi-vibecode.pages.dev").rstrip("/")

# ---- 解析 gen_vibecode.py 的 CHAPTER_SLUG（保证 slug 预留与站点一致） ----
CHAPTER_SLUG = {0: "nav", 1: "layout", 2: "sizing", 3: "positioning", 4: "interaction",
                 5: "responsive", 6: "performance", 7: "forms", 8: "buttons",
                 9: "overlays", 10: "motion"}


def _load_chapter_slug():
    gp = os.path.join(ROOT, "gen_vibecode.py")
    if not os.path.exists(gp):
        return
    try:
        src = open(gp, encoding="utf-8").read()
        m = re.search(r"CHAPTER_SLUG\s*=\s*\{(.*?)\}", src, re.S)
        if m:
            CHAPTER_SLUG.update(ast.literal_eval("{" + m.group(1) + "}"))
    except Exception:
        pass


_load_chapter_slug()


def dv_slug(en):
    s = (en or "").lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")


def _slug_unique(base, seen):
    s = base
    n = 2
    while s in seen:
        s = "%s-%d" % (base, n)
        n += 1
    seen.add(s)
    return s


def load_terms():
    if not os.path.exists(TERMS_PATH):
        return [], {}
    data = json.load(open(TERMS_PATH, encoding="utf-8"))
    terms = data.get("terms", [])
    seen = set(CHAPTER_SLUG.values())
    idx = {}
    for t in terms:
        tid = t.get("id")
        slug = _slug_unique(dv_slug(t.get("en", "")), seen)
        idx[tid] = {"term": t, "slug": slug}
    return terms, idx


TERMS, IDX = load_terms()


def _haystack(t):
    parts = [str(t.get(k, "")) for k in ("cn", "en", "speak", "anti", "fix", "id")]
    plat = t.get("plat") or {}
    if isinstance(plat, dict):
        parts += [str(v) for v in plat.values()]
    return " ".join(parts).lower()


def _term_card(t, slug):
    """把一条术语整理成 LLM 易读的文本卡片。"""
    url = "%s/%s/" % (SITE_BASE, slug)
    tip = t.get("tip") or []
    if not isinstance(tip, list):
        tip = [str(tip)]
    plat = t.get("plat") or {}
    lines = [
        "# %s (%s)" % (t.get("cn", ""), t.get("en", "")),
        "",
        "- URL: %s" % url,
        "- 大白话: %s" % (t.get("speak") or ""),
        "- 反模式: %s" % (t.get("anti") or ""),
        "- 修复: %s" % (t.get("fix") or ""),
    ]
    for tp in tip:
        lines.append("- 提示: %s" % tp)
    if isinstance(plat, dict):
        for kk, vv in plat.items():
            if vv:
                lines.append("- %s 平台: %s" % (kk, vv))
    lines.append("- 可复制提示词: 用大白话描述「%s」，直接产出可运行的前端代码与组件。" % (t.get("speak") or t.get("cn", "")))
    return "\n".join(lines)


def search_terms(query, limit=10):
    q = (query or "").strip().lower()
    if not q:
        return "请输入检索词，例如：吸顶、sticky、modal、无障碍。"
    hits = []
    for t in TERMS:
        if q in _haystack(t):
            slug = IDX[t.get("id")]["slug"]
            hits.append("- [%s (%s)](%s/%s/)：%s" % (
                t.get("cn", ""), t.get("en", ""), SITE_BASE, slug, (t.get("speak") or "")[:60]))
        if len(hits) >= limit:
            break
    if not hits:
        return "未找到与「%s」相关的前端术语。可换个说法，或检索章节：导航/布局/表单/按钮/动效/响应式/无障碍。" % query
    header = "检索「%s」命中 %d 条（展示前 %d）：\n" % (query, len(hits), len(hits))
    return header + "\n".join(hits)


def get_term(name):
    key = (name or "").strip().lower()
    if not key:
        return "请提供术语名称、英文名、slug 或 id，例如：modal-dialog / 模态对话框 / sticky-header-affix-navbar。"
    # 1) 按 id / slug 精确
    if key in IDX:
        t = IDX[key]["term"]
        return _term_card(t, IDX[key]["slug"])
    # 2) 按 en/cn 精确或包含
    for t in TERMS:
        en = (t.get("en") or "").lower()
        cn = (t.get("cn") or "").lower()
        if key == en or key == cn or key == dv_slug(t.get("en", "")):
            return _term_card(t, IDX[t.get("id")]["slug"])
    # 3) 包含匹配，取第一条
    for t in TERMS:
        if key in _haystack(t):
            return _term_card(t, IDX[t.get("id")]["slug"])
    return "未找到术语「%s」。可用 search_vibecode_terms 先检索。" % name


# ===================== MCP 传输层（stdio + Content-Length 帧） =====================
def _read_message(rbuf):
    headers = {}
    while True:
        line = rbuf.readline()
        if not line:
            return None
        if isinstance(line, bytes):
            line = line.decode("utf-8")
        line = line.rstrip("\r\n")
        if line == "":
            break
        if ":" in line:
            k, v = line.split(":", 1)
            headers[k.strip().lower()] = v.strip()
    cl = headers.get("content-length")
    if cl is None:
        return None
    n = int(cl)
    body = rbuf.read(n)
    if isinstance(body, bytes):
        body = body.decode("utf-8")
    return json.loads(body)


def _write_message(wbuf, msg):
    body = json.dumps(msg, ensure_ascii=False).encode("utf-8")
    wbuf.write(("Content-Length: %d\r\n\r\n" % len(body)).encode("utf-8"))
    wbuf.write(body)
    wbuf.flush()


TOOLS = [
    {
        "name": "search_vibecode_terms",
        "description": "检索码译·VibeCode 前端组件术语库。当用户问到前端组件、CSS 布局、交互、响应式、无障碍等概念时调用。"
                       "支持中文名、英文名、大白话释义、反模式、平台差异等关键词。返回相关术语的中文名、英文名、链接与一句话释义。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "检索词，如「吸顶」「sticky」「modal」「无障碍」「z-index」"},
                "limit": {"type": "integer", "description": "最多返回条数，默认 10", "default": 10}
            },
            "required": ["query"]
        }
    },
    {
        "name": "get_vibecode_term",
        "description": "获取某条前端术语的完整解释：大白话释义、反模式、修复建议、平台差异、可复制提示词。"
                       "参数可以是中文名、英文名、slug 或 id。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "术语名称/英文名/slug/id，如「模态对话框」「modal-dialog」「sticky-header-affix-navbar」"}
            },
            "required": ["name"]
        }
    }
]


def _handle(msg):
    method = msg.get("method")
    mid = msg.get("id")
    if method == "initialize":
        return {"jsonrpc": "2.0", "id": mid, "result": {
            "protocolVersion": "2024-11-05",
            "capabilities": {"tools": {}},
            "serverInfo": {"name": "vibecode-mcp", "version": "1.0.0"}
        }}
    if method == "ping":
        return {"jsonrpc": "2.0", "id": mid, "result": {}}
    if method == "tools/list":
        return {"jsonrpc": "2.0", "id": mid, "result": {"tools": TOOLS}}
    if method == "tools/call":
        name = msg.get("params", {}).get("name")
        args = msg.get("params", {}).get("arguments", {}) or {}
        if name == "search_vibecode_terms":
            text = search_terms(args.get("query", ""), int(args.get("limit", 10) or 10))
        elif name == "get_vibecode_term":
            text = get_term(args.get("name", ""))
        else:
            text = "未知工具：%s" % name
        return {"jsonrpc": "2.0", "id": mid, "result": {
            "content": [{"type": "text", "text": text}],
            "isError": False
        }}
    # 未知方法 / 通知：不返回（通知无 id）
    return None


def main():
    rbuf = sys.stdin.buffer
    wbuf = sys.stdout.buffer
    while True:
        try:
            msg = _read_message(rbuf)
        except Exception as e:
            sys.stderr.write("read error: %s\n" % e)
            break
        if msg is None:
            break
        # 通知（无 id）不回复
        resp = _handle(msg)
        if resp is not None and msg.get("id") is not None:
            _write_message(wbuf, resp)


if __name__ == "__main__":
    main()
