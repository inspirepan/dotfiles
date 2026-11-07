"""Remove only the five retired global skills owned by their upstream locks."""

import json
import os
from pathlib import Path
import subprocess

DESCRIPTION = "精简五项受管全局技能，保留个人内容"

RETIRED = {
    "playwright": "openai/skills",
    "unslop": "backnotprop/pstack",
    "ketchup-video": "backnotprop/pstack",
    "no-comments": "backnotprop/pstack",
    "make-bot-ui": "backnotprop/pstack",
}

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
    return [name for name, source in RETIRED.items() if records.get(name, {}).get("source") == source]


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
    for name in selected:
        canonical = home / ".agents/skills" / name
        if canonical.is_symlink() or (canonical.exists() and not canonical.is_dir()):
            raise RuntimeError(f"保留个人内容，请先比较处理：{canonical}")
        for directory in clients:
            path = directory / name
            if path == canonical:
                continue
            if os.path.lexists(path) and not (path.is_symlink() and path.resolve() == canonical.resolve()):
                raise RuntimeError(f"保留个人内容，请先比较处理：{path}")
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
