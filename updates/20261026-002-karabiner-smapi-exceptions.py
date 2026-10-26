"""Keep the Karabiner configuration linked to the repository."""

import os

DESCRIPTION = "Karabiner 在 Steam 和星露谷物语（含 SMAPI）中停用全部按键映射"


def check(repository, home):
    source = repository / "config/.config/karabiner/karabiner.json"
    target = home / ".config/karabiner/karabiner.json"
    return source.is_file() and target.is_symlink() and target.exists() and target.samefile(source)


def apply(repository, home):
    if check(repository, home):
        return
    target = home / ".config/karabiner/karabiner.json"
    source = repository / "config/.config/karabiner/karabiner.json"
    if os.path.lexists(target):
        raise RuntimeError(f"需要先比较并合并已有 Karabiner 配置：{target}；原内容已保留")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.symlink_to(os.path.relpath(source, target.parent))
