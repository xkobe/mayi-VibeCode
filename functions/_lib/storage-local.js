// 本地存储后端（仅开发/测试用，生产必须用 GitHubStorage）
// 注意：Cloudflare Workers 生产运行时没有真实文件系统，此模块只在本地/测试时被动态导入。
import { readFileSync, writeFileSync, existsSync, mkdirSync, unlinkSync } from "node:fs";
import { join, dirname } from "node:path";

export class LocalFileStorage {
  constructor(env) {
    this.root = (env && env.PROJECT_ROOT) || process.cwd();
  }
  _p(p) {
    return join(this.root, p);
  }
  readText(p) {
    const fp = this._p(p);
    if (!existsSync(fp)) return null;
    return readFileSync(fp, "utf-8");
  }
  readJSON(p) {
    const t = this.readText(p);
    return t ? JSON.parse(t) : null;
  }
  writeText(p, text) {
    const fp = this._p(p);
    mkdirSync(dirname(fp), { recursive: true });
    writeFileSync(fp, text, "utf-8");
    return true;
  }
  writeJSON(p, data) {
    return this.writeText(p, JSON.stringify(data, null, 1));
  }
  uploadAsset(name, base64Content) {
    const fp = this._p(`assets/${name}`);
    mkdirSync(dirname(fp), { recursive: true });
    writeFileSync(fp, Buffer.from(base64Content, "base64"));
    return true;
  }
  deleteAsset(name) {
    const fp = this._p(`assets/${name}`);
    if (existsSync(fp)) {
      try {
        unlinkSync(fp);
      } catch (e) {
        // 某些沙箱环境拦截 unlink（safe-delete），本地开发时可忽略
      }
      return true;
    }
    return false;
  }
}
