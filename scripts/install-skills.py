# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Install pinned skills from declared sources through Vercel Skills."""

import argparse
import json
import os
from pathlib import Path
import re
import subprocess


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
        if not re.fullmatch(r"[0-9a-f]{40}", source["revision"]):
            raise ValueError("revision 必须是完整提交 SHA")
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
            foreign_client = os.path.lexists(client) and not (
                canonical.exists() and client.is_symlink() and client.resolve() == canonical.resolve()
            )
            if (os.path.lexists(canonical) and (not owned or canonical.is_symlink())) or foreign_client:
                conflicts.append(name)
            elif (
                not (canonical / "SKILL.md").is_file()
                or not (client / "SKILL.md").is_file()
                or record.get("source") != source["repository"]
                or record.get("ref") != source["revision"]
            ):
                pending.append(name)
    return config, pending, conflicts


def install(repository, home, check=False):
    config, pending, conflicts = plan(repository, home)
    for name in conflicts:
        print(f"保留个人技能：{name}（来源未授权接管，或客户端是独立内容）", flush=True)
    for source in sources(config):
        selected = [name for name in source["enabled"] if name in pending]
        if not selected:
            continue
        print(f"待安装／更新 [{source['repository']}]：" + ", ".join(selected), flush=True)
        if check:
            continue
        url = f"https://github.com/{source['repository']}/tree/{source['revision']}"
        command = ["npx", "--yes", "skills@1.7.4", "add", url, "--global", "--agent", "codex", "claude-code", "--skill", *selected, "--yes", "--json"]
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
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--update", action="store_true", help="仍按清单固定版本安装")
    args = parser.parse_args()
    return install(Path(__file__).resolve().parents[1], Path.home(), args.check)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, KeyError, RuntimeError) as error:
        raise SystemExit(f"技能安装失败：{error}") from error
