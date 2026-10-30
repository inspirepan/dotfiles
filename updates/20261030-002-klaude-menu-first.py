"""Keep Klaude first in a personal copy of the Herdr new-tab menu."""

import json
import os
from pathlib import Path
import shutil
import tempfile

DESCRIPTION = "Herdr app 菜单将 Klaude 置顶，Cmd+T 新建标签页"
FILES = tuple(
    f"mods/{mod}/{name}"
    for mod in ("klaude-menu", "klaude-tabs")
    for name in ("main.js", "mod.json")
)


def entries(repository, home):
    return {
        home / ".config/herdr-app" / name: repository / "config/.config/herdr-app" / name
        for name in FILES
    }


def tab_blocks(node):
    content = node.get("content", {})
    if content.get("mod") in ("tabs", "klaude-tabs"):
        yield content
    for child in node.get("children", []):
        yield from tab_blocks(child)


def check(repository, home):
    if not all(
        source.is_file() and path.is_symlink() and path.exists() and path.samefile(source)
        for path, source in entries(repository, home).items()
    ):
        return False
    layout = home / ".config/herdr-app/layouts/main.json"
    if not layout.is_file():
        return False
    blocks = list(tab_blocks(json.loads(layout.read_text())))
    return bool(blocks) and all(block["mod"] == "klaude-tabs" for block in blocks)


def apply(repository, home):
    targets = entries(repository, home)
    layout = home / ".config/herdr-app/layouts/main.json"
    if not layout.is_file() or layout.is_symlink():
        raise RuntimeError(f"请先启动 Herdr app 生成本机 main 布局，或检查已有布局链接：{layout}")
    original = layout.read_text()
    document = json.loads(original)
    blocks = list(tab_blocks(document))
    if not blocks:
        raise RuntimeError(f"main 布局没有可替换的 tabs，原布局已保留：{layout}")
    for path, source in targets.items():
        if not source.is_file():
            raise RuntimeError(f"缺少 Herdr app mod：{source}")
        if path.exists() and not path.is_symlink() and not path.is_file():
            raise RuntimeError(f"mod 目标不是文件，原内容已保留：{path}")
    for path in (*targets, layout):
        for parent in path.parents:
            if parent == home:
                break
            if parent.is_symlink() or (parent.exists() and not parent.is_dir()):
                raise RuntimeError(f"配置父路径不是普通目录，原内容已保留：{parent}")
    replace_layout = any(block["mod"] == "tabs" for block in blocks)
    pending = {
        path: source for path, source in targets.items()
        if not (path.is_symlink() and path.exists() and path.samefile(source))
    }
    if not pending and not replace_layout:
        return
    backups = home / ".local/state/dotfiles/backups"
    backups.mkdir(parents=True, exist_ok=True)
    backup = Path(tempfile.mkdtemp(prefix="klaude-menu-", dir=backups))
    print(f"Herdr app 菜单及布局备份：{backup}", flush=True)
    for path, source in pending.items():
        if os.path.lexists(path):
            saved = backup / path.relative_to(home)
            saved.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(path), saved)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.symlink_to(os.path.relpath(source.resolve(), path.parent.resolve()))
    if replace_layout:
        saved = backup / layout.relative_to(home)
        saved.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(layout, saved)
        if layout.read_text() != original:
            raise RuntimeError("Herdr app 布局已变化，未覆盖，请重试更新")
        for block in blocks:
            block["mod"] = "klaude-tabs"
        with tempfile.NamedTemporaryFile(mode="w", dir=layout.parent, delete=False) as stream:
            json.dump(document, stream, indent=2, ensure_ascii=False)
            stream.write("\n")
        os.replace(stream.name, layout)