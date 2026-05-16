#!/usr/bin/env python3
"""
Integrity checker for the devaing skill suite.

Checks:
  1. Step references  — navigation text (go to / skip to / etc.) points to a step
                        that exists in the same skill
  2. Variable defs    — <var> placeholders used inside bash blocks are defined
                        somewhere in the same skill via "Store as" or explicit set
  3. .devaing.md      — fields read from .devaing.md by non-init skills are
                        written by devaing-init or devaing-ship

Usage:
  python -m scripts.check_integrity                      # all skills
  python -m scripts.check_integrity skills/devaing-ship  # single skill
"""

import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

SKILLS_DIR = Path(__file__).parent.parent / "skills"

# Who writes each .devaing.md field
DEVAING_MD_CONTRACT = {
    "granularity": "devaing-init",
    "prototyper":  "devaing-init",
    "project":     "devaing-init",
    "prod_url":    "devaing-ship",
    "prod_db_url": "devaing-ship",
}

# Placeholders that come from shell/CLI or are computed inline — never "Stored as" in prose
_BASH_EXTERNALS = frozenset({
    # CLI / shell derived
    "owner", "branch", "name", "n", "pr", "slug", "repo",
    # Milestone / epic iteration
    "milestone", "epic-name", "issue-number", "milestone-slug",
    # GitHub Project plumbing (all set inline in bash, not via prose)
    "project-number", "project-id", "item-id",
    "status-field", "field-id", "in-progress-id", "done-id",
    # Issue capture vars (set via ISSUE_URL=$(...))
    "retroactive-url", "retroactive-n",
    "issue-url", "issue-n",
    # Stack-inferred commands (determined at runtime from the project stack)
    "migration-command", "seed-command",
    # GitHub dependency API (internal IDs from inline fetch)
    "b-number", "a-internal-id",
    # Content placeholders used as gh CLI arguments (title, body fragments, comments)
    # — these are filled from conversation context, not stored via "Store as"
    "title", "epic", "epic-description", "description", "reason",
    "new-title",
    # Git tag determined contextually in Step 7 of devaing-ship
    "tag-name",
})


# ── data types ────────────────────────────────────────────────────────────────

@dataclass
class Issue:
    level: str   # ERROR | WARN
    line: int
    message: str

    def __str__(self) -> str:
        return f"  {self.level:<5}  line {self.line:4d}  {self.message}"


@dataclass
class SkillResult:
    name: str
    issues: list[Issue] = field(default_factory=list)

    @property
    def status(self) -> str:
        if any(i.level == "ERROR" for i in self.issues):
            return "ERROR"
        if any(i.level == "WARN" for i in self.issues):
            return "WARN"
        return "PASS"


# ── file reading ──────────────────────────────────────────────────────────────

def read_lines(skill_path: Path) -> list[str]:
    return (skill_path / "SKILL.md").read_text(encoding="utf-8").splitlines()


# ── check 1: step references ─────────────────────────────────────────────────

# Step ID extraction from headings and bold markers
# Note: step IDs never contain periods, so we use [A-Za-z0-9_-]* (no dot)
_HEADING_STEP  = re.compile(r"^#{1,4}\s+Step\s+([A-Za-z0-9][A-Za-z0-9_-]*)", re.I)
_HEADING_NAMED = re.compile(r"^#{1,4}\s+(Closing|Final report|Hotfix flow|Opening)\b", re.I)
_BOLD_STEP     = re.compile(r"\*\*Step\s+([A-Za-z0-9][A-Za-z0-9_-]*)", re.I)

# Navigation verbs that precede "Step X"
# Trailing punctuation like "Step 4." must not be captured — hence no dot in char class
_NAV_TO_STEP = re.compile(
    r"(?:go to|skip to|proceed to|resume at|resume from|continue to|"
    r"return to|move to|back to)\s+Step\s+([A-Za-z0-9][A-Za-z0-9_-]*)",
    re.I,
)
# "skip to Closing" / "skip to Final report"
_NAV_TO_NAMED = re.compile(
    r"(?:go to|skip to|proceed to|resume at|continue to)"
    r"\s+(Closing|Final report|Hotfix flow)\b",
    re.I,
)


def _extract_step_ids(lines: list[str]) -> set[str]:
    ids: set[str] = set()
    for line in lines:
        m = _HEADING_STEP.match(line)
        if m:
            ids.add(m.group(1).lower())
        m = _HEADING_NAMED.match(line)
        if m:
            ids.add(m.group(1).lower())
        for m in _BOLD_STEP.finditer(line):
            ids.add(m.group(1).lower())
    return ids


def check_step_refs(lines: list[str]) -> list[Issue]:
    issues: list[Issue] = []
    step_ids = _extract_step_ids(lines)

    for lineno, line in enumerate(lines, 1):
        for m in _NAV_TO_STEP.finditer(line):
            ref = m.group(1).lower()
            if ref not in step_ids:
                issues.append(Issue("ERROR", lineno,
                    f"references 'Step {m.group(1)}' which does not exist "
                    f"(known steps: {', '.join(sorted(step_ids))})"))
        for m in _NAV_TO_NAMED.finditer(line):
            ref = m.group(1).lower()
            if ref not in step_ids:
                issues.append(Issue("ERROR", lineno,
                    f"references '{m.group(1)}' section which does not exist"))

    return issues


# ── check 2: bash variable definitions ───────────────────────────────────────

_STORE_AS      = re.compile(r"[Ss]tor(?:e|ed)\s+(?:result\s+)?as\s+`<([^>]+)>`")
_SET_FLAG      = re.compile(r"set\s+(?:a\s+flag\s+)?`<([^>]+)>`\s*(?:=|to\b)", re.I)
_ASSIGN_INLINE = re.compile(r"`<([^>]+)>`\s*=\s*(?:true|false|`)")
# Template lines inside .devaing.md blocks: "granularity: <granularity>"
_DEVAING_TMPL  = re.compile(r"^([a-z_]+):\s+<[^>]")

# <var> placeholders inside bash blocks (lowercase with hyphens/underscores)
_BASH_VAR = re.compile(r"<([a-z][a-z0-9_-]*)>", re.I)


def _extract_defined_vars(lines: list[str]) -> set[str]:
    defined: set[str] = set()
    for line in lines:
        for pat in (_STORE_AS, _SET_FLAG, _ASSIGN_INLINE):
            for m in pat.finditer(line):
                defined.add(m.group(1).lower())
        m = _DEVAING_TMPL.match(line)
        if m:
            defined.add(m.group(1).lower())
    return defined


def check_bash_vars(lines: list[str]) -> list[Issue]:
    issues: list[Issue] = []
    defined = _extract_defined_vars(lines)
    in_bash = False
    in_heredoc = False
    seen_warnings: set[str] = set()

    for lineno, line in enumerate(lines, 1):
        stripped = line.strip()

        if re.match(r"^```(bash|sh)\b", stripped):
            in_bash = True
            in_heredoc = False
            continue
        if in_bash and stripped == "```":
            in_bash = False
            in_heredoc = False
            continue
        if not in_bash:
            continue

        # Track heredoc boundaries: <<'EOF' or <<"EOF" or <<EOF opens a heredoc;
        # a bare "EOF" on its own closes it. Placeholders inside heredocs are
        # content templates (issue bodies, commit messages), not bash variables.
        if not in_heredoc and re.search(r"<<['\"]?EOF['\"]?", line):
            in_heredoc = True
            continue
        if in_heredoc:
            if stripped == "EOF":
                in_heredoc = False
            continue

        for m in _BASH_VAR.finditer(line):
            var = m.group(1).lower()
            if var in _BASH_EXTERNALS or var in defined:
                continue
            if len(var) <= 2:
                continue
            if var in seen_warnings:
                continue
            seen_warnings.add(var)
            issues.append(Issue("WARN", lineno,
                f"<{var}> used in bash block but not defined via 'Store as' in this skill"))

    return issues


# ── check 3: .devaing.md contract ────────────────────────────────────────────

# Patterns that indicate reading a specific field from .devaing.md.
# _READ_GREP must not be greedy: require the field name to appear immediately
# after "grep" (with only optional whitespace + quote + caret) so that
# "grep \"^project:\" .devaing.md" extracts "project" and not a spurious "t".
_READ_GREP  = re.compile(r'grep\s+["\']?\^?([a-z_]+):["\']?\s+\.devaing\.md', re.I)
_READ_PROSE = re.compile(r'`([a-z_]+):`\s+(?:line|value|from)\s+\.devaing\.md', re.I)


def check_devaing_contract(skill_name: str, lines: list[str]) -> list[Issue]:
    if skill_name == "devaing-init":
        return []

    issues: list[Issue] = []
    for lineno, line in enumerate(lines, 1):
        for pat in (_READ_GREP, _READ_PROSE):
            for m in pat.finditer(line):
                f = m.group(1).lower()
                if f not in DEVAING_MD_CONTRACT:
                    issues.append(Issue("WARN", lineno,
                        f".devaing.md field '{f}' is read here but not in the "
                        f"known contract ({', '.join(sorted(DEVAING_MD_CONTRACT))})"))

    return issues


# ── runner ────────────────────────────────────────────────────────────────────

def check_skill(skill_path: Path) -> SkillResult:
    result = SkillResult(name=skill_path.name)
    try:
        lines = read_lines(skill_path)
    except Exception as e:
        result.issues.append(Issue("ERROR", 0, f"Cannot read SKILL.md: {e}"))
        return result

    result.issues += check_step_refs(lines)
    result.issues += check_bash_vars(lines)
    result.issues += check_devaing_contract(skill_path.name, lines)
    result.issues.sort(key=lambda i: i.line)
    return result


def format_output(results: list[SkillResult]) -> str:
    sym = {"PASS": "OK", "WARN": "!!", "ERROR": "XX"}
    out: list[str] = []

    for r in results:
        out.append(f"\n{sym.get(r.status, '?')} {r.name}  [{r.status}]")
        if r.issues:
            out += [str(i) for i in r.issues]
        else:
            out.append("  (no issues)")

    total   = len(results)
    passed  = sum(1 for r in results if r.status == "PASS")
    warned  = sum(1 for r in results if r.status == "WARN")
    errored = sum(1 for r in results if r.status == "ERROR")
    out.append(f"\n{'-' * 64}")
    out.append(f"  {passed}/{total} passed  {warned} warnings  {errored} errors")
    return "\n".join(out)


def main() -> None:
    if len(sys.argv) > 1:
        paths = [Path(sys.argv[1])]
    else:
        if not SKILLS_DIR.exists():
            print(f"Skills directory not found: {SKILLS_DIR}")
            sys.exit(1)
        paths = sorted(
            p for p in SKILLS_DIR.iterdir()
            if p.is_dir() and (p / "SKILL.md").exists()
        )

    if not paths:
        print("No skills found.")
        sys.exit(1)

    results = [check_skill(p) for p in paths]
    print(format_output(results))
    sys.exit(1 if any(r.status == "ERROR" for r in results) else 0)


if __name__ == "__main__":
    main()
