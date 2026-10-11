# 码译 · VibeCode —— MCP Server

让 Cursor / Claude Desktop / 任意支持 MCP（Model Context Protocol）的客户端，直接查询
本仓库的「前端组件术语库」。AI 编程助手在写前端代码时，可随时检索术语、获取大白话解释、
反模式、修复建议与可复制提示词。

> 这是参考 [HeroUI](https://www.heroui.com/) 的 AI 工具链思路做的：把领域知识封装成
> AI 可消费的格式（llms.txt + MCP），让 LLM 在编码时「用得上」你的内容。

## 零依赖

仅需 Python 3.8+，**不需要 `pip install`**。整个 server 只用 Python 标准库。

## 提供的能力

| 工具 | 作用 |
|------|------|
| `search_vibecode_terms` | 按关键词检索术语（支持中文名 / 英文名 / 大白话 / 反模式 / 平台差异），返回链接与一句话释义 |
| `get_vibecode_term` | 取某条术语完整解释：大白话、反模式、修复、平台差异、可复制提示词。参数可为名称 / 英文名 / slug / id |

URL slug 复刻 `gen_vibecode.py` 的算法，与线上站点 `https://mayi-vibecode.pages.dev/<slug>/` 完全一致。

## 接入方式

### 1) Cursor

在项目根新建 `.cursor/mcp.json`（或全局 `~/.cursor/mcp.json`）：

```json
{
  "mcpServers": {
    "vibecode": {
      "command": "python",
      "args": ["/绝对路径/到/mayi-VibeCode/mcp/vibecode_mcp.py"]
    }
  }
}
```

> 如果 `python` 不在 PATH，把 `command` 换成 python 可执行文件的绝对路径。

### 2) Claude Desktop

编辑 `claude_desktop_config.json`（macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
／ Windows: `%APPDATA%\Claude\claude_desktop_config.json`）：

```json
{
  "mcpServers": {
    "vibecode": {
      "command": "python",
      "args": ["/绝对路径/到/mayi-VibeCode/mcp/vibecode_mcp.py"]
    }
  }
}
```

### 3) 其他 MCP 客户端

只要是 stdio 传输的 MCP client，把启动命令指到 `vibecode_mcp.py` 即可。

## 验证是否连上

在客户端里问一句：「用 VibeCode 查一下 sticky 吸顶怎么写」，若 AI 能返回
`导航栏悬浮吸顶` 的链接与解释，说明 MCP 已生效。

也可手动发一条 JSON-RPC 自测：

```bash
printf '{"jsonrpc":"2.0","id":1,"method":"tools/list"}\n' | python mcp/vibecode_mcp.py
```

（注：标准 MCP 使用 `Content-Length` 帧；上面这是最简冒烟测试，正式通信由客户端完成。）

## 环境变量

- `VIBECODE_SITE_BASE`：覆写术语详情页基地址（默认 `https://mayi-vibecode.pages.dev`）。

## 文件

- `vibecode_mcp.py` —— server 本体（标准库实现，无第三方依赖）
- `README.md` —— 本说明

## 配合 llms.txt 使用

站点根目录还生成了 `llms.txt` 与 `llms-full.txt`（由 `gen_vibecode.py` 构建时产出），
是给 LLM 抓取的浓缩知识索引。MCP 偏「交互式精确查询」，llms.txt 偏「一次性喂给模型的
全量索引」，两者互补。
