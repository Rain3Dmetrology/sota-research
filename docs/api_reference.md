# API Reference

> Complete documentation of all API endpoints used in the SOTA Research Workflow.

## 1. CodeSOTA API

**Base URL:** `https://www.codesota.com/api/sota`
**Auth:** None required
**Rate Limit:** None (5-minute cache)

### Endpoints

```bash
# List all tasks with scored runs
curl https://www.codesota.com/api/sota

# Get SOTA for a specific task (short alias)
curl https://www.codesota.com/api/sota/ocr?tier=sota

# Get SOTA using full task ID
curl https://www.codesota.com/api/sota/document-ocr?tier=sota
```

### Task Aliases

| Short | Full ID |
|-------|---------|
| ocr | document-ocr |
| code | code-generation |
| asr | speech-recognition |
| stt | speech-recognition |
| tts | text-to-speech |
| vqa | visual-question-answering |
| caption | image-captioning |
| t2i | text-to-image |
| t2v | text-to-video |

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| task | string | Short alias |
| task_full_id | string | Full DB id |
| pick | object | SOTA model entry |
| pick.model_name | string | Model name |
| pick.score | number | Score |
| pick.score_metric | string | Metric name |
| runners_up | array | Top 3 alternatives |

---

## 2. SerpApi (Google Scholar)

**Base URL:** `https://serpapi.com/search`
**Auth:** API Key (query parameter `api_key`)
**Free Tier:** 100 searches/month

### Search

```bash
curl "https://serpapi.com/search?engine=google_scholar&q=vision+transformer&api_key=YOUR_KEY&num=5&hl=en"
```

### Related Articles

```bash
curl "https://serpapi.com/search?engine=google_scholar&q=related:Paper+Title&api_key=YOUR_KEY&num=10"
```

### Key Response Fields

| Field | Path |
|-------|------|
| Title | `organic_results[].title` |
| Link | `organic_results[].link` |
| Cited By | `organic_results[].inline_links.cited_by.total` |
| Publication Info | `organic_results[].publication_info.summary` |
| Related Searches | `related_searches[]` |

---

## 3. Semantic Scholar API

**Base URL:** `https://api.semanticscholar.org/graph/v1`
**Auth:** API Key (optional, header `x-api-key`)
**Rate Limit:** 100 req/5min (no key), 100 req/min (with key)

### Search Paper

```bash
curl "https://api.semanticscholar.org/graph/v1/paper/search?query=vision+transformer&limit=5&fields=title,year,citationCount,externalIds,tldr,abstract,authors,venue,openAccessPdf,influentialCitationCount"
```

### Get References

```bash
curl "https://api.semanticscholar.org/graph/v1/paper/{paperId}/references?fields=title,year,citationCount,externalIds&limit=10"
```

### Get Recommendations

```bash
curl "https://api.semanticscholar.org/graph/v1/paper/{paperId}/recommendations?fields=title,year,citationCount,externalIds,venue&limit=5"
```

### Key Fields

| Field | Description |
|-------|-------------|
| paperId | Unique identifier (SHA hash) |
| tldr.text | Auto-generated summary |
| citationCount | Total citations |
| influentialCitationCount | High-impact citations |
| externalIds.ArXiv | arXiv ID |
| externalIds.DOI | DOI |
| openAccessPdf.url | Free PDF link |

---

## 4. GitHub REST API

**Base URL:** `https://api.github.com`
**Auth:** Token (header `Authorization: token ghp_...`)
**Rate Limit:** 60 req/hr (no token), 5000 req/hr (with token)

### Search Repositories

```bash
curl -H "Authorization: token YOUR_TOKEN" \
  "https://api.github.com/search/repositories?q=vision+transformer+language:python&sort=stars&order=desc&per_page=5"
```

### Key Response Fields

| Field | Path |
|-------|------|
| Full Name | `items[].full_name` |
| Stars | `items[].stargazers_count` |
| Forks | `items[].forks_count` |
| Language | `items[].language` |
| License | `items[].license.spdx_id` |
| Updated At | `items[].updated_at` |
| Open Issues | `items[].open_issues_count` |
| Topics | `items[].topics[]` |
| HTML URL | `items[].html_url` |

---

## 5. Hugging Face Hub API

**Base URL:** `https://huggingface.co/api`
**Auth:** None required (optional token for private models)
**Rate Limit:** No hard limit

### Search Models

```bash
curl "https://huggingface.co/api/models?search=vision+transformer&sort=downloads&direction=-1&limit=5&full=false"
```

### Get Models by arXiv Paper

```bash
curl "https://huggingface.co/api/arxiv/{arxiv_id}/repos"
```

### Get Daily Papers

```bash
curl "https://huggingface.co/api/daily_papers"
```

### Key Response Fields

| Field | Path |
|-------|------|
| Model ID | `[].id` |
| Downloads | `[].downloads` |
| Likes | `[].likes` |
| Pipeline Tag | `[].pipeline_tag` |
| Library | `[].library_name` |
| Tags | `[].tags[]` |

---

## 6. ModelScope OpenAPI

**Base URL:** `https://modelscope.cn/openapi/v1`
**Auth:** Bearer Token (header `Authorization: Bearer ms-...`)
**Rate Limit:** Free with account

### Search Models

```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "https://modelscope.cn/openapi/v1/models?search=vision+transformer&limit=10"
```

### Key Response Fields

| Field | Path |
|-------|------|
| Success | `success` |
| Models | `data.models[]` |
| Model ID | `data.models[].id` |
| Downloads | `data.models[].downloads` |
| Likes | `data.models[].likes` |
| Tasks | `data.models[].tasks[]` |
| Tags | `data.models[].tags[]` |
| License | `data.models[].license` |
| Total Count | `data.total_count` |

---

## 7. arXiv API

**Base URL:** `http://export.arxiv.org/api/query`
**Auth:** None required
**Rate Limit:** No hard limit (3-second interval recommended)

### Search

```bash
curl "http://export.arxiv.org/api/query?search_query=cat:cs.CV+AND+all:vision+transformer&start=0&max_results=10&sortBy=submittedDate&sortOrder=descending"
```

### Response Format

XML (Atom feed). Key elements:

| Element | XPath |
|---------|-------|
| Title | `entry/title` |
| Summary | `entry/summary` |
| Published | `entry/published` |
| Updated | `entry/updated` |
| Authors | `entry/author/name` |
| Categories | `entry/category@term` |
| PDF Link | `entry/link[@type='application/pdf']@href` |

---

## 8. Connected Papers API (Optional)

**Python Package:** `connectedpapers-py` (pip install)
**Auth:** Early-access token (email hello@connectedpapers.com)
**Rate Limit:** 5 builds per minute, 500 total

### Usage

```python
from connectedpapers import ConnectedPapersClient

client = ConnectedPapersClient(access_token="YOUR_TOKEN")
graph = client.get_graph_sync("PAPER_SHA_ID")
remaining = client.get_remaining_usages_sync()
```

### Test Token

Use `TEST_TOKEN` to access only the DeepFruits paper (ID: `9397e7acd062245d37350f5c05faf56e9cfae0d6`).

---

## 9. OpenAlex API (v1.3+)

**Base URL:** `https://api.openalex.org`
**Auth:** None required (polite pool: add `mailto=` param for higher rate limit)
**Rate Limit:** 10 req/s recommended, 100,000/day (polite pool)

### Search Works (Papers)

```bash
curl "https://api.openalex.org/works?search=vision+transformer&per_page=10&sort=relevance_score:desc"
```

### Filter by Preprints

```bash
curl "https://api.openalex.org/works?search=anomaly+detection&filter=type:preprint&per_page=5"
```

### Get Citation Data

```bash
curl "https://api.openalex.org/works?filter=doi:10.1109/CVPR52729.2023.01954&select=id,title,cited_by_count,publication_year"
```

### Key Response Fields

| Field | Path |
|-------|------|
| Title | `results[].title` |
| Citation Count | `results[].cited_by_count` |
| Publication Year | `results[].publication_year` |
| DOI | `results[].doi` |
| Type | `results[].type` |

---

## 10. Hugging Face Mirror (v1.4+)

**Base URL:** `https://hf-mirror.com/api`
**Auth:** None required
**Note:** Automatic fallback when `huggingface.co` is unreachable.

---

## 11. Gitee API v5 (v1.4+)

**Base URL:** `https://gitee.com/api/v5`
**Auth:** Personal Access Token (`?access_token=...`)

### Search Repositories

```bash
curl "https://gitee.com/api/v5/search/repositories?access_token=YOUR_TOKEN&q=deep+learning&per_page=5"
```

### Known Issues

Search API may return empty results platform-wide (confirmed as of 2026-07).

---

## 12. GitLab API v4 (v1.4+)

**Base URL:** `https://gitlab.com/api/v4`
**Auth:** None required (public projects)

### Search Projects

```bash
curl "https://gitlab.com/api/v4/projects?search=anomaly+detection&per_page=5"
```

### Limitations

GitLab.com is blocked in China (DNS level since 2020).

---

*Last updated: 2026-07-09 (v1.5.0)*
