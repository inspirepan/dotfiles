"""Retire the legacy Herdr CLI config link without touching Herdr app."""

from pathlib import Path
import shutil
import tempfile

DESCRIPTION = "移除旧 Herdr CLI 配置链接，保留 Herdr app"


def check(repository, home):
    path = home / ".config/herdr/config.toml"
    source = repository / "config/.config/herdr/config.toml"
    return not (path.is_symlink() and path.resolve() == source.resolve())


def apply(repository, home):
    if check(repository, home):
        return
    path = home / ".config/herdr/config.toml"
    backups = home / ".local/state/dotfiles/backups"
    backups.mkdir(parents=True, exist_ok=True)
    backup = Path(tempfile.mkdtemp(prefix="herdr-cli-config-", dir=backups))
    shutil.move(str(path), backup / "config.toml")
    print(f"旧 Herdr CLI 配置链接备份：{backup}", flush=True)