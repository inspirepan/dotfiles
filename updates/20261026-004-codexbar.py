"""Install CodexBar through Homebrew."""

import subprocess

DESCRIPTION = "安装 CodexBar 菜单栏用量查看工具"


def check(repository, home):
    try:
        result = subprocess.run(
            ["brew", "list", "--cask", "codexbar"],
            capture_output=True,
            check=False,
        )
    except FileNotFoundError:
        return False
    return result.returncode == 0


def apply(repository, home):
    if not check(repository, home):
        subprocess.run(["brew", "install", "--cask", "codexbar"], check=True)