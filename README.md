# Deep Market Research — 深度市场调研 Skill

> 跨平台 AI Agent 调研工作流：源分级 + ≥2 源交叉验证 + 去重/去旧/去假/去矛盾 + 吸收真实用户热评，输出质量稳定、可复现、带置信度标签的调研报告。

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
遵循 [Agent Skills 开放标准](https://agentskills.io/)（Anthropic 发起，Claude Code / OpenAI Codex / TRAE / Qodo / WorkBuddy 等 50+ 平台原生支持）。

---

## ✨ 特性（v2.0.0）

- **确定性流水线**：每次调研走固定 Step 0–8，跨次可复现、可对比。
- **源分级（NATO Admiralty 适配）**：T1 一手官方 / T2 专家 / T3 二手记录 / T4 社媒 UGC，每条结论带置信标签。
- **≥2 源交叉验证 + 去假去矛盾**：事实单元拆解，冲突显式标注，绝不强行共识。
- **三方三角验证**：大众情绪 × 专家源 × 实时联网查证，差异即认知套利点。
- **三套输出模板**：通用调研 / 行业赛道五大板块（麦肯锡风）/ 公司竞品四维分析（SWOT + 情景推演）。
- **吸收真实用户热评**：经社媒/UGC 拉取真实反馈，与官方 PR 分离，仅作信号。
- **增量知识沉淀（Karpathy 模式）**：重跑同主题自动 Lint 历史结论（矛盾/过时/孤儿），标注更新/推翻/维持。
- **分析透镜库（可选）**：波特五力 / PESTEL / BCG / 3C / TAM-SOM 等，按意图触发，不堆砌。
- **开箱即用**：纯方法论 Skill，调用 Agent 内置联网/文档工具，无需额外 Python 依赖。

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
| 搜索入口 | 内置 WebSearch/WebFetch + **Tavily**（API key，最佳搜索入口） | 联网检索、查证 | ✅ 真实可用 |
| 社媒 / 热评 | **agent-reach** / **agent-browser** / web-access | 小红书/知乎/Reddit/评论抓取 | ✅ 真实可用 |
| 文档净化 | **markitdown** | PDF/Word → Markdown | ✅ 真实可用 |
| A 股财务 | **通达信 tdx-connector**（v2.0.0 竞品实测已用） | 上市公司 F10 财报/股东/资金流 | ✅ 真实可用 |
| 专利 | 智慧芽 / PatSnap | 技术壁垒分析 | 按需连接 |
| 财经 | 腾讯自选股 / westock | 上市公司基本面 | 按需连接 |
| 法律 | 威科先行 / 元典 | 诉讼/资质核查 | 按需连接 |
| 代码 | **GitHub**（连接器已连） | 开源实现/技术栈 | ✅ 真实可用 |
| 知识库 | ima / Obsidian | 用户自有资料、增量 Lint 沉淀 | 按需连接 |

> **诚实声明（重要）**：本 Skill 只集成**当前环境真实存在**的 Skill / 连接器。Firecrawl 等在本环境未提供的服务**不会**被声明为已集成——若你所在平台提供，可自行在 Step 1 搜索入口追加，但 README / SKILL.md 不虚假标注。Tavily 与 GitHub 为当前环境真实可用项，已在上表标 ✅。

---

## 📜 许可证

[MIT License](LICENSE)
