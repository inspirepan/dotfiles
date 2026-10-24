# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Install latest skills from declared sources through Vercel Skills."""

import argparse
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile


def sources(config):
    return [config, *config.get("sources", [])]


def load_config(repository):
    config = json.loads((repository / "Skillfile.json").read_text())
    if config.get("version") != 1:
        raise ValueError("不支持的 Skillfile 版本")
    if not isinstance(config.get("sources", []), list):
        raise ValueError("sources 必须是来源列表")
    seen = set()
    for source in sources(config):
        if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", source["repository"]):
            raise ValueError("repository 必须是 owner/repo")
        names = source["enabled"]
        if not isinstance(names, list) or any(
            not isinstance(name, str) or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name) for name in names
        ):
            raise ValueError("enabled 必须是技能名列表")
        if len(set(names)) != len(names) or seen.intersection(names):
            raise ValueError("同一技能名只能启用一个来源")
        seen.update(names)
        replaces = source.get("replaces", [])
        if not isinstance(replaces, list) or any(
            not isinstance(old, str) or not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", old) for old in replaces
        ):
            raise ValueError("replaces 必须是允许迁移的原来源列表")
    return config


def legacy_commit(repository, source, name, canonical, client):
    target = (repository / "skills/commit").resolve()
    return (
        name == "commit"
        and source["repository"] == "inspirepan/agent-skills"
        and canonical.is_symlink()
        and canonical.resolve() == target
        and (not os.path.lexists(client) or (client.is_symlink() and client.resolve() == target))
    )


def plan(repository, home):
    config = load_config(repository)
    state_home = os.environ.get("XDG_STATE_HOME")
    lock_path = Path(state_home) / "skills/.skill-lock.json" if state_home else home / ".agents/.skill-lock.json"
    lock = json.loads(lock_path.read_text()).get("skills", {}) if lock_path.exists() else {}
    shared = home / ".agents/skills"
    claude = Path(os.environ.get("CLAUDE_CONFIG_DIR", str(home / ".claude"))).expanduser() / "skills"
    pending, conflicts = [], []
    for source in sources(config):
        for name in source["enabled"]:
            canonical, client = shared / name, claude / name
            record = lock.get(name, {})
            owned = record.get("source") in [source["repository"], *source.get("replaces", [])]
            if (not record or owned) and legacy_commit(repository, source, name, canonical, client):
                pending.append(name)
                continue
            foreign_client = os.path.lexists(client) and not (
                canonical.exists() and client.is_symlink() and client.resolve() == canonical.resolve()
            )
            if (os.path.lexists(canonical) and (not owned or canonical.is_symlink())) or foreign_client:
                conflicts.append(name)
            elif (
                not (canonical / "SKILL.md").is_file()
                or not (client / "SKILL.md").is_file()
                or record.get("source") != source["repository"]
                or re.fullmatch(r"[0-9a-fA-F]{40}", record.get("ref") or "")
            ):
                pending.append(name)
    return config, pending, conflicts


def install(repository, home, check=False, update=False):
    config, pending, conflicts = plan(repository, home)
    for name in conflicts:
        print(f"保留个人技能：{name}（来源未授权接管，或客户端是独立内容）", flush=True)
    for source in sources(config):
        selected = [name for name in source["enabled"] if name not in conflicts and (update or name in pending)]
        if not selected:
            continue
        print(f"待安装／更新 [{source['repository']}]：" + ", ".join(selected), flush=True)
        if check:
            continue
        for name in selected:
            canonical = home / ".agents/skills" / name
            client = Path(os.environ.get("CLAUDE_CONFIG_DIR", str(home / ".claude"))).expanduser() / "skills" / name
            if legacy_commit(repository, source, name, canonical, client):
                backups = home / ".local/state/dotfiles/backups"
                backups.mkdir(parents=True, exist_ok=True)
                backup = Path(tempfile.mkdtemp(prefix="legacy-commit-", dir=backups))
                if client.is_symlink():
                    shutil.move(str(client), backup / "claude-link")
                shutil.move(str(canonical), backup / "shared-link")
                print(f"旧 commit 入口已备份：{backup}", flush=True)
        command = ["npx", "--yes", "skills@latest", "add", source["repository"], "--global", "--agent", "codex", "claude-code", "--skill", *selected, "--yes", "--json"]
        result = subprocess.run(command, env={**os.environ, "HOME": str(home), "DO_NOT_TRACK": "1"}, capture_output=True, text=True)
        if result.returncode:
            raise RuntimeError(f"{source['repository']}：{result.stderr or result.stdout}")
        _, remaining, new_conflicts = plan(repository, home)
        if set(selected).intersection(remaining) or set(selected).intersection(new_conflicts):
            raise RuntimeError("Vercel 安装记录或入口未通过验证：" + ", ".join(selected))
    _, remaining, conflicts = plan(repository, home)
    print(f"{'检查' if check else '安装'}完成：{len(remaining)} 项待同步，{len(conflicts)} 项保留冲突")
    return 2 if conflicts else 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="只检查本地来源、入口与旧 SHA ref，不联网检查最新版")
    parser.add_argument("--update", action="store_true", help="刷新清单中全部无冲突技能到上游最新版")
    args = parser.parse_args()
    return install(Path(__file__).resolve().parents[1], Path.home(), check=args.check, update=args.update)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, KeyError, RuntimeError) as error:
        raise SystemExit(f"技能安装失败：{error}") from error
