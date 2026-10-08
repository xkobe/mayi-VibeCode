// 存储工厂：生产用 GitHub，本地/测试用本地文件（动态导入，避免生产打包 node:fs）
export async function getStorage(env) {
  if (env && env.GH_TOKEN && env.GH_REPO) {
    const { GitHubStorage } = await import("./github.js");
    return new GitHubStorage(env);
  }
  const { LocalFileStorage } = await import("./storage-local.js");
  return new LocalFileStorage(env);
}
