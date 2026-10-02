import { json } from "../../_lib/util.js";
import { requireAuth } from "../../_lib/auth.js";
import { getStorage } from "../../_lib/storage.js";
import { GitHubStorage } from "../../_lib/github.js";

export async function onRequest(context) {
  const user = await requireAuth(context);
  if (!user) return json({ error: "unauthorized" }, 401);
  const storage = await getStorage(context.env);
  const terms = ((await storage.readJSON("data/terms.json")) || { terms: [] }).terms
    .length;
  const assets = ((await storage.readJSON("data/assets.json")) || []).length;
  const users = ((await storage.readJSON("data/users.json")) || []).length;
  let deploy = "本地模式（未配置 GitHub 写回）";
  if (context.env.GH_TOKEN && context.env.GH_REPO) {
    try {
      const gh = new GitHubStorage(context.env);
      const c = await gh.lastCommit();
      if (c) deploy = `最近部署：${c.sha} · ${c.date}`;
    } catch (e) {
      deploy = "GitHub 查询失败：" + e.message;
    }
  }
  return json({ stats: { terms, assets, users, deploy } });
}
