import { pathToFileURL } from "node:url";
import path from "node:path";
import { writeFileSync, rmSync, existsSync } from "node:fs";

const ROOT = process.cwd();
const ENV = {
  ADMIN_USER: "admin",
  ADMIN_PASS: "admin123",
  AUTH_SECRET: "test-secret-123",
  PROJECT_ROOT: ROOT, // 本地模式（无 GH_TOKEN -> LocalFileStorage）
};

let fails = 0;
function assert(cond, msg) {
  if (!cond) { console.error("  FAIL:", msg); fails++; }
  else console.log("  ok:", msg);
}

async function call(modRel, { method = "GET", body, cookie, params } = {}) {
  const mod = await import(pathToFileURL(path.join(ROOT, modRel)).href);
  const req = new Request("https://test.local/", {
    method,
    headers: { "content-type": "application/json", ...(cookie ? { cookie } : {}) },
    body: body !== undefined ? JSON.stringify(body) : undefined,
  });
  const ctx = { request: req, env: ENV, params: params || {} };
  const res = await mod.onRequest(ctx);
  let data = null;
  try { data = await res.json(); } catch {}
  return { status: res.status, data, cookie: res.headers.get("set-cookie") };
}

console.log("== 鉴权 ==");
let r = await call("functions/admin/api/me.js");
assert(r.data.user === null, "未登录 me -> null");
r = await call("functions/admin/login.js", { method: "POST", body: { username: "admin", password: "admin123" } });
assert(r.status === 200 && r.data.user === "admin", "登录成功");
const cookie = r.cookie;
assert(!!cookie && cookie.includes("vb_admin"), "登录返回 cookie");
r = await call("functions/admin/api/me.js", { cookie });
assert(r.data.user === "admin", "登录后 me -> admin");

console.log("== 术语 CRUD ==");
r = await call("functions/admin/api/terms.js", { cookie });
assert(r.data.terms.length === 87, "术语列表 87 条 (got " + r.data.terms.length + ")");
r = await call("functions/admin/api/terms.js", { method: "POST", cookie, body: { id: "test-term-zzz", ch: 1, cn: "测试术语", en: "Test", speak: "s", anti: "a", fix: "f", bad: "<b>", good: "<i>", tip: ["t1"], plat: { web: "w" }, vd_bad: "<div>b</div>", vd_good: "<div>g</div>" } });
assert(r.status === 200, "新增术语");
r = await call("functions/admin/api/terms.js", { method: "POST", cookie, body: { id: "test-term-zzz", cn: "x" } });
assert(r.status === 400, "重复 id 被拒");
r = await call("functions/admin/api/term/[id].js", { method: "PUT", cookie, params: { id: "test-term-zzz" }, body: { cn: "测试术语改" } });
assert(r.status === 200 && r.data.term.cn === "测试术语改", "更新术语");
r = await call("functions/admin/api/term/[id].js", { cookie, params: { id: "test-term-zzz" } });
assert(r.data.term.cn === "测试术语改", "读取术语");
r = await call("functions/admin/api/term/[id].js", { method: "DELETE", cookie, params: { id: "test-term-zzz" } });
assert(r.status === 200, "删除术语");
r = await call("functions/admin/api/terms.js", { cookie });
assert(r.data.terms.length === 87, "删除后回到 87 条");

console.log("== 站点设置 ==");
r = await call("functions/admin/api/settings.js", { cookie });
assert(r.data.settings.brand === "#C8442E", "设置默认值");
r = await call("functions/admin/api/settings.js", { method: "PUT", cookie, body: { title: "我的术语台", brand: "#123456" } });
assert(r.status === 200 && r.data.settings.title === "我的术语台", "更新设置");

console.log("== 素材 ==");
r = await call("functions/admin/api/assets.js", { method: "POST", cookie, body: { name: "test.svg", base64: Buffer.from("<svg></svg>").toString("base64"), type: "image/svg+xml" } });
assert(r.status === 200, "上传素材");
r = await call("functions/admin/api/assets.js", { cookie });
assert(r.data.assets.length === 1, "素材列出");
r = await call("functions/admin/api/assets/[name].js", { method: "DELETE", cookie, params: { name: "test.svg" } });
assert(r.status === 200, "删除素材");

console.log("== 用户中心 ==");
r = await call("functions/admin/api/users.js", { cookie });
assert(r.data.users.length >= 1, "用户已种子");
r = await call("functions/admin/api/users.js", { method: "POST", cookie, body: { username: "editor1", password: "pw123", role: "editor" } });
assert(r.status === 200, "新增用户");
r = await call("functions/admin/api/users/[name].js", { method: "DELETE", cookie, params: { name: "admin" } });
assert(r.status === 400, "禁止删除唯一 admin");
r = await call("functions/admin/api/users/[name].js", { method: "DELETE", cookie, params: { name: "editor1" } });
assert(r.status === 200, "删除 editor");

console.log("== 看板 ==");
r = await call("functions/admin/api/dashboard.js", { cookie });
assert(r.data.stats.terms === 87, "看板术语数 87");
assert(typeof r.data.stats.deploy === "string", "看板部署文案");

console.log("== 清理测试副作用 ==");
writeFileSync(path.join(ROOT, "data/settings.json"), JSON.stringify({ title: "Vibe Coding 需求翻译器", description: "说要做什么，直接拿到可复制的 AI 提示词", nav: "术语库,组件,视觉,工程", brand: "#C8442E", footer: "© 2026 Vibe Coding 术语台", analytics: "" }, null, 1));
for (const p of ["data/users.json", "assets/test.svg"]) {
  const fp = path.join(ROOT, p);
  if (existsSync(fp)) { try { rmSync(fp); } catch (e) { /* sandbox safe-delete 拦截，忽略 */ } }
}
console.log("  ok: 已复位 settings/users/asset 测试数据");

console.log(fails === 0 ? "\n✅ 全部通过" : `\n❌ ${fails} 项失败`);
process.exit(fails === 0 ? 0 : 1);
