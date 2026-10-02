import { json } from "../_lib/util.js";
import { checkCredentials, makeToken, setCookie } from "../_lib/auth.js";

export async function onRequest(context) {
  if (context.request.method !== "POST")
    return json({ error: "method not allowed" }, 405);
  const body = await context.request.json().catch(() => ({}));
  const user = await checkCredentials(context, body.username || "", body.password || "");
  if (!user) return json({ error: "用户名或密码错误" }, 401);
  const secret = context.env.AUTH_SECRET || "dev-secret-change-me";
  const token = await makeToken(user, secret);
  return json({ ok: true, user }, 200, { "Set-Cookie": setCookie(token) });
}
