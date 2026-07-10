#!/usr/bin/env python3
"""
Research Workflow v1.6.0: 引导式收敛学术论文与代码复现工作流
五步链路 + 发现模式(Discover Mode) + 中英文兼容 + 模糊/关联搜索 + OpenAlex 兜底

APIs:
  Step 0 - 引导式领域收敛:  中文映射 + 关键词关联 + 模糊匹配 + 模型族匹配 (本地)
  Step 1 - SOTA 发现:      CodeSOTA API → OpenAlex (主力并行源) → SerpApi Google Scholar (补充)
  Step 2 - 论文深度分析:    OpenAlex (主力) + Semantic Scholar (补充 TLDR)
  Step 3 - 同族工作扩展:    OpenAlex 双向引用 (主力) + Google Scholar + Semantic Scholar (补充)
  Step 4 - 多平台实现检索:   GitHub + Hugging Face + ModelScope + SOTA 评分 (工程就绪度 25 分)
  Step 5 - 最新预印本追踪:   arXiv API + Hugging Face Daily Papers

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
import os
import urllib.request
import urllib.parse
import urllib.error
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from pathlib import Path

# =============================================================================
# Configuration
# =============================================================================

def _load_config():
    """Load API configuration from config file or environment variables."""
    config_paths = [
        Path(__file__).parent.parent / "config" / "api_config.json",
        Path("config/api_config.json"),
    ]
    for p in config_paths:
        if p.exists():
            try:
                with open(p, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
    return {}

_CFG = _load_config()

SERPAPI_KEY = os.environ.get("SERPAPI_KEY", _CFG.get("serpapi_key", ""))
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", _CFG.get("github_token", ""))
SEMANTIC_SCHOLAR_API_KEY = os.environ.get("SEMANTIC_SCHOLAR_API_KEY", _CFG.get("semantic_scholar_key", ""))
CONNECTED_PAPERS_TOKEN = os.environ.get("CONNECTED_PAPERS_TOKEN", _CFG.get("connected_papers_token", ""))
MODELSCOPE_TOKEN = os.environ.get("MODELSCOPE_TOKEN", _CFG.get("modelscope_token", ""))
GITEE_TOKEN = os.environ.get("GITEE_TOKEN", _CFG.get("gitee_token", ""))
HF_MIRROR = os.environ.get("HF_MIRROR", _CFG.get("hf_mirror", "https://hf-mirror.com"))

SEMANTIC_SCHOLAR_BASE = "https://api.semanticscholar.org/graph/v1"
ARXIV_BASE = "https://export.arxiv.org/api/query"
GITHUB_BASE = "https://api.github.com"
SERPAPI_BASE = "https://serpapi.com/search"
CODESOTA_BASE = "https://www.codesota.com/api/sota"
HF_BASE = "https://huggingface.co"
HF_PAPERS_BASE = f"{HF_BASE}/api/papers"
MODELSCOPE_BASE = "https://modelscope.cn/openapi/v1"
OPENALEX_BASE = "https://api.openalex.org"
OPENALEX_MAILTO = "sota-research-skill@example.com"
GITEE_BASE = "https://gitee.com/api/v5"
GITLAB_BASE = "https://gitlab.com/api/v4"

HEADERS = {
    "User-Agent": "ResearchWorkflow/1.6.0 (Academic Research Tool)",
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
    # CV 细分方向
    "实例分割": "instance-segmentation",
    "全景分割": "panoptic-segmentation",
    "三维目标检测": "3d-object-detection",
    "3D目标检测": "3d-object-detection",
    "小目标检测": "small-object-detection",
    "多目标跟踪": "multi-object-tracking",
    "目标跟踪": "multi-object-tracking",
    "工业缺陷检测": "industrial-defect-detection",
    "缺陷检测": "industrial-defect-detection",
    "无样本缺陷检测": "anomaly-detection",
    "开放词汇检测": "open-vocabulary-detection",
    "定位式检测": "grounded-detection",
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
    "instance": ["instance-segmentation"],
    "panoptic": ["panoptic-segmentation"],
    "3d": ["3d-object-detection"],
    "tracking": ["multi-object-tracking"],
    "mot": ["multi-object-tracking"],
    "defect": ["industrial-defect-detection", "anomaly-detection"],
    "open-vocabulary": ["open-vocabulary-detection"],
    "grounded": ["grounded-detection", "open-vocabulary-detection"],
    "small-object": ["small-object-detection"],
    "industrial": ["industrial-defect-detection"],
    "yolo": ["object-detection", "small-object-detection"],
    "detr": ["object-detection"],
    "sam": ["instance-segmentation", "panoptic-segmentation", "image-segmentation"],
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
    "instance-segmentation", "panoptic-segmentation", "3d-object-detection",
    "small-object-detection", "multi-object-tracking", "industrial-defect-detection",
    "open-vocabulary-detection", "grounded-detection",
])


# Model family mapping for Discover Mode
_C_MODEL_FAMILY_MAP = {
    "RT-DETR": ["object-detection", "3d-object-detection"],
    "YOLOv3": ["object-detection", "small-object-detection"],
    "YOLOv5": ["object-detection", "small-object-detection", "industrial-defect-detection"],
    "YOLOv7": ["object-detection", "small-object-detection"],
    "YOLOv8": ["object-detection", "instance-segmentation", "keypoint-detection"],
    "YOLOv9": ["object-detection", "small-object-detection"],
    "YOLOv10": ["object-detection"],
    "YOLOv11": ["object-detection", "instance-segmentation", "panoptic-segmentation"],
    "YOLO": ["object-detection", "small-object-detection"],
    "DINO": ["object-detection"],
    "Co-DETR": ["object-detection"],
    "Grounding DINO": ["open-vocabulary-detection", "grounded-detection"],
    "SAM": ["instance-segmentation", "panoptic-segmentation", "image-segmentation"],
    "Segment Anything": ["instance-segmentation", "image-segmentation"],
    "Mask R-CNN": ["instance-segmentation"],
    "DETR": ["object-detection"],
    "Dinomaly": ["anomaly-detection"],
    "EfficientAD": ["anomaly-detection"],
    "PatchCore": ["anomaly-detection"],
    "FastRE": ["anomaly-detection"],
}


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

    # --- 2.5: 模型族匹配 ---
    for model_name, task_ids in _C_MODEL_FAMILY_MAP.items():
        if model_name.lower() in clean_q:
            for tid in task_ids:
                candidates.append({
                    "task_id": tid,
                    "match_type": "模型族",
                    "match_score": 0.85,
                    "reason": f"模型 '{model_name}' 关联到任务 '{tid}'",
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
      1b. OpenAlex API    — 主力并行源 (学术论文搜索)
      1c. SerpApi (GS)    — 补充 (当 1a+1b 结果不足时触发)
    如果已通过 discover() 收敛到精确任务，直接使用该任务 ID。
    """
    log("=" * 60)
    log("STEP 1: SOTA 发现 — CodeSOTA → OpenAlex → Google Scholar")
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
                "benchmark_url": f"https://www.codesota.com/benchmark/{codesota_results.get('benchmark_slug', codesota_results.get('benchmark', search_task).lower().replace(' ', '-'))}",
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
                    "benchmark_url": f"https://www.codesota.com/benchmark/{codesota_results.get('benchmark_slug', search_task)}",
                })
                seen_titles.add(title)
    elif codesota_results and "error" in codesota_results:
        log(f"  [CodeSOTA] Task '{search_task}' not found in registry.")

    # --- 1a-x: CodeSOTA 交叉验证 (OpenAlex 被引数验证) ---
    codesota_papers_for_verification = [p for p in papers if p["source"].startswith("CodeSOTA") and p.get("url")]
    if codesota_papers_for_verification:
        log(f"  [Cross-Validate] Verifying {len(codesota_papers_for_verification)} CodeSOTA results via OpenAlex...")
        for cp in codesota_papers_for_verification[:3]:
            model_name = cp.get("title", "").replace("SOTA: ", "").replace("Runner-up: ", "")
            oa_check = _cross_validate_scores(model_name)
            if oa_check:
                cp["cross_validation"] = oa_check
        log(f"  [Cross-Validate] Verification complete")

    time.sleep(1)

    # --- 1b: OpenAlex Search (主力并行源) ---
    log(f"  [OpenAlex] Searching: {query}")
    oa_results = _search_openalex(query, max_papers=max_papers)
    for r in oa_results:
        title = r.get("title", "")
        if title and title not in seen_titles:
            papers.append(r)
            seen_titles.add(title)
    if oa_results:
        log(f"  [OpenAlex] Found {len(oa_results)} papers")
    else:
        log(f"  [OpenAlex] No additional results")

    time.sleep(1)

    # --- 1c: SerpApi Google Scholar Search (补充，仅在前两者结果不足时触发) ---
    needs_serpapi = (len(papers) < max_papers)
    if needs_serpapi:
        log(f"  [Google Scholar] Searching: {query}")
        gs_url = (
            f"{SERPAPI_BASE}?engine=google_scholar"
            f"&q={urllib.parse.quote(query)}"
            f"&api_key={SERPAPI_KEY}"
            f"&num={max_papers + 2}"
            f"&hl=en"
        )
        gs_data = api_get_json(gs_url)

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
    else:
        log(f"  [Google Scholar] Skipped (sufficient results from CodeSOTA + OpenAlex)")
        gs_results = []

    log(f"  [Step 1] Found {len(papers)} candidate papers\n")
    return papers, gs_results


def _reconstruct_abstract(inverted_index):
    """从 OpenAlex inverted index 重建摘要文本。"""
    if not inverted_index:
        return ""
    try:
        tokens = []
        for pos, word in sorted(inverted_index.items(), key=lambda x: int(x[0])):
            tokens.append(word)
        return " ".join(tokens)
    except Exception:
        return ""


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
            f"{OPENALEX_BASE}/works?mailto={OPENALEX_MAILTO}"
            f"?search={urllib.parse.quote(query)}"
            f"&per_page={max_papers}"
            f"&sort=relevance_score:desc"
            f"&select=id,title,display_name,cited_by_count,publication_year,"
            f"primary_location,authorships,doi,open_access,type,biblio,"
            f"abstract_inverted_index,concepts,referenced_works,related_works"
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
                "openalex_id": w.get("id", ""),
                "abstract_reconstructed": _reconstruct_abstract(w.get("abstract_inverted_index")),
                "concepts": [c.get("display_name", "") for c in (w.get("concepts") or [])[:10]],
            })
    except Exception as e:
        log(f"  [OpenAlex] Error: {e}")

    return results


def _search_openalex_paper_by_title(title, retries=1):
    """通过 OpenAlex 精确搜索获取单篇论文完整元数据。"""
    url = (
        f"{OPENALEX_BASE}/works?mailto={OPENALEX_MAILTO}"
        f"&search={urllib.parse.quote(title)}"
        f"&per_page=1"
        f"&select=id,title,abstract_inverted_index,cited_by_count,publication_year,"
        f"concepts,referenced_works,related_works,primary_location,authorships,doi,"
        f"open_access,biblio,type"
    )
    raw = api_get(url, timeout=15, retries=retries)
    if not raw:
        return None
    data = json.loads(raw)
    results = data.get("results", [])
    return results[0] if results else None


def _cross_validate_scores(model_name):
    """通过 OpenAlex 交叉验证 CodeSOTA 排行分数。
    搜索同名论文，获取被引数、年份等元数据，供人工判断数据新鲜度。"""
    try:
        url = (
            f"{OPENALEX_BASE}/works?mailto={OPENALEX_MAILTO}"
            f"?search={urllib.parse.quote(model_name)}"
            f"&per_page=3"
            f"&sort=cited_by_count:desc"
            f"&select=id,title,cited_by_count,publication_year,primary_location,doi"
        )
        raw = api_get(url, timeout=10, retries=1)
        if not raw:
            return None
        data = json.loads(raw)
        matches = []
        for w in data.get("results", []):
            matches.append({
                "title": w.get("title", "")[:80],
                "cited_by": w.get("cited_by_count", 0),
                "year": w.get("publication_year"),
                "doi": w.get("doi", ""),
            })
        if matches:
            return {"source": "OpenAlex", "matches": matches}
    except Exception as e:
        log(f"  [Cross-Validate] Error: {e}")
    return None


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
    log("STEP 2: 论文深度分析 — OpenAlex (主力) + Semantic Scholar (补充)")
    log("=" * 60)

    analyses = []
    analyzed_titles = set()
    paper_id_map = {}  # title -> {"openalex_id": ..., "ss_paperId": ..., "arxiv_id": ...}

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

        analysis = {}

        # --- Primary: OpenAlex title search ---
        oa_work = _search_openalex_paper_by_title(clean_title)
        if oa_work:
            oa_id = oa_work.get("id", "")
            analysis["openalex_id"] = oa_id
            analysis["openalex_abstract"] = _reconstruct_abstract(oa_work.get("abstract_inverted_index"))
            analysis["openalex_concepts"] = [c.get("display_name", "") for c in (oa_work.get("concepts") or [])[:10]]
            analysis["citation_count"] = oa_work.get("cited_by_count", 0)
            analysis["year"] = oa_work.get("publication_year")
            analysis["doi"] = (oa_work.get("doi") or "").replace("https://doi.org/", "")

            oa_authorships = oa_work.get("authorships") or []
            analysis["authors"] = [a["author"]["display_name"] for a in oa_authorships[:5] if a.get("author", {}).get("display_name")]

            oa_loc = oa_work.get("primary_location") or {}
            analysis["venue"] = (oa_loc.get("source") or {}).get("display_name", "")

            oa_oa = oa_work.get("open_access") or {}
            analysis["open_access_pdf"] = oa_oa.get("oa_url", "")

            # Extract arxiv_id from DOI or biblio
            arxiv_id = ""
            doi = oa_work.get("doi", "") or ""
            biblio = oa_work.get("biblio") or {}
            if "arxiv" in doi.lower():
                arxiv_id = doi.split("arxiv.org/abs/")[-1] if "arxiv.org/abs/" in doi else ""
            analysis["arxiv_id"] = arxiv_id

            # Update paper_id_map
            paper_id_map[clean_title] = {
                "openalex_id": oa_id,
                "arxiv_id": arxiv_id,
                "doi": analysis["doi"],
            }

            log(f"    [OpenAlex] Citations: {analysis['citation_count']} | Year: {analysis.get('year', 'N/A')}")
            time.sleep(1)

        # --- Supplementary: Semantic Scholar for TLDR + influential citations ---
        search_url = (
            f"{SEMANTIC_SCHOLAR_BASE}/paper/search"
            f"?query={urllib.parse.quote(clean_title)}"
            f"&limit=1"
            f"&fields=title,year,citationCount,externalIds,tldr,abstract,authors,venue,openAccessPdf,influentialCitationCount"
        )
        if SEMANTIC_SCHOLAR_API_KEY:
            search_url += f"&api_key={SEMANTIC_SCHOLAR_API_KEY}"

        data = api_get_json(search_url)
        if data and data.get("data"):
            ss_paper = data["data"][0]
            ss_paper_id = ss_paper.get("paperId")
            analysis["ss_title"] = ss_paper.get("title", "")
            analysis["tldr"] = ss_paper.get("tldr", {}).get("text", "N/A") if ss_paper.get("tldr") else "N/A"
            analysis["influential_citations"] = ss_paper.get("influentialCitationCount", 0)

            # Use SS abstract only if OpenAlex didn't provide one
            if not analysis.get("openalex_abstract"):
                analysis["abstract"] = (ss_paper.get("abstract") or "")[:500]
            else:
                analysis["abstract"] = analysis["openalex_abstract"][:500]

            # Fill missing fields from SS
            if not analysis.get("citation_count"):
                analysis["citation_count"] = ss_paper.get("citationCount", 0)
            if not analysis.get("year"):
                analysis["year"] = ss_paper.get("year")
            if not analysis.get("venue"):
                analysis["venue"] = ss_paper.get("venue", "")
            if not analysis.get("authors"):
                analysis["authors"] = [a.get("name", "") for a in ss_paper.get("authors", [])[:5]]
            if not analysis.get("arxiv_id"):
                analysis["arxiv_id"] = ss_paper.get("externalIds", {}).get("ArXiv", "")
            if not analysis.get("doi"):
                analysis["doi"] = ss_paper.get("externalIds", {}).get("DOI", "")
            if not analysis.get("open_access_pdf"):
                analysis["open_access_pdf"] = ss_paper.get("openAccessPdf", {}).get("url", "")

            # Update paper_id_map with SS paperId
            if clean_title not in paper_id_map:
                paper_id_map[clean_title] = {}
            paper_id_map[clean_title]["ss_paperId"] = ss_paper_id

            # Get references from SS
            if ss_paper_id:
                ref_url = (
                    f"{SEMANTIC_SCHOLAR_BASE}/paper/{ss_paper_id}/references"
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

            log(f"    [SS] TLDR available | Influential: {analysis.get('influential_citations', 0)}")
            time.sleep(3)
        else:
            log(f"    Not found on Semantic Scholar")
            analysis["ss_title"] = clean_title
            analysis["tldr"] = "N/A"
            analysis["influential_citations"] = 0
            if not analysis.get("abstract"):
                analysis["abstract"] = ""
            time.sleep(3)

        analysis["ss_analysis"] = analysis
        analyses.append({**paper, "ss_analysis": analysis})

        if len(analyses) >= max_papers:
            break

    log(f"  [Step 2] Analyzed {len(analyses)} papers\n")
    return analyses, paper_id_map


def _traverse_openalex_citations(openalex_id, max_results=15):
    """通过 OpenAlex 双向引用遍历获取同族工作。"""
    results = []
    seen_ids = set()
    seen_ids.add(openalex_id)
    
    # 反向引用（谁引用了这篇论文）
    try:
        url = (
            f"{OPENALEX_BASE}/works?mailto={OPENALEX_MAILTO}"
            f"&filter=cites:{openalex_id}"
            f"&sort=cited_by_count:desc"
            f"&per_page=20"
            f"&select=id,title,cited_by_count,publication_year,primary_location,doi,authorships"
        )
        raw = api_get(url, timeout=15, retries=1)
        if raw:
            data = json.loads(raw)
            for w in data.get("results", []):
                wid = w.get("id", "")
                title = w.get("title", "")
                if wid and wid not in seen_ids and title:
                    seen_ids.add(wid)
                    doi = w.get("doi", "") or ""
                    authorships = w.get("authorships") or []
                    authors = [a["author"]["display_name"] for a in authorships[:3] if a.get("author", {}).get("display_name")]
                    venue = (w.get("primary_location") or {}).get("source", {}).get("display_name", "")
                    results.append({
                        "source": "OpenAlex Cited By",
                        "title": title,
                        "url": f"https://doi.org/{doi.replace('https://doi.org/', '')}" if doi else f"https://openalex.org/works/{wid.split('/')[-1]}",
                        "cited_by": w.get("cited_by_count", 0),
                        "year": w.get("publication_year"),
                        "authors": ", ".join(authors) + (" et al." if len(authors) >= 3 else ""),
                        "venue": venue,
                    })
    except Exception as e:
        log(f"  [OpenAlex] Citation traversal error: {e}")
    
    # 正向引用（这篇论文引用了哪些）
    try:
        fwd_url = (
            f"{OPENALEX_BASE}/works/{openalex_id.split('/')[-1]}"
            f"?select=referenced_works"
        )
        raw = api_get(fwd_url, timeout=10, retries=1)
        if raw:
            work = json.loads(raw)
            ref_ids = work.get("referenced_works", [])[:25]
            if ref_ids:
                # 批量查询 (OpenAlex filter | up to 50)
                filter_ids = "|".join(ref_ids[:50])
                batch_url = (
                    f"{OPENALEX_BASE}/works?mailto={OPENALEX_MAILTO}"
                    f"&filter=openalex:{filter_ids}"
                    f"&per_page=25"
                    f"&select=id,title,cited_by_count,publication_year,doi"
                )
                raw2 = api_get(batch_url, timeout=15, retries=1)
                if raw2:
                    data2 = json.loads(raw2)
                    for w in data2.get("results", []):
                        wid = w.get("id", "")
                        title = w.get("title", "")
                        if wid and wid not in seen_ids and title:
                            seen_ids.add(wid)
                            doi = w.get("doi", "") or ""
                            results.append({
                                "source": "OpenAlex References",
                                "title": title,
                                "url": f"https://doi.org/{doi.replace('https://doi.org/', '')}" if doi else f"https://openalex.org/works/{wid.split('/')[-1]}",
                                "cited_by": w.get("cited_by_count", 0),
                                "year": w.get("publication_year"),
                            })
    except Exception as e:
        log(f"  [OpenAlex] Reference traversal error: {e}")
    
    return results[:max_results]


# =============================================================================
# Step 3: Related Work Expansion
# =============================================================================

def step3_related_work(analyses, max_related=10, paper_id_map=None):
    log("=" * 60)
    log("STEP 3: 同族工作扩展 — OpenAlex 双向引用 (主力) + GS + SS (补充)")
    log("=" * 60)

    all_related = []
    seen_titles = set()

    paper_id_map = paper_id_map or {}

    for paper in analyses[:2]:
        ss = paper.get("ss_analysis") or {}
        title = ss.get("ss_title") or paper.get("title", "")
        if not title or title.startswith("SOTA:") or title.startswith("Runner-up:"):
            continue

        # Clean title for lookup
        if title.startswith("SOTA: "):
            clean_title = title.replace("SOTA: ", "")
        elif title.startswith("Runner-up: "):
            clean_title = title.replace("Runner-up: ", "")
        else:
            clean_title = title

        # --- Primary: OpenAlex bidirectional citation traversal ---
        oa_id = None
        if paper_id_map:
            for k, v in paper_id_map.items():
                if k.lower() == clean_title.lower() or k.lower() == title.lower():
                    oa_id = v.get("openalex_id")
                    break

        if oa_id:
            log(f"  [OpenAlex] Citation traversal for: {clean_title[:60]}")
            oa_related = _traverse_openalex_citations(oa_id, max_results=max_related)
            for r in oa_related:
                t = r.get("title", "")
                if t and t not in seen_titles:
                    seen_titles.add(t)
                    r["seed_paper"] = title[:50]
                    all_related.append(r)
            log(f"    [OpenAlex] Found {len(oa_related)} related works via citations")
            time.sleep(1)

        # --- Supplementary: Google Scholar related ---
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
            log(f"    Found {len(related_data['organic_results'])} related papers from GS")

        time.sleep(2)

        # --- Supplementary: Semantic Scholar recommendations (only if no paper_id_map) ---
        ss_paper_id = None
        if paper_id_map:
            for k, v in paper_id_map.items():
                if k.lower() == clean_title.lower() or k.lower() == title.lower():
                    ss_paper_id = v.get("ss_paperId")
                    break

        if ss_paper_id:
            rec_url = (
                f"{SEMANTIC_SCHOLAR_BASE}/paper/{ss_paper_id}/recommendations"
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
                        except Exception:
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


def _fetch_hf_readme(model_id):
    """获取 Hugging Face 模型 README 内容。"""
    try:
        readme_url = f"{HF_BASE}/raw/{model_id}/README.md"
        raw = api_get(readme_url, timeout=10, retries=0)
        if raw:
            return raw[:3000]  # Limit to first 3000 chars
    except Exception:
        pass
    return ""


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

        # Fallback to HF_MIRROR if huggingface.co fails (SSL issues, etc.)
        if not hf_data:
            try:
                mirror_url = (
                    f"{HF_MIRROR}/api/models"
                    f"?search={urllib.parse.quote(keywords)}"
                    f"&sort=downloads"
                    f"&direction=-1"
                    f"&limit={max_per_query}"
                    f"&full=false"
                )
                log(f"    [Hugging Face] Retrying via HF_MIRROR: {mirror_url[:80]}")
                hf_data = api_get_json(mirror_url)
                if hf_data:
                    log(f"    [Hugging Face] HF_MIRROR succeeded")
            except Exception as e:
                log(f"    [Hugging Face] HF_MIRROR fallback error: {e}")

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
                        "hf_tags": tags,
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
    except Exception:
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
        except json.JSONDecodeError as e:
            log(f"  [ModelScope] JSON decode error: {e}")
            continue
        except Exception as e:
            log(f"  [ModelScope] Error fetching: {e}")
            continue

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

        time.sleep(2)
        if len(models) >= max_total:
            break

    models.sort(key=lambda x: x.get("score", 0), reverse=True)
    return models[:max_total]


def _search_gitee(search_queries, max_per_query=5, max_total=5):
    """Gitee (码云) 仓库搜索 - 中文开源社区补充。
    需要配置 gitee_token (api_config.json 或 GITEE_TOKEN 环境变量)。"""
    results = []
    gitee_token = GITEE_TOKEN
    if not gitee_token:
        log("  [Gitee] Skipped (no gitee_token configured)")
        return results
    seen = set()
    for q in search_queries:
        if len(results) >= max_total:
            break
        url = (f"{GITEE_BASE}/search/repositories"
               f"?access_token={gitee_token}"
               f"&q={urllib.parse.quote(q)}"
               f"&order=star_count&sort=desc&per_page={max_per_query}")
        try:
            raw = api_get(url, timeout=15, retries=1)
            if not raw:
                continue
            try:
                data = json.loads(raw)
            except json.JSONDecodeError:
                continue
            if isinstance(data, dict) and "items" in data:
                items = data["items"]
            elif isinstance(data, list):
                items = data
            else:
                continue
            for item in items:
                full_name = item.get("full_name") or item.get("path") or ""
                if full_name in seen:
                    continue
                seen.add(full_name)
                results.append({
                    "platform": "Gitee",
                    "name": full_name,
                    "url": item.get("html_url") or f"https://gitee.com/{full_name}",
                    "description": (item.get("description") or "")[:200],
                    "stars": item.get("stargazers_count") or item.get("star_count") or 0,
                    "forks": item.get("forks_count") or 0,
                    "language": item.get("language") or "",
                    "license": (item.get("license", {}) or {}).get("spdx_id") if isinstance(item.get("license"), dict) else (item.get("license") or ""),
                    "updated": item.get("updated_at") or "",
                    "topics": [],
                    "open_issues": item.get("open_issues_count") or 0,
                })
                if len(results) >= max_total:
                    break
        except Exception as e:
            log(f"  [Gitee] Error: {e}")
        time.sleep(1)
    return results


def _search_gitlab(search_queries, max_per_query=5, max_total=5):
    """GitLab 公开项目搜索 - 国际开源社区补充"""
    results = []
    seen = set()
    for q in search_queries:
        if len(results) >= max_total:
            break
        url = f"{GITLAB_BASE}/projects?search={urllib.parse.quote(q)}&per_page={max_per_query}"
        try:
            raw = api_get(url, timeout=15, retries=1)
            if not raw:
                continue
            try:
                data = json.loads(raw)
            except json.JSONDecodeError:
                continue
            if not isinstance(data, list):
                continue
            for item in data:
                iid = item.get("id")
                if iid in seen:
                    continue
                seen.add(iid)
                results.append({
                    "platform": "GitLab",
                    "name": item.get("path_with_namespace") or "",
                    "url": item.get("web_url") or "",
                    "description": (item.get("description") or "")[:200],
                    "stars": item.get("star_count") or 0,
                    "forks": item.get("forks_count") or 0,
                    "language": item.get("repository_language") or "",
                    "license": (item.get("license", {}) or {}).get("name") if isinstance(item.get("license"), dict) else (item.get("license") or ""),
                    "updated": item.get("last_activity_at") or "",
                    "topics": item.get("topics") or [],
                    "open_issues": item.get("open_issues_count") or 0,
                })
                if len(results) >= max_total:
                    break
        except Exception as e:
            log(f"  [GitLab] Error: {e}")
        time.sleep(1)
    return results


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

        # Engineering Readiness (expanded from 10 to 25 points)
        # Sub-dimension 1: Pipeline/Task match (3 pts)
        readiness_pipeline = 3 if pipeline and pipeline not in ("N/A", "") else 0

        # Sub-dimension 2: Model efficiency (5 pts)
        tags = impl.get("hf_tags", []) or impl.get("topics", [])
        readme_snippet = impl.get("hf_readme", "") or ""
        has_flops_info = any(kw in readme_snippet.lower() for kw in ["flops", "params", "gflops", "parameters"])
        has_fps_info = any(kw in readme_snippet.lower() for kw in ["fps", "frames per second", "inference speed", "latency"])
        if has_flops_info and has_fps_info:
            efficiency_score = 5
        elif has_flops_info or has_fps_info:
            efficiency_score = 3
        else:
            efficiency_score = 1

        # Sub-dimension 3: Pretrained weights availability (5 pts)
        has_pytorch = any(t in tags for t in ["pytorch", "safetensors"])
        has_coco = any(kw in readme_snippet.lower() for kw in ["coco", "voc", "imagenet", "pretrained", "pre-trained"])
        if has_pytorch and has_coco:
            weights_score = 5
        elif has_pytorch or has_coco:
            weights_score = 3
        else:
            weights_score = 1

        # Sub-dimension 4: Fine-tuning support (4 pts)
        has_finetune = any(kw in readme_snippet.lower() for kw in ["finetune", "fine-tune", "fine_tune", "training script", "train.py", "custom dataset"])
        has_config = any(kw in readme_snippet.lower() for kw in ["config.yaml", "config.yml", "hyperparameters", "hyp.scratch"])
        if has_finetune and has_config:
            finetune_score = 4
        elif has_finetune or has_config:
            finetune_score = 2
        else:
            finetune_score = 0

        # Sub-dimension 5: Deployment support (4 pts)
        deploy_tags = {"onnx", "tensorrt", "ncnn", "openvino", "tflite", "coreml", "rknn"}
        deploy_count = sum(1 for t in tags if any(dt in str(t).lower() for dt in deploy_tags))
        if deploy_count >= 2:
            deploy_score = 4
        elif deploy_count == 1:
            deploy_score = 2
        else:
            has_deploy_readme = any(kw in readme_snippet.lower() for kw in ["onnx", "tensorrt", "ncnn", "deployment", "export"])
            deploy_score = 1 if has_deploy_readme else 0

        # Sub-dimension 6: Environment setup (4 pts)
        has_docker = any(kw in readme_snippet.lower() for kw in ["docker", "dockerfile", "docker-compose"])
        has_requirements = any(kw in readme_snippet.lower() for kw in ["requirements.txt", "pip install", "setup.py", "environment.yml", "conda"])
        if has_docker and has_requirements:
            env_score = 4
        elif has_docker or has_requirements:
            env_score = 2
        else:
            env_score = 0

        readiness = readiness_pipeline + efficiency_score + weights_score + finetune_score + deploy_score + env_score

        total_score = community + quality + maintenance + relevance + readiness

        impl["sota_scores"] = scores
        impl["sota_total"] = total_score
        impl["sota_breakdown"] = {
            "community_activity": (community, 25),
            "code_quality": (quality, 20),
            "maintenance": (maintenance, 15),
            "relevance": (relevance, 15),
            "engineering_readiness": (readiness, 25),
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
            f"| 社区:{s['sota_breakdown']['community_activity'][0]}/25 "
            f"| 质量:{s['sota_breakdown']['code_quality'][0]}/20 "
            f"| 维护:{s['sota_breakdown']['maintenance'][0]}/15 "
            f"| 相关:{s['sota_breakdown']['relevance'][0]}/15 "
            f"| 就绪:{s['sota_breakdown']['engineering_readiness'][0]}/25")

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
    gitee_repos = _search_gitee(search_queries, max_total=5)
    gitlab_projects = _search_gitlab(search_queries, max_total=5)

    all_results = github_repos + hf_models + hf_arxiv_models + ms_models + gitee_repos + gitlab_projects

    # Fetch README for top HF candidates (for engineering readiness scoring)
    for impl in all_results[:5]:
        if impl.get("platform", "").startswith("Hugging Face") and impl.get("url"):
            model_id = impl.get("name", "")
            if model_id:
                readme = _fetch_hf_readme(model_id)
                if readme:
                    impl["hf_readme"] = readme

    all_results = _score_and_rank_implementations(all_results, query)

    total_github = sum(1 for r in all_results if r.get("platform") == "GitHub")
    total_hf = sum(1 for r in all_results if r.get("platform", "").startswith("Hugging Face"))
    total_ms = sum(1 for r in all_results if r.get("platform") == "ModelScope")
    total_gitee = sum(1 for r in all_results if r.get("platform") == "Gitee")
    total_gitlab = sum(1 for r in all_results if r.get("platform") == "GitLab")

    log(f"  [Step 4] GitHub: {total_github} repos | Hugging Face: {total_hf} models | ModelScope: {total_ms} models | Gitee: {total_gitee} | GitLab: {total_gitlab}")
    log(f"  [Step 4] Total: {len(all_results)} implementations (scored & ranked)\n")
    return all_results


# =============================================================================
# Step 5: Latest Preprints Tracking
# =============================================================================

def _fetch_hf_daily_papers(query=None, days=7, max_papers=10):
    """从 Hugging Face Daily Papers 获取前沿论文。"""
    results = []
    try:
        url = f"{HF_PAPERS_BASE}?limit={max_papers}"
        raw = api_get(url, timeout=15, retries=1)
        if not raw:
            return results
        data = json.loads(raw)
        for paper in data if isinstance(data, list) else data.get("papers", data.get("data", [])):
            title = paper.get("title", "")
            arxiv_id = paper.get("arxiv_id", "") or paper.get("id", "")
            if not title:
                continue
            if query:
                q_lower = query.lower()
                title_lower = title.lower()
                if q_lower not in title_lower:
                    continue
            results.append({
                "source": "HF Daily Papers",
                "title": title,
                "url": f"https://huggingface.co/papers/{arxiv_id}" if arxiv_id else paper.get("url", ""),
                "arxiv_id": arxiv_id,
                "upvotes": paper.get("upvotes", 0),
                "comments": paper.get("comments", 0),
                "published_at": paper.get("published_at", paper.get("date", "")),
                "summary": (paper.get("summary", "") or "")[:300],
            })
    except Exception as e:
        log(f"  [HF Papers] Error: {e}")
    return results


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
            if "/abs/" in href:
                arxiv_id = href.split("/abs/")[-1]
            if "/pdf/" in href:
                pdf_url = href
                if not arxiv_id:
                    arxiv_id = pdf_url.split("/pdf/")[-1]

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

    # --- 5b: OpenAlex 交叉验证 arXiv 预印本 ---
    if preprints:
        log(f"  [arXiv + OpenAlex] Cross-validating {len(preprints)} preprints...")
        oa_titles = set()
        try:
            date_threshold = datetime.now() - timedelta(days=months * 30)
            oa_url = (
                f"{OPENALEX_BASE}/works?mailto={OPENALEX_MAILTO}"
                f"?search={urllib.parse.quote(query)}"
                f"&filter=from_publication_date:{date_threshold.strftime('%Y-%m-%d')},type:preprint"
                f"&per_page={max_papers}"
                f"&sort=relevance_score:desc"
                f"&select=id,title,cited_by_count,publication_year,primary_location_source_display_name"
            )
            oa_raw = api_get(oa_url, timeout=15, retries=1)
            if oa_raw:
                oa_data = json.loads(oa_raw)
                for w in oa_data.get("results", []):
                    oa_titles.add(w.get("title", ""))
                # 标记 arXiv 论文是否在 OpenAlex 也有记录
                for p in preprints:
                    p["oa_verified"] = any(
                        _similarity(p.get("title", "").lower(), t.lower()) > 0.7
                        for t in oa_titles
                    )
                verified = sum(1 for p in preprints if p.get("oa_verified"))
                log(f"  [arXiv + OpenAlex] {verified}/{len(preprints)} preprints verified in OpenAlex")
        except Exception as e:
            log(f"  [arXiv + OpenAlex] Cross-validation error: {e}")

    log(f"  [Step 5] Found {len(preprints)} recent preprints\n")

    # --- 5c: HF Daily Papers ---
    hf_papers = _fetch_hf_daily_papers(query=query, max_papers=max_papers)
    if hf_papers:
        log(f"  [HF Daily Papers] Found {len(hf_papers)} papers")
        seen_arxiv_ids = set()
        for p in preprints:
            aid = p.get("arxiv_id", "")
            if aid:
                seen_arxiv_ids.add(aid.lower())
        for hf in hf_papers:
            aid = hf.get("arxiv_id", "")
            if aid and aid.lower() in seen_arxiv_ids:
                continue
            preprints.append({
                "title": hf.get("title", ""),
                "abstract": hf.get("summary", ""),
                "published": (hf.get("published_at", "") or "")[:10],
                "authors": [],
                "categories": [],
                "arxiv_id": aid,
                "pdf_url": "",
                "url": hf.get("url", ""),
                "source": "HF Daily Papers",
                "upvotes": hf.get("upvotes", 0),
            })
            seen_arxiv_ids.add(aid.lower())

    log(f"  [Step 5] Total: {len(preprints)} preprints (including HF Daily Papers)\n")
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
    lines.append(f"**Workflow:** SOTA Discovery → Paper Analysis → Related Work → Code Search + Scoring → Preprint Tracking + HF Papers")
    lines.append("\n---\n")

    # Step 1
    lines.append("## Step 1: SOTA 发现\n")
    if papers:
        lines.append("| # | Title | Source | Cited | Link | Benchmark |")
        lines.append("|---|-------|--------|-------|------|-----------|")
        for i, p in enumerate(papers, 1):
            title = p.get("title", "N/A")[:70]
            url = p.get("url", "")
            cited = p.get("cited_by", p.get("score", ""))
            source = p.get("source", "N/A")
            link = f"[Link]({url})" if url else "N/A"
            benchmark_url = p.get("benchmark_url", "")
            benchmark = f"[Benchmark]({benchmark_url})" if benchmark_url else ""
            lines.append(f"| {i} | {title} | {source} | {cited} | {link} | {benchmark} |")
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
            c = f"{bd.get('community_activity', (0,25))[0]}/{bd.get('community_activity', (0,25))[1]}"
            q = f"{bd.get('code_quality', (0,20))[0]}/{bd.get('code_quality', (0,20))[1]}"
            m = f"{bd.get('maintenance', (0,15))[0]}/{bd.get('maintenance', (0,15))[1]}"
            rel = f"{bd.get('relevance', (0,15))[0]}/{bd.get('relevance', (0,15))[1]}"
            eng = f"{bd.get('engineering_readiness', (0,25))[0]}/{bd.get('engineering_readiness', (0,25))[1]}"
            link = f"[{name[:45]}]({url})" if url else name[:45]
            lines.append(f"| {i} | **{level}** | {link} | {plat} | **{total}** | {c} | {q} | {m} | {rel} | {eng} |")
        lines.append("")

        lines.append("**评级标准：** A+ (>=80) | A (>=65) | B+ (>=50) | B (>=35) | C (>=20) | D (<20)  ")
        lines.append("**评分维度：** 社区活跃度 (25) + 代码质量 (20) + 维护状态 (15) + 相关性 (15) + 工程就绪度 (25) = 满分 100  ")
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
        # Separate HF Daily Papers from arXiv preprints
        arxiv_preprints = [p for p in preprints if p.get("source") != "HF Daily Papers"]
        hf_preprints = [p for p in preprints if p.get("source") == "HF Daily Papers"]

        lines.append("| # | Title | Date | Authors | Categories |")
        lines.append("|---|-------|------|---------|------------|")
        for i, p in enumerate(arxiv_preprints, 1):
            title = p.get("title", "N/A")[:60]
            url = p.get("url", "")
            date = p.get("published", "")[:10]
            authors = p.get("authors", [])
            author_str = ", ".join(authors[:3]) + (" et al." if len(authors) > 3 else "")
            cats = ", ".join(p.get("categories", []))
            if url:
                title = f"[{title}]({url})"
            lines.append(f"| {i} | {title} | {date} | {author_str} | {cats} |")

        if hf_preprints:
            lines.append("")
            lines.append("### Hugging Face Daily Papers\n")
            lines.append("| # | Title | Upvotes | Date |")
            lines.append("|---|-------|---------|------|")
            for i, p in enumerate(hf_preprints, 1):
                title = p.get("title", "N/A")[:60]
                url = p.get("url", "")
                upvotes = p.get("upvotes", 0)
                date = p.get("published", "")[:10]
                if url:
                    title = f"[{title}]({url})"
                lines.append(f"| {i} | {title} | {upvotes} | {date} |")
    else:
        lines.append("No recent preprints found.")
    lines.append("")

    lines.append("---\n")
    lines.append(f"*Report generated by Research Workflow v1.6.0 | {now}*")
    lines.append(f"*APIs used: CodeSOTA, SerpApi (Google Scholar), OpenAlex, Semantic Scholar, GitHub, Hugging Face, ModelScope, Gitee, GitLab, arXiv*")

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
    print("║          Research Workflow v1.6.0 — 学术论文与代码复现          ║")
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
    analyses, paper_id_map = step2_paper_analysis(papers, max_papers=max_papers)
    related = step3_related_work(analyses, max_related=max_papers * 3, paper_id_map=paper_id_map)
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
        description="Research Workflow v1.6.0: 引导式收敛学术论文与代码复现工作流",
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
