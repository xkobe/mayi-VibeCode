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
  await storage.deleteAsset(name);
  const list = (await storage.readJSON("data/assets.json")) || [];
  await storage.writeJSON(
    "data/assets.json",
    list.filter((x) => x.name !== name),
    `delete asset ${name}`
  );
  return json({ ok: true });
}
