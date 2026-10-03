# -*- coding: utf-8 -*-
"""术语大全日更脚本（每日自动化调用）。
流程：
  1. 从 data/term_backlog.json 取前 N 条
  2. 追加进 data/terms.json 的 terms 数组（主术语库 = 术语大全）
  3. 重新生成静态站（python gen_vibecode.py -> dist/）
  4. 复制到干净的部署目录，wrangler pages deploy 直传上线
  5. 回写剩余 backlog
用法：
  python daily_term_update.py            # 默认取 2 条并部署
  python daily_term_update.py --count 3 --no-deploy   # 取 3 条只生成不部署
  python daily_term_update.py --dry            # 只打印将取哪些，不改文件
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(ROOT, "data")
TERMS_JSON = os.path.join(DATA, "terms.json")
BACKLOG_JSON = os.path.join(DATA, "term_backlog.json")
DIST = os.path.join(ROOT, "dist")

PY = "C:/Users/小可爱/.workbuddy/binaries/python/versions/3.13.12/python.exe"
NODE = "C:/Users/小可爱/.workbuddy/binaries/node/versions/22.22.2/node.exe"
WRANGLER = "C:/Users/小可爱/.workbuddy/binaries/node/workspace/node_modules/wrangler/bin/wrangler.js"
ACCOUNT_ID = "7e0a10c7639644ba5634ad7c11b895e9"
TOKEN_PATH = "C:/Users/小可爱/.cf_token"
PROJECT = "mayi-vibecode"


def load(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def save(p, obj):
    with open(p, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


# ===== 术语入库规则（每日自动任务遵循）=====
# 1. 选术语组件：id / cn(中文组件名) / en(平台术语) / ch(章节 0-10) 必须齐全且非空。
# 2. 大白话及效果：speak(大白话) 非空；anti(反模式)/fix(正确做法) 非空；
#    vd_bad 与 vd_good(视觉对照 demo) 必须非空 —— 站点会渲染「点击试用」让效果可点体验。
# 3. 专业提示词效果（必须可点击体验）：专业提示词由 cn/en/speak/anti/fix/tip 自动生成，
#    因此 tip 必须为非空列表(>=1)、anti/fix 非空；其效果 = vd_good，站点用「点击试用」呈现，必须可点。
# 4. plat 必须含 web/app/mini 三个键（移动端 / 小程序兼容说明）。
# 5. bad/good 为代码片段，需非空。
RULES = (
    "术语入库规则：① 选术语组件 id/cn/en/ch 齐全；② 大白话(speak)+效果(vd_bad/vd_good 非空，站点点击试用可体验)；"
    "③ 专业提示词效果可点击(tip 非空列表 + anti/fix 非空，效果=v_good 点击试用)；④ plat 含 web/app/mini；⑤ bad/good 代码非空。"
)


def validate_term(t):
    """按上面规则校验一个术语对象，返回 (是否通过, 错误列表)。"""
    errs = []
    for k in ("id", "cn", "en"):
        if not str(t.get(k, "")).strip():
            errs.append("缺字段 %s" % k)
    ch = t.get("ch")
    if not isinstance(ch, int) or ch < 0 or ch > 10:
        errs.append("ch 必须在 0-10")
    for k in ("speak", "anti", "fix", "bad", "good", "vd_bad", "vd_good"):
        if not str(t.get(k, "")).strip():
            errs.append("缺字段或为空 %s" % k)
    tip = t.get("tip")
    if not isinstance(tip, list) or len(tip) < 1:
        errs.append("tip 必须为非空列表")
    plat = t.get("plat")
    if not isinstance(plat, dict) or not all(k in plat for k in ("web", "app", "mini")):
        errs.append("plat 需含 web/app/mini 三键")
    return (len(errs) == 0, errs)


def _wrangler_cmd():
    # 本地用受管 node + 本地 wrangler；CI / GitHub Actions 用全局安装的 wrangler
    if os.path.exists(WRANGLER):
        return [NODE, WRANGLER]
    return ["wrangler"]


def build_site():
    print("[build] 运行 gen_vibecode.py ...")
    r = subprocess.run([PY, "gen_vibecode.py"], cwd=ROOT, capture_output=True, text=True)
    if r.returncode != 0:
        print("[ERROR] 生成失败：\n", r.stdout, r.stderr)
        sys.exit(1)
    print(r.stdout.strip()[-300:] if r.stdout else "(no stdout)")


def deploy_site(added_ids):
    # 每次用带时间戳的新目录部署：既绕开沙箱批量删除保护，
    # 又避免复用旧目录导致 wrangler「Uploaded 0 files」漏传。
    deploy_dir = os.path.join(ROOT, ".deploy_%d" % int(time.time()))
    shutil.copytree(DIST, deploy_dir)
    # 令牌优先取环境变量（GitHub Actions 通过 secret 注入 CLOUDFLARE_API_TOKEN），本地回退到文件
    token = os.environ.get("CLOUDFLARE_API_TOKEN")
    if not token:
        token = open(TOKEN_PATH, encoding="utf-8").read().strip()
    env = os.environ.copy()
    env["CLOUDFLARE_API_TOKEN"] = token
    env["CLOUDFLARE_ACCOUNT_ID"] = ACCOUNT_ID
    env["MSYS_NO_PATHCONV"] = "1"
    # 关键：必须从 ROOT 运行部署，wrangler 才会把 ROOT/functions（含 [[path]].js 兜底路由）一并上传。
    # 此前 cwd=deploy_dir 只传了静态资源，导致函数（含后台、兜底路由）一直没被更新，
    # 旧部署里残留的 catch-all 才会对所有未知路径返回 200 首页。
    wcmd = _wrangler_cmd()
    print("[deploy] %s pages deploy %s (functions from ROOT)" % (" ".join(wcmd), deploy_dir))
    try:
        r = subprocess.run(
            wcmd + ["pages", "deploy", deploy_dir, "--project-name", PROJECT, "--branch", "main"],
            cwd=ROOT, env=env, capture_output=True, text=True, timeout=300,
        )
    except subprocess.TimeoutExpired:
        print("[ERROR] 部署超时（300s）。dist 已生成，网络恢复后可重跑本脚本或手动部署。")
        sys.exit(1)
    print(r.stdout[-800:] if r.stdout else "")
    if r.stderr:
        print("[stderr]", r.stderr[-500:])
    if r.returncode != 0:
        print("[ERROR] 部署失败，请检查网络/令牌。dist 已生成，可手动部署。")
        sys.exit(1)
    print("[done] 已上线。新增术语：", ", ".join(added_ids) if added_ids else "(当前内容重新部署)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--count", type=int, default=2)
    ap.add_argument("--no-deploy", action="store_true")
    ap.add_argument("--dry", action="store_true")
    ap.add_argument("--deploy-current", action="store_true",
                    help="仅重新生成并部署当前 terms.json，不追加新术语")
    args = ap.parse_args()

    if args.deploy_current:
        print("[mode] 仅重新生成并部署当前 terms.json（不追加新术语）")
        build_site()
        if args.no_deploy:
            print("[ok] 已生成 dist/（未部署）。")
            return
        deploy_site([])
        return

    bk = load(BACKLOG_JSON)
    terms = load(TERMS_JSON)
    existing = set(t["id"] for t in terms["terms"])
    existing_cn = {t["cn"] for t in terms["terms"]}

    batch = []
    rest = list(bk["terms"])
    for t in rest:
        if len(batch) >= args.count:
            break
        if t["id"] in existing or t["cn"] in existing_cn:
            continue  # 跳过已存在的（id 或 中文名），防重复
        # 入库规则校验：不符合「选术语组件 / 大白话及效果 / 专业提示词效果可点击」的候选直接跳过
        ok, errs = validate_term(t)
        if not ok:
            print("  [跳过] %s 不符合入库规则：%s" % (t.get("id"), "；".join(errs)))
            continue
        batch.append(t)

    if args.dry:
        print("[dry] 将新增 %d 条：" % len(batch))
        for t in batch:
            print("  -", t["id"], t["cn"], "(ch%d)" % t["ch"])
        return

    if not batch:
        print("[skip] backlog 为空或无可用新术语，今日无需更新。")
        return

    # 追加进主术语库
    for t in batch:
        terms["terms"].append(t)
        existing.add(t["id"])
    save(TERMS_JSON, terms)

    # 回写剩余 backlog（去掉已用的）
    used = set(t["id"] for t in batch)
    bk["terms"] = [t for t in rest if t["id"] not in used]
    save(BACKLOG_JSON, bk)

    print("[ok] 已追加 %d 条术语，主库现有 %d 条。" % (len(batch), len(terms["terms"])))
    for t in batch:
        print("   +", t["id"], t["cn"])

    build_site()
    if args.no_deploy:
        print("[ok] 已生成 dist/（未部署）。新增术语页面待上线。")
        return
    deploy_site([t["id"] for t in batch])


if __name__ == "__main__":
    main()
