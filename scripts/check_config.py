#!/usr/bin/env python3
"""
SOTA Research Skill — Configuration & Environment Checker
Validates API keys, dependencies, and network connectivity.
Usage: python3 scripts/check_config.py
"""

import json
import os
import sys
import urllib.request
import urllib.error
from pathlib import Path


def _check_url(name, url, headers=None, timeout=10):
    """Try to reach a URL, return (ok, msg)."""
    try:
        req = urllib.request.Request(url, headers=headers or {})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            if resp.status < 400:
                return True, f"OK ({resp.status})"
            return False, f"HTTP {resp.status}"
    except urllib.error.HTTPError as e:
        return False, f"HTTP {e.code}"
    except urllib.error.URLError as e:
        return False, f"Network error: {e.reason}"
    except Exception as e:
        return False, str(e)


def main():
    skill_root = Path(__file__).parent.parent
    config_path = skill_root / "config" / "api_config.json"
    example_path = skill_root / "config" / "api_config.example.json"

    print("=" * 60)
    print("  SOTA Research Skill — Configuration Check")
    print("=" * 60)
    print()

    # --- 1. File structure ---
    print("[1] File Structure")
    required = [
        "SKILL.md",
        "scripts/research_workflow.py",
        "config/api_config.example.json",
        "config/codesota_tasks.json",
        "templates/report_template.md",
    ]
    all_ok = True
    for f in required:
        exists = (skill_root / f).exists()
        status = "OK" if exists else "MISSING"
        if not exists:
            all_ok = False
        print(f"    {f}: {status}")
    print()

    # --- 2. Config file ---
    print("[2] API Configuration")
    if config_path.exists():
        print(f"    config/api_config.json: Found")
        with open(config_path, "r") as fh:
            cfg = json.load(fh)
        keys_info = {
            "serpapi_key": "SerpApi (Google Scholar)",
            "github_token": "GitHub",
            "semantic_scholar_key": "Semantic Scholar",
            "modelscope_token": "ModelScope",
            "gitee_token": "Gitee",
            "connected_papers_token": "Connected Papers",
        }
        for k, label in keys_info.items():
            val = cfg.get(k, "")
            if val:
                # Mask the value for display
                masked = val[:6] + "..." + val[-4:] if len(val) > 10 else "***"
                print(f"    {label}: {masked}")
            else:
                print(f"    {label}: NOT SET (optional, some features limited)")
    elif example_path.exists():
        print("    config/api_config.json: NOT FOUND")
        print(f"    config/api_config.example.json: Found (template)")
        print("    -> Copy template: cp config/api_config.example.json config/api_config.json")
    else:
        print("    No config files found")
    print()

    # --- 3. Environment variables ---
    print("[3] Environment Variables (override config file)")
    env_keys = {
        "SERPAPI_KEY": "SerpApi",
        "GITHUB_TOKEN": "GitHub",
        "SEMANTIC_SCHOLAR_API_KEY": "Semantic Scholar",
        "MODELSCOPE_TOKEN": "ModelScope",
        "GITEE_TOKEN": "Gitee",
    }
    for ek, label in env_keys.items():
        val = os.environ.get(ek, "")
        if val:
            print(f"    {label}: SET")
        else:
            print(f"    {label}: not set")
    print()

    # --- 4. Python version ---
    print("[4] Python Environment")
    print(f"    Python version: {sys.version.split()[0]}")
    if sys.version_info >= (3, 8):
        print("    Requirement (>=3.8): OK")
    else:
        print("    Requirement (>=3.8): NOT MET")
    print()

    # --- 5. Network connectivity ---
    print("[5] Network Connectivity (quick probe)")
    probes = [
        ("CodeSOTA", "https://www.codesota.com/api/sota/tasks/anomaly-detection"),
        ("OpenAlex", "https://api.openalex.org/works?search=test&per_page=1"),
        ("arXiv", "https://export.arxiv.org/api/query?search_query=all:electron&max_results=1"),
        ("GitHub API", "https://api.github.com"),
        ("Semantic Scholar", "https://api.semanticscholar.org/graph/v1/paper/search?query=test&limit=1"),
        ("Hugging Face", "https://huggingface.co/api/models?limit=1"),
        ("ModelScope", "https://modelscope.cn/api/v1/models?PageNumber=1&PageSize=1"),
        ("Gitee", "https://gitee.com/api/v5/repos?access_token=test&page=1&per_page=1"),
    ]
    for name, url in probes:
        ok, msg = _check_url(name, url, timeout=8)
        icon = "OK" if ok else "FAIL"
        print(f"    {name}: {icon} — {msg}")
    print()

    # --- 6. SKILL.md validation ---
    print("[6] SKILL.md Validation (Agent Skills spec)")
    skill_md = skill_root / "SKILL.md"
    if skill_md.exists():
        with open(skill_md, "r") as f:
            content = f.read()
        if content.startswith("---"):
            lines = content.split("\n")
            # Find end of frontmatter
            fm_end = -1
            for i, line in enumerate(lines):
                if i > 0 and line.strip() == "---":
                    fm_end = i
                    break
            if fm_end > 0:
                fm = "\n".join(lines[:fm_end])
                for field in ["name:", "description:"]:
                    if field in fm:
                        print(f"    {field.strip(':')}: Found")
                    else:
                        print(f"    {field.strip(':')}: MISSING (required)")
                for field in ["license:", "compatibility:", "metadata:"]:
                    if field in fm:
                        print(f"    {field.strip(':')}: Found")
                    else:
                        print(f"    {field.strip(':')}: Not set (optional)")
            else:
                print("    Could not parse YAML frontmatter")
        else:
            print("    Missing YAML frontmatter (---)")
    else:
        print("    SKILL.md not found")
    print()

    # --- Summary ---
    print("=" * 60)
    print("  Check complete. Follow the steps above to resolve issues.")
    print("=" * 60)


if __name__ == "__main__":
    main()
