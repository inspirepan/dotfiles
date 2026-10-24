# Dotfiles

个人 macOS dotfiles 仓库。配置文件用 GNU Stow 管理 symlink，手动步骤用 markdown 文档记录，供 agent 阅读后协助配置新机器。

## 目录结构

- `zsh/`, `git/`, `ssh/`, `config/`, `claude/`, `codex/`, `klaude/` -- stow 包，目录结构镜像 `$HOME`。执行 `cd ~/code/dotfiles && stow --no-folding -t ~ zsh git config ssh claude codex klaude` 创建 symlink。Ghostty 自定义主题在 `config/.config/ghostty/themes/` 中。
- `omz-custom/` -- oh-my-zsh 自定义主题 (`jj.zsh-theme`)，由 `scripts/setup-omz.sh` 链接到 `~/.oh-my-zsh/custom/themes/`。
- `themes/` -- 自定义主题。`themes/vscode-blue-light/` 存放 VSCode 主题源文件和 vsix。
- `Brewfile` -- 所有 Homebrew formulae、cask 和字体。
- `skills/` -- 历史个人技能源码；已有安装不由新同步器自动接管或覆盖。通用技能内容统一维护在 `agent-skills` 仓库。
- `Skillfile.json` -- 共享技能源仓库、固定的完整提交和启用列表；由 `scripts/setup-skills.sh` 调用 Vercel Skills CLI 安装给 Codex / Claude Code，klaude 读取共享目录。
- `templates/` -- 需要合并到本机文件的配置片段，不直接 stow；目前包含 Claude Code 的无凭证设置。
- `scripts/` -- 辅助脚本（oh-my-zsh 安装、macOS 系统设置、skills 安装）。
- `docs/` -- 安装指南和参考笔记。

## 关键文件

| 文件 | 用途 |
|------|------|
| `docs/setup-guide.md` | 新机器配置清单（Phase 0 手动 bootstrap，Phase 1-10 agent 执行） |
| `docs/fonts.md` | 字体清单（brew 安装） |
| `docs/proxy-tunnel.md` | FlClash TUN 与 Cloudflare Tunnel/Tailscale 共存方案 |
| `Brewfile` | `brew bundle --file=Brewfile` 一次装齐所有包 |
| `scripts/setup-omz.sh` | 安装 oh-my-zsh + 插件 + jj 主题 |
| `scripts/macos-defaults.sh` | 通过 `defaults write` 设置 macOS 系统偏好 |
| `scripts/setup-skills.sh` | 共享技能同步入口，支持 `--check`，严格跟随清单提交 |
| `scripts/dotfiles.sh` | `init` 初始化、`status` 检查、`update` 顺序增量更新 |
| `updates/` | 已发布更新不可改写，新增步骤承载后续配置变化 |
| `Skillfile.json` | 固定来源版本与启用列表 |
| `docs/third-party-skills.md` | 第三方技能来源与上游直装命令，只记录、不自动安装 |

## 约定

- 配置文件放 stow 包里，文档和手动步骤放 `docs/`。
- 密钥、API key、token 不入库。放在 `~/.zshenv.secret`（被 `.zshrc` source）。
- Agent 配置维护 Klaude、Claude Code，以及 Codex 的共享指令入口。`claude/.claude/CLAUDE.md` 是 Claude / Codex 的唯一共享指令源；`codex/.codex/AGENTS.md` 链接到它。Claude 的 `settings.json` 与生成 hook 不入库，Klaude 仅维护无凭证配置，认证文件不入库。
- 新增配置时同步更新 `docs/setup-guide.md`。
- VSCode 配置由其自带的 Settings Sync 管理，不在这里维护。

## 共享技能与设备更新

- 技能正文在 `agent-skills` 维护；固定提交与启用项在 `Skillfile.json`；安装委托给 `npx skills`。
- `scripts/setup-skills.sh --check` 检查；已有个人内容保留并返回 2，不得将冲突标为已完成。
- 新设备按安装指南运行 `scripts/dotfiles.sh init`；已有设备拉取后运行 `status` 和 `update`。
- 恢复维护时先运行 `scripts/dotfiles.sh status`，读取未完成步骤及其依赖；不要重复加载整份历史。
- 每次影响设备配置的变化新增 `updates/` 步骤，不改写已发布步骤；见 `updates/README.md`。
- 验证：`uv run --no-project python -m unittest discover -s tests -v`。
