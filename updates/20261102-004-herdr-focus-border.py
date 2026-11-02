"""Use a subtle focus border in the personal Herdr layout."""

import json
import os
from pathlib import Path
import shutil
import tempfile

DESCRIPTION = "Herdr app 使用低调的激活边框"
FOCUS = {"width": 1, "color": "selection"}


def panes(node):
    if not isinstance(node, dict):
        raise ValueError("invalid layout node")
    content = node.get("content", {})
    if isinstance(content, dict) and content.get("tab") == "active":
        pane = content.get("pane")
        if not isinstance(pane, dict):
            raise ValueError("missing pane")
        yield pane
    for child in node.get("children", []):
        yield from panes(child)


def read_layout(path, state=False):
    if path.is_symlink() or not path.is_file():
        raise RuntimeError(f"布局不是普通文件：{path}")
    original = path.read_bytes()
    try:
        document = json.loads(original)
        found = list(panes(document["file"] if state else document))
        if len(found) != 1 or not isinstance(found[0].get("focus"), dict):
            raise ValueError("missing or ambiguous focus")
    except (ValueError, TypeError, KeyError) as error:
        raise RuntimeError(f"布局 pane 配置无效：{path}") from error
    return original, document, found[0]


def check(repository, home):
    path = home / ".config/herdr-app/layouts/klaude.json"
    state = path.parent / ".state/klaude.json"
    try:
        if read_layout(path)[2]["focus"] != FOCUS:
            return False
        return not os.path.lexists(state) or read_layout(state, True)[2]["focus"] == FOCUS
    except (OSError, RuntimeError):
        return False


def apply(repository, home):
    path = home / ".config/herdr-app/layouts/klaude.json"
    state = path.parent / ".state/klaude.json"
    for parent in path.parents:
        if parent == home:
            break
        if parent.is_symlink() or not parent.is_dir():
            raise RuntimeError(f"布局父路径不是普通目录：{parent}")
    original, document, pane = read_layout(path)
    if os.path.lexists(state) and read_layout(state, True)[2]["focus"] != FOCUS:
        raise RuntimeError("Herdr 布局运行时状态覆盖边框设置，请先在 App 中调整个人布局，未修改文件")
    if pane["focus"] == FOCUS:
        return
    if pane["focus"] not in ({"width": 1, "color": "accent"}, {"width": 0, "color": "accent"}):
        raise RuntimeError("个人布局已有不同的激活边框，未覆盖")
    backups = home / ".local/state/dotfiles/backups"
    backups.mkdir(parents=True, exist_ok=True)
    backup = Path(tempfile.mkdtemp(prefix="herdr-focus-border-", dir=backups))
    saved = backup / path.relative_to(home)
    saved.parent.mkdir(parents=True)
    saved.write_bytes(original)
    shutil.copystat(path, saved)
    pane["focus"] = FOCUS.copy()
    with tempfile.NamedTemporaryFile(mode="w", dir=path.parent, delete=False) as stream:
        json.dump(document, stream, indent=2, ensure_ascii=False)
        stream.write("\n")
    if path.is_symlink() or path.read_bytes() != original:
        raise RuntimeError(f"布局已变化，停止覆盖：{path}")
    os.replace(stream.name, path)
