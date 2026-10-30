"""Move the patched main layout to a device-local personal layout."""

import json
import os
from pathlib import Path
import shutil
import tempfile

DESCRIPTION = "Herdr app 使用个人 klaude 布局并原样恢复内置 main"
SUPERSEDES = ("20261030-002-klaude-menu-first",)


def tab_blocks(node):
    content = node.get("content", {})
    if content.get("mod") in ("tabs", "klaude-tabs"):
        yield content
    for child in node.get("children", []):
        yield from tab_blocks(child)


def plan(home):
    main = home / ".config/herdr-app/layouts/main.json"
    personal = main.with_name("klaude.json")
    for path in (main, personal):
        for parent in path.parents:
            if parent == home:
                break
            if parent.is_symlink() or (parent.exists() and not parent.is_dir()):
                raise RuntimeError(f"布局父路径不是普通目录，未覆盖：{parent}")
        if path.is_symlink() or (path.exists() and not path.is_file()):
            raise RuntimeError(f"布局不是普通文件，未覆盖：{path}")
    if not main.is_file():
        raise RuntimeError(f"缺少本机 main 布局，未修改：{main}")
    current = main.read_bytes()
    existing = personal.read_bytes() if personal.exists() else None
    try:
        document = json.loads(current)
        personal_document = json.loads(existing) if existing is not None else None
    except ValueError as error:
        raise RuntimeError("main 或个人布局不是有效 JSON，未覆盖；请先检查本机布局") from error
    backups = home / ".local/state/dotfiles/backups"
    for backup in sorted(backups.glob("klaude-menu-*/.config/herdr-app/layouts/main.json")):
        original = backup.read_bytes()
        patched = json.loads(original)
        blocks = list(tab_blocks(patched))
        if not blocks:
            continue
        for block in blocks:
            block["mod"] = "klaude-tabs"
        if document != patched and not (current == original and personal_document == patched):
            continue
        if existing is not None and personal_document != patched:
            raise RuntimeError(f"个人布局与迁移内容不同，未覆盖：{personal}")
        pending = {}
        if existing is None:
            pending[personal] = (None, current)
        if current != original:
            pending[main] = (current, original)
        return pending
    raise RuntimeError("main 布局与任何 002 备份及其 tabs 替换结果不匹配；可能有用户修改，未覆盖")


def check(repository, home):
    try:
        main = home / ".config/herdr-app/layouts/main.json"
        personal = main.with_name("klaude.json")
        if any(path.is_symlink() or not path.is_file() for path in (main, personal)):
            return False
        blocks = list(tab_blocks(json.loads(personal.read_bytes())))
        return bool(blocks) and all(block["mod"] == "klaude-tabs" for block in blocks) and not any(
            block["mod"] == "klaude-tabs" for block in tab_blocks(json.loads(main.read_bytes()))
        )
    except (OSError, ValueError, RuntimeError):
        return False


def apply(repository, home):
    if check(repository, home):
        return
    pending = plan(home)
    if not pending:
        return
    backups = home / ".local/state/dotfiles/backups"
    backup = Path(tempfile.mkdtemp(prefix="personal-herdr-layout-", dir=backups))
    print(f"Herdr app 个人布局迁移备份：{backup}", flush=True)
    for path, (before, after) in pending.items():
        if path.is_symlink() or (path.read_bytes() if path.exists() else None) != before:
            raise RuntimeError(f"布局已变化，停止覆盖：{path}")
        if before is not None:
            saved = backup / path.relative_to(home)
            saved.parent.mkdir(parents=True, exist_ok=True)
            saved.write_bytes(before)
            shutil.copystat(path, saved)
        with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as stream:
            stream.write(after)
        if path.is_symlink() or (path.read_bytes() if path.exists() else None) != before:
            raise RuntimeError(f"布局已变化，停止覆盖：{path}")
        os.replace(stream.name, path)
