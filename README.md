# Deep Market Research — 深度市场调研 Skill

> 跨平台 AI Agent 调研工作流：源分级 + ≥2 源交叉验证 + 去重/去旧/去假/去矛盾 + 吸收真实用户热评，输出质量稳定、可复现、带置信度标签的调研报告。

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
遵循 [Agent Skills 开放标准](https://agentskills.io/)（Anthropic 发起，Claude Code / OpenAI Codex / TRAE / Qodo / WorkBuddy 等 50+ 平台原生支持）。

---

## ✨ 特性（v2.2.5）

- **v2.2.4 规范性增强（回应 SkillHub TRACE 测评 Convention 4.3 短板）**：新增**常见问题 FAQ**、**完整端到端示例（Step 0→8 落地）**、**附录 A 完整更新史**；补充质量规则 15「环境受限≠能力不足」；并将 〇 节更新史压缩为摘要 + 附录指针。本地 / 仓库 / 发布包三端统一为 v2.2.4。详见 SKILL.md 第八、九节与附录 A。
- **v2.2.5 方法论 sharpening（仅措辞显式化）**：Step 2 去重补「信息密度优先」选择准则 + 「同源多样性权重（同源衰减）」防单域霸屏；Step 2 新增「语义相关度 × 时效 × 源层级 三轴混合」排序准则（与 Step 5 冲突裁决轴互补）。零新工具 / 零新硬门槛 / 不替 WebSearch / 不接 anysearch 工具。详见 SKILL.md 附录 A。
- **确定性流水线**：每次调研走固定 Step 0–8，跨次可复现、可对比。
- **源分级（NATO Admiralty 适配）**：T1 一手官方 / T2 专家 / T3 二手记录 / T4 社媒 UGC，每条结论带置信标签。
- **≥2 源交叉验证 + 去假去矛盾**：事实单元拆解，冲突显式标注，绝不强行共识。
- **三方三角验证**：大众情绪 × 专家源 × 实时联网查证，差异即认知套利点。
- **三套输出模板**：通用调研 / 行业赛道五大板块（麦肯锡风）/ 公司竞品四维分析（SWOT + 情景推演）。
- **吸收真实用户热评**：经社媒/UGC 拉取真实反馈，与官方 PR 分离，仅作信号。
- **增量知识沉淀（Karpathy 模式）**：重跑同主题自动 Lint 历史结论（矛盾/过时/孤儿），标注更新/推翻/维持。
- **分析透镜库（可选）**：波特五力 / PESTEL / BCG / 3C / TAM-SOM 等，按意图触发，不堆砌。
- **开箱即用**：纯方法论 Skill，调用 Agent 内置联网/文档工具，无需额外 Python 依赖。
- **学术数据源模块（v2.1.0）**：arXiv / PubMed / Semantic Scholar / Google Scholar / CNKI 多源并行检索 + 引文处理（BibTeX / RIS / JSON），含访问伦理与严格 `作者.题名.出处.年.DOI/URL` 引文格式；新增第 4 套「学术 / 基准 / 技术选型 / 尽调模板」。
- **intel-brief 输出风格（v2.1.0）**：对监测/快报类查询，每条信息按「事实 → 影响 → 原因」三元组织，并用 `[矛盾] / [待核实] / [已证伪]` 标记。
- **宏观监测源（v2.1.0）**：Trading Economics / FRED / 国家统计局 / 央行·证监会 / 财联社 / 华尔街见闻，每条宏观指标附白话解读与超预期/不及预期判断（T3）。
- **更多信号源（v2.1.0）**：微信公众号文章检索（wechat-article-search）、Perplexity AI 搜索（可选 `PERPLEXITY_API_KEY`）、NPR 等 RSS 源，UGC 平台覆盖扩至 14+（agent-reach）。
- **互补 Skill 吸收审计（v2.1.0）**：对 9 个与本研究域重叠的已安装研究类 skill 做了「吸收 / 淘汰」审计，择优吸收其方法论并**显式拒绝**过度约束项（完整清单见 SKILL.md「互补 Skill 方法论吸收」小节）。
- **学术与开放科研数据源大扩充（v2.2.0，去粗取精·优先免费 API）**：把学术检索升级为分层源库并**优先「🆓 免费 API 直调」**（比抓 HTML 更稳、可复现、可溯源）——论文/元数据（OpenAlex / Semantic Scholar / arXiv / PubMed / bioRxiv / EMBL-EBI）、引文溯源（Crossref / OpenCitations）、科研数据仓库（Zenodo / Figshare / 哈佛 Dataverse / NASA）、专利（智慧芽已连 / Google Patents）、代码与模型（GitHub Trending / Hugging Face / 魔塔 ModelScope）、工程化讨论（Stack Overflow / Hacker News / Reddit / 知乎 MCP / CSDN / Product Hunt / TechCrunch / Bluesky / X）。同步对学术三件套做**优胜劣汰**：留 `literature-search`、`academic-research-hub` 降为可选、`google-scholar-search` 列卸载候选。
- **技能去粗取精执行（v2.2.1 落地；v2.2.2 准确性修正；v2.2.3 一致性修正）**：GitHub MCP **已真实连接**（`mcp__github__*` 工具齐全，可作搜索/代码/Issue/PR/Release）；将重复冗余且已被吸收的 6 个 skill **全部永久删除（不可逆）**——`google-scholar-search`（实为 Semantic Scholar 封装）、`academic-research-hub`（Proprietary + OpenClawCLI）、`deep-research`（工作流已吸收）、`news-summary`（RSS 已吸收）、`perplexity` / `tavily`（与内置 WebSearch 重复的 AI 搜索）。保留 `literature-search`（最优方法论）与 `agent-reach` / `wechat-article-search` / `intel-osint-daily` / `macro-monitor`（独特能力/独立调度角色）。

---

## 🌐 支持的平台

本仓库遵循 [Agent Skills 开放标准](https://agentskills.io/)，以下平台原生支持，**直接安装即可被自动发现并触发**：

| 平台 | Skills 目录 | 触发方式 |
|------|------------|---------|
| **Claude Code / Claude** | `~/.claude/skills/` | 自动发现 + `/deep-market-research` |
| **OpenAI Codex** | `~/.codex/skills/` | 自动发现 |
| **TRAE** | `~/.trae/skills/` | 自动发现 |
| **Qodo (Qoder)** | `~/.qodo/skills/` | 自动发现 |
| **WorkBuddy / CodeBuddy** | `~/.workbuddy/skills/` | 自动发现 |
| 其他 agentskills 兼容平台 | 对应 `skills/` 目录 | 自动发现 |

> 完整的兼容平台列表见 [agentskills.io/clients](https://agentskills.io/clients)。

---

## 📦 安装

### 方式一：一键安装脚本（推荐）

克隆后运行安装脚本，会自动检测本机已安装的 Agent 平台并复制到对应 `skills/` 目录：

```bash
# Unix / macOS / Git Bash
git clone https://github.com/Rain3Dmetrology/deep-market-research.git
cd deep-market-research
./install.sh

# Windows (PowerShell)
git clone https://github.com/Rain3Dmetrology/deep-market-research.git
cd deep-market-research
powershell -ExecutionPolicy Bypass -File install.ps1
```

脚本会检测 `~/.claude`、`~/.codex`、`~/.trae`、`~/.qodo`、`~/.workbuddy` 中**已存在**的目录并安装，未安装的自动跳过。

### 方式二：手动安装

将整个 `deep-market-research/` 文件夹复制到目标平台的 skills 目录：

```bash
git clone https://github.com/Rain3Dmetrology/deep-market-research.git
# Claude Code / Codex / Cursor / Windsurf / Gemini CLI 等
cp -r deep-market-research ~/.claude/skills/
# WorkBuddy
cp -r deep-market-research ~/.workbuddy/skills/
# TRAE
cp -r deep-market-research ~/.trae/skills/
# Qodo
cp -r deep-market-research ~/.qodo/skills/
```

安装后**重启 Agent**（或执行 skill 刷新指令）即可加载。

---

## 🚀 使用

直接对 Agent 说（自动匹配 `SKILL.md` 的 `description` 触发）：

- 「调研一下工业 AI 3D 视觉测量的竞争格局」
- 「竞品分析：海康机器人 vs 深视智能 vs 天准科技」
- 「行业趋势：中国机器视觉产业链投资机会」
- 「扒一下 Keyence 中国的底」

Agent 会按 SKILL.md 的固定流程执行：范围收敛 → 多源采集 → 去重去旧 → 源分级 → 交叉验证去假 → 矛盾消解 → 吸收热评 → 100 分评分 → 结构化输出。

---

## 📂 目录结构

```
deep-market-research/
├── SKILL.md          # 核心：元数据 + 完整工作流指令（Step 0–8 + 三套模板 + 分析透镜 + 质量规则）
├── README.md         # 本文件
├── LICENSE           # MIT
├── CONTRIBUTING.md   # 贡献指南
├── install.sh        # Unix 安装脚本
├── install.ps1       # Windows 安装脚本
└── .gitignore
```

> Skill 为**自包含**：所有工作流、模板、规则都内嵌在 `SKILL.md` 中，无需额外脚本或配置文件。

---

## ⚙️ 可选数据源与增强 Skill（按需接入，优雅降级）

Skill 本身调用 Agent 内置联网工具（WebSearch / WebFetch）即可工作。若你的 Agent 已装以下 Skill 或连以下 MCP，会自动获得更强深度；**缺失时一律优雅降级，不会中断调研**：

| 维度 | 数据源 / Skill | 用途 | 状态 |
|------|--------|------|------|
| **搜索入口** | 内置 WebSearch/WebFetch（优先）+ **Tavily**（API key 直调，skill 已于 v2.2.1 永久删除） | 通用联网检索、查证 | ✅ 真实可用 |
| **AI 搜索（可选）** | **Perplexity** / **Tavily**（有 key 直调其 API，skill 已于 v2.2.1 永久删除） | 带引用的 AI 搜索，无 key 跳过 | 可选源（需 key） |
| **社媒 / 热评** | **agent-reach** / **agent-browser** / web-access | 小红书/知乎/Reddit/Bluesky/X/评论抓取（14 平台） | ✅ 真实可用 |
| **知乎（技术+反馈）** | **zhihu MCP**（search_content + hot_list） | 中文技术教程、用户反馈、产品体验交叉验证 | ✅ 真实可用 |
| **微信公众号文章** | **wechat-article-search** | 中文一手深度文章检索，补 UGC 评论之外的文章级缺口 | ✅ 真实可用 |
| **文档净化** | **markitdown** | PDF/Word/财报 → Markdown | ✅ 真实可用 |
| **A 股财务** | **通达信 tdx-connector**（v2.0.0 实测已用） | 上市公司 F10 财报/股东/资金流 | ✅ 真实可用 |
| **专利** | **智慧芽 PatSnap MCP**（已连） | 技术壁垒、专利家族、引用分析 | ✅ 真实可用 |
| **代码 / 项目** | GitHub 搜索 + Trending（`github` MCP ✅ 已连 + `gh` CLI 已认证 + web） | 开源实现、技术栈、Star/PR 趋势（MCP 直连优先，gh CLI 兜底） | ✅ 真实可用（MCP 已连） |
| **学术论文 / 元数据** | **OpenAlex** / **Semantic Scholar** / **arXiv** / **PubMed** / **bioRxiv** / **EMBL-EBI·Europe PMC**；`literature-search` skill 作方法论参考 | 论文元数据、引用网络、TLDR 摘要、预印本 | 🆓 免费 API 直调 |
| **引文溯源** | **Crossref**（DOI 元数据+参考文献）/ **OpenCitations**（开放引文网络） | DOI 权威元数据、被引/引用关系 | 🆓 免费 API 直调 |
| **科研数据仓库** | **Zenodo** / **Figshare** / **哈佛 Dataverse** / **NASA** | 数据集/软件/成果，均带 DOI 可溯源 | 🆓 免费 API 直调 |
| **AI 模型 / 数据集** | **Hugging Face Hub API** / 魔塔 ModelScope | AI 模型、代码、应用文档、数据集 | 🆓 HF 免费 API（魔塔用户持只读 token 可直调） |
| **开发者社区** | **Stack Overflow** + **Hacker News**（Stack Exchange / Algolia API）/ Reddit / CSDN | 技术选型讨论、真实踩坑反馈 | 🆓 SO/HN 免费 API（余 🌐） |
| **财经** | 腾讯自选股 / westock-mcp | 上市公司基本面、行情、研报 | 按需连接 |
| **法律 / 合规** | 威科先行 / 元典 | 诉讼、资质、行政处罚 | 按需连接 |
| **企业工商 / 风险** | 天眼查 MCP / 企查查 MCP | 股权、司法、经营异常、知识产权 | 按需连接（当前未启用） |
| **美股 / SEC** | SEC EDGAR MCP | 10-K/10-Q/财报附注 | 按需连接（当前未启用） |
| **顶刊 / 中文文献** | Nature / Science（引 DOI）/ CNKI / Google Scholar（仅用户导出） | 顶刊一手（摘要公开，全文多需订阅）；访问伦理 | 🌐 通用联网可达 |
| **宏观经济** | Trading Economics / FRED / 国家统计局 / 央行·证监会 / 财联社 / 华尔街见闻 | 宏观指标 + 超预期/不及预期判断 | 🌐 通用联网可达 |
| **专利（公开库）** | Google Patents / USPTO / EPO / WIPO | 专利原文、法律状态 | 🌐 通用联网可达 |
| **开放百科** | Wikipedia / 百度百科 | 概念科普、背景知识 | 🌐 通用联网可达 |
| **产品 / 创投** | Product Hunt / TechCrunch / 36氪 / 虎嗅 | 新品发布、融资、市场热度 | 🌐 通用联网可达 |
| **中文社区** | 博客园 / V2EX / 小红书 / B站 | 用户反馈、产品体验、教程 | 🌐 通用联网可达 |
| **国际社媒** | Bluesky / X(Twitter) / YouTube / LinkedIn | 官方动态、KOL 评论、用户情绪 | 🌐 通用联网可达 |
| **新闻 / 资讯** | aihot（免 key 中文 AI 资讯）/ BBC / Reuters / Al Jazeera | 行业快讯、国际一手新闻 | 可选源（免 key 或公开） |
| **知识库** | ima-mcp / Obsidian / 本地 wiki | 用户自有资料、增量 Lint 沉淀 | 按需连接 |

**状态说明**

- ✅ **真实可用**：当前环境已有 Skill 或已连接 MCP，开箱即用。
- 🆓 **免费 API 直调**（v2.2.0 去粗取精重点）：源提供**免费公开 REST API**，可经 WebFetch/curl **直调**（无 key 或 DEMO_KEY），比抓 HTML 更稳、可复现、可溯源——优先于网页抓取。
- **按需连接**：当前环境有对应 MCP/Skill，但未启用或需用户手动配置（如 SEC EDGAR、天眼查、企查查）。
- 🌐 **通用联网可达**：无专用 API/连接器，通过 WebSearch/WebFetch/agent-reach/agent-browser 抓取或用户导出；按源分级处理（通常 T3 媒体/官方记录或 T4 UGC 信号）。
- **可选源（免 key 或公开）**：公开可访问的新闻/资讯站点，无需专用连接器。

> **诚实声明（重要）**：本 Skill 只集成**当前环境真实存在**的 Skill / 连接器。Firecrawl、Crunchbase Pro、PitchBook 等在本环境未提供的服务**不会**被声明为已集成——若你所在平台提供，可自行在 Step 1 搜索入口追加，但 README / SKILL.md 不虚假标注。**GitHub MCP 已于 v2.2.1 确认真实连接**（`mcp__github__*` 工具齐全），可直连搜索/代码/Issue/PR/Release，亦可用 `gh` CLI 兜底。当前环境已安装/已连的互补 skill（方法论已被 dmr 吸收，缺失一律优雅降级）：`agent-reach`、`agent-browser`、`markitdown`、`tdx-connector`、`patsnap-search`（智慧芽）、`zhihu`、`ima-mcp`、`wechat-article-search`、`literature-search`（最优方法论参考）、`intel-osint-daily`、`macro-monitor`。**v2.2.1 已永久删除（不可逆）**的重复冗余 skill（方法论已并入 dmr）：`google-scholar-search`（实为 Semantic Scholar 封装）、`academic-research-hub`（Proprietary + OpenClawCLI）、`deep-research`（工作流已吸收）、`news-summary`（RSS 已吸收）、`perplexity` / `tavily`（与 WebSearch 重复的 AI 搜索）。标 🆓 的学术/数据源为免费公开 API，无需专用连接器即可直调。

---

## ❓ 常见问题与完整示例

- **FAQ（7 问）**：本 skill 与 WebSearch 的区别、核心源不可达怎么办、模板 B/C/D 如何选择、是否需要付费 key、矛盾源如何处理、报告长度、增量沉淀是否必须 ima —— 见 SKILL.md [第八节 · 常见问题（FAQ）](SKILL.md#八常见问题faq)。
- **端到端示例**：从「调研中国工业机器人赛道 + 减速器国产化 + 埃斯顿/汇川对位」用户提问，到 Step 0→8 逐环产出物（采集 / 去重 / 验证 / 矛盾消解 / 分级 / 模板 / 评分卡）—— 见 SKILL.md [第九节 · 完整示例](SKILL.md#九完整示例端到端从用户提问到报告)。
- **完整更新史**：v2.0.0 → v2.2.5 每项变更细节 —— 见 SKILL.md [附录 A](SKILL.md#附录-a完整更新史v200--v225)。

---

## 📜 许可证

[MIT License](LICENSE)
