## Deep Market Research v2.3.0

平台无关化 + 深度研究闭环（去粗取精、泛化优先）。任意加载本技能的 agent 均可"开箱即用、开箱即研"。

### 核心变更（倒序 · 最新特性）
- **平台无关化**：默认零依赖、零安装（仅 LLM 内置 web_search / web_fetch + 免费 REST API）；不假设任何平台 MCP 配置 / agent-team 协议 / 专有后端。
- **三-B 深度研究闭环（平台无关，纯提示词编排）**：吸收多平台深度研究 agent 团队精华（多轮迭代 / 章节级审稿 / 研究参数卡跨阶段共享 / 进度通报），去其平台专有约束。
- **竞品关键参数交叉验证 >=2 -> >=3**（质量规则 18；普通事实维持 >=2 控成本）。
- **质量规则增补**：19（可选工具非质量前提）/ 20（不绑定特定平台机制）。
- **新增 `references/cross-platform-tools.md`**：WorkBuddy / Claude / Codex / Trae / qoder / Cursor 六平台可选增强工具接入指南。

### 可视化（内联 SVG · 已修复渲染）
原 Mermaid 图改为内联 SVG，GitHub 直接渲染、无外部依赖：
- **调研流水线（Pipeline）** — 主管线 Step 0–8 与三-B 深度研究闭环正交，质量由方法论保证而非某个搜索 API；可选增强层在 Step 1 多源采集处接入，缺失即优雅降级。
- **技术栈（Stack）** — 默认层零依赖零安装（质量基座）；可选增强层按推荐层级标注（🥇 首选 / 🥈 备选 / 🛟 兜底 / 🎯 个性化），缺失即优雅降级。

![调研流水线](https://raw.githubusercontent.com/Rain3Dmetrology/deep-market-research/main/assets/pipeline.svg)
![技术栈](https://raw.githubusercontent.com/Rain3Dmetrology/deep-market-research/main/assets/stack.svg)

### 可选数据源与增强 Skill（去粗取精 · 优胜劣汰）
- 按「分类 + 推荐层级」对可选源做统一排名并**折叠进原表**（不再单列小节）。推荐层级：🥇 首选（默认增强）· 🥈 备选（同级替代）· 🛟 兜底（keyless 默认层，缺 key 也能跑）· 🎯 个性化（需 key / 账号 / 特定平台）· ⚠️ 不推荐通用。
- **补 keyless 缺口**：SearXNG（免 key 多引擎元搜索，🛟 兜底）、Novada（免费 1000/月综合网页数据，🥈 备选）。
- **去重去旧去低质**：移除与现有源重复 / 付费 / 超范围的项（Kagi · Search1API · 各 RAG 平台包装等）；解释性语言与安装状态描述大幅压减。
- 联网交叉验证快照为 2026-07；搜索类 API 季度漂移，生产前请回源官网复核。

### 兼容性
- SKILL.md `compatibility` 已声明：WorkBuddy / CodeBuddy / Claude / Codex / Trae / qoder / Cursor 及任何加载 skills / system prompts 的 agent。
- 可选工具（Firecrawl / DeepWiki / Tavily / Novada / SearXNG / Perplexity / GPT Researcher / ModelScope）缺失即优雅降级，输出质量不降。

> 完整更新史见 SKILL.md 附录 A（v2.0.0 → v2.3.0）。
