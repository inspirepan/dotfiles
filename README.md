# dotfiles

使用 [GNU Stow](https://www.gnu.org/software/stow/) 管理的个人 macOS 配置。

## 结构

```text
dotfiles/
  Brewfile              # Homebrew 包声明
  zsh/.zshrc            # Zsh 配置（oh-my-zsh + Pure 风格提示符）
  git/                  # 带条件 include 的 Git 配置
  config/.config/       # XDG 配置（ghostty、jj、ripgrep 等）
  scripts/              # 初始化脚本（oh-my-zsh 等）
  docs/                 # 分步骤设置指南
```

## 快速开始

```bash
# 安装 stow
brew install stow

# 克隆并应用配置
cd ~/code/dotfiles
stow zsh git config
```

## 完整设置

完整的新机器初始化清单见 [docs/setup-guide.md](docs/setup-guide.md)。
