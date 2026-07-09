# SOTA Research Workflow Skill

> AI/CV 学术论文与代码复现全链路自动化工具包 | [Agent Skills](https://agentskills.io/) 开放标准

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Version: 1.3.0](https://img.shields.io/badge/version-1.3.0-green.svg)](#)

## 项目简介

本 Skill 技能包实现了一个 **5+1 步自动化科研工作流**，覆盖从论文发现到代码复现的完整链路。支持中英文关键词输入、模糊搜索、关联搜索，通过引导式交互将搜索范围逐步收敛到精确领域。

### 工作流

```
Step 0: 引导式领域收敛 (Discover Mode)
  └─ 中文映射(84+) + 关键词关联(16组) + 模糊匹配 → 精确任务ID

Step 1: SOTA 发现 (三层降级)
  └─ CodeSOTA API → Google Scholar → OpenAlex (兜底)

Step 2: 论文深度分析
  └─ Semantic Scholar API (TLDR + 被引 + 参考文献 + OA PDF)

Step 3: 同族工作扩展
  └─ Google Scholar Related + Semantic Scholar Recommendations

Step 4: 多平台代码检索 + SOTA 评分
  └─ GitHub + Hugging Face + ModelScope → 100分制评分排名

Step 5: 最新预印本追踪
  └─ arXiv API (按日期降序)
```

### 核心特性

- **中英文兼容**: 84+ 条中文关键词映射，输入"图像分割"自动转换为 `image-segmentation`
- **模糊搜索**: 单词相似度 >=0.3 的模糊匹配，容忍拼写差异
- **关联搜索**: 16 个语义群组自动扩展（如 "vision" → 7 个 CV 任务）
- **三层降级**: CodeSOTA → Google Scholar → OpenAlex，确保检索不中断
- **SOTA 评分**: 5 维度 100 分制（社区活跃度/代码质量/维护状态/相关性/工程就绪度）
- **跨平台**: 遵循 Agent Skills 开放标准，兼容 Claude Code / Codex / Cursor / Windsurf / Gemini CLI

## 快速开始

### 1. 安装

```bash
git clone https://github.com/Rain3Dmetrology/sota-research-skill.git
cd sota-research-skill
```

### 2. 配置 API Keys

```bash
cp config/api_config.example.json config/api_config.json
# 编辑 api_config.json，填入你的 API keys
```

或通过环境变量：

```bash
export SERPAPI_KEY="your_serpapi_key"
export GITHUB_TOKEN="your_github_token"
export MODELSCOPE_TOKEN="your_modelscope_token"
# 以下可选
export SEMANTIC_SCHOLAR_API_KEY="your_ss_key"
export CONNECTED_PAPERS_API_KEY="your_cp_key"
```

### 3. 运行

```bash
# Discover 模式 — 引导收敛
python3 scripts/research_workflow.py "图像分割" --discover

# 完整工作流
python3 scripts/research_workflow.py "image segmentation" --max-papers 5 --arxiv-cat cs.CV

# 中文查询（自动收敛）
python3 scripts/research_workflow.py "目标检测" --max-papers 3 --arxiv-cat cs.CV
```

## API 清单

| API | 用途 | 认证 | 免费额度 |
|-----|------|------|---------|
| CodeSOTA | SOTA 模型查询 | 无需 | 无限 |
| SerpApi | Google Scholar 搜索 | API Key | 100次/月 |
| OpenAlex | 论文兜底检索 | 无需 | 无限 |
| Semantic Scholar | 论文分析+推荐 | 可选 | 100req/5min |
| GitHub | 仓库搜索 | 可选 | 60/hr |
| Hugging Face | 模型搜索 | 无需 | 无限 |
| ModelScope | 魔搭模型搜索 | Token | 免费注册 |
| arXiv | 预印本搜索 | 无需 | 无限 |

## SOTA 评分体系

| 维度 | 满分 | 指标 |
|------|:---:|------|
| 社区活跃度 | 30 | stars/likes, downloads, forks |
| 代码质量 | 25 | license, language, description |
| 维护状态 | 20 | last_update, open_issues |
| 相关性 | 15 | 名称/描述/标签匹配 |
| 工程就绪度 | 10 | pipeline/task, params |

评级: A+(>=80) | A(>=65) | B+(>=50) | B(>=35) | C(>=20) | D(<20)

## 作为 Agent Skill 安装

### Claude Code / Codex / Cursor / Windsurf

```bash
# 复制到 skills 目录
cp -r sota-research-skill ~/.claude/skills/sota-research
# 或对应平台的 skills 目录
```

安装后，在对话中输入 `/sota-research` 或提及 SOTA 相关关键词即可自动触发。

## 文件结构

```
sota-research-skill/
├── SKILL.md                    # Skill 入口 (含 YAML 元数据)
├── README.md                   # 本文件
├── LICENSE                     # MIT 许可证
├── CONTRIBUTING.md             # 贡献指南
├── .gitignore
├── scripts/
│   └── research_workflow.py    # 自动化脚本 v1.3
├── config/
│   ├── api_config.example.json # API 配置模板
│   └── codesota_tasks.json     # CodeSOTA 任务索引 (90任务)
├── templates/
│   └── report_template.md      # 报告模板
└── docs/
    ├── api_reference.md        # API 端点文档
    └── migration_notes.md      # PWC → CodeSOTA 迁移说明
```

## 已知限制

- Papers With Code 已关闭 (2025.07)，CodeSOTA 为替代方案
- Hugging Face API 在部分网络环境存在 SSL 限制
- Semantic Scholar 无 API Key 时限流 (100 req/5min)
- SerpApi 免费版限制 100 次/月

## 许可证

[MIT](LICENSE)

## 致谢

- [CodeSOTA](https://www.codesota.com/) — SOTA 模型注册表
- [Semantic Scholar](https://www.semanticscholar.org/) — 论文分析 API
- [OpenAlex](https://openalex.org/) — 开放学术图谱
- [arXiv](https://arxiv.org/) — 预印本平台
- [SerpApi](https://serpapi.com/) — Google Scholar 搜索
- [Hugging Face](https://huggingface.co/) — 模型仓库
- [ModelScope](https://modelscope.cn/) — 魔搭社区
