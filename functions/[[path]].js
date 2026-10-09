// 全站兜底路由（catch-all）。
// 作用：
//   1) 真实存在的静态资源（首页 / 章节页 / 术语页 / assets / robots.txt / sitemap.xml 等）
//      通过 env.ASSETS 原样返回；
//   2) 找不到的资源（拼写错、已删除、爬虫乱扫）一律返回「真 404」+ 自定义 404 页面。
// 优先级：本文件是 [[path]] 最宽泛路由，低于 /admin/* 等具体路由，
// 所以后台 API / 管理页仍由各专属函数处理，不受影响。
export async function onRequest(context) {
  const { request, env } = context;
  const url = new URL(request.url);

  // 用「同 URL 重新构造的 Request」取静态资源。
  // 坑：直接把原始 request 传给 env.ASSETS.fetch 时，Cloudflare 在 catch-all 下对
  // 带扩展名的嵌套路径（如 /foo/index.html）会解析失败返回 404；
  // 重新构造一个相同 URL 的 Request 即可正常命中（目录式 /foo/ 的补 index 也是这么做的）。
  const fetchAsset = (p) =>
    env.ASSETS.fetch(new Request(url.origin + p + url.search, request));

  // 1) 先按原始路径取静态资源
  let res = await fetchAsset(url.pathname);

  // 2) 目录式访问（/foo 或 /foo/）尝试补 index.html
  if ((!res || res.status === 404) && !url.pathname.endsWith(".html") && url.pathname !== "/") {
    const candidate = url.pathname.endsWith("/")
      ? url.pathname + "index.html"
      : url.pathname + "/index.html";
    res = await fetchAsset(candidate);
  }

  // 3) 命中真实资源 -> 直接返回
  if (res && res.status === 200) return res;

  // 4) 未命中 -> 真 404（带自定义 404 页）
  const nf = await fetchAsset("/404.html");
  if (nf && nf.status === 200) {
    return new Response(nf.body, {
      status: 404,
      headers: {
        "Content-Type": "text/html; charset=utf-8",
        "Cache-Control": "public, max-age=0, must-revalidate",
      },
    });
  }
  return new Response("404 Not Found", {
    status: 404,
    headers: { "Content-Type": "text/plain; charset=utf-8" },
  });
}
