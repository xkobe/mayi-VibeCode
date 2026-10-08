// GitHub 存储后端（生产环境）：通过 REST API 读写仓库文件，触发 CF Pages 重建
export class GitHubStorage {
  constructor(env) {
    this.token = env.GH_TOKEN;
    this.repo = env.GH_REPO; // "owner/repo"
    this.branch = env.GH_BRANCH || "main";
    this.api = "https://api.github.com";
  }
  async _req(path, init = {}) {
    const isGet = (init.method || "GET") === "GET";
    const url = `${this.api}/repos/${this.repo}/contents/${path}${
      isGet ? `?ref=${this.branch}` : ""
    }`;
    return fetch(url, {
      ...init,
      headers: {
        Authorization: `Bearer ${this.token}`,
        Accept: "application/vnd.github+json",
        "User-Agent": "vb-admin",
        ...(init.headers || {}),
      },
    });
  }
  async readText(path) {
    const r = await this._req(path, { method: "GET" });
    if (r.status === 404) return null;
    if (!r.ok) throw new Error(`GH read ${path} ${r.status}`);
    const j = await r.json();
    return Buffer.from(j.content, "base64").toString("utf-8");
  }
  async readJSON(path) {
    const t = await this.readText(path);
    return t ? JSON.parse(t) : null;
  }
  async _put(path, contentB64, message, isBinary) {
    let sha = null;
    try {
      const r = await this._req(path, { method: "GET" });
      if (r.ok) sha = (await r.json()).sha;
    } catch {}
    const body = {
      message: message || `admin update ${path}`,
      content: contentB64,
      branch: this.branch,
    };
    if (sha) body.sha = sha;
    const r = await this._req(path, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    if (!r.ok)
      throw new Error(`GH write ${path} ${r.status} ${await r.text()}`);
    return true;
  }
  async writeText(path, text, message) {
    return this._put(path, Buffer.from(text, "utf-8").toString("base64"), message);
  }
  async writeJSON(path, data, message) {
    return this.writeText(path, JSON.stringify(data, null, 1), message);
  }
  async uploadAsset(name, base64Content, message) {
    return this._put(`assets/${name}`, base64Content, message || `upload ${name}`, true);
  }
  async deleteAsset(name) {
    const r = await this._req(`assets/${name}`, { method: "GET" });
    if (!r.ok) return false;
    const j = await r.json();
    const dr = await fetch(
      `${this.api}/repos/${this.repo}/contents/assets/${name}`,
      {
        method: "DELETE",
        headers: {
          Authorization: `Bearer ${this.token}`,
          "User-Agent": "vb-admin",
          Accept: "application/vnd.github+json",
        },
        body: JSON.stringify({ message: `delete ${name}`, sha: j.sha, branch: this.branch }),
      }
    );
    return dr.ok;
  }
  // 最近一次提交（用于看板展示部署时间）
  async lastCommit() {
    const r = await fetch(
      `${this.api}/repos/${this.repo}/commits?per_page=1&sha=${this.branch}`,
      {
        headers: {
          Authorization: `Bearer ${this.token}`,
          "User-Agent": "vb-admin",
        },
      }
    );
    if (!r.ok) return null;
    const arr = await r.json();
    if (!arr.length) return null;
    return { sha: arr[0].sha.slice(0, 7), msg: arr[0].commit.message, date: arr[0].commit.author.date };
  }
}
