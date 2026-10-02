import { json } from "../../_lib/util.js";
import { requireAuth } from "../../_lib/auth.js";
import { getStorage } from "../../_lib/storage.js";

const DEFAULTS = {
  title: "",
  description: "",
  nav: "",
  brand: "#C8442E",
  footer: "",
  analytics: "",
};

export async function onRequest(context) {
  const user = await requireAuth(context);
  if (!user) return json({ error: "unauthorized" }, 401);
  const storage = await getStorage(context.env);
  if (context.request.method === "GET") {
    const s = (await storage.readJSON("data/settings.json")) || {};
    return json({ settings: { ...DEFAULTS, ...s } });
  }
  if (context.request.method === "PUT") {
    const b = await context.request.json().catch(() => ({}));
    const s = { ...DEFAULTS, ...b };
    await storage.writeJSON("data/settings.json", s, "admin update settings");
    return json({ ok: true, settings: s });
  }
  return json({ error: "method" }, 405);
}
