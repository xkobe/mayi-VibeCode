import { json } from "../_lib/util.js";
import { clearCookie } from "../_lib/auth.js";

export async function onRequest() {
  return json({ ok: true }, 200, { "Set-Cookie": clearCookie() });
}
