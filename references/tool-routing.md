# Tool Routing & MCP Configuration — deep-market-research v2.3.0

> 配合 SKILL.md「三-B、工具路由与三层收敛兜底（质量优先）」节。提供开箱即用的零 key 配置、质量优先 L1 升级配置，以及个性化 `§setup` 流程。

## 0. 优先级总纲

**质量+全面性 > 免费 > 速度 > 0key**

- 0key 工具是**兜底不断流**层，不是质量首选。
- 质量由四去管道 + 源分级 + 交叉验证保证，不依赖某个具体搜索 API。

## 1. 零 key 默认配置（L2/L3，任何人开箱即用）

把以下内容写入 WorkBuddy 的 `~/.workbuddy/mcp.json`（或对应 MCP 配置文件）即可，**无需注册任何账号**：

```json
{
  "mcpServers": {
    "exa-keyless": {
      "url": "https://mcp.exa.ai/mcp"
    },
    "firecrawl-keyless": {
      "url": "https://mcp.firecrawl.dev/v2/mcp"
    },
    "deepwiki": {
      "url": "https://mcp.deepwiki.com/mcp"
    },
    "duckduckgo": {
      "command": "npx",
      "args": ["-y", "@nickclyde/duckduckgo-mcp-server"]
    }
  }
}
```

- **Exa keyless** (`mcp.exa.ai/mcp`)：官方明写 "No API key required"，免费计划限流，基础搜索+抓取。
- **Firecrawl Keyless** (`mcp.firecrawl.dev/v2/mcp`)：2026 新上线，每月 1000 免费额度、零 key，覆盖 search/scrape/interact（其 `/interact` `/agent` 已吸收 agent-browser 能力）。
- **DeepWiki** (`mcp.deepwiki.com/mcp`)：零 key 仓库研究。
- **DuckDuckGo MCP**：零 key 无限（按限流），终极兜底。
- 再加 WorkBuddy 内置 **WebSearch / web-access** 作为永远可用的兜底。

## 2. 质量优先 L1 升级配置（需个性化提供 key）

在零 key 基础上，追加需 key 的 L1 主用源（用户按 §3 `§setup` 提供）：

```json
{
  "mcpServers": {
    "exa": {
      "url": "https://mcp.exa.ai/mcp",
      "headers": { "Authorization": "Bearer ${EXA_API_KEY}" }
    },
    "firecrawl": {
      "url": "https://mcp.firecrawl.dev/v2/mcp",
      "headers": { "Authorization": "Bearer ${FIRECRAWL_API_KEY}" }
    },
    "tavily": {
      "url": "https://mcp.tavily.com/mcp",
      "headers": { "Authorization": "Bearer ${TAVILY_API_KEY}" }
    }
  }
}
```

GPT Researcher 作为深度闭环引擎，需以独立服务运行（Python 3.10+ + OpenAI/Tavily key），经其 MCP Server 接入 WorkBuddy；或在 Step 1 直接以 `deep_research` 工具调用。

### L1 所需 key（个性化提供，按优先级）

| 优先级 | 工具 | 环境变量 | 申请地址 | 免费额度 |
|------|------|---------|---------|---------|
| 必选 | OpenAI | `OPENAI_API_KEY` | platform.openai.com | 试用额度 |
| 必选(二选一) | Tavily | `TAVILY_API_KEY` | tavily.com（现 Nebius 旗下） | 1000/mo |
| 必选(二选一) | Exa | `EXA_API_KEY` | exa.ai | 20000/mo |
| 推荐 | Firecrawl | `FIRECRAWL_API_KEY` | firecrawl.dev | keyless 1000/mo |
| 可选(L2) | Brave | `BRAVE_API_KEY` | search.brave.com/api | 2000/mo |
| 可选(L2) | Perplexity | `PERPLEXITY_API_KEY` | perplexity.ai/api | 免费层 |

**最小可用 L1**：`OPENAI_API_KEY` + （`TAVILY_API_KEY` 或 `EXA_API_KEY`）。加 `FIRECRAWL_API_KEY` 获得摄取/监控质量。Brave/Perplexity 仅作 L2 免费交叉验证，可后补。

## 3. §setup 个性化流程（skill 内交互）

1. **探测已接入**：检查 `mcp.json` 与环境变量，列出已可用的 L1/L2 源。
2. **推荐勾选**：未提供 L1 key 时，向质量优先用户推荐去申请（给上表 signup URL）。
3. **粘贴写入**：用户粘贴 key 后，自动写入 `mcp.json` 的对应 `headers`；拒绝则保留零 key 层并诚实标注「深度闭环降级为广覆盖」。
4. **降级兜底**：任何 key 缺失/限流 → 自动回退 L2/L3，不阻断 Step 0→8。

## 4. 数据快照与复核提醒

- 定价/额度为 **2026-07-21 快照**；搜索引擎 API 季度漂移快，生产前回源官网复核。
- **Tavily 已被 Nebius 收购（2026-02-10，$275M–$400M，NASDAQ: NBIS）**，独立性丧失；默认路由避开其作唯一交叉验证源，改 **Brave / Exa** 作独立索引交叉验证。
- **Firecrawl Keyless** 的零 key 工具清单随版本微调，回源 `mcp.firecrawl.dev` 复核。
- **竞品关键参数**（定价/版本/MCP/许可/收购归属/配额）须 ≥3 独立源（见 SKILL.md 质量规则 18）；普通事实维持 ≥2。
