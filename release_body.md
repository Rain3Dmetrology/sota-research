# v2.3.1 — MCP 修复 + 跨机器同步 + 可选源增补

> **2026-07-23** · 维护性小版本（基于 v2.3.0 增量修复 + 可选源吸收）
> 主管线（Step 0→8 + 三-B 深度研究闭环）零变动，仅 bug 修复 / 工具增强 / 可选源文档。

---

## 🐛 关键修复

- **MCP 鉴权前缀 BUG（全局）**：原 mcp.json 的 env 类 server 带 `APIKEY:` / `access token：` 前缀 → 上游 API **全 401 拒**。修正为裸 token 形式后 Exa / Firecrawl / HF / ModelScope / Tavily 全部 HTTP 200。
- **Tavily MCP 桥接策略**：从 mcp-remote（强制浏览器 OAuth）改用官方 `tavily-mcp` stdio 包 → 无头免 OAuth，自动化可用。
- **Zhihu MCP 端点路径**：URL 从 `/mcp/.../sse`（404/SPA）纠正为 `/api/mcp/.../v1/sse`，并强制 `--transport sse-only`（mcp-remote 默认 `http-first` 对纯 SSE 端点返 405/SPA）。3 个端点（搜索/可信全网/热榜）实测 initialize + tools/list + tools/call 全部返回**真实知乎数据**。
- **裸 key 文件解析兜底**：原 `extract_key` 仅识别带前缀行 → 修复为「无前缀时回退到首个非空行」，兼容 novada 类单行长 key。

---

## ✨ 新增能力

### 跨机器 MCP 同步（`scripts/setup_mcp.py`）
- **零硬编码 key**、读 OneDrive 桌面 key 文件、自动剥前缀（Rule 1）、生成 `~/.workbuddy/mcp.json`
- 同时输出 `~/.workbuddy/dmr_keys.env`（FRED/Novada 等非 MCP key），完成 dmr 全配置跨机器同步
- 隐私自查通过：无任何硬编码 key、无绝对路径泄露、GitHub 仓库 grep 无 key 泄露

### 新增可选源（`references/cross-platform-tools.md`）
| 源 | 类型 | 价值 | 决策 |
|---|---|---|---|
| **FRED**（美联储经济数据） | 结构化时间序列（GDP/CPI/利率/就业/M2 80万+ 系列） | 免费官方权威，补 dmr **结构化经济数据空白** | ✅ **吸收**（强烈建议） |
| **Novada Web Unblocker** | 住宅代理 / 反爬解锁 | 与 Firecrawl 反爬部分重叠 | ✅ 吸收为**兜底解锁层** |
| **Connected Papers** | 论文关联图谱（S2 ShaID → 研究邻里） | early-access，余 ~50 次构建 | ✅ 吸收为**深度尽调可选源** |
| **AnySearch** | 通用实时搜索聚合 | 与 exa/tavily/firecrawl 高度重叠 | ❌ 不吸收（仅存 APIKEY） |
| **agent-reach** | 14 平台社媒聚合（Twitter/Reddit/B 站/小红书/抖音/微博/公众号 等） | 覆盖 8 MCP 未触及的社媒/UGC 另类数据 | ✅ 吸收为**社媒增强层**（已激活） |
| **agent-browser** | 浏览器自动化 | 与 Firecrawl 重叠且更重 | ⚠️ 仅作交互兜底，不进核心 |

### 新增脚本
- **`scripts/fred_query.py`**：轻量 FRED 查询工具（按系列 ID 查观测 / 按关键词搜索系列），自动读桌面 key（Rule 1 剥前缀）。

---

## 📊 8 个 MCP 实测状态（本机 WorkBuddy 验证 · 2026-07-23）

| MCP | 工具数 | 状态 |
|---|---|---|
| exa | 2/2 | 🟢 |
| firecrawl | 26/26 | 🟢 |
| tavily | 5/5 | 🟢 |
| huggingface | 10/10 + 2 Prompt + 12 资源 | 🟢 |
| modelscope | 9/9 | 🟢 |
| zhihu-search / global / hotlist | 各 1/1 | 🟢 |

---

## ⚠️ 已知 / 待用户手动

- **SkillHub 重发**：旧泄漏 listing `deep-market-webresearch`（v2.2.10）仍在线，需在 SkillHub Web UI 手动删除并用本版重发。
- **agent-reach 频道配置**：已激活（`disable: false`），社媒频道需跑 `agent-reach doctor` 配置（小红书/抖音/公众号等需登录 cookie）。

---

## 🔐 隐私红线

- 本仓库**零真实 key**、**零个人 MCP 连接状态**、**零绝对路径泄露**
- 仅含：连接器类型、官方端点 URL（keyless 远程 MCP）、Rule-1 剥前缀脚本、公开文档
- 所有 key 仅存于本机 `OneDrive/Desktop/` + `~/.workbuddy/mcp.json` / `dmr_keys.env`
- 跨机器同步 = 跑 `scripts/setup_mcp.py` + WorkBuddy MCP 管理页对每个 server 点 Trust
