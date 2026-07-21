# 跨平台可选工具接入指南（deep-market-research v2.3.0）

> 本文件是 `SKILL.md` 的**可选补充**。核心调研流程（Step 0–8 + 三-B 深度研究闭环）**零依赖、零安装**即可运行，只用 LLM 内置 `web_search` / `web_fetch` + 🆓 免费 REST API。
> 本文档仅说明：如何为**有需要的用户**在各自平台上接入**可选增强工具**（Exa / Firecrawl / Tavily / Perplexity / GPT Researcher / ModelScope）以丰富素材来源。
> **缺失任何工具都不影响主流程**——未接入则自动回退默认层，输出质量不降。

---

## 0. 通用原则

1. **可选 ≠ 必需**：所有工具仅作素材源增强；主检索永远由内置搜索 + 免费 API 兜底。
2. **优雅降级**：某工具未配置 / 无 key / 调用失败 → 跳过并在报告注明"未覆盖该维度"，绝不报错中断。
3. **不绑死平台**：SKILL.md 主管线不引用任何平台的 MCP 文件名、agent-team 协议或专有后端。换平台无需改技能。
4. **远程优先**：优先用官方远程 MCP（URL 形式，零安装）；本地进程（GPT Researcher / ModelScope 服务端）仅作"最强深度"可选项。

---

## 1. 可选工具清单（按接入方式分类）

| 工具 | 能力 | 接入方式 | 免费额度（2026-07 快照） |
|------|------|----------|------------------------|
| **Exa** | 神经/垂直索引搜索 | 远程 MCP `https://mcp.exa.ai/mcp`（keyless）或 API key | 20,000 请求/月 |
| **Firecrawl** | 网页抓取 / 监控 / agent | 远程 MCP `https://mcp.firecrawl.dev/v2/mcp`（keyless 1000/月）或 API key | keyless 1000/月 |
| **DeepWiki** | 代码仓库研究 | 远程 MCP `https://mcp.deepwiki.com/mcp`（keyless） | 免费 |
| **Tavily** | 搜索 API | 远程 MCP `https://mcp.tavily.com/mcp` 或 API key | 1,000 请求/月 |
| **Perplexity Sonar** | 带引用一站式答案 | API key 直调 | 免费层 |
| **Brave** | 独立索引搜索 | API key 直调 | 2,000 查询/月 |
| **GPT Researcher** | 自动化深度研究闭环 | 本地进程（Python）或远程部署 MCP | 需 OpenAI/Exa key |
| **ModelScope 魔塔** | 中文模型/数据集/推理 | API token 直调或 MCP | 免费（需实名） |

> 定价为 **2026-07 快照**，搜索 API 季度漂移，生产前回源官网复核。

---

## 2. WorkBuddy

**远程 MCP（零安装，推荐）**：编辑 `~/.workbuddy/mcp.json`（或 `.mcp.json`）加入：

```json
{
  "mcpServers": {
    "exa":        { "url": "https://mcp.exa.ai/mcp" },
    "firecrawl":  { "url": "https://mcp.firecrawl.dev/v2/mcp" },
    "deepwiki":   { "url": "https://mcp.deepwiki.com/mcp" },
    "tavily":     { "url": "https://mcp.tavily.com/mcp",
                    "headers": { "Authorization": "Bearer ${TAVILY_API_KEY}" } }
  }
}
```

**API key 直调**（Perplexity / Brave / Exa / Tavily）：在环境变量或配置中提供 key，技能按 `PERPLEXITY_API_KEY` / `BRAVE_API_KEY` 等探测。

**GPT Researcher（本地进程，可选最强深度）**：
```bash
pip install "gpt-researcher[mcp]"   # 建议装入独立 venv，勿污染全局
python -m gpt_researcher.mcp        # 启动 stdio MCP server
```
在 `mcp.json` 中以 stdio 方式接入，并设置 `LLM_PROVIDER` / `SEARCH_API` 等 env。

**ModelScope（可选）**：`pip install modelscope-mcp-server`，用 API token 以 stdio MCP 接入。

---

## 3. Claude（Claude CLI / Desktop / Codex 类）

Claude 系列通过 **MCP 配置** 接入远程服务，或在提示词中直接调用 API。

**远程 MCP（Claude Desktop / CLI）**：
```bash
claude mcp add exa --transport http https://mcp.exa.ai/mcp
claude mcp add firecrawl --transport http https://mcp.firecrawl.dev/v2/mcp
claude mcp add deepwiki --transport http https://mcp.deepwiki.com/mcp
```

**API key 直调**：在对话中提供 `EXA_API_KEY` / `TAVILY_API_KEY` / `PERPLEXITY_API_KEY` 等，技能按环境变量探测；或写入 shell profile 供 Claude Code 读取。

**本地进程（GPT Researcher / ModelScope）**：同上 `pip install` 后，以 stdio MCP 注册到 Claude 的 MCP 配置（`~/.claude.json` 或项目 `.mcp.json`）。

---

## 4. Codex（OpenAI Codex CLI）

Codex CLI 支持 MCP 配置（与 Claude 类似）。

**远程 MCP**：在 Codex 的 MCP 配置（通常 `~/codex/config.toml` 或 `--mcp` 参数）中加入上述 URL。

**API key 直调**：Codex 原生可读取 `OPENAI_API_KEY`；其他 key 通过环境变量注入。

**本地进程**：同 WorkBuddy 节，GPT Researcher / ModelScope 以 stdio MCP 接入。

---

## 5. Trae（字节 Trae IDE）

Trae 支持 MCP 设置面板 / 配置文件（`~/.trae/mcp.json` 或项目内）。

**远程 MCP**：在 MCP 设置中添加 Exa / Firecrawl / DeepWiki / Tavily 的 URL（HTTP 传输）。

**API key 直调**：在 Trae 设置或环境变量中提供 key。

**本地进程**：GPT Researcher / ModelScope 以 stdio MCP 接入 Trae 的 MCP 列表。

---

## 6. qoder（阿里云 qoder）

qoder 技能目录位于 `~/.qoder/skills/`，MCP 配置见其设置。

**远程 MCP**：在 qoder 的 MCP 配置中加入上述 URL。

**API key 直调**：通过环境变量或 qoder 设置面板提供。

**本地进程**：GPT Researcher / ModelScope 以 stdio MCP 接入。

---

## 7. Cursor

Cursor 通过项目根目录 `.cursor/mcp.json` 或全局 `~/.cursor/mcp.json` 配置 MCP。

**远程 MCP**：
```json
{
  "mcpServers": {
    "exa":       { "url": "https://mcp.exa.ai/mcp" },
    "firecrawl": { "url": "https://mcp.firecrawl.dev/v2/mcp" },
    "deepwiki":  { "url": "https://mcp.deepwiki.com/mcp" }
  }
}
```

**API key 直调**：在 Cursor 设置或 `.env` 中提供 key，技能按环境变量探测。

**本地进程**：GPT Researcher / ModelScope 以 stdio MCP 接入 `.cursor/mcp.json`。

---

## 8. 降级与故障处理

| 场景 | 处理 |
|------|------|
| 远程 MCP 不可达 | 跳过该工具，回退内置搜索 + 免费 API；报告注明未覆盖 |
| API key 缺失 / 失效 | 跳过该工具，回退默认层；不报错 |
| 本地进程（GPT Researcher）未装 / 启动失败 | 回退纯提示词深度研究闭环（三-B），质量不降 |
| keyless 额度耗尽 | 自动切换需 key 工具或回退默认层 |

> **关键认知**：本技能的质量由 Step 0–8 + 三-B 闭环的方法论保证，而非由某个搜索 API 决定。即使所有可选工具都缺失，输出仍是带源分级、交叉验证、置信标签的可复现报告。可选工具只是"更快 / 更广 / 更深"的加速器。

---

## 9. 安全与隐私提示

- 远程 MCP（Exa / Firecrawl / DeepWiki）的 keyless 端点无需任何密钥，复制 URL 即用。
- 需 key 的工具：key 只存在你本机环境变量 / MCP 配置中，**不要**写进 SKILL.md 或提交到仓库。
- 本地进程（GPT Researcher / ModelScope）仅在你本机运行，数据不出本地（若用云端 LLM key 则检索/生成走云端，符合"非涉密"前提）。
- 涉密 / 隐私敏感调研请走纯本地 LLM（Ollama 等）方案，本技能默认云端路径不假设该场景。
