#!/usr/bin/env bash
set -e

SKILLS_DIR="$HOME/.claude/skills"
REPO_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "Installing devaing skills to $SKILLS_DIR..."

for skill in "$REPO_DIR"/skills/devaing-*/; do
  name="$(basename "$skill")"
  dest="$SKILLS_DIR/$name"
  mkdir -p "$dest"
  cp "$skill/SKILL.md" "$dest/SKILL.md"
  echo "  ✓ $name"
done

echo ""
echo "Done. Restart Claude Code to pick up the new skills."
echo ""
echo "Then run /devaing-init to start your first project."
