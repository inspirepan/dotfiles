"""Share one instruction source between Claude Code and Codex."""

from pathlib import Path
import os
import shutil
import tempfile

DESCRIPTION = "Claude Code 与 Codex 共用一份指令文件"


def entries(repository, home):
    return {
        home / ".claude/CLAUDE.md": repository / "claude/.claude/CLAUDE.md",
        home / ".codex/AGENTS.md": repository / "codex/.codex/AGENTS.md",
    }


def check(repository, home):
    source = repository / "claude/.claude/CLAUDE.md"
    return source.is_file() and all(path.is_symlink() and path.exists() and path.samefile(source) for path in entries(repository, home))


def apply(repository, home):
    source = repository / "claude/.claude/CLAUDE.md"
    targets = entries(repository, home)
    for path in targets:
        if path.is_symlink() and path.exists() and path.samefile(source):
            continue
        if os.path.lexists(path) and not (path.is_file() and (path.stat().st_size == 0 or path.read_bytes() == source.read_bytes())):
            raise RuntimeError(f"需要先比较并合并已有指令：{path}；原内容已保留")
    for path, target in targets.items():
        if path.is_symlink() and path.exists() and path.samefile(source):
            continue
        if os.path.lexists(path):
            backups = home / ".local/state/dotfiles/backups"
            backups.mkdir(parents=True, exist_ok=True)
            backup = Path(tempfile.mkdtemp(prefix="shared-instructions-", dir=backups))
            shutil.move(str(path), backup / path.name)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.symlink_to(os.path.relpath(target, path.parent))
