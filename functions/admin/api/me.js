import { json } from "../../_lib/util.js";
import { requireAuth } from "../../_lib/auth.js";

export async function onRequest(context) {
  const user = await requireAuth(context);
  return json({ user: user || null });
}
