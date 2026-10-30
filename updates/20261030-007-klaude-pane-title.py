"""Deploy a personal agents mod without modifying shipped layouts or runtime state."""

import json
import os
from pathlib import Path
import shutil
import tempfile

DESCRIPTION = "Herdr app pane 显示 Klaude 会话标题"
FILES = ("mods/klaude-pane/main.js", "mods/klaude-pane/mod.json")


def entries(repository, home):
    return {home / '.config/herdr-app' / name: repository / 'config/.config/herdr-app' / name for name in FILES}


def linked(path, source):
    return source.is_file() and path.is_symlink() and path.exists() and path.samefile(source)


def layout_content(home):
    path = home / '.config/herdr-app/layouts/klaude.json'
    for parent in path.parents:
        if parent == home:
            break
        if parent.is_symlink() or (parent.exists() and not parent.is_dir()):
            raise RuntimeError(f"布局父路径不是普通目录，未覆盖：{parent}")
    if path.is_symlink() or not path.is_file():
        raise RuntimeError(f"缺少普通个人布局，未修改：{path}")
    original = path.read_bytes()
    try:
        document = json.loads(original)
        found = []
        def visit(node):
            if not isinstance(node, dict):
                raise ValueError('invalid layout node')
            content = node.get('content')
            if isinstance(content, dict) and 'pane' in content:
                pane = content['pane']
                if not isinstance(pane, dict):
                    raise ValueError('invalid pane')
                header = pane.get('header')
                if not isinstance(header, dict) or not isinstance(header.get('content'), dict):
                    raise ValueError('missing pane header')
                found.append(header['content'])
            for child in node.get('children', []):
                visit(child)
        visit(document)
        if not found or any(content.get('mod') not in ('pane', 'klaude-pane') for content in found):
            raise ValueError('missing or conflicting pane header')
    except (ValueError, TypeError) as error:
        raise RuntimeError(f"个人布局 pane header 缺失或冲突，未修改：{path}") from error
    return path, original, document, found


def check(repository, home):
    try:
        return (all(linked(path, source) for path, source in entries(repository, home).items())
                and all(content['mod'] == 'klaude-pane' for content in layout_content(home)[3]))
    except (OSError, RuntimeError):
        return False


def apply(repository, home):
    layout, original, document, contents = layout_content(home)
    targets = entries(repository, home)
    for path, source in targets.items():
        if not source.is_file():
            raise RuntimeError(f"缺少 Herdr app mod：{source}")
        if path.exists() and not path.is_symlink() and not path.is_file():
            raise RuntimeError(f"mod 目标不是文件，原内容已保留：{path}")
        for parent in path.parents:
            if parent == home:
                break
            if parent.is_symlink() or (parent.exists() and not parent.is_dir()):
                raise RuntimeError(f"配置父路径不是普通目录，原内容已保留：{parent}")
    pending = {path: source for path, source in targets.items() if not linked(path, source)}
    replace_layout = any(content['mod'] == 'pane' for content in contents)
    if not pending and not replace_layout:
        return
    backups = home / '.local/state/dotfiles/backups'
    backups.mkdir(parents=True, exist_ok=True)
    backup = Path(tempfile.mkdtemp(prefix='klaude-pane-', dir=backups))
    print(f"Herdr app 个人 mod 和布局备份：{backup}", flush=True)
    if replace_layout:
        saved = backup / layout.relative_to(home)
        saved.parent.mkdir(parents=True, exist_ok=True)
        saved.write_bytes(original)
        shutil.copystat(layout, saved)
        for content in contents:
            content['mod'] = 'klaude-pane'
        with tempfile.NamedTemporaryFile(mode='w', dir=layout.parent, delete=False) as stream:
            json.dump(document, stream, indent=2, ensure_ascii=False)
            stream.write('\n')
        if layout.is_symlink() or layout.read_bytes() != original:
            raise RuntimeError(f"布局已变化，停止覆盖：{layout}")
        os.replace(stream.name, layout)
    for path, source in pending.items():
        if os.path.lexists(path):
            saved = backup / path.relative_to(home)
            saved.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(path), saved)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.symlink_to(os.path.relpath(source.resolve(), path.parent.resolve()))
