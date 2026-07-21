# 跨平台可选工具接入指南（deep-market-research v2.3.0）

> 本文件是 `SKILL.md` 的**可选补充**。核心调研流程（Step 0–8 + 三-B 深度研究闭环）**零依赖、零安装**即可运行，只用 LLM 内置 `web_search` / `web_fetch` + 🆓 免费 REST API。
> 本文档仅说明：如何为**有需要的用户**在各自平台上接入**可选增强工具**以丰富素材来源。
> **缺失任何工具都不影响主流程**——未接入则自动回退默认层，输出质量不降。

---

## 0. 通用原则

1. **可选 ≠ 必需**：所有工具仅作素材源增强；主检索永远由内置搜索 + 免费 API 兜底。
2. **优雅降级**：某工具未配置 / 无 key / 调用失败 → 跳过并在报告注明"未覆盖该维度"，绝不报错中断。
3. **不绑死平台**：SKILL.md 主管线不引用任何平台的 MCP 文件名、agent-team 协议或专有后端。换平台无需改技能。
4. **远程优先**：优先用官方远程 MCP（URL 形式，零安装）；本地进程仅作"最强深度"可选项。
5. **交叉验证来源**：下列免费额度为 2026-07 通过多家第三方定价聚合站 + 官方文档交叉验证后的快照；搜索 API 季度漂移，生产前请回源官网复核。

---

## 1. 可选工具清单（按推荐层级分类）

### 分类推荐排名表（首选 / 备选 / 兜底 / 个性化）

> 下表按「分类 + 推荐层级」对可选数据源与增强 Skill 做统一排名（2026-07 交叉验证快照；搜索 API 季度漂移，生产前请回源官网复核）。
> **推荐层级**：🥇 首选（默认增强）· 🥈 备选（同级替代）· 🛟 兜底（keyless 默认层，缺 key 也能跑）· 🎯 个性化（需 key / 账号 / 特定平台）· ⚠️ 不推荐通用。

| 分类 | 工具 | 推荐层级 | 关键事实（免费额度 / keyless / 维护） | 适用场景 / 备注 |
|------|------|----------|----------------------------------------|----------------|
| **通用搜索/抓取** | **Firecrawl** | 🥇 首选 | keyless 远程 MCP · 1,000 积分/月（2026-06 上线）· 活跃维护 | 默认结构化抓取/抽取增强；额度耗尽可绑 key |
| 通用搜索/抓取 | Exa | 🥈 备选 | 1,000 请求/月 · 需 key · 活跃维护 | 神经/语义检索；免费层较小 |
| 通用搜索/抓取 | Tavily | 🥈 备选 | 1,000 积分/月 · 需 key · 2026-02 被 Nebius 收购（$275M–$400M） | 通用搜索 API；长期独立性待观察 |
| 通用搜索/抓取 | Brave Search | 🥉 备选 | $5 月度赠金 ≈ 1,000 次 · 需 key · 活跃维护 | 独立索引、隐私优先；需绑卡 |
| 通用搜索/抓取 | AnySearch | 🎯 个性化 | 匿名 1,000 次/天（keyless）/ 免费 key 更高 · 新兴 | 垂直领域搜索有特色；76.4% 系 [VENDOR CLAIM]，质量待验证 |
| 通用搜索/抓取 | DuckDuckGo | 🛟 兜底 | keyless · 免费 · 限额低/非官方 API | 内置层外的轻量兜底检索 |
| **AI 搜索/答案** | Perplexity Sonar | 🎯 个性化 | 无永久免费层 · 付费（$1–$15/1M tokens）· 活跃维护 | 高质量带引用答案；纯免费场景不经济 |
| AI 搜索/答案 | 秘塔搜索 Metaso | 🎯 个性化 | Web 免费 · API ≈ ¥0.03/次（新用户 50 次试用）· CN 活跃 | 中文 AI 搜索 + 事实检验 |
| **深度研究闭环** | GPT Researcher | 🛟 兜底（高级） | 本地进程/Ollama · 依赖重 · 启动慢 | 仅高级用户在独立 venv 部署；纯提示词三-B 已可替代 |
| 深度研究闭环 | local-deep-researcher | ⚠️ 不推荐通用 | 依赖本地 Ollama/LMStudio | 仅涉密/离线场景单独考虑，与“零本地”定位冲突 |
| **代码/仓库/文档** | **DeepWiki** | 🥇 首选 | keyless 远程 MCP · 公共仓库完全免费 · Cognition 官方维护 | 仓库/文档问答默认增强 |
| 代码/仓库/文档 | GitHub MCP / gh CLI | 🥈 备选 | 平台特定 · 多用 token/key | WorkBuddy/Claude 等平台原生接入 |
| **中文/国内** | ModelScope 魔塔 | 🎯 个性化 | 2,000 次/天 · 需阿里云账号 + 实名认证 + token · 活跃 | 中文模型/数据集/推理（Qwen/DeepSeek 等） |
| 中文/国内 | aihot（已内置） | 🛟 兜底 | 免 key · 中文 AI 资讯 · 已吸收为可选源 | 中文 AI 资讯兜底，无需额外接入 |
| **平台专有 Skill** | web-access / agent-reach / agent-browser | 🎯 个性化 | 平台专有 skill（WorkBuddy 等）· 不跨平台 | 仅特定平台 UGC/浏览器覆盖；不纳入平台无关推荐层 |
| **兜底基座** | 内置 `web_search` / `web_fetch` + 🆓 免费 REST API | 🛟 兜底（质量基座） | keyless · 零安装 · 所有平台 | 默认主力检索入口，保证管线永不中断 |

> 规则：🥇 首选 与 🥈 备选 默认接入（keyless 优先）；🛟 兜底 始终在线；🎯 个性化 按用户 key / 平台按需开；⚠️ 不推荐通用 项不纳入默认路径。所有项缺失即优雅跳过，输出质量由 Step 0–8 + 三-B 闭环保证，不降档。

### 1.1 默认层 · 零依赖零安装（质量基座）

| 工具 | 能力 | 接入方式 | 费用 | 备注 |
|------|------|----------|------|------|
| **LLM 内置搜索** | 通用网页搜索 / 网页抓取 | 无需配置 | 包含在模型订阅/额度中 | 各平台实现不同，结果质量取决于模型 |
| **免费 REST API** | 学术/代码/开放数据 | 直调 OpenAlex / arXiv / Crossref / GitHub API 等 | 免费 | 优先用于论文、DOI、开源项目 |
| **DuckDuckGo** | 通用网页搜索 | 社区 MCP（stdio）或 WebFetch | 免费、免 key | HTML 前端抓取，无 SLA，偶发解析失效；适合低频兜底 |

### 1.2 可选增强层 · 按需接入

| 工具 | 能力 | 接入方式 | 免费额度（2026-07 交叉验证） | 推荐度 | 备注 |
|------|------|----------|------------------------------|--------|------|
| **Firecrawl** | 网页抓取 / 搜索 / 页面交互 | 远程 MCP `https://mcp.firecrawl.dev/v2/mcp`（keyless）或 API key | keyless 1,000 积分/月 | ⭐⭐⭐⭐⭐ | 官方 keyless MCP，开箱即用；额度耗尽后可绑 key |
| **DeepWiki** | GitHub 仓库研究 | 远程 MCP `https://mcp.deepwiki.com/mcp`（keyless） | 免费（仅公共仓库） | ⭐⭐⭐⭐⭐ | Cognition 官方，免登录；对技术仓库调研极有价值 |
| **Exa** | 神经/垂直索引搜索 | 远程 MCP `https://mcp.exa.ai/mcp` 需 API key | 1,000 请求/月（免费层） | ⭐⭐⭐⭐ | 神经搜索质量高，$7/1k；免费层较小 |
| **Tavily** | AI 搜索 API | 远程 MCP `https://mcp.tavily.com/mcp` 或 API key | 1,000 积分/月 | ⭐⭐⭐⭐ | LangChain 生态默认；2026-02 被 Nebius 收购（$275M–$400M），长期独立性需观察 |
| **Brave Search** | 独立索引搜索 | API key 直调 | $5 月度赠金 ≈ 1,000 次 | ⭐⭐⭐ | 独立索引、隐私优先；需绑卡/验证 |
| **Perplexity Sonar** | 带引用一站式答案 | API key 直调 | 无永久免费层；Pro 订阅含 $5/月 API 额度 | ⭐⭐⭐ | 答案质量高，但成本随 token 叠加；不适合纯免费场景 |
| **ModelScope 魔塔** | 中文模型/数据集/推理 | API token 直调 | 2,000 次/天（需阿里云账号 + 实名认证） | ⭐⭐⭐⭐ | 国内首选；适合 Qwen/DeepSeek 等中文模型推理 |
| **AnySearch** | 统一实时搜索（23 垂直领域） | 远程 MCP `https://api.anysearch.com/mcp`（keyless 匿名）或 API key | 匿名 1,000 次/天；免费 key 更高 | ⭐⭐⭐ | 新兴工具，垂直领域搜索有特色；质量与稳定性待更多实战验证 |
| **秘塔搜索 Metaso** | 中文 AI 搜索 / 学术搜索 | Web 免费；API 按次计费 | Web 搜索免费；API 约 ¥0.03/次，新用户 50 次试用 | ⭐⭐⭐ | 中文搜索体验好；API 非免费，适合轻量 CN 增强 |

### 1.3 不推荐 / 仅特定场景

| 工具 | 原因 |
|------|------|
| **GPT Researcher（本地进程）** | 需要 `git clone` + `pip install` + 配置多个 API key，依赖重、启动慢，不符合"大多数人开箱即用"目标。仅建议高级用户在独立 venv/容器中使用。 |
| **local-deep-researcher / local-deep-research** | 依赖本地 Ollama/LMStudio，与 skill "零本地、泛化优先"定位冲突。仅推荐涉密/离线场景单独考虑。 |
| **agent-browser / agent-reach** | WorkBuddy 生态专有 skill/工具，不具备跨平台通用性。仅 WorkBuddy 用户可按需安装，不纳入平台无关的推荐层。 |

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

**WorkBuddy 专有 skill**（非跨平台）：
- `agent-browser`：官方浏览器自动化 skill，适合需要点击/截图/表单填写的网页任务。
- `agent-reach`：外部站点/API 访问工具，按需安装。

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
