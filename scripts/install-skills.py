# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Select declared skills; delegate installation and provenance to Vercel Skills."""

import argparse
import json
import os
from pathlib import Path
import re
import subprocess


def load_config(repository):
    config = json.loads((repository / "Skillfile.json").read_text())
    if config.get("version") != 1:
        raise ValueError("不支持的 Skillfile 版本")
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", config["repository"]):
        raise ValueError("repository 必须是 owner/repo")
    if not re.fullmatch(r"[0-9a-f]{40}", config["revision"]):
        raise ValueError("revision 必须是完整提交 SHA")
    names = config["enabled"]
    if not isinstance(names, list) or any(
        not isinstance(name, str) or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name) for name in names
    ) or len(set(names)) != len(names):
        raise ValueError("enabled 必须是无重复的技能名列表")
    return config


def plan(repository, home):
    config = load_config(repository)
    state_home = os.environ.get("XDG_STATE_HOME")
    lock_path = Path(state_home) / "skills/.skill-lock.json" if state_home else home / ".agents/.skill-lock.json"
    lock = json.loads(lock_path.read_text()).get("skills", {}) if lock_path.exists() else {}
    shared = home / ".agents/skills"
    claude = Path(os.environ.get("CLAUDE_CONFIG_DIR", str(home / ".claude"))).expanduser() / "skills"
    pending, conflicts = [], []
    for name in config["enabled"]:
        canonical, client = shared / name, claude / name
        record = lock.get(name, {})
        owned = record.get("source") == config["repository"]
        foreign_client = os.path.lexists(client) and not (
            canonical.exists() and client.is_symlink() and client.resolve() == canonical.resolve()
        )
        if (os.path.lexists(canonical) and (not owned or canonical.is_symlink())) or foreign_client:
            conflicts.append(name)
        elif not (canonical / "SKILL.md").is_file() or not (client / "SKILL.md").is_file() or record.get("ref") != config["revision"]:
            pending.append(name)
    return config, pending, conflicts


def install(repository, home, check=False):
    config, pending, conflicts = plan(repository, home)
    for name in conflicts:
        print(f"保留个人技能：{name}（没有本来源的 Vercel 安装记录，或客户端是独立内容）")
    if pending:
        print("待安装／更新：" + ", ".join(pending))
    if pending and not check:
        source = f"https://github.com/{config['repository']}/tree/{config['revision']}"
        command = ["npx", "--yes", "skills@1.7.4", "add", source, "--global", "--agent", "codex", "claude-code", "--skill", *pending, "--yes", "--json"]
        result = subprocess.run(command, env={**os.environ, "DO_NOT_TRACK": "1"}, capture_output=True, text=True)
        if result.returncode:
            raise RuntimeError(result.stderr or result.stdout)
        _, remaining, new_conflicts = plan(repository, home)
        if remaining:
            raise RuntimeError("Vercel 安装记录或入口未通过验证：" + ", ".join(remaining))
        conflicts = new_conflicts
    print(f"{'检查' if check else '安装'}完成：{len(pending) if check else 0} 项待同步，{len(conflicts)} 项保留冲突")
    return 2 if conflicts else 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--update", action="store_true", help="仍按清单固定版本安装")
    args = parser.parse_args()
    return install(Path(__file__).resolve().parents[1], Path.home(), args.check)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, KeyError, RuntimeError) as error:
        raise SystemExit(f"技能安装失败：{error}") from error
