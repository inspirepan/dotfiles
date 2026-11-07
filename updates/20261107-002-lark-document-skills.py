"""Keep only the enabled document skills from the official Feishu source."""

import importlib.util
import json
import os
from pathlib import Path
import subprocess

DESCRIPTION = "飞书官方技能仅启用文档五项，清理同源未启用项"

# Audited against Skills CLI 1.7.4, including its legacy cleanup paths.
SHARED_AGENTS = [
    "amp", "antigravity", "antigravity-cli", "cline", "codex", "cursor", "deepagents",
    "dexto", "droid", "firebender", "fx", "gemini-cli", "github-copilot", "kilo",
    "kimi-code-cli", "loaf", "opencode", "pi", "replit", "sarvam-code", "warp", "zed",
]


def installer(repository):
    spec = importlib.util.spec_from_file_location("dotfiles_lark_skills", repository / "scripts/install-skills.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def managed(repository, home, skills):
    config = skills.load_config(repository)
    source = next(source for source in skills.sources(config) if source["repository"] == skills.LARK_SOURCE)
    state_home = os.environ.get("XDG_STATE_HOME")
    lock = Path(state_home) / "skills/.skill-lock.json" if state_home else home / ".agents/.skill-lock.json"
    records = json.loads(lock.read_text()).get("skills", {}) if lock.exists() else {}
    return [
        name for name, record in records.items()
        if name.startswith("lark-") and name not in source["enabled"]
        and skills.matches_source(source["repository"], name, record)
    ]


def check(repository, home):
    skills = installer(repository)
    _, pending, conflicts = skills.plan(repository, home)
    return not pending and not conflicts and not managed(repository, home, skills)


def apply(repository, home):
    skills = installer(repository)
    selected = managed(repository, home, skills)
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
    if skills.install(repository, home):
        raise RuntimeError("技能存在个人内容冲突，请先比较处理")
    if selected:
        subprocess.run(
            ["npx", "--yes", "skills@1.7.4", "remove", *selected, "--global", "--agent", *SHARED_AGENTS, "claude-code", "--yes"],
            env={**os.environ, "HOME": str(home), "DO_NOT_TRACK": "1"}, check=True,
        )
    if not check(repository, home):
        raise RuntimeError("飞书技能范围或安装记录未通过验证")
    for name in selected:
        for directory in [home / ".agents/skills", *clients]:
            if os.path.lexists(directory / name):
                raise RuntimeError(f"技能入口未移除：{directory / name}")
