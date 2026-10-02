import { json } from "../../../_lib/util.js";
import { requireAuth } from "../../../_lib/auth.js";
import { getStorage } from "../../../_lib/storage.js";

export async function onRequest(context) {
  const user = await requireAuth(context);
  if (!user) return json({ error: "unauthorized" }, 401);
  if (context.request.method !== "DELETE")
    return json({ error: "method" }, 405);
  const name = decodeURIComponent(context.params.name);
  const storage = await getStorage(context.env);
  const users = (await storage.readJSON("data/users.json")) || [];
  const target = users.find((u) => u.username === name);
  if (!target) return json({ error: "not found" }, 404);
  if (target.role === "admin" && users.filter((u) => u.role === "admin").length <= 1)
    return json({ error: "至少保留一个 admin" }, 400);
  await storage.writeJSON(
    "data/users.json",
    users.filter((u) => u.username !== name),
    `delete user ${name}`
  );
  return json({ ok: true });
}
