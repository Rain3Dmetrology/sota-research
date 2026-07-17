#!/usr/bin/env bash
# Deep Market Research Skill — 跨平台一键安装脚本
# 检测本机已安装的 Agent 平台，将 skill 复制到对应 skills/ 目录。
set -euo pipefail

SKILL_DIR="deep-market-research"
SRC="$(cd "$(dirname "$0")" && pwd)"

# 要复制的文件（排除 .git 与安装脚本自身）
FILES=(SKILL.md README.md LICENSE CONTRIBUTING.md .gitignore)

# 各平台 skills 根目录（存在的才安装）
TARGETS=(
  "$HOME/.claude/skills"
  "$HOME/.codex/skills"
  "$HOME/.trae/skills"
  "$HOME/.qodo/skills"
  "$HOME/.workbuddy/skills"
)

installed=0
for base in "${TARGETS[@]}"; do
  if [ -d "$base" ]; then
    dest="$base/$SKILL_DIR"
    mkdir -p "$dest"
    for f in "${FILES[@]}"; do
      [ -e "$SRC/$f" ] && cp -R "$SRC/$f" "$dest/"
    done
    echo "Installed to $dest"
    installed=$((installed + 1))
  fi
done

if [ "$installed" -eq 0 ]; then
  echo "No supported agent skills directory found on this machine."
  echo "  Manually copy this folder to your agent's skills directory, e.g.:"
  echo "    cp -r $SRC \"\$HOME/.claude/skills/$SKILL_DIR\""
  echo "  Supported: ~/.claude ~/.codex ~/.trae ~/.qodo ~/.workbuddy"
  exit 1
fi

echo ""
echo "Done. Restart your agent (or run /skill refresh) to load 'deep-market-research'."
