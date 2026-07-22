# 跨平台可选工具接入指南（deep-market-research v2.3.1）

> 本文件是 `SKILL.md` 的**可选补充**。核心调研流程（Step 0–8 + 三-B 深度研究闭环）**零依赖、零安装**即可运行，只用 LLM 内置 `web_search` / `web_fetch` + 🆓 免费 REST API。
> 本文档仅说明：如何为**有需要的用户**在各自平台上接入**可选增强工具**以丰富素材来源。
> **缺失任何工具都不影响主流程**——未接入则自动回退默认层，输出质量不降。

---

## 0. 通用原则

1. **可选 ≠ 必需**：所有工具仅作素材源增强；主检索永远由内置搜索 + 免费 API 兜底（基座始终并行调用，增强层并行叠加，结论以 Step 4 交叉验证裁决）。
2. **优雅降级**：某工具未配置 / 无 key / 调用失败 → 跳过并在报告注明"未覆盖该维度"，绝不报错中断。
3. **不绑死平台**：SKILL.md 主管线不引用任何平台的 MCP 文件名、agent-team 协议或专有后端。换平台无需改技能。
4. **远程优先**：优先用官方远程 MCP（URL 形式，零安装）；本地进程仅作"最强深度"可选项。
5. **交叉验证来源**：下列免费额度为 2026-07 通过多家第三方定价聚合站 + 官方文档交叉验证后的快照；搜索 API 季度漂移，生产前请回源官网复核。

---

## 1. 可选工具清单（按推荐层级分类）

> 推荐层级：🥇 首选（keyless 零配置）· 🥈 备选 · 🥉 备选 · 🛟 兜底（缺 key 也能跑）· 🎯 个性化（需 key / 账号 / 特定平台）· ⚠️ 不推荐通用。免费额度为 2026-07 交叉验证快照，搜索 API 季度漂移，生产前请回源官网复核。

### 1.1 默认层 · 零依赖零安装（质量基座 · 🛟 兜底）

| 工具 | 能力 | 接入方式 | 费用 | 推荐层级 | 备注 |
|------|------|----------|------|----------|------|
| LLM 内置搜索 | 通用网页搜索 / 网页抓取 | 无需配置 | 含模型订阅/额度 | 🛟 兜底（基座） | 各平台实现不同，质量取决于模型 |
| 免费 REST API | 学术/代码/开放数据 | 直调 OpenAlex / arXiv / Crossref / GitHub API 等 | 免费 | 🛟 兜底（基座） | 优先用于论文、DOI、开源项目 |
| DuckDuckGo | 通用网页搜索 | 社区 MCP（stdio）或 WebFetch | 免费、免 key | 🛟 兜底 | HTML 前端抓取，无 SLA，偶发解析失效；低频兜底 |

### 1.2 可选增强层 · 按需接入

| 工具 | 能力 | 接入方式 | 免费额度（2026-07 交叉验证） | 推荐层级 | 备注 |
|------|------|----------|------------------------------|----------|------|
| Firecrawl | 网页抓取 / 搜索 / 页面交互 | 远程 MCP `https://mcp.firecrawl.dev/v2/mcp`（keyless）或 API key | keyless 1,000 积分/月 | 🥇 首选 | 官方 keyless MCP，开箱即用；额度耗尽可绑 key |
| DeepWiki | GitHub 仓库研究 | 远程 MCP `https://mcp.deepwiki.com/mcp`（keyless） | 免费（仅公共仓库） | 🥇 首选 | Cognition 官方，免登录；技术仓库调研极有价值 |
| Exa | 神经/垂直索引搜索 | 远程 MCP `https://mcp.exa.ai/mcp` 需 API key | 1,000 请求/月（免费层） | 🥈 备选 | 神经搜索质量高；免费层较小 |
| Tavily | AI 搜索 API | 远程 MCP `https://mcp.tavily.com/mcp` 或 API key | 1,000 积分/月 | 🥈 备选 | 2026-02 被 Nebius 收购（$275M–$400M），长期独立性待观察 |
| Brave Search | 独立索引搜索 | API key 直调 | $5 月度赠金 ≈ 1,000 次 | 🥉 备选 | 独立索引、隐私优先；需绑卡/验证 |
| Novada | 网页搜索/SERP/抓取/提取/地图/爬取/深度研究（25+ 工具） | 托管 Streamable-HTTP MCP，`npx novada-mcp` | 免费 1,000 次/月 | 🥈 备选 | 新兴 SaaS，免安装，覆盖 195 国；长期可用性待观察 |
| Novada Web Unblocker | 住宅代理 / 反爬解锁，抓取地理封锁 / 反 bot 受保护的页面 | 代理网关（用户名+密码，或 `NOVADA_API_KEY`）| 付费（按流量）| 🛟 兜底（解锁层）| 与 Firecrawl 反爬能力部分重叠；Firecrawl 已覆盖多数解锁场景。仅作「Firecrawl/WebFetch 仍被墙」的兜底解锁层，不进核心管线；key 本地仅存 |
| SearXNG | 元搜索引擎（多引擎聚合） | 自托管实例 / 公共实例 MCP | 免费、免 key（自托管） | 🛟 兜底（自托管 keyless） | 元搜索聚合；需自托管或可信公共实例 |
| Perplexity Sonar | 带引用一站式答案 | API key 直调 | 无永久免费层；Pro 订阅含 $5/月 API 额度 | 🎯 个性化 | 答案质量高，成本随 token 叠加；非纯免费场景 |
| ModelScope 魔塔 | 中文模型/数据集/推理 | API token 直调 | 2,000 次/天（需阿里云账号 + 实名认证） | 🎯 个性化 | 国内首选；适合 Qwen/DeepSeek 等中文模型推理 |
| AnySearch | 统一实时搜索（23 垂直领域） | 远程 MCP `https://api.anysearch.com/mcp`（keyless 匿名）或 API key | 匿名 1,000 次/天；免费 key 更高 | 🎯 个性化 | 新兴工具，垂直领域有特色；质量稳定性待验证。**⚠️ 已评估：与 exa/tavily/firecrawl 通用搜索高度重叠，不进核心管线；本地未装 skill（仅存 anysearchAPIKEY.txt），仅作匿名兜底可选** |
| 秘塔搜索 Metaso | 中文 AI 搜索 / 学术搜索 | Web 免费；API 按次计费 | Web 搜索免费；API 约 ¥0.03/次，新用户 50 次试用 | 🎯 个性化 | 中文搜索体验好；API 非免费，轻量 CN 增强 |
| Connected Papers | 论文关联图谱 / 引文网络（S2 ShaID → 研究邻里图） | API key（`connectedpapers-py` 客户端）| 早期访问，限量（用户 key 余 ~50 次图谱构建，5 次/分钟）| 🎯 个性化 | 与 dmr 既有 S2/OpenAlex 引文覆盖重叠；仅作深度技术尽调可选源，**不进核心管线**；key 本地仅存 |
| FRED（美联储经济数据） | 美国经济/金融**结构化时间序列**（GDP/CPI/利率/就业/M2 等 80 万+ 系列） | API key 直调 `api.stlouisfed.org`（或 `scripts/fred_query.py`）| 免费、官方、无限额（需免费 api_key）| 🥈 备选【建议采纳】 | 官方权威宏观数据源，补 dmr **结构化经济数据空白**（exa/tavily 是搜索、非结构化）；免费稳定，强烈建议作为金融/经济深度研究核心可选源；不进核心管线（主流程零依赖），作增强层 |

### 1.3 不推荐 / 仅特定场景

| 工具 | 推荐层级 | 原因 |
|------|----------|------|
| GPT Researcher（本地进程） | ⚠️ 不推荐通用 | 需 git clone + pip install + 多 API key，依赖重、启动慢；仅高级用户在独立 venv/容器部署 |
| local-deep-researcher / local-deep-research | ⚠️ 不推荐通用 | 依赖本地 Ollama/LMStudio，与"零本地、泛化优先"定位冲突；仅涉密/离线场景单独考虑 |
| agent-browser | 🎯 平台专有（已评估） | WorkBuddy 专有浏览器自动化。**抓取/JS 渲染能力与 Firecrawl 重叠且更重**（需 Chromium 500MB+GUI daemon、冷启慢、非无头）。dmr 场景下 Firecrawl 更优 → **不进核心管线**，仅保留为「需登录/点击/表单的交互式高墙源」最后兜底 |
| agent-reach | 🎯 平台专有（已评估·建议采纳为可选社媒层） | WorkBuddy 专有 14 平台聚合（Twitter/X·Reddit·YouTube·Bilibili·小红书·抖音·微博·公众号·LinkedIn·Instagram·RSS + Exa/web）。**覆盖 8 个 MCP + 默认层均未触及的社媒/草根另类数据**，对深度市场研究情绪/趋势信号价值高 → 建议采纳为可选社交/UGC 增强层。注意：(a) 默认 `disable:true`，需改元数据 `disable:false` 并 `agent-reach doctor` 配置频道；(b) 其 Exa/web 频道与现有 exa/tavily/firecrawl 冗余——只取其社媒频道；(c) 小红书/抖音/公众号等需登录 cookie；(d) 不进核心管线 |


---

## 2. 平台接入速查

### 2.1 WorkBuddy

**远程 MCP（零安装，推荐）**：编辑 `~/.workbuddy/mcp.json`（或 `.mcp.json`）加入：

```json
{
  "mcpServers": {
    "firecrawl": { "url": "https://mcp.firecrawl.dev/v2/mcp" },
    "deepwiki":  { "url": "https://mcp.deepwiki.com/mcp" },
    "exa":       { "url": "https://mcp.exa.ai/mcp",
                    "headers": { "Authorization": "Bearer ${EXA_API_KEY}" } },
    "tavily":    { "url": "https://mcp.tavily.com/mcp",
                    "headers": { "Authorization": "Bearer ${TAVILY_API_KEY}" } }
  }
}
```

**API key 直调**（Brave / Perplexity / ModelScope）：在环境变量或配置中提供 key，技能按 `BRAVE_API_KEY` / `PERPLEXITY_API_KEY` / `MODELSCOPE_API_KEY` 等探测。

**WorkBuddy 专有 skill**（非跨平台，本地已装）：
- `agent-browser`：浏览器自动化。**与 Firecrawl 重叠且更重，不进 dmr 核心管线**；仅作需交互/登录的高墙源兜底。
- `agent-reach`：**建议采纳为可选社媒/UGC 增强层**（Twitter/Reddit/YouTube/Bilibili/小红书/抖音/微博/公众号/LinkedIn/RSS 等）。默认 `disable:true`，需改 `disable:false` + `agent-reach doctor` 配频道；只取其社媒频道（Exa/web 频道冗余已有）。

---

### 2.2 Claude（Claude CLI / Desktop）

**远程 MCP**：

```bash
claude mcp add firecrawl --transport http https://mcp.firecrawl.dev/v2/mcp
claude mcp add deepwiki  --transport http https://mcp.deepwiki.com/mcp
```

需 key 的工具：

```bash
claude mcp add exa --transport http https://mcp.exa.ai/mcp --header "Authorization: Bearer ${EXA_API_KEY}"
claude mcp add tavily --transport http https://mcp.tavily.com/mcp --header "Authorization: Bearer ${TAVILY_API_KEY}"
```

**API key 直调**：在对话中提供 `EXA_API_KEY` / `TAVILY_API_KEY` / `PERPLEXITY_API_KEY` 等，或写入 shell profile 供 Claude Code 读取。

---

### 2.3 Codex（OpenAI Codex CLI）

Codex CLI 支持 MCP 配置（与 Claude 类似）。

**远程 MCP**：在 Codex 的 MCP 配置（通常 `~/codex/config.toml` 或 `--mcp` 参数）中加入上述 URL。

**API key 直调**：Codex 原生可读取 `OPENAI_API_KEY`；其他 key 通过环境变量注入。

---

### 2.4 Trae（字节 Trae IDE）

Trae 支持 MCP 设置面板 / 配置文件（`~/.trae/mcp.json` 或项目内）。

**远程 MCP**：在 MCP 设置中添加 Firecrawl / DeepWiki / Exa / Tavily 的 URL（HTTP 传输）。

**API key 直调**：在 Trae 设置或环境变量中提供 key。

---

### 2.5 qoder（阿里云 qoder）

qoder 技能目录位于 `~/.qoder/skills/`，MCP 配置见其设置。

**远程 MCP**：在 qoder 的 MCP 配置中加入上述 URL。

**API key 直调**：通过环境变量或 qoder 设置面板提供。

---

### 2.6 Cursor

Cursor 通过项目根目录 `.cursor/mcp.json` 或全局 `~/.cursor/mcp.json` 配置 MCP。

**远程 MCP**：

```json
{
  "mcpServers": {
    "firecrawl": { "url": "https://mcp.firecrawl.dev/v2/mcp" },
    "deepwiki":  { "url": "https://mcp.deepwiki.com/mcp" },
    "exa":       { "url": "https://mcp.exa.ai/mcp",
                    "headers": { "Authorization": "Bearer ${EXA_API_KEY}" } },
    "tavily":    { "url": "https://mcp.tavily.com/mcp",
                    "headers": { "Authorization": "Bearer ${TAVILY_API_KEY}" } }
  }
}
```

**API key 直调**：在 Cursor 设置或 `.env` 中提供 key，技能按环境变量探测。

---

## 3. 降级与故障处理

| 场景 | 处理 |
|------|------|
| 远程 MCP 不可达 | 跳过该工具，回退内置搜索 + 免费 API；报告注明未覆盖 |
| API key 缺失 / 失效 | 跳过该工具，回退默认层；不报错 |
| keyless 额度耗尽 | 自动切换需 key 工具或回退默认层 |
| 本地进程未装 / 启动失败 | 回退纯提示词深度研究闭环（三-B），质量不降 |

> **关键认知**：本技能的质量由 Step 0–8 + 三-B 闭环的方法论保证，而非由某个搜索 API 决定。即使所有可选工具都缺失，输出仍是带源分级、交叉验证、置信标签的可复现报告。可选工具只是"更快 / 更广 / 更深"的加速器。

---

## 4. 安全与隐私提示

- 远程 MCP 的 keyless 端点（Firecrawl / DeepWiki）无需任何密钥，复制 URL 即用。
- 需 key 的工具：key 只存在你本机环境变量 / MCP 配置中，**不要**写进 SKILL.md 或提交到仓库。
- 本地进程（GPT Researcher / ModelScope 服务端）仅在你本机运行，数据不出本地（若用云端 LLM key 则检索/生成走云端，符合"非涉密"前提）。
- 涉密 / 隐私敏感调研请走纯本地 LLM（Ollama 等）方案，本技能默认云端路径不假设该场景。
