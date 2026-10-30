"""Link personal Herdr app preferences without sharing runtime state."""

import os
from pathlib import Path
import shutil
import tempfile

DESCRIPTION = "管理 Herdr app 个人配置和 Klaude 启动入口"
FILES = (
    "keys.json",
    "settings.json",
    "programs.json",
    "themes/tokyo-night.json",
    "themes/tokyo-night-day.json",
)


def entries(repository, home):
    return {
        home / ".config/herdr-app" / name: repository / "config/.config/herdr-app" / name
        for name in FILES
    }


def check(repository, home):
    return all(
        source.is_file() and path.is_symlink() and path.exists() and path.samefile(source)
        for path, source in entries(repository, home).items()
    )


def apply(repository, home):
    targets = entries(repository, home)
    for path, source in targets.items():
        if not source.is_file():
            raise RuntimeError(f"缺少 Herdr app 配置：{source}")
        if path.exists() and not path.is_symlink() and not path.is_file():
            raise RuntimeError(f"配置目标不是文件，原内容已保留：{path}")
        for parent in path.parents:
            if parent == home:
                break
            if parent.is_symlink() or (parent.exists() and not parent.is_dir()):
                raise RuntimeError(f"配置父路径不是普通目录，原内容已保留：{parent}")
    backup = None
    for path, source in targets.items():
        if path.is_symlink() and path.exists() and path.samefile(source):
            continue
        if os.path.lexists(path):
            if backup is None:
                backups = home / ".local/state/dotfiles/backups"
                backups.mkdir(parents=True, exist_ok=True)
                backup = Path(tempfile.mkdtemp(prefix="herdr-app-", dir=backups))
                print(f"Herdr app 原配置备份：{backup}", flush=True)
            saved = backup / path.relative_to(home)
            saved.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(path), saved)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.symlink_to(os.path.relpath(source, path.parent))