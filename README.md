# SOTA Research Workflow Skill

> AI/CV 学术论文与代码复现全链路自动化工具包

## 项目简介

本 Skill 技能包实现了一个 5 步自动化科研工作流，覆盖从论文发现到代码复现的完整链路：

1. **SOTA 发现** — CodeSOTA API + SerpApi Google Scholar
2. **论文深度分析** — Semantic Scholar API（TLDR、被引、参考文献）
3. **同族工作扩展** — Google Scholar Related + Semantic Scholar Recommendations
4. **多平台实现检索 + SOTA 评分** — GitHub + Hugging Face + ModelScope
5. **最新预印本追踪** — arXiv API

## 安装

### 方式一：Claude Code / Codex CLI

```bash
# 复制到个人 skills 目录（全局可用）
cp -r sota-research/ ~/.claude/skills/

# 或复制到项目 skills 目录（仅当前项目）
cp -r sota-research/ .claude/skills/
```

### 方式二：其他 Agent（Cursor、Windsurf、Gemini CLI）

将 `sota-research/` 目录放到对应 Agent 的 skills 目录下。本 Skill 遵循
[Agent Skills 开放标准](https://agentskills.io/)，跨平台兼容。

### 方式三：独立使用

```bash
# 直接运行脚本
cd sota-research/
python3 scripts/research_workflow.py "vision transformer"
```

## 配置 API Keys

### 方式一：配置文件

```bash
cp config/api_config.example.json config/api_config.json
# 编辑 config/api_config.json 填入你的 API keys
```

### 方式二：环境变量

```bash
export SERPAPI_KEY="your_key"
export GITHUB_TOKEN="your_token"
export MODELSCOPE_TOKEN="your_token"
export SEMANTIC_SCHOLAR_API_KEY="your_key"  # 可选
export CONNECTED_PAPERS_API_KEY="your_token"  # 可选
```

### 各 API Key 获取方式

| API | 注册地址 | 免费额度 | 说明 |
|-----|---------|---------|------|
| **SerpApi** | [serpapi.com](https://serpapi.com) | 100 次/月 | Google Scholar 搜索 |
| **GitHub Token** | [github.com/settings/tokens](https://github.com/settings/tokens) | 5000 次/小时 | 选 Personal Access Token, 勾选 `repo` |
| **Semantic Scholar** | [semanticscholar.org/product/api](https://www.semanticscholar.org/product/api) | 100 次/分钟 | 建议申请，可避免 429 限流 |
| **ModelScope** | [modelscope.cn](https://modelscope.cn) | 免费 | 我的账号 → Access Token → 创建只读 Token |
| **Connected Papers** | 邮件 hello@connectedpapers.com | 500 次 | 申请 early-access token |
| **Hugging Face** | 无需 | 无限制 | 公开 API，无需认证 |
| **arXiv** | 无需 | 无限制 | 公开 API，3 秒间隔 |
| **CodeSOTA** | 无需 | 无限制 | 公开 API |

## 使用方式

### 命令行

```bash
# 基本用法
python3 scripts/research_workflow.py "vision transformer"

# 完整参数
python3 scripts/research_workflow.py "image segmentation" \
  --max-papers 5 \
  --arxiv-cat cs.CV \
  --months 6 \
  --output my_report.md
```

### 在 Agent 中调用

直接对 Agent 说：
- "帮我研究 vision transformer 的最新进展"
- "搜索 image segmentation 的 SOTA 方法和代码实现"
- "追踪 arXiv 上最近三个月的 object detection 预印本"

Agent 会自动加载此 Skill 并执行工作流。

### 参数说明

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `query` | (必填) | 研究主题或论文关键词 |
| `--max-papers` | 3 | 每步最大论文数量 |
| `--arxiv-cat` | None | arXiv 分类过滤（如 cs.CV, cs.CL, cs.AI） |
| `--months` | 3 | 预印本回溯月数 |
| `--output` | 自动生成 | 输出 Markdown 文件路径 |

## SOTA 评分系统

Step 4 对所有实现方案（GitHub 仓库、Hugging Face 模型、ModelScope 模型）进行
统一的 100 分制评分：

| 维度 | 分值 | 评估指标 |
|------|:---:|---------|
| 社区活跃度 | 30 | stars/likes、forks、downloads |
| 代码质量 | 25 | 开源协议、编程语言、文档完整度 |
| 维护状态 | 20 | 最近更新时间、issue 活跃度 |
| 相关性 | 15 | 名称/描述/标签与查询关键词匹配度 |
| 工程就绪度 | 10 | pipeline/task 标签、参数信息 |

**评级标准：** A+ (>=80) | A (>=65) | B+ (>=50) | B (>=35) | C (>=20) | D (<20)

## 输出报告结构

生成的 Markdown 报告包含：

1. **Step 1: SOTA 发现** — 目标论文列表
2. **Step 2: 论文深度分析** — TLDR、被引、参考文献
3. **Step 3: 同族工作扩展** — 相关论文列表
4. **Step 4: 代码与模型实现检索**
   - SOTA 评分比较总表（所有方案按总分排序）
   - A 级推荐方案详解
   - GitHub 仓库列表（带评级）
   - Hugging Face 模型列表（带评级）
   - ModelScope 模型列表（带评级）
5. **Step 5: 最新预印本追踪** — arXiv 最新论文

## 迁移说明

### Papers With Code → CodeSOTA

Papers With Code 已于 2025 年 7 月被 Meta 关闭。本工作流使用 CodeSOTA API
作为替代方案：

- **CodeSOTA API**: `https://www.codesota.com/api/sota`
- **替代历史数据**: [GitHub Archive](https://github.com/paperswithcode/paperswithcode-data)
- **热门论文补充**: [Hugging Face Papers](https://huggingface.co/papers)

详见 `docs/migration_notes.md`。

## 依赖

- Python 3.8+
- 标准库（无需安装额外依赖）：
  - `urllib`, `json`, `xml.etree.ElementTree`, `argparse`, `pathlib`

## 版本历史

| 版本 | 日期 | 更新内容 |
|------|------|---------|
| 1.1.0 | 2026-07-09 | 新增 SOTA 评分系统、ModelScope 支持、Hugging Face 支持 |
| 1.0.0 | 2026-07-09 | 初始版本，5 步工作流 |

## 许可证

MIT License
