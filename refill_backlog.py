# -*- coding: utf-8 -*-
"""自动补料（档二）：当 data/term_backlog.json 低于阈值，调用 LLM 生成符合入库规则的新候选术语并写回。
仅作『补给』，不负责入库（入库由 daily_term_update.py 完成）。

无 LLM_API_KEY 时安全跳过（打印提示并退出 0），不影响日更主流程。
LLM 调用或解析异常均被捕获，绝不中断每日更新。

环境变量（来自 GitHub Secrets）：
  LLM_API_KEY   必填（启用自动补料）
  LLM_BASE_URL  可选，OpenAI 兼容端点，默认 https://api.deepseek.com/v1
  LLM_MODEL     可选，默认 deepseek-chat
  BACKLOG_TARGET可选，backlog 维持目标条数，默认 20
"""
import os
import json
import sys
import urllib.request
import urllib.error

ROOT = os.path.dirname(os.path.abspath(__file__))
BACKLOG = os.path.join(ROOT, "data", "term_backlog.json")
TARGET = int(os.environ.get("BACKLOG_TARGET", "20"))

SCHEMA_HINT = (
    "你是资深前端架构师，精通 Vibe Coding / 前端工程术语库建设。\n"
    "请输出一个 JSON 对象，形如：{\"terms\": [ ... ]}，其中每个元素是符合如下 schema 的术语：\n"
    "{\n"
    "  \"id\": \"kebab-case 唯一英文标识\",\n"
    "  \"cn\": \"中文组件名\",\n"
    "  \"en\": \"英文/平台术语\",\n"
    "  \"ch\": 0-10 整数(0导航 1布局 2尺寸 3定位 4交互 5响应式 6性能 7表单 8按钮 9弹窗 10动效),\n"
    "  \"speak\": \"大白话讲清这组件干嘛、要什么效果\",\n"
    "  \"anti\": \"常见错误写法(反模式)\",\n"
    "  \"fix\": \"正确做法\",\n"
    "  \"bad\": \"反模式代码片段\",\n"
    "  \"good\": \"正确代码片段\",\n"
    "  \"vd_bad\": \"可运行的 HTML 视觉对照(错误效果),非空\",\n"
    "  \"vd_good\": \"可运行的 HTML 视觉对照(正确效果,站点点击试用呈现),非空\",\n"
    "  \"tip\": [\"专业提示词要点1\", \"要点2\"],\n"
    "  \"plat\": {\"web\":\"网页端要点\",\"app\":\"App端要点\",\"mini\":\"小程序端要点\"}\n"
    "}\n"
    "要求：聚焦 Vibe Coding/前端/AI辅助编程的真实易错术语；vd_bad/vd_good 必须是可直接放进 <body> 运行的 HTML(可含<style>)，"
    "能直观看出对错差异；一次性生成多条，覆盖不同 ch 章节、均衡分布；只输出 JSON 对象，不要任何解释文字。"
)


def load(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def save(p, obj):
    with open(p, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


sys.path.insert(0, ROOT)
from daily_term_update import validate_term


def llm_complete(prompt):
    """调用 OpenAI 兼容端点；无 key 返回 None。异常向上抛，由 main 捕获。"""
    key = os.environ.get("LLM_API_KEY")
    if not key:
        return None
    base = os.environ.get("LLM_BASE_URL", "https://api.deepseek.com/v1").rstrip("/")
    model = os.environ.get("LLM_MODEL", "deepseek-chat")
    url = base + "/chat/completions"
    body = {
        "model": model,
        "messages": [
            {"role": "system", "content": "你是资深前端架构师，精通 Vibe Coding 术语库建设。"},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.9,
    }
    if "deepseek" in base or "openai" in base:
        body["response_format"] = {"type": "json_object"}
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(url, data=data, method="POST")
    req.add_header("Authorization", "Bearer " + key)
    req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req, timeout=120) as r:
        j = json.loads(r.read().decode("utf-8"))
    return j["choices"][0]["message"]["content"]


def main():
    try:
        bk = load(BACKLOG)
    except Exception as e:
        print("[refill] 读取 backlog 失败：%s" % e)
        return
    cur = len(bk.get("terms", []))
    if cur >= TARGET:
        print("[refill] backlog 现有 %d 条（>= 目标 %d），无需补料。" % (cur, TARGET))
        return
    need = TARGET - cur
    print("[refill] backlog 仅 %d 条，目标 %d，需补 %d 条。" % (cur, TARGET, need))
    if not os.environ.get("LLM_API_KEY"):
        print("[refill] 未设置 LLM_API_KEY，跳过自动补料。请在仓库 Secrets 配置 LLM_API_KEY"
              "（及可选 LLM_BASE_URL/LLM_MODEL/BACKLOG_TARGET）后启用。日更将只使用现有 backlog。")
        return
    prompt = SCHEMA_HINT + "\n\n请生成 %d 条新术语，输出 {\"terms\":[...]}。" % need
    try:
        raw = llm_complete(prompt)
    except Exception as e:
        print("[refill] LLM 调用异常：%s（跳过补料，不影响日更）" % e)
        return
    if not raw:
        print("[refill] LLM 返回空，跳过补料。")
        return
    try:
        obj = json.loads(raw)
        arr = obj["terms"] if isinstance(obj, dict) and "terms" in obj else obj
        if not isinstance(arr, list):
            arr = []
    except Exception as e:
        print("[refill] 解析 LLM 输出失败：%s（跳过补料）" % e)
        return
    added = 0
    seen = {x.get("id") for x in bk["terms"]}
    for t in arr:
        if not isinstance(t, dict):
            continue
        ok, errs = validate_term(t)
        if not ok:
            print("  [refill 跳过] %s 校验未过：%s" % (t.get("id"), "；".join(errs)))
            continue
        if t.get("id") in seen:
            continue
        bk["terms"].append(t)
        seen.add(t.get("id"))
        added += 1
    try:
        save(BACKLOG, bk)
    except Exception as e:
        print("[refill] 写回 backlog 失败：%s" % e)
        return
    print("[refill] 已写入 %d 条新候选，backlog 现有 %d 条。" % (added, len(bk["terms"])))


if __name__ == "__main__":
    main()
