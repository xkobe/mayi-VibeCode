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

  // 1) 先按原始路径取静态资源
  let res = await env.ASSETS.fetch(request);

  // 2) 目录式访问（/foo 或 /foo/）尝试补 index.html
  if ((!res || res.status === 404) && !url.pathname.endsWith(".html") && url.pathname !== "/") {
    const candidate = url.pathname.endsWith("/")
      ? url.pathname + "index.html"
      : url.pathname + "/index.html";
    const r2 = new Request(url.origin + candidate, request);
    const res2 = await env.ASSETS.fetch(r2);
    if (res2 && res2.status === 200) return res2;
  }

  // 3) 命中真实资源 -> 直接返回
  if (res && res.status === 200) return res;

  // 4) 未命中 -> 真 404（带自定义 404 页）
  const nf = await env.ASSETS.fetch(new Request(url.origin + "/404.html", request));
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
