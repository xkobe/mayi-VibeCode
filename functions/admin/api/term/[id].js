import { json } from "../../../_lib/util.js";
import { requireAuth } from "../../../_lib/auth.js";
import { getStorage } from "../../../_lib/storage.js";

export async function onRequest(context) {
  const user = await requireAuth(context);
  if (!user) return json({ error: "unauthorized" }, 401);
  const id = context.params.id;
  const storage = await getStorage(context.env);
  const data = (await storage.readJSON("data/terms.json")) || { terms: [] };
  const idx = data.terms.findIndex((t) => t.id === id);
  if (context.request.method === "GET") {
    if (idx < 0) return json({ error: "not found" }, 404);
    return json({ term: data.terms[idx] });
  }
  if (context.request.method === "PUT") {
    if (idx < 0) return json({ error: "not found" }, 404);
    const b = await context.request.json().catch(() => ({}));
    data.terms[idx] = { ...data.terms[idx], ...b, id };
    await storage.writeJSON("data/terms.json", data, `admin update term ${id}`);
    return json({ ok: true, term: data.terms[idx] });
  }
  if (context.request.method === "DELETE") {
    if (idx < 0) return json({ error: "not found" }, 404);
    data.terms.splice(idx, 1);
    await storage.writeJSON("data/terms.json", data, `admin delete term ${id}`);
    return json({ ok: true });
  }
  return json({ error: "method" }, 405);
}
