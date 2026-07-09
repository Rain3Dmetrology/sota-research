---
name: sota-research
description: >
  AI/CV SOTA research workflow: discover papers, analyze methods, expand related work,
  find code implementations across GitHub/HuggingFace/ModelScope, score & rank them,
  and track latest arXiv preprints. Use when user asks to research a topic, find SOTA
  models, compare implementations, do literature review, or track preprints.
when_to_use: >
  Triggers: "research", "SOTA", "find papers", "compare implementations",
  "literature review", "arxiv", "huggingface search", "modelscope search",
  "vision transformer", "image segmentation", "code reproduction", "论文检索",
  "SOTA排行", "代码复现", "预印本追踪", "学术工作流", "发现模式", "领域收敛",
  "模糊搜索", "关联搜索", "discover", "搜索论文代码"
version: "1.3.0"
author: "Research Workflow Team"
license: "MIT"
---

# SOTA Research Workflow Skill — 完整工作流

> 版本: 1.3.0 | 更新日期: 2026-07-09 | 许可证: MIT

---

## 一、工作流全景图

```
输入: 研究任务/关键词 (如 "image segmentation" / "图像分割")
         │
         ▼
┌──────────────────────────────────────────────────────────┐
│ Step 0: 引导式领域收敛 (Discover Mode)  v1.2 NEW          │
│  ├─ 0a. 中文关键词 → 英文任务 ID 映射 (84+ 条)             │
│  ├─ 0b. 关键词关联搜索 (16 个语义群组)                      │
│  ├─ 0c. 模糊匹配 (单词相似度 >=0.3)                        │
│  └─ 0d. 唯一精确命中时自动收敛，多候选时列出供选择          │
│  输出: 精确 CodeSOTA task_id (如 "image-segmentation")      │
│  特性: 中英文兼容 · 模糊搜索 · 关联搜索 · 自动/手动收敛     │
└──────────────────────────────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────────────────────────┐
│ Step 1: SOTA 发现 (三层降级)                                │
│  ├─ 1a. CodeSOTA API [首选]                                │
│  │     └─ 查该任务的当前 SOTA 模型 + 论文 (pick + runners_up) │
│  ├─ 1b. SerpApi (Google Scholar) [主力补充]                │
│  │     └─ 按关键词搜索学术论文，获取 title/cited_by/snippet  │
│  └─ 1c. OpenAlex API [兜底]  v1.3 NEW                     │
│        └─ 当 GS 无结果或结果不足时自动触发                   │
│        └─ 2.7亿+ 作品，按相关性排序，提取 DOI/OA/被引数       │
│  降级链: CodeSOTA → Google Scholar → OpenAlex               │
│  去重:   三源结果自动按标题去重合并                         │
│  输出: 目标论文列表 (title, source, cited_by, url, doi)     │
│  API:   CodeSOTA (免费) + SerpApi (100次/月)                │
│         + OpenAlex (免费/无限, polite pool)                  │
└──────────────────────────────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────────────────────────┐
│ Step 2: 论文深度分析                                      │
│  └─ Semantic Scholar API                                  │
│     ├─ 搜索论文 → 获取 paperId                             │
│     ├─ 论文元数据 (title/authors/year/venue/DOI)           │
│     ├─ TLDR 自动摘要                                      │
│     ├─ citationCount + influentialCitationCount             │
│     ├─ abstract (前500字)                                 │
│     ├─ openAccessPdf (免费PDF链接)                         │
│     └─ references (该论文引用了哪些文献, Top 10)           │
│  输出: 论文分析卡片 (元数据+TLDR+引用+参考文献)             │
│  API:   Semantic Scholar (无Key: 100req/5min, 有Key: 100/min)│
│  降级: 429 限流时跳过该论文，继续下一篇                       │
└──────────────────────────────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────────────────────────┐
│ Step 3: 同族工作扩展                                      │
│  ├─ 3a. SerpApi (Google Scholar Related) [主力]           │
│  │     └─ q=related:PaperTitle → 相关论文列表              │
│  └─ 3b. Semantic Scholar Recommendations API [补充]        │
│        └─ paperId/recommendations → 推荐论文列表             │
│  输出: 相关论文 Top-N (按被引次数排序, 去重)                │
│  API:   SerpApi (共享Step1 Key) + Semantic Scholar (共享)  │
│  备注: Connected Papers API 已申请但尚未拿到 token          │
│        拿到后将加入: paper → 图谱(nodes+edges) 扩展          │
└──────────────────────────────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────────────────────────┐
│ Step 4: 多平台代码与模型实现检索 + SOTA 评分               │
│  ├─ 4a. GitHub REST API                                  │
│  │     ├─ 按论文标题/关键词搜索 repositories               │
│  │     ├─ 筛选条件: language:python + stars排序             │
│  │     └─ 提取: stars, forks, language, license,          │
│  │         last_update, open_issues, topics                │
│  ├─ 4b. Hugging Face Hub API                              │
│  │     ├─ /api/models?search=关键词&sort=downloads         │
│  │     └─ /api/arxiv/{arxiv_id}/repos (论文关联模型)       │
│  │     提取: downloads, likes, pipeline_tag, library,      │
│  │           license, tags                                 │
│  ├─ 4c. ModelScope (魔搭) OpenAPI                         │
│  │     └─ /models?search=关键词&limit=10                  │
│  │     提取: downloads, likes, tasks, tags, license,        │
│  │           params, last_modified                         │
│  └─ 4d. SOTA 评分系统 (100分制)                            │
│        ├─ 社区活跃度 (30分): stars/likes, forks, downloads │
│        ├─ 代码质量   (25分): license, language, description │
│        ├─ 维护状态   (20分): last_update, open_issues       │
│        ├─ 相关性     (15分): 关键词匹配(name/desc/tags)      │
│        └─ 工程就绪度 (10分): pipeline/task, params          │
│        评级: A+(>=80) | A(>=65) | B+(>=50) | B(>=35)       │
│              | C(>=20) | D(<20)                             │
│  输出: SOTA评分比较总表 + A级推荐详解                       │
│        + GitHub/HF/ModelScope 分平台列表                    │
│  API:   GitHub (无Token:60/hr, Token:5000/hr)            │
│         Hugging Face (免费/无限)                           │
│         ModelScope (Bearer Token, 免费注册)                │
└──────────────────────────────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────────────────────────┐
│ Step 5: 最新预印本追踪                                     │
│  └─ arXiv API                                             │
│     ├─ 搜索: all:关键词 + cat:cs.CV (可指定分类)            │
│     ├─ 排序: submittedDate descending                      │
│     ├─ 时间范围: 最近 3-6 个月 (可配置 --months 参数)       │
│     └─ 提取: title, abstract, authors, categories,        │
│            published, arxiv_id, pdf_url                   │
│  输出: 最新预印本列表 (按日期降序排列)                      │
│  API:   arXiv (免费/无限, 建议3秒请求间隔)                  │
└──────────────────────────────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────────────────────────┐
│ 汇总输出: Markdown 研究报告 (自动生成)                      │
│  ├─ 1. SOTA 发现结果表格                                   │
│  ├─ 2. 目标论文深度分析卡片                                │
│  │     (TLDR、被引、参考文献、DOI、arXiv链接)               │
│  ├─ 3. 同族工作扩展表格                                    │
│  ├─ 4. SOTA 评分比较总表 (所有方案, 按总分排序)             │
│  ├─ 5. A 级推荐方案详解 (推荐理由、描述、标签)              │
│  ├─ 6. GitHub 仓库列表 (带评级标签)                        │
│  ├─ 7. Hugging Face 模型列表 (带评级标签)                  │
│  ├─ 8. ModelScope 模型列表 (带评级标签)                    │
│  └─ 9. 最新 arXiv 预印本表格                               │
└──────────────────────────────────────────────────────────┘
```

---

## 二、API 清单与认证信息

| # | API | 用途 | 认证方式 | 免费额度 | 获取地址 |
|---|-----|------|---------|---------|---------|
| 1 | CodeSOTA API | Step 1: SOTA模型查询 | 无需认证 | 无限 | https://www.codesota.com/api/sota |
| 2 | SerpApi | Step 1/3: Google Scholar搜索 | API Key (query参数) | 100次/月 | https://serpapi.com |
| 3 | OpenAlex API | Step 1: 论文兜底检索 (v1.3) | 无需认证 (polite pool) | 无限 (建议<10req/s) | https://openalex.org |
| 4 | Semantic Scholar | Step 2/3: 论文分析+推荐 | 可选 (header: x-api-key) | 无Key: 100req/5min | https://semanticscholar.org/product/api |
| 5 | GitHub REST API | Step 4: 仓库搜索 | 可选 (header: Authorization) | 无Token: 60/hr | https://github.com/settings/tokens |
| 6 | Hugging Face Hub | Step 4: 模型搜索+论文关联 | 无需认证 | 无限 | https://huggingface.co/api |
| 7 | ModelScope OpenAPI | Step 4: 魔搭模型搜索 | Bearer Token | 免费注册 | https://modelscope.cn → Access Token |
| 8 | arXiv API | Step 5: 预印本搜索 | 无需认证 | 无限 (3s间隔) | http://export.arxiv.org/api |
| 9 | Connected Papers | Step 3: 论文关系图谱 (待启用) | Early-access token | 500次 | 邮件 hello@connectedpapers.com |

### 认证配置方式

**方式一：配置文件** `config/api_config.json`
```json
{
  "serpapi_key": "你的SerpApi Key",
  "github_token": "ghp_你的GitHub Token",
  "semantic_scholar_key": "你的SS Key (可选,留空则走限速模式)",
  "modelscope_token": "ms-你的ModelScope Token",
  "connected_papers_token": "你的CP Token (可选,申请中)"
}
```

**方式二：环境变量**
```bash
export SERPAPI_KEY="..."
export GITHUB_TOKEN="..."
export SEMANTIC_SCHOLAR_API_KEY="..."  # 可选
export MODELSCOPE_TOKEN="..."
export CONNECTED_PAPERS_API_KEY="..."  # 可选
```

---

## 三、Agent 执行指令

### 快速启动

当用户提供研究主题时，Agent 应执行以下流程：

**1. 检查配置**
```
读取 config/api_config.json (或环境变量)
→ 若不存在，从 config/api_config.example.json 创建模板
→ 提示用户填写 API keys (至少需要 serpapi_key)
```

**2. 选择执行模式**

*模式 A — Discover 模式（推荐首次使用）*
```bash
# 查看候选任务，手动收敛到精确领域
python3 scripts/research_workflow.py "图像分割" --discover
python3 scripts/research_workflow.py "vision transformer" --discover
```

*模式 B — 直接执行完整工作流（已明确任务时）*
```bash
python3 scripts/research_workflow.py "<用户输入的关键词>" \
  --max-papers 3 \
  --arxiv-cat <可选分类> \
  --output research_report_<timestamp>.md

# 跳过自动收敛，直接指定 CodeSOTA 任务
python3 scripts/research_workflow.py "segmentation" --codesota-task semantic-segmentation
```

常用 arXiv 分类：
| 分类 | 领域 |
|------|------|
| cs.CV | 计算机视觉 |
| cs.AI | 人工智能 |
| cs.CL | 计算语言学/自然语言处理 |
| cs.LG | 机器学习 |
| cs.RO | 机器人学 |
| cs.SD | 声音处理 |
| eess.IV | 图像/视频处理 |

**3. 呈现结果摘要**
- Top 3 目标论文（标题 + 被引次数）
- 最佳实现方案（A级推荐 + 总分）
- 最近 3 篇预印本

**4. 深入分析（按需）**
用户可要求：
- `--max-papers 5` 增加检索深度
- 切换 `--arxiv-cat` 调整分类
- 指定 `--output` 自定义输出路径

### 手动降级方案

若 Python 脚本不可用，Agent 可按以下 curl 命令逐步执行（详见 `docs/api_reference.md`）：

```bash
# Step 1: SOTA 发现
curl "https://www.codesota.com/api/sota/{task}?tier=sota"
curl "https://serpapi.com/search?engine=google_scholar&q={query}&api_key={KEY}"
curl "https://api.openalex.org/works?search={query}&per_page=5&sort=relevance_score:desc&select=id,title,cited_by_count,publication_year,doi,open_access"

# Step 2: 论文分析
curl "https://api.semanticscholar.org/graph/v1/paper/search?query={title}&limit=1&fields=title,year,citationCount,tldr,abstract,references"

# Step 3: 相关工作
curl "https://serpapi.com/search?engine=google_scholar&q=related:{title}&api_key={KEY}"

# Step 4: 代码检索
curl -H "Authorization: token {GH_TOKEN}" "https://api.github.com/search/repositories?q={query}+language:python&sort=stars"
curl "https://huggingface.co/api/models?search={query}&sort=downloads&direction=-1&limit=5"
curl -H "Authorization: Bearer {MS_TOKEN}" "https://modelscope.cn/openapi/v1/models?search={query}&limit=10"

# Step 5: 预印本
curl "http://export.arxiv.org/api/query?search_query=all:{query}&max_results=10&sortBy=submittedDate&sortOrder=descending"
```

---

## 四、SOTA 评分体系详解 (Step 4b)

所有实现方案（GitHub 仓库 / Hugging Face 模型 / ModelScope 模型）统一评分：

### 评分维度

| 维度 | 满分 | 指标 | 评分规则 |
|------|:---:|------|---------|
| **社区活跃度** | 30 | stars/likes | 50k+:12, 10k+:10, 1k+:8, 100+:5, 10+:3, else:1 |
| | | downloads | 1M+:10, 100k+:8, 10k+:6, 1k+:4, 100+:2, else:1 |
| | | forks (仅GitHub) | 10k+:8, 1k+:6, 100+:4, 10+:2, else:1 |
| **代码质量** | 25 | license | 有开源协议:10, Other:3, 无:0 |
| | | language | Python/PyTorch/JAX:8, 其他:5, N/A:2 |
| | | description | >=100字:7, >=50字:5, >=20字:3, else:1 |
| **维护状态** | 20 | last update | <=7天:10, <=30天:8, <=90天:6, <=180天:4, <=365天:2, else:1 |
| | | open issues | >=50:10, >=10:7, >=1:4, else:2 |
| **相关性** | 15 | 名称匹配 | >=2词命中:8, 1词:5, 0词:1 |
| | | 描述/标签匹配 | >=3词:7, 2词:5, 1词:3, 0词:1 |
| **工程就绪度** | 10 | pipeline/task | 有pipeline标签:5, 有任务标签:4, else:1 |
| | | params/tags | 有参数信息:5, >=3个tags:4, else:2 |

### 评级标准

| 等级 | 分数区间 | 推荐程度 |
|:---:|:---:|---------|
| **A+** | >= 80 | 强烈推荐，可直接用于生产/二次开发 |
| **A** | >= 65 | 推荐，代码质量和社区活跃度高 |
| **B+** | >= 50 | 可用，需要额外评估和适配 |
| **B** | >= 35 | 备选，存在某些不足 |
| **C** | >= 20 | 不推荐，需要大量改进 |
| **D** | < 20 | 不推荐使用 |

---

## 五、输出报告模板

```markdown
# Research Workflow Report

**Query:** `image segmentation`
**Generated:** 2026-07-09 14:00
**Workflow:** SOTA Discovery → Paper Analysis → Related Work → Code Search + Scoring → Preprint Tracking

---

## Step 1: SOTA 发现

| # | Title | Source | Cited | Link |
|---|-------|--------|-------|------|
| 1 | Paper Title | Google Scholar | 500 | [Link](url) |

## Step 2: 论文深度分析

### 1. Paper Title
- **Year/Venue:** 2026 / CVPR
- **Citations:** 1234 (Influential: 56)
- **TLDR:** Auto-generated summary...
- **arXiv:** [2601.00001](https://arxiv.org/abs/2601.00001)
- **Key References:** 10 papers listed

## Step 3: 同族工作扩展

| # | Title | Source | Cited | Seed Paper |
|---|-------|--------|-------|-----------|
| 1 | Related Paper | GS Related | 200 | Seed Title |

## Step 4: 代码与模型实现检索

### SOTA 评分比较总表
| 排名 | 评级 | 名称 | 平台 | 总分 | 社区 | 质量 | 维护 | 相关 | 就绪 |
|:---:|:---:|------|------|:---:|:---:|:---:|:---:|:---:|:---:|
| 1 | A+ | repo/name | GitHub | 85 | 25/30 | 25/25 | 20/20 | 10/15 | 5/10 |

### A 级推荐方案详解
#### [A+] repo/name (GitHub) — 总分 85
- **推荐理由:** 综合评分优秀；社区高度活跃
- **描述:** ...
- **Tags:** computer-vision, pytorch

### GitHub / Hugging Face / ModelScope 分平台列表
(各平台独立表格，每行带评级标签)

## Step 5: 最新预印本追踪
| # | Title | Date | Authors | Categories |
|---|-------|------|---------|------------|
| 1 | Preprint Title | 2026-07-08 | Authors | cs.CV |
```

---

## 六、文件结构

```
sota-research-skill/
├── SKILL.md                          # 本文件 (入口, 含YAML元数据)
├── README.md                         # 完整使用文档 (中文)
├── scripts/
│   └── research_workflow.py          # 自动化脚本 v1.3 (70KB, 含 Discover + OpenAlex)
├── config/
│   ├── api_config.example.json       # API配置模板 (含端点和限速说明)
│   └── api_config.json               # 用户实际配置 (gitignored, 不入包)
├── templates/
│   └── report_template.md            # 报告输出模板
└── docs/
    ├── api_reference.md              # 8个API的完整端点文档 (含curl示例)
    └── migration_notes.md            # Papers With Code → CodeSOTA 迁移说明
```

---

## 七、使用示例

```bash
# 1. Discover 模式 — 引导收敛（推荐首次使用）
python3 scripts/research_workflow.py "图像分割" --discover
python3 scripts/research_workflow.py "vision transformer" --discover
python3 scripts/research_workflow.py "语音识别" --discover

# 2. 直接运行完整工作流（中文查询自动收敛）
python3 scripts/research_workflow.py "图像分割" --max-papers 3 --arxiv-cat cs.CV

# 3. 英文查询 + 增加深度
python3 scripts/research_workflow.py "image segmentation" \
  --max-papers 5 --arxiv-cat cs.CV

# 4. 跳过自动收敛，直接指定 CodeSOTA 任务
python3 scripts/research_workflow.py "segmentation" \
  --codesota-task semantic-segmentation

# 5. NLP 领域
python3 scripts/research_workflow.py "large language model" \
  --arxiv-cat cs.CL

# 6. 自定义输出路径
python3 scripts/research_workflow.py "object detection" \
  --output my_report.md

# 7. 追踪更长时间的预印本
python3 scripts/research_workflow.py "diffusion model" \
  --arxiv-cat cs.CV --months 6 --max-papers 3
```

---

## 八、已知限制与注意事项

1. **Papers With Code 已关闭** (2025.07)。CodeSOTA 是替代方案，但覆盖的任务尚不完整，
   不存在的任务返回 404，自动降级到 Google Scholar。
2. **Discover Mode 中文映射** 基于内置 84+ 条映射 + JSON 配置扩展，非 exhaustive。
   如遇未覆盖的中文术语，会降级到模糊匹配和 Google Scholar。
3. **模糊匹配阈值** 默认为单词相似度 >=0.3，可能产生少量不相关候选。
   多候选场景建议用户手动确认（`--discover` 模式）。
4. **Hugging Face API** 在部分网络环境（如 TRAE 远程沙箱）存在 SSL 限制，
   本地运行不受影响。
5. **Semantic Scholar 无 API Key 时限流严格**（429 错误，约 100 req/5min）。
   建议申请免费 Key 以提升到 100 req/min。
6. **Connected Papers API token** 需邮件申请 hello@connectedpapers.com，
   审批时间不确定。当前使用 SerpApi Google Scholar related 作为降级方案。
7. **SerpApi 免费版限制 100 次/月**，高频使用需升级付费版。
8. **arXiv API 无硬性限速**，但官方建议 3 秒请求间隔，脚本已内置。

---

## 九、跨平台兼容性

遵循 [Agent Skills 开放标准](https://agentskills.io/)，兼容以下平台：

| 平台 | 安装路径 | 触发方式 |
|------|---------|---------|
| Claude Code | `~/.claude/skills/sota-research/` | 自动发现 + `/sota-research` |
| Codex CLI | 同上 | 自动发现 |
| Cursor | 同上 | 自动发现 |
| Windsurf | 同上 | 自动发现 |
| Gemini CLI | 同上 | 自动发现 |
| 独立使用 | 任意目录 | `python3 scripts/research_workflow.py` |
