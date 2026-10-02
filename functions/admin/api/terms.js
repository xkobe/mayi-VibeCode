import { json } from "../../_lib/util.js";
import { requireAuth } from "../../_lib/auth.js";
import { getStorage } from "../../_lib/storage.js";

export async function onRequest(context) {
  const user = await requireAuth(context);
  if (!user) return json({ error: "unauthorized" }, 401);
  const storage = await getStorage(context.env);
  if (context.request.method === "GET") {
    const data = (await storage.readJSON("data/terms.json")) || { terms: [] };
    return json({ terms: data.terms });
  }
  if (context.request.method === "POST") {
    const b = await context.request.json().catch(() => ({}));
    if (!b.id) return json({ error: "id 必填" }, 400);
    const data = (await storage.readJSON("data/terms.json")) || { terms: [] };
    if (data.terms.some((t) => t.id === b.id))
      return json({ error: "id 已存在" }, 400);
    const rec = {
      id: b.id,
      ch: b.ch || 0,
      speak: b.speak || "",
      cn: b.cn || "",
      en: b.en || "",
      anti: b.anti || "",
      fix: b.fix || "",
      bad: b.bad || "",
      good: b.good || "",
      tip: Array.isArray(b.tip) ? b.tip : [],
      plat: b.plat || {},
      vd_bad: b.vd_bad || "",
      vd_good: b.vd_good || "",
    };
    data.terms.push(rec);
    await storage.writeJSON("data/terms.json", data, `admin add term ${b.id}`);
    return json({ ok: true, term: rec });
  }
  return json({ error: "method" }, 405);
}
