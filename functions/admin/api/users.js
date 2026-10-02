import { json } from "../../_lib/util.js";
import { requireAuth } from "../../_lib/auth.js";
import { getStorage } from "../../_lib/storage.js";
import { hashPassword } from "../../_lib/auth.js";

async function ensureSeed(storage, env) {
  let users = await storage.readJSON("data/users.json");
  if (!users || !users.length) {
    const uname = env.ADMIN_USER || "admin";
    const pw = env.ADMIN_PASS || "admin123";
    users = [{ username: uname, role: "admin", passwordHash: await hashPassword(pw) }];
    await storage.writeJSON("data/users.json", users, "seed admin user");
  }
  return users;
}

export async function onRequest(context) {
  const user = await requireAuth(context);
  if (!user) return json({ error: "unauthorized" }, 401);
  const storage = await getStorage(context.env);
  if (context.request.method === "GET") {
    const users = await ensureSeed(storage, context.env);
    return json({
      users: users.map((u) => ({ username: u.username, role: u.role })),
    });
  }
  if (context.request.method === "POST") {
    const b = await context.request.json().catch(() => ({}));
    if (!b.username || !b.password)
      return json({ error: "用户名密码必填" }, 400);
    const users = await ensureSeed(storage, context.env);
    if (users.some((u) => u.username === b.username))
      return json({ error: "用户名已存在" }, 400);
    users.push({
      username: b.username,
      role: b.role || "editor",
      passwordHash: await hashPassword(b.password),
    });
    await storage.writeJSON("data/users.json", users, `add user ${b.username}`);
    return json({
      ok: true,
      user: { username: b.username, role: b.role || "editor" },
    });
  }
  return json({ error: "method" }, 405);
}
