// 鉴权：基于 HMAC 签名 cookie 的会话（Web Crypto，兼容 Workers / Node）
const COOKIE = "vb_admin";
const enc = new TextEncoder();

function b64url(buf) {
  return Buffer.from(buf).toString("base64url");
}
function b64urlStr(s) {
  return Buffer.from(s, "utf-8").toString("base64url");
}
async function hmac(secret, data) {
  const key = await crypto.subtle.importKey(
    "raw",
    enc.encode(secret),
    { name: "HMAC", hash: "SHA-256" },
    false,
    ["sign"]
  );
  const sig = await crypto.subtle.sign("HMAC", key, enc.encode(data));
  return b64url(sig);
}

export async function makeToken(user, secret) {
  const exp = Date.now() + 1000 * 60 * 60 * 24 * 7; // 7 天
  const payload = b64urlStr(JSON.stringify({ user, exp }));
  const sig = await hmac(secret, payload);
  return payload + "." + sig;
}
export async function verifyToken(token, secret) {
  if (!token || !token.includes(".")) return null;
  const [payload, sig] = token.split(".");
  if (!payload || !sig) return null;
  if ((await hmac(secret, payload)) !== sig) return null;
  try {
    const data = JSON.parse(Buffer.from(payload, "base64url").toString("utf-8"));
    if (data.exp < Date.now()) return null;
    return data.user;
  } catch {
    return null;
  }
}
export function getCookie(req, name) {
  const c = req.headers.get("cookie") || "";
  for (const part of c.split(";")) {
    const idx = part.indexOf("=");
    if (idx < 0) continue;
    if (part.slice(0, idx).trim() === name)
      return decodeURIComponent(part.slice(idx + 1).trim());
  }
  return null;
}
export function setCookie(token) {
  return `${COOKIE}=${token}; Path=/; HttpOnly; SameSite=Lax; Max-Age=${60 * 60 * 24 * 7}`;
}
export function clearCookie() {
  return `${COOKIE}=; Path=/; HttpOnly; Max-Age=0`;
}
export async function requireAuth(context) {
  const secret = context.env.AUTH_SECRET || "dev-secret-change-me";
  const token = getCookie(context.request, COOKIE);
  return await verifyToken(token, secret);
}
export async function checkCredentials(context, username, password) {
  const { getStorage } = await import("./storage.js");
  const storage = await getStorage(context.env);
  // 1) 托管账号（data/users.json）
  try {
    const users = (await storage.readJSON("data/users.json")) || [];
    const u = users.find((u) => u.username === username);
    if (u && (await verifyHash(password, u.passwordHash))) return username;
  } catch {}
  // 2) 环境变量兜底单管理员
  if (
    context.env.ADMIN_USER &&
    context.env.ADMIN_PASS &&
    username === context.env.ADMIN_USER &&
    password === context.env.ADMIN_PASS
  )
    return username;
  return null;
}

// PBKDF2 密码哈希（Web Crypto）
async function pbkdf2(pw, salt, iter) {
  const baseKey = await crypto.subtle.importKey(
    "raw",
    enc.encode(pw),
    "PBKDF2",
    false,
    ["deriveBits"]
  );
  const bits = await crypto.subtle.deriveBits(
    { name: "PBKDF2", salt, iterations: iter, hash: "SHA-256" },
    baseKey,
    256
  );
  return new Uint8Array(bits);
}
export async function hashPassword(pw) {
  const salt = crypto.getRandomValues(new Uint8Array(16));
  const key = await pbkdf2(pw, salt, 100000);
  return b64url(salt) + ":" + b64url(key);
}
export async function verifyHash(pw, stored) {
  const [saltB64, keyB64] = (stored || "").split(":");
  if (!saltB64 || !keyB64) return false;
  const salt = new Uint8Array(Buffer.from(saltB64, "base64url"));
  const key = await pbkdf2(pw, salt, 100000);
  return b64url(key) === keyB64;
}
