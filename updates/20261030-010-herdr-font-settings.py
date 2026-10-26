"""Verify the shared Herdr settings link after the font and zoom update."""

DESCRIPTION = "Herdr app 使用 TX-02-Variable / Geist 字体和 1.1 缩放"


def check(repository, home):
    source = repository / "config/.config/herdr-app/settings.json"
    target = home / ".config/herdr-app/settings.json"
    return source.is_file() and target.is_symlink() and target.exists() and target.samefile(source)


def apply(repository, home):
    # Step 001 links and repairs the current shared configuration first.
    raise RuntimeError("Herdr app 设置未链接到仓库配置，请先检查 001 配置迁移步骤")