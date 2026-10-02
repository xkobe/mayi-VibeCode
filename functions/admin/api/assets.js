import { json } from "../../_lib/util.js";
import { requireAuth } from "../../_lib/auth.js";
import { getStorage } from "../../_lib/storage.js";

export async function onRequest(context) {
  const user = await requireAuth(context);
  if (!user) return json({ error: "unauthorized" }, 401);
  const storage = await getStorage(context.env);
  if (context.request.method === "GET") {
    const a = (await storage.readJSON("data/assets.json")) || [];
    return json({ assets: a });
  }
  if (context.request.method === "POST") {
    const b = await context.request.json().catch(() => ({}));
    if (!b.name || !b.base64) return json({ error: "name/base64 必填" }, 400);
    await storage.uploadAsset(b.name, b.base64, `upload ${b.name}`);
    const list = (await storage.readJSON("data/assets.json")) || [];
    const meta = { name: b.name, type: b.type || "", uploadedAt: new Date().toISOString() };
    const i = list.findIndex((x) => x.name === b.name);
    if (i >= 0) list[i] = meta;
    else list.push(meta);
    await storage.writeJSON("data/assets.json", list, `assets meta ${b.name}`);
    return json({ ok: true, asset: meta });
  }
  return json({ error: "method" }, 405);
}
