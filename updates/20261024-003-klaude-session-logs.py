"""Remove the managed old name after installing klaude-session-logs."""

import json
import os
from pathlib import Path
import subprocess

# Skills CLI 1.7.4 treats these agents as shared-directory consumers.
SHARED_AGENTS = [
    "amp", "antigravity", "antigravity-cli", "cline", "codex", "cursor", "deepagents",
    "dexto", "droid", "firebender", "fx", "gemini-cli", "github-copilot", "kilo",
    "kimi-code-cli", "loaf", "opencode", "pi", "replit", "sarvam-code", "warp", "zed",
]

DESCRIPTION = "session-logs 更名为 klaude-session-logs"


def managed(repository, home):
    state_home = os.environ.get("XDG_STATE_HOME")
    lock = Path(state_home) / "skills/.skill-lock.json" if state_home else home / ".agents/.skill-lock.json"
    records = json.loads(lock.read_text()).get("skills", {}) if lock.exists() else {}
    source = json.loads((repository / "Skillfile.json").read_text())["repository"]
    return records.get("session-logs", {}).get("source") == source


def check(repository, home):
    return not managed(repository, home)


def apply(repository, home):
    if not managed(repository, home):
        return
    canonical = home / ".agents/skills/session-logs"
    client = Path(os.environ.get("CLAUDE_CONFIG_DIR", str(home / ".claude"))).expanduser() / "skills/session-logs"
    config_home = Path(os.environ.get("XDG_CONFIG_HOME", str(home / ".config")))
    # The CLI also removes legacy per-agent entries; preserve independent content.
    legacy = [home / path / "skills/session-logs" for path in (
        ".gemini/antigravity", ".gemini/antigravity-cli", ".cursor", ".deepagents/agent",
        ".factory", ".firebender", ".gemini", ".copilot", ".kilo",
    )]
    legacy += [config_home / path / "skills/session-logs" for path in ("agents", "opencode")]
    for path in [client, *legacy]:
        if canonical.is_symlink() or (os.path.lexists(path) and not (path.is_symlink() and path.resolve() == canonical.resolve())):
            raise RuntimeError(f"旧 session-logs 入口已被个人内容接管；保留原状，请先比较处理：{path}")
    subprocess.run(
        ["npx", "--yes", "skills@1.7.4", "remove", "session-logs", "--global", "--agent", *SHARED_AGENTS, "claude-code", "--yes"],
        env={**os.environ, "HOME": str(home), "DO_NOT_TRACK": "1"}, check=True,
    )
    if not check(repository, home):
        raise RuntimeError("旧技能仍被其他 Agent 使用；请核对其入口后再重试")
