"""Retire selected global pstack skills and their install records."""

import json
import os
from pathlib import Path
import subprocess

DESCRIPTION = "移除 poteto-mode 与已停用的 pstack 技能，保留七条通用原则"

SOURCE = "backnotprop/pstack"
RETIRED = (
    "poteto-mode",
    "create-formal-verification-skill",
    "maintain-formal-verification-skill",
    "maintain-verification-skill",
    "statechart",
    "poteto-help",
    "setup-pstack",
    "reflect",
    "principle-attack-the-premise",
    "principle-build-the-lever",
    "principle-encode-lessons-in-structure",
    "principle-exhaust-the-design-space",
    "principle-experience-first",
    "principle-foundational-thinking",
    "principle-guard-the-context-window",
    "principle-laziness-protocol",
    "principle-migrate-callers-then-delete-legacy-apis",
    "principle-minimize-reader-load",
    "principle-model-the-domain",
    "principle-never-block-on-the-human",
    "principle-outcome-oriented-execution",
    "principle-redesign-from-first-principles",
    "principle-separate-before-serializing-shared-state",
    "principle-sequence-verifiable-units",
    "principle-subtract-before-you-add",
)

# Audited against Skills CLI 1.7.4, including its legacy cleanup paths.
SHARED_AGENTS = [
    "amp", "antigravity", "antigravity-cli", "cline", "codex", "cursor", "deepagents",
    "dexto", "droid", "firebender", "fx", "gemini-cli", "github-copilot", "kilo",
    "kimi-code-cli", "loaf", "opencode", "pi", "replit", "sarvam-code", "warp", "zed",
]


def managed(home):
    state_home = os.environ.get("XDG_STATE_HOME")
    lock = Path(state_home) / "skills/.skill-lock.json" if state_home else home / ".agents/.skill-lock.json"
    records = json.loads(lock.read_text()).get("skills", {}) if lock.exists() else {}
    return [name for name in RETIRED if records.get(name, {}).get("source") == SOURCE]


def check(repository, home):
    return not managed(home)


def apply(repository, home):
    selected = managed(home)
    if not selected:
        return
    claude = Path(os.environ.get("CLAUDE_CONFIG_DIR", "").strip() or home / ".claude")
    config_home = Path(os.environ.get("XDG_CONFIG_HOME") or home / ".config")
    clients = [claude / "skills"]
    clients += [home / path / "skills" for path in (
        ".gemini/antigravity", ".gemini/antigravity-cli", ".cursor", ".deepagents/agent",
        ".factory", ".firebender", ".gemini", ".copilot", ".kilo",
    )]
    clients += [config_home / path / "skills" for path in ("agents", "opencode")]
    entries = []
    for name in selected:
        canonical = home / ".agents/skills" / name
        if canonical.is_symlink() or (canonical.exists() and not canonical.is_dir()):
            raise RuntimeError(f"保留个人内容，请先比较处理：{canonical}")
        for directory in dict.fromkeys(clients):
            path = directory / name
            if path == canonical:
                continue
            if not os.path.lexists(path):
                continue
            if not path.is_symlink() or path.resolve() != canonical.resolve():
                raise RuntimeError(f"保留个人内容，请先比较处理：{path}")
            entries.append(str(path))
        if canonical.exists():
            entries.append(str(canonical))
    if entries:
        subprocess.run(["trash", *entries], check=True)
    # Named removal also handles records whose files were already trashed.
    subprocess.run(
        ["npx", "--yes", "skills@1.7.4", "remove", *selected, "--global", "--agent", *SHARED_AGENTS, "claude-code", "--yes"],
        env={**os.environ, "HOME": str(home), "DO_NOT_TRACK": "1"}, check=True,
    )
    if not check(repository, home):
        raise RuntimeError("受管技能仍有安装记录；请核对其他 Agent 入口后重试")
    for name in selected:
        for directory in [home / ".agents/skills", *clients]:
            if os.path.lexists(directory / name):
                raise RuntimeError(f"技能入口未移除：{directory / name}")
