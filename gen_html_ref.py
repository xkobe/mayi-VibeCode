# -*- coding: utf-8 -*-
"""
gen_html_ref.py — 生成「HTML 元素参考」栏目（dist/html/）

数据来源：MDN Web Docs（CC-BY-SA 2.5，署名）。
逻辑：读取 data/html_elements.json 的 imported 列表，输出
  - dist/html/index.html        元素卡片墙 + 每日同步署名说明
  - dist/html/<tag>/index.html  单元素详情页（大白话用途 / 实时示例 / 属性表 / 坑 / MDN 链接）
并把栏目 URL 追加进 dist/sitemap.xml。

本脚本只负责 /html 子树，不碰主站（主站由 gen_vibecode.py 生成）。
"""
import io
import json
import os
import re
import html as _html

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(ROOT, "data", "html_elements.json")
DIST = os.path.join(ROOT, "dist")
OUT = os.path.join(DIST, "html")

BRAND = "#C8442E"
BRAND_SOFT = "#fbeae6"

BASE_CSS = """
:root{--brand:#C8442E;--brand-soft:#fbeae6;--ink:#23211f;--ink-2:#5b5752;--ink-3:#8a857e;--line:#ece8e3;--line-2:#f3f0ec;--good:#2e9e5b;--bad:#d6453a;--bg:#fbfaf8;}
*{box-sizing:border-box}
body{margin:0;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"PingFang SC","Microsoft YaHei",sans-serif;color:var(--ink);background:var(--bg);line-height:1.65}
a{color:var(--brand);text-decoration:none}
a:hover{text-decoration:underline}
.wrap{max-width:1080px;margin:0 auto;padding:24px 18px 60px}
.top{display:flex;align-items:center;gap:12px;padding:16px 18px;border-bottom:1px solid var(--line);background:#fff;position:sticky;top:0;z-index:5}
.logo{width:34px;height:34px;border-radius:9px;background:linear-gradient(135deg,#E25738,var(--brand));display:flex;align-items:center;justify-content:center;color:#fff;font-weight:900;font-size:15px;flex:none}
.brand{font-weight:900;font-size:17px;color:var(--ink)}
.brand small{font-weight:600;color:var(--ink-3);font-size:12px;margin-left:6px}
.back{margin-left:auto;font-size:13px;font-weight:700;color:var(--brand);border:1px solid var(--line);padding:7px 14px;border-radius:999px;background:#fff}
.back:hover{background:var(--brand-soft);text-decoration:none}
.hero{margin:26px 0 8px}
.hero h1{font-size:26px;margin:0 0 6px}
.hero p{color:var(--ink-2);margin:4px 0;font-size:14.5px}
.note{margin:14px 0 22px;padding:12px 16px;border:1px solid var(--line);border-left:4px solid var(--brand);border-radius:10px;background:#fff;color:var(--ink-2);font-size:13px}
.note b{color:var(--ink)}
.meta{display:flex;gap:10px;flex-wrap:wrap;margin:6px 0 20px}
.chip{font-size:12px;font-weight:700;color:var(--brand);background:var(--brand-soft);border-radius:999px;padding:5px 12px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:12px}
.card{border:1px solid var(--line);border-radius:12px;background:#fff;padding:14px;transition:.15s;display:flex;flex-direction:column;gap:4px}
.card:hover{border-color:var(--brand);box-shadow:0 6px 18px rgba(200,68,46,.12);transform:translateY(-2px)}
.card code{font-size:15px;font-weight:800;color:var(--brand)}
.card .zh{font-size:12.5px;color:var(--ink-2);line-height:1.5;min-height:34px}
.card .dep{font-size:11px;color:var(--bad);font-weight:700}
.detail .tag{font-size:30px;font-weight:900;color:var(--brand);margin:6px 0}
.detail .en{color:var(--ink-3);font-size:13px;font-style:italic;margin-bottom:14px}
.block{margin:22px 0}
.block h2{font-size:18px;margin:0 0 10px;display:flex;align-items:center;gap:8px}
.block h2::before{content:"";width:6px;height:18px;border-radius:3px;background:var(--brand);display:inline-block}
.zh-txt{font-size:15px;color:var(--ink);background:#fff;border:1px solid var(--line);border-radius:12px;padding:16px}
.preview{border:1px solid var(--line);border-radius:12px;overflow:hidden;background:#fff}
.preview .bar{background:var(--line-2);padding:7px 12px;font-size:11.5px;color:var(--ink-3);font-weight:700;display:flex;justify-content:space-between}
.preview iframe{width:100%;height:170px;border:0;display:block;background:#fff}
pre{background:#1e1c1a;color:#f4efe9;padding:14px 16px;border-radius:12px;overflow:auto;font-size:13px;line-height:1.6;margin:10px 0}
pre code{font-family:"SFMono-Regular",Consolas,monospace}
table{width:100%;border-collapse:collapse;background:#fff;border:1px solid var(--line);border-radius:12px;overflow:hidden;font-size:14px}
th,td{text-align:left;padding:10px 12px;border-bottom:1px solid var(--line-2);vertical-align:top}
th{background:var(--brand-soft);color:var(--brand);font-weight:800;font-size:12.5px}
tr:last-child td{border-bottom:0}
td code{color:var(--brand);font-weight:700}
.pit{background:#fff;border:1px solid var(--line);border-left:4px solid var(--bad);border-radius:10px;padding:14px 16px;font-size:14px;color:var(--ink)}
.pit b{color:var(--bad)}
.src{display:inline-flex;align-items:center;gap:6px;margin-top:8px;font-size:13px;font-weight:700;border:1px solid var(--brand);color:var(--brand);padding:8px 14px;border-radius:999px}
.src:hover{background:var(--brand-soft);text-decoration:none}
.pager{display:flex;justify-content:space-between;margin-top:30px;gap:12px}
.pager a{font-size:13.5px;font-weight:700;border:1px solid var(--line);padding:9px 16px;border-radius:10px;background:#fff;flex:1;text-align:center}
.pager a:hover{background:var(--brand-soft);text-decoration:none}
.empty{text-align:center;color:var(--ink-3);padding:50px 0;font-size:15px}
footer{text-align:center;color:var(--ink-3);font-size:12.5px;margin-top:40px;padding-top:20px;border-top:1px solid var(--line)}
@media(max-width:600px){.grid{grid-template-columns:repeat(auto-fill,minmax(130px,1fr))}.hero h1{font-size:22px}}
"""

def load():
    with io.open(DATA, encoding="utf-8") as f:
        return json.load(f)


def esc(s):
    return _html.escape(str(s), quote=True)


def top_bar(site_label, brand):
    return ('<div class="top"><div class="logo">码</div>'
            '<div class="brand">%s<small>HTML 元素参考 · 来自 MDN</small></div>'
            '<a class="back" href="/">← 返回术语站</a></div>' % esc(site_label))


def render_index(d):
    imported = d.get("imported", [])
    label = d.get("site_label", "码译 · VibeCode")
    note = d.get("note", "")
    src = d.get("source_name", "MDN Web Docs")
    lic = d.get("source_license", "")
    updated = imported[0].get("imported_date") if imported else "—"
    cards = []
    for el in imported:
        dep = ' <span class="dep">已废弃</span>' if el.get("deprecated") else ""
        zh = el.get("purpose_zh", "")
        zh = (zh[:42] + "…") if len(zh) > 43 else zh
        cards.append(
            '<a class="card" href="/html/%s/index.html"><code>&lt;%s&gt;</code>'
            '<div class="zh">%s%s</div></a>' % (esc(el["tag"]), esc(el["tag"]), esc(zh), dep))
    grid = '<div class="grid">%s</div>' % "".join(cards) if cards else \
        '<div class="empty">敬请期待 —— 栏目内容正按日从 %s 自动同步收录中。</div>' % esc(src)
    body = (
        '<div class="hero"><h1>HTML 元素参考</h1>'
        '<p>把 MDN 的 HTML 元素文档，配上中文「大白话」讲解，每天自动多收录一个。</p></div>'
        '<div class="note"><b>版权与署名：</b>%s 原始内容版权归 %s 贡献者所有，依 %s 署名发布；中文讲解为本站原创补充。</div>'
        '<div class="meta"><span class="chip">已收录 %d 个</span>'
        '<span class="chip">最近更新 %s</span>'
        '<span class="chip">源站 %s</span></div>'
        '%s' % (esc(note), esc(src), esc(lic), len(imported), esc(updated), esc(src), grid))
    return _page(label, "HTML 元素参考 · 码译 VibeCode", body)


def render_detail(d, el, prev_tag, next_tag):
    label = d.get("site_label", "码译 · VibeCode")
    src = d.get("source_license", "")
    tag = el["tag"]
    mdn_url = el.get("mdn_url", d.get("source_base", "") + tag)
    purpose_zh = el.get("purpose_zh", "")
    purpose_en = el.get("purpose_en", "")
    example = el.get("example_html", "")
    attrs = el.get("attributes", [])
    pitfalls = el.get("pitfalls_zh", "")
    dep = '<span class="dep" style="font-size:13px">（该元素已被 HTML 标准废弃，仅作历史参考）</span>' if el.get("deprecated") else ""

    # example preview
    if example.strip():
        iframe = ('<div class="preview"><div class="bar"><span>实时效果</span><span>沙箱预览</span></div>'
                  '<iframe sandbox="allow-same-origin" srcdoc="%s"></iframe></div>' % esc(example))
        code = '<pre><code>%s</code></pre>' % esc(example)
        example_block = '<div class="block"><h2>可运行示例</h2>%s%s</div>' % (iframe, code)
    else:
        example_block = ""

    # attributes table
    if attrs:
        rows = "".join('<tr><td><code>%s</code></td><td>%s</td></tr>' % (esc(a["name"]), esc(a.get("desc_zh", ""))) for a in attrs)
        attr_block = '<div class="block"><h2>常用属性（大白话）</h2><table><thead><tr><th>属性</th><th>是干嘛的</th></tr></thead><tbody>%s</tbody></table></div>' % rows
    else:
        attr_block = ""

    pit_block = '<div class="block"><h2>新手常踩的坑</h2><div class="pit">%s</div></div>' % esc(pitfalls) if pitfalls else ""

    purpose_block = ('<div class="block"><h2>一句话说清</h2>'
                     '<div class="zh-txt"><b>大白话：</b>%s%s</div>'
                     '<div style="color:var(--ink-3);font-size:12.5px;margin-top:8px">MDN 原文：%s</div></div>'
                     % (esc(purpose_zh), dep, esc(purpose_en))) if purpose_zh else ""

    prev_a = '<a href="/html/%s/index.html">← &lt;%s&gt;</a>' % (esc(prev_tag), esc(prev_tag)) if prev_tag else '<a style="visibility:hidden">-</a>'
    next_a = '<a href="/html/%s/index.html">&lt;%s&gt; →</a>' % (esc(next_tag), esc(next_tag)) if next_tag else '<a style="visibility:hidden">-</a>'

    body = (
        '<div class="detail"><div class="tag">&lt;%s&gt;</div><div class="en">%s</div></div>'
        '%s%s%s%s'
        '<a class="src" href="%s" target="_blank" rel="noopener">查看 MDN 原文 ↗</a>'
        '<div class="pager">%s%s</div>'
        '<footer>本页元素定义与示例版权归 MDN 贡献者所有（%s）；中文「大白话」讲解为码译 · VibeCode 原创补充。</footer>'
        % (esc(tag), esc(purpose_en), purpose_block, example_block, attr_block, pit_block,
           esc(mdn_url), prev_a, next_a, esc(src)))
    return _page(label, "<%s> · HTML 元素参考 · 码译 VibeCode" % tag, body, back_link=False)


def _page(label, title, body, back_link=True):
    return ('<!DOCTYPE html><html lang="zh-CN"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width,initial-scale=1">'
            '<title>%s</title>'
            '<link rel="icon" href="/assets/logo.svg">'
            '<style>%s</style></head><body>%s%s</body></html>'
            % (esc(title), BASE_CSS, top_bar(label, BRAND), body))


def update_sitemap(d):
    sp = os.path.join(DIST, "sitemap.xml")
    if not os.path.exists(sp):
        return
    urls = ['  <url><loc>%s/html/</loc></url>' % d.get("site_base", "https://mayi-vibecode.pages.dev").rstrip("/")]
    for el in d.get("imported", []):
        urls.append('  <url><loc>%s/html/%s/</loc></url>' % (d.get("site_base", "https://mayi-vibecode.pages.dev").rstrip("/"), el["tag"]))
    add = "\n".join(urls)
    s = io.open(sp, encoding="utf-8").read()
    if "/html/" in s:
        return  # already added (idempotent)
    s = s.replace("</urlset>", add + "\n</urlset>")
    io.open(sp, "w", encoding="utf-8").write(s)


def main():
    d = load()
    if not os.path.exists(DIST):
        print("dist/ 不存在，请先运行 gen_vibecode.py 生成主站")
        return
    os.makedirs(OUT, exist_ok=True)
    # index
    io.open(os.path.join(OUT, "index.html"), "w", encoding="utf-8").write(render_index(d))
    imported = d.get("imported", [])
    n = len(imported)
    for i, el in enumerate(imported):
        tag = el["tag"]
        prev_tag = imported[i - 1]["tag"] if i > 0 else None
        next_tag = imported[i + 1]["tag"] if i < n - 1 else None
        tdir = os.path.join(OUT, tag)
        os.makedirs(tdir, exist_ok=True)
        io.open(os.path.join(tdir, "index.html"), "w", encoding="utf-8").write(render_detail(d, el, prev_tag, next_tag))
    update_sitemap(d)
    print("OK 生成 %d 个元素详情页 + 索引，输出目录 dist/html/" % n)


if __name__ == "__main__":
    main()
