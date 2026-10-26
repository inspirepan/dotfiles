"""Verify the personal agents mod link after the folder label update."""

DESCRIPTION = "Herdr app Agents 只显示文件夹名，固定时间与图钉宽度"


def check(repository, home):
    source = repository / "config/.config/herdr-app/mods/klaude-agents/main.js"
    target = home / ".config/herdr-app/mods/klaude-agents/main.js"
    return source.is_file() and target.is_symlink() and target.exists() and target.samefile(source)


def apply(repository, home):
    # Step 006 maintains the personal agents mod link first.
    raise RuntimeError("Herdr app Agents mod 未链接到仓库配置，请先检查 006 更新步骤")