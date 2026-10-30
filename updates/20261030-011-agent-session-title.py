"""Verify both personal mod links for generic terminal titles and official layout."""

DESCRIPTION = "Herdr app Agents 与 pane 通用显示终端标题，恢复官方布局约束"
SUPERSEDES = ("20261030-009-agent-folder-label",)


def check(repository, home):
    for mod in ("klaude-agents", "klaude-pane"):
        source = repository / f"config/.config/herdr-app/mods/{mod}/main.js"
        target = home / f".config/herdr-app/mods/{mod}/main.js"
        if not (source.is_file() and target.is_symlink() and target.exists() and target.samefile(source)):
            return False
    return True


def apply(repository, home):
    # Steps 006 and 007 maintain these links first.
    raise RuntimeError("Herdr app Agents 或 pane mod 未链接到仓库配置，请先检查 006、007 更新步骤")