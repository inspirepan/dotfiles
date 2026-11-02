"""Verify the shared Blue Light interface themes."""

DESCRIPTION = "Herdr app 界面使用 Blue Light 深浅配色"
FILES = ("themes/blue-light.json", "themes/blue-light-dark.json")


def check(repository, home):
    return all(
        (source := repository / "config/.config/herdr-app" / name).is_file()
        and (target := home / ".config/herdr-app" / name).is_symlink()
        and target.exists()
        and target.samefile(source)
        for name in FILES
    )


def apply(repository, home):
    # Step 002 links the shared themes first.
    raise RuntimeError("Herdr app 主题未链接到仓库配置，请先检查 002 配置迁移步骤")
