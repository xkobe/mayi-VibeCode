# 部署与运营手册 · 码译 VibeCode

本站点 = **静态生成站点（前端）** + **Cloudflare Pages Functions（管理后台 CMS）**，
后台通过 **写回 GitHub 自动重建** 的方式更新内容。

> **已确认事项**：项目名 **码译 · VibeCode**，品牌色 `#C8442E`，Logo 为内联 SVG（圆角红方块 + 白色代码括号 + 双向翻译箭头）。部署平台确认为 **Cloudflare Pages**，先用免费 `*.pages.dev` 子域（即 `mayi-vibecode.pages.dev`）上线，暂不需要自定义域名。

---

## 1. 架构总览

```
┌──────────────┐   git push    ┌──────────────────────────────────────────┐
│  你 / CMS后台  │ ───────────▶ │  GitHub 仓库（main 分支）                   │
└──────────────┘               │   data/terms.json  ← CMS 写回触发 commit   │
                               └──────────────────────────────────────────┘
                                            │ 自动触发
                                            ▼
                               ┌──────────────────────────────────────────┐
                               │  Cloudflare Pages 构建                      │
                               │   构建命令: python gen_vibecode.py         │
                               │   输出目录: dist                           │
                               │   → 读取 data/terms.json 重新生成 101 页    │
                               └──────────────────────────────────────────┘
                                            │ 发布
                                            ▼
                               ┌──────────────────────────────────────────┐
                               │  公开站点  https://mayi-vibecode.pages.dev    │
                               │  /admin  → Pages Functions 后台            │
                               └──────────────────────────────────────────┘
```

- **前端**：`gen_vibecode.py` 把 `data/terms.json`（87 条术语）渲染成 101 个静态 HTML 页 + `sitemap.xml` + `robots.txt`。百度蜘蛛无需 JS 即可抓取中文内容。
- **后台 `/admin`**：Cloudflare Pages Functions（`functions/`），账号密码保护，编辑内容后调用 GitHub API 写回 `data/*.json` 并 commit，从而触发上面的自动重建。
- **数据外部化**：术语内容已抽离到 `data/terms.json`，后台改内容即写回该文件，**无需改代码、无需重新部署**。

---

## 2. 仓库结构（推到 GitHub 的内容）

```
gen_vibecode.py            # 站点生成器（构建时运行）
_engine_snapshot.pyc       # 渲染引擎快照（Python 3.13 编译，见 §7 风险）
data/
  terms.json              # 87 条术语（CMS 主要写回对象）
  settings.json           # 站点设置（CMS 可改）
  assets.json             # 素材索引（CMS 上传后追加）
  users.json              # 后台账号（首次新增/改账号时生成；勿手改密码明文）
wrangler.toml             # CF Pages 配置
functions/                # Pages Functions 后台
  package.json            # { "type": "module" }
  _lib/                   # auth / github / storage / util
  admin/                  # 后台路由 + UI
    index.js  login.js  logout.js  _ui.js
    api/                  # terms / term/[id] / settings / assets / users / dashboard / me
.python-version           # 3.13（锁定 CF 构建 Python 版本）
dist/                     # 构建产物（由 CF 构建生成，已在 .gitignore 忽略）
```

> `dist/` 不进仓库，完全由 CF 构建时生成；若想本地预览可手动 `python gen_vibecode.py` 生成。内容回滚走 GitHub 对 `data/*.json` 的 commit 历史即可。

---

## 3. 前置准备

1. 一个 GitHub 仓库（空仓即可，稍后把上述文件推上去）。
2. 一个 **Fine-grained Personal Access Token（PAT）**：
   - 作用范围：仅勾选目标仓库
   - 权限 `Repository permissions → Contents: Read and write`
   - 过期时间建议设长一点（如 1 年），到期前轮换
3. 一个 Cloudflare 账号（免费版 Pages 足够）。

---

## 4. Cloudflare Pages 接入

1. **创建项目** → 连接 Git → 选该仓库。
2. **构建设置**：
   - 构建命令：`python gen_vibecode.py`
   - 构建输出目录：`dist`
   - 根目录：（默认仓库根）
3. **Python 版本**：仓库根放有 `.python-version=3.13`，CF 会据此安装对应版本（见 §7）。若 CF 实际版本非 3.13，构建会报 magic number 错误 —— 参见 §7 处理。
4. **环境变量 / 密钥**（Settings → Environment variables）：
   - 公开变量（Plaintext，仅需补一项；其余已在 `wrangler.toml` 的 `[vars]` 声明）：
     - `VB_SITE_BASE` = `https://mayi-vibecode.pages.dev`（用于 sitemap.xml / robots.txt 里的绝对 URL；不填则回退此默认值）
     - `GH_REPO` / `GH_BRANCH` / `ADMIN_USER` 已由 `wrangler.toml` 提供，无需在网页重复填
   - 机密（Encrypt，用 `wrangler pages secret put` 或后台 Encrypt 表单，**切勿写进仓库**）：
     - `GH_TOKEN` = 上面的 PAT
     - `AUTH_SECRET` = 任意长随机串（用于会话签名 cookie，例如 `openssl rand -hex 32`）
     - `ADMIN_PASS` = 后台登录密码（首次登录后可在「用户中心」改）
5. **保存并首次部署**（手动触发一次 Deploy）。

> 也可用 `wrangler.toml` 里已声明的公开变量 + `wrangler pages secret put GH_TOKEN` / `AUTH_SECRET` / `ADMIN_PASS` 推送机密，无需在网页逐个填。

---

## 5. 首次运行后台

1. 打开 `https://mayi-vibecode.pages.dev/admin` → 用 `ADMIN_USER` / `ADMIN_PASS` 登录。
2. 进入「用户中心」把默认 admin 密码改成你自己的强密码。
3. 在「站点设置」里确认 title / description / 品牌色，保存（写回 `data/settings.json` 并触发一次重建）。
4. 说明：`data/users.json` 在你第一次通过「用户中心」新增/修改账号时生成（基于 `ADMIN_USER`+`ADMIN_PASS` 的 PBKDF2 哈希）；在此之前登录一直走环境变量兜底，**之后改密码只改 `users.json`**。

---

## 6. 日常运营 / 更新流程

| 你想做的事 | 怎么做 | 生效方式 |
|---|---|---|
| 改某条术语的文案 / 对错示例 | 后台「术语」搜索 → 编辑 → 保存 | 自动 commit `data/terms.json` → CF 重建（约 1–2 分钟） |
| 新增一条术语 | 后台「术语」→ 新增（id 不可重复） | 同上 |
| 删术语 | 后台「术语」→ 删除（二次确认） | 同上 |
| 改站点标题 / 品牌色 / 页脚 | 后台「设置」→ 保存 | 写回 `data/settings.json`（注：当前生成器尚未消费该文件，见 §8） |
| 上传图片素材 | 后台「素材」→ 上传（base64 存仓） | 写回 `data/assets.json` |
| 加/删后台账号 | 后台「用户中心」 | 写回 `data/users.json` |

> 所有写回都走 GitHub API，**仓库即唯一数据源**，本地无需维护副本。
> 若某次重建失败，进 GitHub 看 Actions/部署日志，或临时把上一次成功的 `dist/` 重新指向。

---

## 7. ⚠️ 关键风险：Python 版本与 .pyc

`gen_vibecode.py` 在构建时通过 `_engine_snapshot.pyc` 恢复渲染引擎，该文件由 **Python 3.13.12** 编译：

- 若 CF 构建容器 Python 版本 ≠ 3.13，**会报 `bad magic number` / ImportError，构建直接失败**。
- 已用仓库根 `.python-version = 3.13` 锁定；CF Pages 通常能识别并安装对应版本。
- **若部署时构建报 pyc / magic number 错误**，两种解法：
  1. 确认 `.python-version` 已推上仓库且 CF 已识别（重新触发 Deploy）；或
  2. （兜底）在你本机用 **Python 3.13** 重新生成一次 `.pyc`：
     ```bash
     python -c "import py_compile, _engine_snapshot"   # 仅示意
     # 实际：用当前 3.13 解释器重新 import 并保存快照 shell
     ```
     或联系我，把引擎导出为纯 `.py` 源码（彻底去掉 pyc 依赖，最稳）。

---

## 8. 已知边界（后续可迭代）

- `data/settings.json` 当前**只是 CMS 数据落库点**，生成器尚未在构建时读取它（站点标题/品牌色仍由 `gen_vibecode.py` 内硬编码）。后续可让生成器优先读 `settings.json` 覆盖默认值，使「设置」面板真正驱动站点外观。
- 图片素材目前以 base64 写入 `data/assets.json` 并随仓库增长；大图建议先压缩到 ≤800px。
- 后台为「账号密码」单层保护，非多因子；公网暴露请务必使用强密码 + 定期轮换。

---

## 9. 本地开发与验证

```bash
# 1) 生成站点
python gen_vibecode.py
# 预期：loaded 87 terms from data/terms.json → OK terms=87 → DIST: 101 pages + sitemap.xml + robots.txt + assets

# 2) 本地预览
python -m http.server 8099
# 打开 http://localhost:8099/

# 3) 后台逻辑本地测试（无需 CF / GitHub）
node test_admin.mjs
# 预期：✅ 全部通过（鉴权 / 术语 CRUD / 设置 / 素材 / 用户 / 看板）

# 4) 本地起 Functions（需 wrangler；未装则用上面的 test_admin.mjs 验证逻辑）
# npx wrangler pages dev . --compatibility-date=2024-09-23
```

---

## 10. SEO 要点（百度收录）

- 站点为**预渲染中文静态 HTML**，百度蜘蛛无需执行 JS 即可抓取标题/描述/正文，对收录友好。
- `dist/robots.txt` 已放行 `Baiduspider` 并指向 `sitemap.xml`。
- **Cloudflare 切勿开启 Bot Fight Mode / Under Attack 模式**，否则会拦截百度蜘蛛。
- 上线后在「百度搜索资源平台」提交 `https://mayi-vibecode.pages.dev/sitemap.xml`。
- 内地回源偶慢属正常，不影响收录质量；如追求极致可后续接 CN 加速。

---

## 11. 回滚与备份

- **内容回滚**：GitHub 仓库有完整 `data/terms.json` 历史，直接 revert 某次 commit 即触发旧内容重建。
- **整站回滚**：`dist/` 若已提交，可 checkout 到旧 commit 后重新 Deploy。
- **密钥泄露**：立即在 GitHub 撤销 PAT，并在 CF 轮换 `GH_TOKEN` / `AUTH_SECRET` / `ADMIN_PASS`。

---

## 12. 常见坑（实测踩过）

- **必须建「Pages」项目，不是「Worker」**：连 GitHub 时若在 CF 控制台走了 Worker 路径（项目 URL 形如 `dash.cloudflare.com/<acct>/workers/services/view/...`），部署命令会被当成 Worker 的 `npx wrangler deploy`，要求 `main` 或 `[assets]`，而我们 toml 用的是 Pages 专属的 `pages_build_output_dir`，会报 `✘ [ERROR] Missing entry-point to Worker script or to assets directory`。`/admin` 后台（Pages Functions）在 Worker 里也不会被识别。
  - ✅ 正确做法：Workers & Pages → Create → **选 Pages** → Connect to Git → 设 Build command=`python gen_vibecode.py`、Output=`dist`、**Deploy command 留空**。`functions/` 会自动作为 Pages Functions 上线。
- **Deploy command 别填 `npx wrangler deploy`**：那是 Worker 命令。Pages 项目留空即可自动部署；若一定要指定，用 `npx wrangler pages deploy`。
- **API Token 权限要含「Account Resources」**：自定义 token 即使勾了 `Cloudflare Pages: Edit`，若没在 Account Resources 里 Include 账户，调 Pages API 会返回 `code: 10000 Authentication error`。
- **`wrangler.toml` 里绝不能写明文机密**：`AUTH_SECRET` / `ADMIN_PASS` / `GH_TOKEN` 一律走 `wrangler pages secret put` 或控制台 Encrypt 变量；公开仓库一旦提交明文即泄露。
- **Python 版本**：`.python-version=3.13` 锁定，匹配 CF Pages v3 构建镜像默认 Python 3.13.x，确保 `_engine_snapshot.pyc`（3.13 编译）能正常加载，构建不炸。
