"""Install selected skills through the standard CLI."""

import importlib.util
import subprocess
import os

DESCRIPTION = "通过 npx skills 安装固定版本的共享技能"


def installer(repository):
    spec = importlib.util.spec_from_file_location("dotfiles_skills", repository / "scripts/install-skills.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def check(repository, home):
    _, pending, conflicts = installer(repository).plan(repository, home)
    return not pending and not conflicts


def apply(repository, home):
    subprocess.run([str(repository / "scripts/setup-skills.sh")], env={**os.environ, "HOME": str(home)}, check=True)
