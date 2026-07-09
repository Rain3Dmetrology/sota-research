# Migration Notes: Papers With Code → CodeSOTA

## Timeline

- **2018**: Papers With Code (PWC) launched as the default ML leaderboard.
- **2025-07-24/25**: Meta shut down Papers With Code. Old API endpoints stopped working.
- **2025-08+**: CodeSOTA launched as a replacement SOTA registry.

## What Changed

| Aspect | Papers With Code (old) | CodeSOTA (new) |
|--------|----------------------|----------------|
| **API** | `paperswithcode.com/api/v1` | `codesota.com/api/sota` |
| **Auth** | None | None |
| **Scope** | Papers + code + datasets + methods + SOTA | SOTA registry only (no paper metadata) |
| **Data** | Broad ML/AI task coverage | Growing registry, some tasks may be missing |
| **Historical Data** | Lost (API decommissioned) | [GitHub Archive](https://github.com/paperswithcode/paperswithcode-data) available |

## Migration Strategy

### For SOTA Lookups

Replace all `paperswithcode.com/api/v1` calls with `codesota.com/api/sota`:

```bash
# Old (broken):
curl "https://paperswithcode.com/api/v1/tasks/"

# New:
curl "https://www.codesota.com/api/sota"
curl "https://www.codesota.com/api/sota/{task_alias}?tier=sota"
```

### For Paper Metadata

PWC used to provide paper metadata alongside SOTA. CodeSOTA does not. Use
**Semantic Scholar API** for paper metadata:

```bash
curl "https://api.semanticscholar.org/graph/v1/paper/search?query=YOUR_QUERY&fields=title,year,citationCount,tldr"
```

### For Code Links

PWC used to link papers to GitHub repos. Use **GitHub Search API** directly:

```bash
curl "https://api.github.com/search/repositories?q=PAPER_TITLE&sort=stars"
```

### For Historical PWC Data

The full PWC data dump is available on GitHub:

```bash
git clone https://github.com/paperswithcode/paperswithcode-data
```

This contains historical JSON snapshots of papers, datasets, methods, and evaluations.

## Workflow Adaptation

The original 5-step workflow used PWC as Step 1. The updated workflow:

1. **CodeSOTA API** — Check if the task has a registered SOTA entry
2. **Fallback: SerpApi Google Scholar** — If CodeSOTA returns 404 (task not in registry),
   fall back to Google Scholar search to find relevant papers
3. **Hugging Face Papers** — Supplement with daily trending papers

This fallback mechanism is built into `scripts/research_workflow.py` and requires
no manual intervention.

## CodeSOTA Task Coverage

CodeSOTA is actively expanding. As of 2026-04, known task aliases include:

- `ocr` (document-ocr)
- `code` (code-generation)
- `asr` / `stt` (speech-recognition)
- `tts` (text-to-speech)
- `vqa` (visual-question-answering)
- `caption` (image-captioning)
- `t2i` (text-to-image)
- `t2v` (text-to-video)

For tasks not yet in CodeSOTA (e.g., "image segmentation", "object detection"),
the workflow automatically falls back to Google Scholar search.
