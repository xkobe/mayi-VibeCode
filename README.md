# 码译 · VibeCode

> 把 Vibe Coding 黑话翻译成能落地的需求 —— 一个零依赖、SEO 友好的中文静态术语站 + 可视化后台 CMS。

## 这是什么

- **前端**：由 `gen_vibecode.py` 把 `data/terms.json`（87 条术语）渲染成 101 个预渲染中文 HTML 页 + `sitemap.xml` + `robots.txt`，百度蜘蛛无需执行 JS 即可抓取，对收录友好。
- **后台 `/admin`**：Cloudflare Pages Functions（`functions/`），账号密码保护，编辑内容后写回 GitHub 并自动重建站点，无需改代码、无需重新部署。

## 快速开始

```bash
# 1. 生成站点
python gen_vibecode.py
# 预期：loaded 87 terms → OK terms=87 → DIST: 101 pages + sitemap.xml + robots.txt + assets

# 2. 本地预览
python -m http.server 8099
# 打开 http://localhost:8099/

# 3. 后台逻辑本地测试（无需 CF / GitHub）
node test_admin.mjs
# 预期：✅ 全部通过（鉴权 / 术语 CRUD / 设置 / 素材 / 用户 / 看板）
```

## 部署（Cloudflare Pages）

详见 [DEPLOY.md](./DEPLOY.md)。要点：

- 构建命令 `python gen_vibecode.py`，输出目录 `dist`
- 公开变量（`wrangler.toml` 已声明）：`ADMIN_USER` / `GH_REPO` / `GH_BRANCH`
- 机密（`wrangler pages secret put`）：`GH_TOKEN` / `AUTH_SECRET` / `ADMIN_PASS`
- 构建变量：`VB_SITE_BASE = https://mayi-vibecode.pages.dev`

## 目录结构

```
gen_vibecode.py            # 站点生成器（构建时运行）
_engine_snapshot.pyc       # 渲染引擎快照（Python 3.13 编译，构建必需）
data/                      # 术语内容 / 设置 / 素材索引（CMS 写回对象）
functions/                 # Pages Functions 后台（账号密码保护）
wrangler.toml              # CF Pages 配置
.python-version            # 3.13（锁定 CF 构建 Python 版本）
DEPLOY.md                  # 部署与运营手册
test_admin.mjs             # 后台逻辑本地测试
```
