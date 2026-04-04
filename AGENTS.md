# Dotfiles

个人 macOS dotfiles 仓库。配置文件用 GNU Stow 管理 symlink，手动步骤用 markdown 文档记录，供 agent 阅读后协助配置新机器。

## 目录结构

- `zsh/`, `git/`, `ssh/`, `config/` -- stow 包，目录结构镜像 `$HOME`。执行 `cd ~/code/dotfiles && stow zsh git config ssh` 创建 symlink。Ghostty 自定义主题在 `config/.config/ghostty/themes/` 中。
- `omz-custom/` -- oh-my-zsh 自定义主题 (`jj.zsh-theme`)，由 `scripts/setup-omz.sh` 复制到 `~/.oh-my-zsh/custom/themes/`。
- `themes/` -- 自定义主题。`themes/vscode-blue-light/` 存放 VSCode 主题源文件和 vsix。
- `fonts/` -- 手动安装的字体文件（brew 装不了的）。包含商业/内部字体，仓库应保持 **private**。
- `Brewfile` -- 所有 Homebrew formulae、cask 和字体。
- `scripts/` -- 辅助脚本（oh-my-zsh 安装、macOS 系统设置）。
- `docs/` -- 安装指南和参考笔记。

## 关键文件

| 文件 | 用途 |
|------|------|
| `docs/setup-guide.md` | 新机器配置的有序清单（Phase 1-12） |
| `docs/fonts.md` | 字体清单：brew 可装 vs 手动安装 |
| `docs/proxy-tunnel.md` | Clash/Mihomo 与 Cloudflare Tunnel/Tailscale 共存方案 |
| `Brewfile` | `brew bundle --file=Brewfile` 一次装齐所有包 |
| `scripts/setup-omz.sh` | 安装 oh-my-zsh + 插件 + jj 主题 |
| `scripts/macos-defaults.sh` | 通过 `defaults write` 设置 macOS 系统偏好 |

## 约定

- 配置文件放 stow 包里，文档和手动步骤放 `docs/`。
- 密钥、API key、token 不入库。放在 `~/.zshenv.secret`（被 `.zshrc` source）。
- 新增配置时同步更新 `docs/setup-guide.md`。
- VSCode 配置由其自带的 Settings Sync 管理，不在这里维护。
