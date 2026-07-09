#!/usr/bin/env python3
"""
Research Workflow v1.3: 引导式收敛学术论文与代码复现工作流
五步链路 + 发现模式(Discover Mode) + 中英文兼容 + 模糊/关联搜索 + OpenAlex 兜底

APIs:
  Step 0 - 引导式领域收敛:  中文映射 + 关键词关联 + 模糊匹配 (本地)
  Step 1 - SOTA 发现:      CodeSOTA API → SerpApi Google Scholar → OpenAlex (三层降级)
  Step 2 - 论文深度分析:    Semantic Scholar API
  Step 3 - 同族工作扩展:    SerpApi Google Scholar (主力) + Semantic Scholar recommendations
  Step 4 - 多平台实现检索:   GitHub + Hugging Face + ModelScope + SOTA 评分
  Step 5 - 最新预印本追踪:   arXiv API

Usage:
  # 发现模式 - 引导收敛到精确领域
  python research_workflow.py "vision transformer" --discover

  # 直接运行完整工作流
  python research_workflow.py "image segmentation" --max-papers 5

  # 中文查询
  python research_workflow.py "图像分割" --max-papers 3 --arxiv-cat cs.CV
"""

import argparse
import json
import re
import sys
import time
import urllib.request
import urllib.parse
import urllib.error
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from pathlib import Path

# =============================================================================
# Configuration
# =============================================================================
# NOTE: All API keys/tokens should be set via environment variables or
#       config/api_config.json. Do NOT hardcode credentials in this file.
import os

def _load_config():
    """Load API keys from environment variables or config file."""
    config_path = Path(__file__).parent.parent / "config" / "api_config.json"
    cfg = {}
    if config_path.exists():
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                cfg = json.load(f)
        except Exception:
            pass
    return cfg

_CFG = _load_config()

SERPAPI_KEY = os.environ.get("SERPAPI_KEY", _CFG.get("serpapi_key", ""))
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", _CFG.get("github_token", ""))
SEMANTIC_SCHOLAR_API_KEY = os.environ.get("SEMANTIC_SCHOLAR_API_KEY", _CFG.get("semantic_scholar_key", ""))
CONNECTED_PAPERS_TOKEN = os.environ.get("CONNECTED_PAPERS_API_KEY", _CFG.get("connected_papers_token", ""))
MODELSCOPE_TOKEN = os.environ.get("MODELSCOPE_TOKEN", _CFG.get("modelscope_token", ""))

SEMANTIC_SCHOLAR_BASE = "https://api.semanticscholar.org/graph/v1"
ARXIV_BASE = "http://export.arxiv.org/api/query"
GITHUB_BASE = "https://api.github.com"
SERPAPI_BASE = "https://serpapi.com/search"
CODESOTA_BASE = "https://www.codesota.com/api/sota"
HF_BASE = "https://huggingface.co"
MODELSCOPE_BASE = "https://modelscope.cn/openapi/v1"
OPENALEX_BASE = "https://api.openalex.org"

HEADERS = {
    "User-Agent": "ResearchWorkflow/1.3 (Academic Research Tool)",
}
if GITHUB_TOKEN:
    HEADERS["Authorization"] = f"token {GITHUB_TOKEN}"

# =============================================================================
# CodeSOTA Task Mapping (Loaded from config or embedded fallback)
# =============================================================================

# Fallback Chinese-to-Task mapping (embedded for standalone usage)
# Full mapping loaded from config/codesota_tasks.json if available
_C_CODESOTA_TASKS = {
    "图像分割": "image-segmentation",
    "语义分割": "semantic-segmentation",
    "图像分类": "image-classification",
    "目标检测": "object-detection",
    "文字识别": "ocr",
    "光学字符识别": "ocr",
    "文档识别": "document-ocr",
    "语音识别": "asr",
    "语音合成": "tts",
    "文本转语音": "tts",
    "视觉问答": "vqa",
    "图像描述": "image-captioning",
    "图像生成": "text-to-image",
    "文生图": "text-to-image",
    "代码生成": "code-generation",
    "问答系统": "question-answering",
    "文本分类": "text-classification",
    "文本摘要": "text-summarization",
    "机器翻译": "machine-translation",
    "命名实体识别": "named-entity-recognition",
    "异常检测": "anomaly-detection",
    "医学图像分割": "medical-image-segmentation",
    "医学影像": "medical-image-segmentation",
    "时间序列预测": "time-series-forecasting",
    "视频分类": "video-classification",
    "视频理解": "video-understanding",
    "特征提取": "feature-extraction",
    "数学推理": "mathematical-reasoning",
    "常识推理": "commonsense-reasoning",
    "多步推理": "multi-step-reasoning",
    "逻辑推理": "logical-reasoning",
    "算术推理": "arithmetic-reasoning",
    "语言模型": "language-modeling",
    "自然语言推理": "natural-language-inference",
    "情感分析": "text-classification",
    "手写识别": "handwriting-recognition",
    "场景文字检测": "scene-text-detection",
    "场景文字识别": "scene-text-recognition",
    "表格识别": "table-recognition",
    "文档解析": "document-parsing",
    "文档布局分析": "document-layout-analysis",
    "文档理解": "document-understanding",
    "文档分类": "document-classification",
    "表格问答": "table-question-answering",
    "零样本分类": "zero-shot-classification",
    "节点分类": "node-classification",
    "链接预测": "link-prediction",
    "知识图谱补全": "knowledge-graph-completion",
    "关系抽取": "relation-extraction",
    "实体链接": "entity-linking",
    "语义相似度": "semantic-similarity",
    "文本排序": "text-ranking",
    "阅读理解": "reading-comprehension",
    "声音事件检测": "sound-event-detection",
    "音频分类": "audio-classification",
    "音频描述": "audio-captioning",
    "音乐生成": "music-generation",
    "语音克隆": "voice-cloning",
    "说话人验证": "speaker-verification",
    "语音翻译": "speech-translation",
    "视频生成": "video-to-video",
    "视频语言模型": "video-language-models",
    "关键点检测": "keypoint-detection",
    "连续控制": "continuous-control",
    "机器人操作": "robot-manipulation",
    "疾病分类": "disease-classification",
    "分子性质预测": "molecular-property-prediction",
    "SWE测试": "swe-bench",
    "自主编码": "autonomous-coding",
    "编程修复": "program-repair",
    "代码补全": "code-completion",
    "代码翻译": "code-translation",
    "代码摘要": "code-summarization",
    "漏洞检测": "bug-detection",
    "图推理": "knowledge-graph-completion",
    "智能体": "agents",
    "网络代理": "web-agents",
    "编码代理": "coding-agents",
    "工具使用": "tool-use",
    "时序预测": "time-series-forecasting",
    "表格分类": "tabular-classification",
    "表格回归": "tabular-regression",
    "雅达利游戏": "atari-games",
    "Mask填充": "fill-mask",
}

_C_KEYWORD_ASSOCIATIONS = {
    "segmentation": ["image-segmentation", "semantic-segmentation", "medical-image-segmentation"],
    "detection": ["object-detection", "scene-text-detection", "anomaly-detection", "bug-detection", "sound-event-detection"],
    "classification": ["image-classification", "text-classification", "disease-classification", "document-classification", "zero-shot-classification", "audio-classification", "video-classification", "node-classification", "tabular-classification"],
    "ocr": ["ocr", "document-ocr", "scene-text-recognition", "handwriting-recognition", "ocr-capabilities"],
    "speech": ["asr", "tts", "voice-cloning", "speaker-verification", "speech-translation", "audio-text-to-text"],
    "vision": ["image-classification", "object-detection", "semantic-segmentation", "image-segmentation", "vqa", "image-captioning", "image-text-to-text"],
    "nlp": ["text-classification", "text-summarization", "question-answering", "named-entity-recognition", "machine-translation", "natural-language-inference", "text-ranking"],
    "code": ["code-generation", "code-completion", "code-translation", "code-summarization", "bug-detection", "program-repair", "autonomous-coding", "swe-bench"],
    "medical": ["medical-image-segmentation", "disease-classification"],
    "video": ["video-classification", "video-understanding", "video-language-models", "video-to-video"],
    "audio": ["asr", "tts", "audio-classification", "audio-captioning", "sound-event-detection", "voice-cloning", "speaker-verification", "music-generation"],
    "reasoning": ["mathematical-reasoning", "commonsense-reasoning", "multi-step-reasoning", "logical-reasoning", "arithmetic-reasoning"],
    "agent": ["agents", "web-agents", "coding-agents", "tool-use"],
    "document": ["document-ocr", "document-parsing", "document-layout-analysis", "document-understanding", "document-classification", "table-recognition"],
    "table": ["table-recognition", "table-question-answering", "tabular-classification", "tabular-regression"],
    "graph": ["node-classification", "link-prediction", "knowledge-graph-completion", "relation-extraction", "entity-linking"],
}

_C_ALL_TASK_IDS = set([
    "agents", "anomaly-detection", "arithmetic-reasoning", "asr", "atari-games",
    "audio-captioning", "audio-classification", "autonomous-coding", "bug-detection",
    "caption", "code", "code-completion", "code-generation", "code-translation",
    "coding-agents", "commonsense-reasoning", "continuous-control", "disease-classification",
    "document-classification", "document-layout-analysis", "document-ocr", "document-parsing",
    "document-understanding", "feature-extraction", "fill-mask", "handwriting-recognition",
    "hcast", "image-captioning", "image-classification", "image-segmentation",
    "image-text-to-text", "keypoint-detection", "knowledge-graph-completion", "language-modeling",
    "link-prediction", "logical-reasoning", "machine-translation", "mathematical-reasoning",
    "medical-image-segmentation", "multi-step-reasoning", "music-generation", "named-entity-recognition",
    "natural-language-inference", "node-classification", "object-detection", "ocr", "ocr-capabilities",
    "program-repair", "question-answering", "react-native-code-generation", "reading-comprehension",
    "relation-extraction", "robot-manipulation", "scene-text-detection", "scene-text-recognition",
    "semantic-segmentation", "semantic-similarity", "sound-event-detection", "speaker-verification",
    "speech-recognition", "speech-translation", "swe-bench", "table-question-answering",
    "table-recognition", "tabular-classification", "tabular-regression", "text-classification",
    "text-ranking", "text-summarization", "text-to-image", "text-to-speech", "time-series-forecasting",
    "tool-use", "tts", "t2i", "vqa", "video-classification", "video-language-models",
    "video-to-video", "video-understanding", "voice-cloning", "web-agents", "zero-shot-classification",
    "polish-llm-general", "polish-cultural-competency", "polish-text-understanding",
    "polish-conversation-quality", "polish-emotional-intelligence",
])


def _load_codesota_mapping():
    """Load enhanced CodeSOTA task mapping from JSON if available."""
    paths = [
        Path(__file__).parent.parent / "config" / "codesota_tasks.json",
        Path("config/codesota_tasks.json"),
    ]
    for p in paths:
        if p.exists():
            try:
                with open(p, "r", encoding="utf-8") as f:
                    data = json.load(f)
                return (
                    data.get("chinese_to_task", _C_CODESOTA_TASKS),
                    data.get("keyword_associations", _C_KEYWORD_ASSOCIATIONS),
                    set(data.get("all_task_ids", list(_C_ALL_TASK_IDS))),
                    data.get("tasks", []),
                )
            except Exception:
                pass
    return _C_CODESOTA_TASKS, _C_KEYWORD_ASSOCIATIONS, _C_ALL_TASK_IDS, []


CHINESE_TO_TASK, KEYWORD_ASSOCIATIONS, ALL_TASK_IDS, CODESOTA_TASK_LIST = _load_codesota_mapping()


def log(msg):
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] {msg}", flush=True)


def api_get(url, timeout=20, retries=2):
    for attempt in range(retries + 1):
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return resp.read().decode("utf-8", errors="replace")
        except urllib.error.HTTPError as e:
            if e.code == 429:
                wait = 5 * (attempt + 1)
                if attempt < retries:
                    log(f"  Rate limited (429). Waiting {wait}s before retry {attempt+1}/{retries}...")
                    time.sleep(wait)
                else:
                    log(f"  ERROR: Rate limited (429) after {retries} retries. Skipping.")
                    return None
            else:
                if attempt < retries:
                    wait = 2 ** attempt
                    log(f"  Retry {attempt+1}/{retries} after error: {e}")
                    time.sleep(wait)
                else:
                    log(f"  ERROR: {e}")
                    return None
        except Exception as e:
            if attempt < retries:
                wait = 2 ** attempt
                log(f"  Retry {attempt+1}/{retries} after error: {e}")
                time.sleep(wait)
            else:
                log(f"  ERROR: {e}")
                return None


def api_get_json(url, timeout=20, retries=2):
    raw = api_get(url, timeout=timeout, retries=retries)
    if not raw:
        return None
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        log(f"  JSON parse failed for {url[:80]}")
        return None


# =============================================================================
# Discover & Task Matching (Step 0: 引导式收敛)
# =============================================================================

def _contains_chinese(text):
    return bool(re.search(r'[\u4e00-\u9fff]', text))


def _normalize(text):
    """Normalize text for fuzzy matching."""
    return re.sub(r'[^\w\u4e00-\u9fff]', ' ', text.lower()).strip()


def _similarity(a, b):
    """Simple word overlap similarity score (0-1)."""
    words_a = set(a.split())
    words_b = set(b.split())
    if not words_a or not words_b:
        return 0.0
    intersection = words_a & words_b
    union = words_a | words_b
    return len(intersection) / len(union) if union else 0.0


def _match_codesota_task(query):
    """
    多维度任务匹配：支持中文映射、直接命中、关键词关联、模糊匹配。
    返回按匹配度排序的候选任务列表。
    """
    candidates = []
    norm_q = _normalize(query)
    q_words = set(norm_q.split())

    # --- 1. 中文直接映射 ---
    if _contains_chinese(query):
        for zh, en_tid in CHINESE_TO_TASK.items():
            if zh in query or query in zh:
                score = 1.0 if zh == query else 0.9
                candidates.append({
                    "task_id": en_tid,
                    "match_type": "中文映射",
                    "match_score": score,
                    "reason": f"中文关键词 '{zh}' 映射到 '{en_tid}'",
                })

    # --- 2. 英文直接命中 (task id / alias) ---
    clean_q = query.lower().strip()
    for tid in ALL_TASK_IDS:
        if clean_q == tid:
            candidates.append({
                "task_id": tid,
                "match_type": "精确命中",
                "match_score": 1.0,
                "reason": f"查询词精确匹配任务 ID '{tid}'",
            })

    # --- 3. 关键词关联搜索 ---
    for kw, tasks in KEYWORD_ASSOCIATIONS.items():
        if kw in clean_q or any(w in clean_q for w in kw.split('-')):
            for tid in tasks:
                candidates.append({
                    "task_id": tid,
                    "match_type": "关键词关联",
                    "match_score": 0.7,
                    "reason": f"关键词 '{kw}' 关联到任务 '{tid}'",
                })

    # --- 4. 模糊匹配 (单词相似度) ---
    for tid in ALL_TASK_IDS:
        tid_norm = tid.replace("-", " ")
        sim = _similarity(norm_q, tid_norm)
        if sim >= 0.3:
            candidates.append({
                "task_id": tid,
                "match_type": "模糊匹配",
                "match_score": sim * 0.8,
                "reason": f"查询词 '{query}' 与任务 '{tid}' 相似度 {sim:.2f}",
            })

    # --- 去重 + 排序 ---
    seen = set()
    unique = []
    for c in sorted(candidates, key=lambda x: x["match_score"], reverse=True):
        if c["task_id"] not in seen:
            seen.add(c["task_id"])
            unique.append(c)

    return unique[:8]


def discover(query):
    """
    发现模式：将用户宽泛输入收敛到精确领域。
    返回候选任务列表 + 建议，不执行完整工作流。
    """
    print()
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║           Discover Mode — 引导式领域收敛                      ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    print(f"\n  输入: {query}")
    print()

    matches = _match_codesota_task(query)

    if not matches:
        print("  ⚠ 未在 CodeSOTA 注册表中找到匹配任务。")
        print("  建议尝试以下方向：")
        print("    - 使用更具体的技术术语（如 'image segmentation' 而非 'AI'）")
        print("    - 使用 CodeSOTA 已注册的任务名（如 'object-detection'）")
        print("    - 使用中文术语（如 '图像分割'、'目标检测'）")
        print()
        print("  将降级到 Google Scholar 进行通用学术搜索。")
        print()
        return None

    # 检查是否唯一精确命中
    exact = [m for m in matches if m["match_type"] in ("中文映射", "精确命中")]
    if len(exact) == 1:
        best = exact[0]
        print(f"  ✅ 唯一精确命中: '{best['task_id']}'")
        print(f"     {best['reason']}")
        print(f"     可直接执行完整工作流。")
        print()
        return best["task_id"]

    # 多候选 — 展示让用户选择
    print(f"  🔍 找到 {len(matches)} 个候选任务，请选择最匹配的一项：\n")
    for i, m in enumerate(matches, 1):
        badge = "【推荐】" if m["match_score"] >= 0.7 else ""
        print(f"    {i}. [{m['match_type']}] {m['task_id']} {badge}")
        print(f"       → {m['reason']}")
        print()

    print("  请输入编号选择，或直接输入精确任务名执行。")
    print(f"  建议任务: {matches[0]['task_id']}")
    print()
    return matches


# =============================================================================
# Step 1: SOTA Discovery (Enhanced)
# =============================================================================

def step1_sota_discovery(query, max_papers=5, codesota_task=None):
    """
    Step 1: 三层降级论文发现。
      1a. CodeSOTA API    — 查 SOTA 模型 + 论文
      1b. SerpApi (GS)    — 学术论文搜索 (主力补充)
      1c. OpenAlex API    — 兜底 (当 GS 无结果或结果不足时触发)
    如果已通过 discover() 收敛到精确任务，直接使用该任务 ID。
    """
    log("=" * 60)
    log("STEP 1: SOTA 发现 — CodeSOTA → Google Scholar → OpenAlex")
    log("=" * 60)

    papers = []
    seen_titles = set()

    # --- 优先使用已收敛的精确任务 ---
    search_task = codesota_task or query

    # --- 1a: CodeSOTA SOTA Lookup ---
    log(f"  [CodeSOTA] Searching SOTA for: {search_task}")
    codesota_results = api_get_json(f"{CODESOTA_BASE}/{urllib.parse.quote(search_task)}?tier=sota")

    if codesota_results and "error" not in codesota_results:
        log(f"  [CodeSOTA] Task: {codesota_results.get('task_name', search_task)}")
        pick = codesota_results.get("pick", {})
        if pick:
            model_name = pick.get("model_name", "N/A")
            score = pick.get("score", "N/A")
            metric = pick.get("score_metric", "N/A")
            log(f"  [CodeSOTA] SOTA Model: {model_name} (score: {score}, metric: {metric})")
            model_url = pick.get("model_url", "")
            papers.append({
                "source": "CodeSOTA SOTA",
                "title": f"SOTA: {model_name}",
                "url": model_url,
                "score": score,
                "metric": metric,
                "notes": f"Current SOTA on {codesota_results.get('benchmark', 'N/A')}",
                "codesota_task": search_task,
            })
            seen_titles.add(f"SOTA: {model_name}")
        for ru in codesota_results.get("runners_up", [])[:3]:
            title = f"Runner-up: {ru.get('model_name', 'N/A')}"
            if title not in seen_titles:
                papers.append({
                    "source": "CodeSOTA Runner-up",
                    "title": title,
                    "url": ru.get("model_url", ""),
                    "score": ru.get("score", "N/A"),
                    "codesota_task": search_task,
                })
                seen_titles.add(title)
    elif codesota_results and "error" in codesota_results:
        log(f"  [CodeSOTA] Task '{search_task}' not found in registry.")

    time.sleep(1)

    # --- 1b: SerpApi Google Scholar Search ---
    log(f"  [Google Scholar] Searching: {query}")
    gs_url = (
        f"{SERPAPI_BASE}?engine=google_scholar"
        f"&q={urllib.parse.quote(query)}"
        f"&api_key={SERPAPI_KEY}"
        f"&num={max_papers + 2}"
        f"&hl=en"
    )
    gs_data = api_get_json(gs_url)
    gs_results = []

    if gs_data and "organic_results" in gs_data:
        for r in gs_data["organic_results"][:max_papers]:
            title = r.get("title", "N/A")
            if title not in seen_titles:
                cited = r.get("inline_links", {}).get("cited_by", {}).get("total", 0)
                pub_info = r.get("publication_info", {}).get("summary", "")
                papers.append({
                    "source": "Google Scholar",
                    "title": title,
                    "url": r.get("link", ""),
                    "cited_by": cited,
                    "pub_info": pub_info,
                    "snippet": r.get("snippet", ""),
                    "authors": _extract_authors(pub_info),
                    "year": _extract_year(pub_info),
                })
                seen_titles.add(title)
        gs_results = gs_data.get("related_searches", [])
    else:
        log(f"  [Google Scholar] No results returned.")

    time.sleep(1)

    # --- 1c: OpenAlex Fallback (当 GS 无结果或结果不足时) ---
    needs_fallback = (len([p for p in papers if p["source"] == "Google Scholar"]) < 2)
    if needs_fallback:
        log(f"  [OpenAlex] Fallback search for: {query}")
        oa_results = _search_openalex(query, max_papers=max_papers)
        for r in oa_results:
            title = r.get("title", "")
            if title and title not in seen_titles:
                papers.append(r)
                seen_titles.add(title)
        if oa_results:
            log(f"  [OpenAlex] Found {len(oa_results)} supplementary papers")
        else:
            log(f"  [OpenAlex] No additional results")
    else:
        log(f"  [OpenAlex] Skipped (Google Scholar returned sufficient results)")

    log(f"  [Step 1] Found {len(papers)} candidate papers\n")
    return papers, gs_results


def _search_openalex(query, max_papers=5):
    """
    OpenAlex API 搜索：作为 Step 1 的第三层降级兜底。
    检索论文标题、被引数、发表年份、DOI、开放获取链接。
    API 免费无速率限制 (建议 <10 req/s, polite pool)。
    """
    results = []
    try:
        # 先按相关性排序取 top 结果
        url = (
            f"{OPENALEX_BASE}/works"
            f"?search={urllib.parse.quote(query)}"
            f"&per_page={max_papers}"
            f"&sort=relevance_score:desc"
            f"&select=id,title,display_name,cited_by_count,publication_year,"
            f"primary_location,authorships,doi,open_access,type,biblio"
        )
        raw = api_get(url, timeout=15, retries=1)
        if not raw:
            return results

        data = json.loads(raw)
        meta = data.get("meta", {})
        total = meta.get("count", 0)
        log(f"  [OpenAlex] Total matching works: {total:,}")

        for w in data.get("results", []):
            title = w.get("title") or w.get("display_name", "")
            if not title:
                continue

            # DOI
            doi = w.get("doi", "") or ""
            doi_url = f"https://doi.org/{doi.replace('https://doi.org/', '')}" if doi else ""

            # 开放获取 PDF
            oa = w.get("open_access") or {}
            oa_url = oa.get("oa_url", "") or ""

            # 作者
            authorships = w.get("authorships") or []
            authors = []
            for a in authorships[:3]:
                if a.get("author", {}).get("display_name"):
                    authors.append(a["author"]["display_name"])
            author_str = ", ".join(authors) + (" et al." if len(authors) > 3 or len(authorships) > 3 else "")

            # 来源期刊/会议
            primary_loc = w.get("primary_location") or {}
            source = primary_loc.get("source") or {}
            venue = source.get("display_name", "") or ""

            results.append({
                "source": "OpenAlex",
                "title": title,
                "url": doi_url or oa_url or f"https://openalex.org/works/{w.get('id', '').split('/')[-1]}",
                "cited_by": w.get("cited_by_count", 0),
                "year": w.get("publication_year"),
                "authors": author_str,
                "venue": venue,
                "doi": doi,
                "oa_pdf": oa_url,
                "work_type": w.get("type", ""),
            })
    except Exception as e:
        log(f"  [OpenAlex] Error: {e}")

    return results


def _extract_authors(pub_info):
    match = re.match(r"^(.+?)(?:\s*[-–]\s|\s*$)", pub_info or "")
    if match:
        authors_str = match.group(1).strip()
        parts = re.split(r",\s*(?=[A-Z])", authors_str)
        if len(parts) > 3:
            return ", ".join(parts[:3]) + " et al."
        return authors_str
    return ""


def _extract_year(pub_info):
    years = re.findall(r"\b(19|20)\d{2}\b", pub_info or "")
    return years[-1] if years else ""


# =============================================================================
# Step 2: Paper Deep Analysis
# =============================================================================

def step2_paper_analysis(papers, max_papers=3):
    log("=" * 60)
    log("STEP 2: 论文深度分析 — Semantic Scholar")
    log("=" * 60)

    analyses = []
    analyzed_titles = set()

    for paper in papers[:max_papers * 2]:
        title = paper.get("title", "")
        if not title or title in analyzed_titles:
            continue
        if title.startswith("SOTA:") or title.startswith("Runner-up:"):
            clean_title = title.replace("SOTA: ", "").replace("Runner-up: ", "")
        else:
            clean_title = title

        log(f"  Analyzing: {clean_title[:70]}")
        analyzed_titles.add(title)

        search_url = (
            f"{SEMANTIC_SCHOLAR_BASE}/paper/search"
            f"?query={urllib.parse.quote(clean_title)}"
            f"&limit=1"
            f"&fields=title,year,citationCount,externalIds,tldr,abstract,authors,venue,openAccessPdf,influentialCitationCount"
        )
        if SEMANTIC_SCHOLAR_API_KEY:
            search_url += f"&api_key={SEMANTIC_SCHOLAR_API_KEY}"

        data = api_get_json(search_url)
        if not data or not data.get("data"):
            log(f"    Not found on Semantic Scholar")
            analyses.append({**paper, "ss_analysis": None})
            time.sleep(3)
            continue

        ss_paper = data["data"][0]
        paper_id = ss_paper.get("paperId")

        analysis = {
            "ss_title": ss_paper.get("title", ""),
            "year": ss_paper.get("year"),
            "venue": ss_paper.get("venue", ""),
            "citation_count": ss_paper.get("citationCount", 0),
            "influential_citations": ss_paper.get("influentialCitationCount", 0),
            "tldr": ss_paper.get("tldr", {}).get("text", "N/A") if ss_paper.get("tldr") else "N/A",
            "abstract": (ss_paper.get("abstract") or "")[:500],
            "authors": [a.get("name", "") for a in ss_paper.get("authors", [])[:5]],
            "open_access_pdf": ss_paper.get("openAccessPdf", {}).get("url", ""),
            "arxiv_id": ss_paper.get("externalIds", {}).get("ArXiv", ""),
            "doi": ss_paper.get("externalIds", {}).get("DOI", ""),
        }

        time.sleep(3)

        if paper_id:
            ref_url = (
                f"{SEMANTIC_SCHOLAR_BASE}/paper/{paper_id}/references"
                f"?fields=title,year,citationCount,externalIds"
                f"&limit=10"
            )
            if SEMANTIC_SCHOLAR_API_KEY:
                ref_url += f"&api_key={SEMANTIC_SCHOLAR_API_KEY}"
            ref_data = api_get_json(ref_url)
            if ref_data:
                refs = []
                for r in ref_data.get("data", [])[:10]:
                    cited = r.get("citedPaper", {})
                    refs.append({
                        "title": cited.get("title", ""),
                        "year": cited.get("year"),
                        "citations": cited.get("citationCount", 0),
                        "arxiv": (cited.get("externalIds") or {}).get("ArXiv", ""),
                    })
                analysis["references"] = refs
            time.sleep(3)

        analyses.append({**paper, "ss_analysis": analysis})
        log(f"    Citations: {analysis['citation_count']} | "
            f"Influential: {analysis['influential_citations']}")

        if len(analyses) >= max_papers:
            break

    log(f"  [Step 2] Analyzed {len(analyses)} papers\n")
    return analyses


# =============================================================================
# Step 3: Related Work Expansion
# =============================================================================

def step3_related_work(analyses, max_related=10):
    log("=" * 60)
    log("STEP 3: 同族工作扩展 — Google Scholar + Semantic Scholar")
    log("=" * 60)

    all_related = []
    seen_titles = set()

    for paper in analyses[:2]:
        ss = paper.get("ss_analysis") or {}
        title = ss.get("ss_title") or paper.get("title", "")
        if not title or title.startswith("SOTA:") or title.startswith("Runner-up:"):
            continue

        log(f"  [Google Scholar] Related to: {title[:60]}")
        related_url = (
            f"{SERPAPI_BASE}?engine=google_scholar"
            f"&q=related:{urllib.parse.quote(title)}"
            f"&api_key={SERPAPI_KEY}"
            f"&num={max_related}"
        )
        related_data = api_get_json(related_url)

        if related_data and "organic_results" in related_data:
            for r in related_data["organic_results"]:
                t = r.get("title", "")
                if t and t not in seen_titles:
                    seen_titles.add(t)
                    cited = r.get("inline_links", {}).get("cited_by", {}).get("total", 0)
                    all_related.append({
                        "source": "Google Scholar Related",
                        "title": t,
                        "url": r.get("link", ""),
                        "cited_by": cited,
                        "pub_info": r.get("publication_info", {}).get("summary", ""),
                        "snippet": r.get("snippet", ""),
                        "seed_paper": title[:50],
                    })
            log(f"    Found {len(related_data['organic_results'])} related papers")

        time.sleep(2)

        ss_title = ss.get("ss_title") or paper.get("title", "")
        search_url = (
            f"{SEMANTIC_SCHOLAR_BASE}/paper/search"
            f"?query={urllib.parse.quote(ss_title)}"
            f"&limit=1"
            f"&fields=paperId"
        )
        if SEMANTIC_SCHOLAR_API_KEY:
            search_url += f"&api_key={SEMANTIC_SCHOLAR_API_KEY}"
        search_data = api_get_json(search_url)

        if search_data and search_data.get("data"):
            paper_id = search_data["data"][0].get("paperId")
            if paper_id:
                rec_url = (
                    f"{SEMANTIC_SCHOLAR_BASE}/paper/{paper_id}/recommendations"
                    f"?fields=title,year,citationCount,externalIds,venue"
                    f"&limit=5"
                )
                if SEMANTIC_SCHOLAR_API_KEY:
                    rec_url += f"&api_key={SEMANTIC_SCHOLAR_API_KEY}"
                rec_data = api_get_json(rec_url)

                if rec_data and rec_data.get("data"):
                    for r in rec_data["data"]:
                        t = r.get("title", "")
                        if t and t not in seen_titles:
                            seen_titles.add(t)
                            all_related.append({
                                "source": "Semantic Scholar Recommendations",
                                "title": t,
                                "year": r.get("year"),
                                "citations": r.get("citationCount", 0),
                                "venue": r.get("venue", ""),
                                "arxiv": (r.get("externalIds") or {}).get("ArXiv", ""),
                                "seed_paper": title[:50],
                            })
                    log(f"    [Semantic Scholar] +{len(rec_data['data'])} recommendations")

                time.sleep(1)

    all_related.sort(key=lambda x: x.get("cited_by", 0) or x.get("citations", 0), reverse=True)

    log(f"  [Step 3] Found {len(all_related)} related papers (deduplicated)\n")
    return all_related[:max_related * 2]


# =============================================================================
# Step 4: Multi-Platform Code & Model Implementation Search + SOTA Scoring
# =============================================================================

def _search_github(search_queries, max_per_query=5, max_total=10):
    repos = []
    seen = set()

    for q in list(search_queries)[:4]:
        log(f"  [GitHub] Searching repos: {q[:60]}")
        clean_q = q.replace("SOTA: ", "").replace("Runner-up: ", "")

        for filter_str in [f" language:python", ""]:
            if filter_str:
                gh_search = clean_q + filter_str
            else:
                gh_search = clean_q
            gh_url = (
                f"{GITHUB_BASE}/search/repositories"
                f"?q={urllib.parse.quote(gh_search)}"
                f"&sort=stars&order=desc&per_page={max_per_query}"
            )
            gh_data = api_get_json(gh_url)
            if gh_data and "items" in gh_data:
                for item in gh_data["items"]:
                    full_name = item.get("full_name", "")
                    if full_name not in seen:
                        seen.add(full_name)
                        updated = item.get("updated_at", "")
                        try:
                            last_update = datetime.strptime(updated, "%Y-%m-%dT%H:%M:%SZ")
                            days_ago = (datetime.now() - last_update).days
                        except:
                            days_ago = -1

                        repos.append({
                            "platform": "GitHub",
                            "name": full_name,
                            "description": (item.get("description") or "")[:200],
                            "stars": item.get("stargazers_count", 0),
                            "forks": item.get("forks_count", 0),
                            "language": item.get("language", "N/A"),
                            "license": (item.get("license") or {}).get("spdx_id", "N/A"),
                            "last_update_days": days_ago,
                            "open_issues": item.get("open_issues_count", 0),
                            "url": item.get("html_url", ""),
                            "topics": item.get("topics", [])[:5],
                            "score": item.get("stargazers_count", 0),
                        })

            time.sleep(2)
            if len(repos) >= max_total:
                break

    repos.sort(key=lambda x: x.get("score", 0), reverse=True)
    return repos[:max_total]


def _search_huggingface(search_queries, max_per_query=5, max_total=8):
    models = []
    seen = set()

    for q in list(search_queries)[:3]:
        log(f"  [Hugging Face] Searching models: {q[:60]}")
        clean_q = q.replace("SOTA: ", "").replace("Runner-up: ", "")
        words = clean_q.split()
        keywords = " ".join(words[:4]) if len(words) > 4 else clean_q
        hf_url = (
            f"{HF_BASE}/api/models"
            f"?search={urllib.parse.quote(keywords)}"
            f"&sort=downloads"
            f"&direction=-1"
            f"&limit={max_per_query}"
            f"&full=false"
        )
        hf_data = api_get_json(hf_url)

        if hf_data and isinstance(hf_data, list):
            for m in hf_data:
                model_id = m.get("id", "")
                if model_id and model_id not in seen:
                    seen.add(model_id)
                    downloads = m.get("downloads", 0)
                    likes = m.get("likes", 0)
                    tags = m.get("tags", [])
                    pipeline = m.get("pipeline_tag", "N/A")
                    lib = m.get("library_name", "N/A")
                    score = downloads + likes * 100

                    models.append({
                        "platform": "Hugging Face",
                        "name": model_id,
                        "description": (m.get("cardData", {}).get("metadata", {}).get("description", "") or "")[:200],
                        "stars": likes,
                        "forks": downloads,
                        "language": lib,
                        "license": next((t.replace("license:", "") for t in tags if t.startswith("license:")), "N/A"),
                        "last_update_days": -1,
                        "open_issues": 0,
                        "url": f"https://huggingface.co/{model_id}",
                        "topics": [pipeline] + [t for t in tags if not t.startswith("license:")][:4],
                        "score": score,
                        "pipeline": pipeline,
                        "downloads": downloads,
                    })
            log(f"    Found {len(hf_data)} models")

        time.sleep(2)
        if len(models) >= max_total:
            break

    models.sort(key=lambda x: x.get("score", 0), reverse=True)
    return models[:max_total]


def _search_huggingface_by_arxiv(arxiv_ids, max_total=5):
    models = []
    seen = set()

    for arxiv_id in arxiv_ids[:3]:
        if not arxiv_id:
            continue
        log(f"  [Hugging Face] Finding models for arxiv:{arxiv_id}")
        hf_url = f"{HF_BASE}/api/arxiv/{arxiv_id}/repos"
        hf_data = api_get_json(hf_url)

        if hf_data and isinstance(hf_data, dict):
            for m in hf_data.get("models", [])[:max_total]:
                model_id = m.get("id", "")
                if model_id and model_id not in seen:
                    seen.add(model_id)
                    downloads = m.get("downloads", 0)
                    likes = m.get("likes", 0)
                    tags = m.get("tags", [])
                    pipeline = m.get("pipeline_tag", "N/A")
                    score = downloads + likes * 100

                    models.append({
                        "platform": "Hugging Face (by arXiv)",
                        "name": model_id,
                        "description": (m.get("cardData", {}).get("metadata", {}).get("description", "") or "")[:200],
                        "stars": likes,
                        "forks": downloads,
                        "language": m.get("library_name", "N/A"),
                        "license": next((t.replace("license:", "") for t in tags if t.startswith("license:")), "N/A"),
                        "url": f"https://huggingface.co/{model_id}",
                        "topics": [pipeline] + [t for t in tags if not t.startswith("license:")][:4],
                        "score": score,
                        "pipeline": pipeline,
                        "downloads": downloads,
                        "arxiv_link": arxiv_id,
                    })

        time.sleep(2)

    models.sort(key=lambda x: x.get("score", 0), reverse=True)
    return models[:max_total]


def _parse_ms_date(date_str):
    if not date_str:
        return -1
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ")
        return (datetime.now() - dt).days
    except:
        return -1


def _search_modelscope(search_queries, max_total=5):
    if not MODELSCOPE_TOKEN:
        log("  [ModelScope] Skipped (no MODELSCOPE_TOKEN configured)")
        return []

    models = []
    seen = set()
    ms_headers = dict(HEADERS)
    ms_headers["Authorization"] = f"Bearer {MODELSCOPE_TOKEN}"

    for q in list(search_queries)[:2]:
        log(f"  [ModelScope] Searching models: {q[:60]}")
        clean_q = q.replace("SOTA: ", "").replace("Runner-up: ", "")
        words = clean_q.split()
        keywords = " ".join(words[:3]) if len(words) > 3 else clean_q
        ms_url = (
            f"{MODELSCOPE_BASE}/models"
            f"?search={urllib.parse.quote(keywords)}"
            f"&limit=10"
        )

        try:
            req = urllib.request.Request(ms_url, headers=ms_headers)
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode("utf-8"))

            if data and data.get("success"):
                model_list = data.get("data", {}).get("models", [])
                total = data.get("data", {}).get("total_count", 0)
                log(f"    Found {len(model_list)} models (total match: {total})")

                for m in model_list:
                    model_id = m.get("id", "")
                    if model_id and model_id not in seen:
                        seen.add(model_id)
                        downloads = m.get("downloads", 0)
                        likes = m.get("likes", 0)
                        tasks = m.get("tasks", [])
                        tags = m.get("tags", [])
                        license_str = m.get("license", "") or next(
                            (t.replace("license:", "") for t in tags if t.startswith("license:")), "N/A"
                        )
                        libs = [t.replace("library:", "") for t in tags if t.startswith("library:")]
                        score = downloads + likes * 100

                        models.append({
                            "platform": "ModelScope",
                            "name": model_id,
                            "display_name": m.get("display_name", ""),
                            "description": (m.get("description") or "")[:200],
                            "stars": likes,
                            "forks": downloads,
                            "language": ", ".join(libs) if libs else "N/A",
                            "license": license_str,
                            "last_update_days": _parse_ms_date(m.get("last_modified", "")),
                            "open_issues": 0,
                            "url": f"https://modelscope.cn/models/{model_id}",
                            "topics": tasks + [t.replace("custom_tag:", "") for t in tags if t.startswith("custom_tag:")][:3],
                            "score": score,
                            "pipeline": ", ".join(tasks) if tasks else "N/A",
                            "downloads": downloads,
                            "params": m.get("params", 0),
                        })

                        if len(models) >= max_total:
                            break

        except Exception as e:
            log(f"    ModelScope error: {e}")

        time.sleep(2)
        if len(models) >= max_total:
            break

    models.sort(key=lambda x: x.get("score", 0), reverse=True)
    return models[:max_total]


def _score_and_rank_implementations(implementations, query):
    """
    SOTA 评分筛选与比较分析：对多平台实现方案进行多维度评分。
    """
    log("=" * 50)
    log("  Step 4b: SOTA 评分筛选与比较分析")
    log("=" * 50)

    query_words = set(query.lower().split())
    scored = []

    for impl in implementations:
        scores = {}
        stars = impl.get("stars", 0)
        downloads = impl.get("downloads", 0) or impl.get("forks", 0)
        forks = impl.get("forks", 0) if impl.get("platform") == "GitHub" else 0

        if stars >= 50000: scores["stars"] = 12
        elif stars >= 10000: scores["stars"] = 10
        elif stars >= 1000: scores["stars"] = 8
        elif stars >= 100: scores["stars"] = 5
        elif stars >= 10: scores["stars"] = 3
        else: scores["stars"] = 1

        if downloads >= 1000000: scores["downloads"] = 10
        elif downloads >= 100000: scores["downloads"] = 8
        elif downloads >= 10000: scores["downloads"] = 6
        elif downloads >= 1000: scores["downloads"] = 4
        elif downloads >= 100: scores["downloads"] = 2
        else: scores["downloads"] = 1

        if forks >= 10000: scores["forks"] = 8
        elif forks >= 1000: scores["forks"] = 6
        elif forks >= 100: scores["forks"] = 4
        elif forks >= 10: scores["forks"] = 2
        else: scores["forks"] = 1

        community = scores["stars"] + scores["downloads"] + scores["forks"]

        license_str = impl.get("license", "N/A")
        lang = impl.get("language", "N/A")

        if license_str and license_str not in ("N/A", "", "Other", "none"): scores["license"] = 10
        elif license_str in ("Other", "none"): scores["license"] = 3
        else: scores["license"] = 0

        popular_langs = {"Python", "PyTorch", "pytorch", "JAX", "jax", "transformers", "diffusers", "TensorFlow"}
        if lang in popular_langs: scores["language"] = 8
        elif lang not in ("N/A", "", "None"): scores["language"] = 5
        else: scores["language"] = 2

        desc = impl.get("description", "")
        if len(desc) >= 100: scores["description"] = 7
        elif len(desc) >= 50: scores["description"] = 5
        elif len(desc) >= 20: scores["description"] = 3
        else: scores["description"] = 1

        quality = scores["license"] + scores["language"] + scores["description"]

        days_ago = impl.get("last_update_days", -1)
        if days_ago <= 7: scores["freshness"] = 10
        elif days_ago <= 30: scores["freshness"] = 8
        elif days_ago <= 90: scores["freshness"] = 6
        elif days_ago <= 180: scores["freshness"] = 4
        elif days_ago <= 365: scores["freshness"] = 2
        elif days_ago >= 0: scores["freshness"] = 1
        else: scores["freshness"] = 5

        issues = impl.get("open_issues", 0)
        if issues >= 50: scores["engagement"] = 10
        elif issues >= 10: scores["engagement"] = 7
        elif issues >= 1: scores["engagement"] = 4
        else: scores["engagement"] = 2

        maintenance = scores["freshness"] + scores["engagement"]

        name_words = set(impl.get("name", "").lower().replace("-", " ").replace("_", " ").split())
        desc_words = set(impl.get("description", "").lower().split())
        topic_words = set()
        for t in impl.get("topics", []):
            topic_words.update(str(t).lower().replace("-", " ").split())

        name_overlap = query_words & name_words
        if len(name_overlap) >= 2: scores["name_relevance"] = 8
        elif len(name_overlap) == 1: scores["name_relevance"] = 5
        else: scores["name_relevance"] = 1

        desc_overlap = query_words & (desc_words | topic_words)
        if len(desc_overlap) >= 3: scores["desc_relevance"] = 7
        elif len(desc_overlap) >= 2: scores["desc_relevance"] = 5
        elif len(desc_overlap) >= 1: scores["desc_relevance"] = 3
        else: scores["desc_relevance"] = 1

        relevance = scores["name_relevance"] + scores["desc_relevance"]

        pipeline = impl.get("pipeline", "")
        tasks = impl.get("topics", [])
        task_str = " ".join(str(t) for t in tasks).lower()

        if pipeline and pipeline not in ("N/A", ""): scores["pipeline"] = 5
        elif any(kw in task_str for kw in query_words): scores["pipeline"] = 4
        else: scores["pipeline"] = 1

        params = impl.get("params", 0)
        if params > 0: scores["params"] = 5
        elif len(impl.get("topics", [])) >= 3: scores["params"] = 4
        else: scores["params"] = 2

        readiness = scores["pipeline"] + scores["params"]

        total_score = community + quality + maintenance + relevance + readiness

        impl["sota_scores"] = scores
        impl["sota_total"] = total_score
        impl["sota_breakdown"] = {
            "community_activity": (community, 30),
            "code_quality": (quality, 25),
            "maintenance": (maintenance, 20),
            "relevance": (relevance, 15),
            "engineering_readiness": (readiness, 10),
        }

        if total_score >= 80: impl["sota_level"] = "A+"
        elif total_score >= 65: impl["sota_level"] = "A"
        elif total_score >= 50: impl["sota_level"] = "B+"
        elif total_score >= 35: impl["sota_level"] = "B"
        elif total_score >= 20: impl["sota_level"] = "C"
        else: impl["sota_level"] = "D"

        reasons = []
        if total_score >= 65: reasons.append("综合评分优秀")
        if community >= 25: reasons.append("社区高度活跃")
        if quality >= 20: reasons.append("代码质量高")
        if maintenance >= 15: reasons.append("维护活跃")
        if relevance >= 10: reasons.append("与查询高度相关")
        impl["sota_reasons"] = "；".join(reasons) if reasons else "需进一步评估"

        scored.append(impl)

    scored.sort(key=lambda x: x.get("sota_total", 0), reverse=True)

    for i, s in enumerate(scored[:5], 1):
        log(f"  #{i} [{s['sota_level']}] {s.get('name', 'N/A')[:40]} "
            f"| 总分:{s['sota_total']} "
            f"| 社区:{s['sota_breakdown']['community_activity'][0]}/30 "
            f"| 质量:{s['sota_breakdown']['code_quality'][0]}/25 "
            f"| 维护:{s['sota_breakdown']['maintenance'][0]}/20 "
            f"| 相关:{s['sota_breakdown']['relevance'][0]}/15 "
            f"| 就绪:{s['sota_breakdown']['engineering_readiness'][0]}/10")

    return scored


def step4_code_search(papers, analyses, related, query="", max_repos=10, max_models=8):
    log("=" * 60)
    log("STEP 4: 代码与模型实现检索 — GitHub + Hugging Face + ModelScope")
    log("=" * 60)

    search_queries = set()
    arxiv_ids = []
    search_queries.add(query)

    for paper in papers[:2]:
        title = paper.get("title", "")
        if title and not title.startswith("SOTA:") and not title.startswith("Runner-up:"):
            search_queries.add(title)

    for analysis in analyses[:2]:
        ss = analysis.get("ss_analysis") or {}
        title = ss.get("ss_title", "")
        if title:
            search_queries.add(title)
        arxiv_id = ss.get("arxiv_id", "")
        if arxiv_id:
            search_queries.add(arxiv_id)
            arxiv_ids.append(arxiv_id)

    github_repos = _search_github(search_queries, max_per_query=5, max_total=max_repos)
    hf_models = _search_huggingface(search_queries, max_per_query=5, max_total=max_models)
    hf_arxiv_models = _search_huggingface_by_arxiv(arxiv_ids, max_total=5)
    ms_models = _search_modelscope(search_queries, max_total=5)

    all_results = github_repos + hf_models + hf_arxiv_models + ms_models
    all_results = _score_and_rank_implementations(all_results, query)

    total_github = sum(1 for r in all_results if r.get("platform") == "GitHub")
    total_hf = sum(1 for r in all_results if r.get("platform", "").startswith("Hugging Face"))
    total_ms = sum(1 for r in all_results if r.get("platform") == "ModelScope")

    log(f"  [Step 4] GitHub: {total_github} repos | Hugging Face: {total_hf} models | ModelScope: {total_ms} models")
    log(f"  [Step 4] Total: {len(all_results)} implementations (scored & ranked)\n")
    return all_results


# =============================================================================
# Step 5: Latest Preprints Tracking
# =============================================================================

def step5_arxiv_preprints(query, arxiv_cat=None, months=3, max_papers=10):
    log("=" * 60)
    log("STEP 5: 最新预印本追踪 — arXiv")
    log("=" * 60)

    if arxiv_cat:
        search_q = f"cat:{arxiv_cat} AND all:{query}"
    else:
        search_q = f"all:{query}"

    arxiv_url = (
        f"{ARXIV_BASE}?"
        f"search_query={urllib.parse.quote(search_q)}"
        f"&start=0"
        f"&max_results={max_papers}"
        f"&sortBy=submittedDate"
        f"&sortOrder=descending"
    )

    log(f"  [arXiv] Query: {search_q[:80]}")
    raw_xml = api_get(arxiv_url, timeout=30)

    if not raw_xml:
        log(f"  [arXiv] Failed to fetch results")
        return []

    try:
        root = ET.fromstring(raw_xml)
    except ET.ParseError as e:
        log(f"  [arXiv] XML parse error: {e}")
        return []

    ns = {"atom": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}
    preprints = []

    for entry in root.findall("atom:entry", ns):
        title = entry.find("atom:title", ns)
        summary = entry.find("atom:summary", ns)
        published = entry.find("atom:published", ns)
        link = None
        for l in entry.findall("atom:link", ns):
            if l.get("type") == "text/html":
                link = l.get("href")

        arxiv_id = ""
        pdf_url = ""
        for l in entry.findall("atom:link", ns):
            href = l.get("href", "")
            if "/pdf/" in href:
                pdf_url = href
                break

        authors = []
        for author in entry.findall("atom:author", ns):
            name = author.find("atom:name", ns)
            if name is not None and name.text:
                authors.append(name.text)

        categories = []
        for cat in entry.findall("atom:category", ns):
            term = cat.get("term", "")
            if term:
                categories.append(term)

        preprints.append({
            "title": (title.text or "").strip().replace("\n", " "),
            "abstract": (summary.text or "").strip()[:400],
            "published": published.text[:10] if published is not None and published.text else "",
            "authors": authors[:5],
            "categories": categories[:3],
            "arxiv_id": arxiv_id,
            "pdf_url": pdf_url,
            "url": link or f"https://arxiv.org/abs/{arxiv_id}",
        })

    log(f"  [Step 5] Found {len(preprints)} recent preprints\n")
    return preprints


# =============================================================================
# Report Generation
# =============================================================================

def generate_report(query, papers, analyses, related, repos, preprints, output_path):
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = []
    lines.append(f"# Research Workflow Report")
    lines.append(f"\n**Query:** `{query}`  ")
    lines.append(f"**Generated:** {now}  ")
    lines.append(f"**Workflow:** SOTA Discovery → Paper Analysis → Related Work → Code Search + Scoring → Preprint Tracking")
    lines.append("\n---\n")

    # Step 1
    lines.append("## Step 1: SOTA 发现\n")
    if papers:
        lines.append("| # | Title | Source | Cited | Link |")
        lines.append("|---|-------|--------|-------|------|")
        for i, p in enumerate(papers, 1):
            title = p.get("title", "N/A")[:70]
            url = p.get("url", "")
            cited = p.get("cited_by", p.get("score", ""))
            source = p.get("source", "N/A")
            link = f"[Link]({url})" if url else "N/A"
            lines.append(f"| {i} | {title} | {source} | {cited} | {link} |")
    else:
        lines.append("No SOTA results found.")
    lines.append("")

    # Step 2
    lines.append("## Step 2: 论文深度分析\n")
    for i, a in enumerate(analyses, 1):
        ss = a.get("ss_analysis")
        if ss:
            lines.append(f"### {i}. {ss.get('ss_title', 'N/A')}\n")
            lines.append(f"- **Year:** {ss.get('year', 'N/A')}  ")
            lines.append(f"- **Venue:** {ss.get('venue', 'N/A')}  ")
            lines.append(f"- **Citations:** {ss.get('citation_count', 0)}  ")
            lines.append(f"- **Influential Citations:** {ss.get('influential_citations', 0)}  ")
            authors = ss.get("authors", [])
            if authors:
                lines.append(f"- **Authors:** {', '.join(authors[:5])}")
            if ss.get("doi"):
                lines.append(f"- **DOI:** [{ss['doi']}](https://doi.org/{ss['doi']})  ")
            if ss.get("arxiv_id"):
                lines.append(f"- **arXiv:** [{ss['arxiv_id']}](https://arxiv.org/abs/{ss['arxiv_id']})  ")
            if ss.get("open_access_pdf"):
                lines.append(f"- **PDF:** [Open Access]({ss['open_access_pdf']})  ")
            lines.append(f"\n**TLDR:** {ss.get('tldr', 'N/A')}  ")
            if ss.get("abstract"):
                lines.append(f"\n**Abstract (excerpt):** {(ss['abstract'][:300])}...  ")
            refs = ss.get("references", [])
            if refs:
                lines.append(f"\n**Key References ({len(refs)}):**")
                for r in refs[:5]:
                    lines.append(f"  - [{r.get('title', 'N/A')[:60]}] — {r.get('citations', 0)} citations")
            lines.append("")
        else:
            lines.append(f"### {i}. {a.get('title', 'N/A')}\n")
            lines.append("*Semantic Scholar analysis not available.*\n")

    # Step 3
    lines.append("## Step 3: 同族工作扩展\n")
    if related:
        lines.append("| # | Title | Source | Cited | Seed Paper |")
        lines.append("|---|-------|--------|-------|-----------|")
        for i, r in enumerate(related, 1):
            title = r.get("title", "N/A")[:60]
            cited = r.get("cited_by", r.get("citations", 0))
            source = r.get("source", "N/A")
            seed = r.get("seed_paper", "N/A")[:40]
            url = r.get("url", "")
            if url:
                title = f"[{title}]({url})"
            lines.append(f"| {i} | {title} | {source} | {cited} | {seed} |")
    else:
        lines.append("No related work found.")
    lines.append("")

    # Step 4
    lines.append("## Step 4: 代码与模型实现检索\n")

    if repos:
        lines.append("### SOTA 评分比较总表\n")
        lines.append("| 排名 | 评级 | 名称 | 平台 | 总分 | 社区活跃 | 代码质量 | 维护状态 | 相关性 | 工程就绪 |")
        lines.append("|:---:|:---:|------|------|:---:|:---:|:---:|:---:|:---:|:---:|")
        for i, r in enumerate(repos, 1):
            name = r.get("name", "N/A")
            url = r.get("url", "")
            plat = r.get("platform", "N/A").replace("Hugging Face", "HF").replace("Hugging Face (by arXiv)", "HF/arXiv")
            level = r.get("sota_level", "N/A")
            total = r.get("sota_total", 0)
            bd = r.get("sota_breakdown", {})
            c = f"{bd.get('community_activity', (0,30))[0]}/{bd.get('community_activity', (0,30))[1]}"
            q = f"{bd.get('code_quality', (0,25))[0]}/{bd.get('code_quality', (0,25))[1]}"
            m = f"{bd.get('maintenance', (0,20))[0]}/{bd.get('maintenance', (0,20))[1]}"
            rel = f"{bd.get('relevance', (0,15))[0]}/{bd.get('relevance', (0,15))[1]}"
            eng = f"{bd.get('engineering_readiness', (0,10))[0]}/{bd.get('engineering_readiness', (0,10))[1]}"
            link = f"[{name[:45]}]({url})" if url else name[:45]
            lines.append(f"| {i} | **{level}** | {link} | {plat} | **{total}** | {c} | {q} | {m} | {rel} | {eng} |")
        lines.append("")

        lines.append("**评级标准：** A+ (>=80) | A (>=65) | B+ (>=50) | B (>=35) | C (>=20) | D (<20)  ")
        lines.append("**评分维度：** 社区活跃度 (30) + 代码质量 (25) + 维护状态 (20) + 相关性 (15) + 工程就绪度 (10) = 满分 100  ")
        lines.append("")

        a_plus = [r for r in repos if r.get("sota_level") in ("A+", "A")]
        if a_plus:
            lines.append("### A 级推荐方案详解\n")
            for r in a_plus:
                name = r.get("name", "N/A")
                url = r.get("url", "")
                plat = r.get("platform", "N/A")
                total = r.get("sota_total", 0)
                reasons = r.get("sota_reasons", "")
                link = f"[{name}]({url})" if url else name
                lines.append(f"#### [{r['sota_level']}] {link} ({plat}) — 总分 {total}\n")
                lines.append(f"- **推荐理由：** {reasons}")
                lines.append(f"- **描述：** {r.get('description', 'N/A')}")
                if r.get("downloads"):
                    lines.append(f"- **Downloads:** {r['downloads']:,}")
                if r.get("stars"):
                    lines.append(f"- **Stars/Likes:** {r['stars']:,}")
                topics = r.get("topics", [])
                if topics:
                    lines.append(f"- **Tags:** {', '.join(str(t) for t in topics[:5])}")
                pipeline = r.get("pipeline", "")
                if pipeline and pipeline not in ("N/A", ""):
                    lines.append(f"- **Pipeline/Task:** {pipeline}")
                lines.append("")

        platforms = {}
        for r in repos:
            plat = r.get("platform", "Unknown")
            if plat not in platforms:
                platforms[plat] = []
            platforms[plat].append(r)

        if "GitHub" in platforms:
            lines.append("### GitHub 仓库\n")
            lines.append("| # | Repository | ⭐ | Lang | License | Updated | 评级 |")
            lines.append("|---|-----------|-----|------|---------|---------|:---:|")
            for i, r in enumerate(platforms["GitHub"], 1):
                name = r.get("name", "N/A")
                url = r.get("url", "")
                stars = r.get("stars", 0)
                lang = r.get("language", "N/A")
                lic = r.get("license", "N/A")
                days = r.get("last_update_days", -1)
                update_str = f"{days}d ago" if days >= 0 else "N/A"
                level = r.get("sota_level", "-")
                link = f"[{name[:40]}]({url})" if url else name[:40]
                lines.append(f"| {i} | {link} | {stars:,} | {lang} | {lic} | {update_str} | **{level}** |")
            lines.append("")

        hf_keys = [k for k in platforms.keys() if k.startswith("Hugging Face")]
        if hf_keys:
            for hk in hf_keys:
                lines.append(f"### {hk}\n")
                lines.append("| # | Model | ❤ | ⬇️ | Pipeline | License | 评级 |")
                lines.append("|---|-------|----|-----|----------|---------|:---:|")
                for i, r in enumerate(platforms[hk], 1):
                    name = r.get("name", "N/A")
                    url = r.get("url", "")
                    likes = r.get("stars", 0)
                    downloads = r.get("downloads", 0) or r.get("forks", 0)
                    pipeline = r.get("pipeline", "N/A")
                    lic = r.get("license", "N/A")
                    level = r.get("sota_level", "-")
                    link = f"[{name[:40]}]({url})" if url else name[:40]
                    lines.append(f"| {i} | {link} | {likes} | {downloads:,} | {pipeline} | {lic} | **{level}** |")
                lines.append("")

        if "ModelScope" in platforms:
            lines.append("### ModelScope (魔搭) 模型\n")
            lines.append("| # | Model | ❤ | ⬇️ | Task | License | 评级 |")
            lines.append("|---|-------|----|-----|------|---------|:---:|")
            for i, r in enumerate(platforms["ModelScope"], 1):
                name = r.get("name", "N/A")
                url = r.get("url", "")
                likes = r.get("stars", 0)
                downloads = r.get("forks", 0)
                tasks = ", ".join(str(t) for t in r.get("topics", [])[:3])
                lic = r.get("license", "N/A")
                level = r.get("sota_level", "-")
                link = f"[{name[:40]}]({url})" if url else name[:40]
                lines.append(f"| {i} | {link} | {likes} | {downloads:,} | {tasks} | {lic} | **{level}** |")
            lines.append("")
    else:
        lines.append("No implementations found.")
    lines.append("")

    # Step 5
    lines.append("## Step 5: 最新预印本追踪\n")
    if preprints:
        lines.append("| # | Title | Date | Authors | Categories |")
        lines.append("|---|-------|------|---------|------------|")
        for i, p in enumerate(preprints, 1):
            title = p.get("title", "N/A")[:60]
            url = p.get("url", "")
            date = p.get("published", "")[:10]
            authors = p.get("authors", [])
            author_str = ", ".join(authors[:3]) + (" et al." if len(authors) > 3 else "")
            cats = ", ".join(p.get("categories", []))
            if url:
                title = f"[{title}]({url})"
            lines.append(f"| {i} | {title} | {date} | {author_str} | {cats} |")
    else:
        lines.append("No recent preprints found.")
    lines.append("")

    lines.append("---\n")
    lines.append(f"*Report generated by Research Workflow v1.3 | {now}*")
    lines.append(f"*APIs used: CodeSOTA, SerpApi (Google Scholar), OpenAlex, Semantic Scholar, GitHub, Hugging Face, ModelScope, arXiv*")

    report = "\n".join(lines)

    output = Path(output_path)
    output.write_text(report, encoding="utf-8")
    log(f"Report saved to: {output}")
    return report


# =============================================================================
# Main Workflow
# =============================================================================

def run_workflow(query, max_papers=3, arxiv_cat=None, months=3, output=None, codesota_task=None):
    """Execute the complete 5-step research workflow."""

    print()
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║          Research Workflow v1.3 — 学术论文与代码复现          ║")
    print("║  发现论文 → 理解方法 → 扩展同族 → 获取代码 → 追踪预印本       ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    print(f"\n  Query: {query}")
    if codesota_task:
        print(f"  CodeSOTA Task: {codesota_task}")
    print(f"  Max papers per step: {max_papers}")
    print(f"  arXiv category filter: {arxiv_cat or 'None'}")
    print()

    start = time.time()

    papers, related_searches = step1_sota_discovery(query, max_papers=max_papers, codesota_task=codesota_task)
    analyses = step2_paper_analysis(papers, max_papers=max_papers)
    related = step3_related_work(analyses, max_related=max_papers * 3)
    repos = step4_code_search(papers, analyses, related, query=query,
                              max_repos=max_papers * 3,
                              max_models=max_papers * 3)
    preprints = step5_arxiv_preprints(query, arxiv_cat=arxiv_cat, months=months, max_papers=max_papers * 3)

    elapsed = time.time() - start
    output = output or f"research_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    report = generate_report(query, papers, analyses, related, repos, preprints, output)

    print()
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║                     Workflow Complete!                       ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    print(f"\n  Step 1 (SOTA):           {len(papers)} papers found")
    print(f"  Step 2 (Analysis):      {len(analyses)} papers analyzed")
    print(f"  Step 3 (Related):       {len(related)} related papers")
    total_github = sum(1 for r in repos if r.get("platform") == "GitHub")
    total_hf = sum(1 for r in repos if r.get("platform", "").startswith("Hugging Face"))
    total_ms = sum(1 for r in repos if r.get("platform") == "ModelScope")
    print(f"  Step 4 (Implementations): {len(repos)} total (GitHub:{total_github} HF:{total_hf} ModelScope:{total_ms})")
    print(f"  Step 5 (Preprints):     {len(preprints)} recent preprints")
    print(f"\n  Total time: {elapsed:.1f}s")
    print(f"  Report: {output}")
    print()

    return report


def main():
    parser = argparse.ArgumentParser(
        description="Research Workflow v1.3: 引导式收敛学术论文与代码复现工作流",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # 发现模式 — 引导收敛到精确领域
  python research_workflow.py "vision transformer" --discover

  # 直接运行完整工作流
  python research_workflow.py "image segmentation" --max-papers 5

  # 中文查询
  python research_workflow.py "图像分割" --max-papers 3 --arxiv-cat cs.CV

  # 指定 CodeSOTA 任务名直接执行
  python research_workflow.py "object detection" --codesota-task semantic-segmentation
        """,
    )
    parser.add_argument("query", help="Research topic or paper title (supports Chinese)")
    parser.add_argument("--max-papers", type=int, default=3, help="Max papers per step (default: 3)")
    parser.add_argument("--arxiv-cat", type=str, default=None,
                        help="arXiv category filter (e.g., cs.CV, cs.AI, cs.CL)")
    parser.add_argument("--months", type=int, default=3,
                        help="Number of months to look back for preprints (default: 3)")
    parser.add_argument("--output", type=str, default=None,
                        help="Output markdown file path (default: auto-generated)")
    parser.add_argument("--discover", action="store_true",
                        help="Discover mode: show candidate tasks without running full workflow")
    parser.add_argument("--codesota-task", type=str, default=None,
                        help="Skip discovery and directly use this CodeSOTA task ID")

    args = parser.parse_args()

    if args.discover:
        result = discover(args.query)
        if result and isinstance(result, str):
            # Unique exact match — ask if user wants to proceed
            print(f"检测到唯一精确匹配 '{result}'。")
            print("是否直接执行完整工作流？(请输入 y 或直接回车)")
        sys.exit(0)

    # Run discovery silently to find best CodeSOTA task
    codesota_task = args.codesota_task
    if not codesota_task:
        matches = _match_codesota_task(args.query)
        exact = [m for m in matches if m["match_type"] in ("中文映射", "精确命中")]
        if len(exact) == 1:
            codesota_task = exact[0]["task_id"]
            log(f"Auto-converged to CodeSOTA task: {codesota_task}")
        elif matches:
            log(f"CodeSOTA candidates: {', '.join(m['task_id'] for m in matches[:3])}")
            log(f"Using primary candidate: {matches[0]['task_id']}")
            codesota_task = matches[0]["task_id"]

    run_workflow(
        query=args.query,
        max_papers=args.max_papers,
        arxiv_cat=args.arxiv_cat,
        months=args.months,
        output=args.output,
        codesota_task=codesota_task,
    )


if __name__ == "__main__":
    main()
