"""Verify the shared key configuration for Cmd+K sending Ctrl+L."""

DESCRIPTION = "Herdr app 将 Cmd+K 映射为 Ctrl+L 清屏"


def check(repository, home):
    source = repository / "config/.config/herdr-app/keys.json"
    target = home / ".config/herdr-app/keys.json"
    return source.is_file() and target.is_symlink() and target.exists() and target.samefile(source)


def apply(repository, home):
    # Step 001 links and repairs the current shared configuration first.
    raise RuntimeError("Herdr app 快捷键未链接到仓库配置，请先检查 001 配置迁移步骤")