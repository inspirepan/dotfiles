# dotfiles

使用 [GNU Stow](https://www.gnu.org/software/stow/) 管理的个人 macOS 配置文件。

完整的新机器初始化清单见 [docs/setup-guide.md](docs/setup-guide.md)。

## 快速开始

```bash
cd ~/code/dotfiles
brew install stow
stow -t ~ zsh git config ssh
```

## 目录结构

```
dotfiles/
  Brewfile                  # Homebrew 包声明
  zsh/                      # .zshrc、别名、函数
  git/                      # .gitconfig（含条件 include）
  config/.config/           # ghostty、jj、karabiner、ripgrep、zed 等
  ssh/                      # SSH 配置
  omz-custom/               # 自定义 oh-my-zsh 主题（jj.zsh-theme）
  themes/                   # 自定义主题（VSCode、Ghostty）
  skills/                   # Claude Code / klaude 的 agent skills
  scripts/                  # 初始化脚本
  docs/                     # 设置指南、代理笔记、字体清单
```

## 特色配置

### Blue Light 主题

自制的浅色主题，同时移植到 VSCode 和 Ghostty。

- **VSCode**：打包为 vsix，位于 `themes/vscode-blue-light/`，安装方式：`code --install-extension *.vsix`
- **Ghostty**：主题文件在 `config/.config/ghostty/themes/`，支持跟随系统自动切换明暗：
  ```
  theme = light:blue-light,dark:blue-light-dark
  ```

### Jujutsu (jj) 工作流

这个仓库使用 [Jujutsu](https://github.com/jj-vcs/jj) 作为主要版本控制工具（Git 后端）。围绕 jj 构建了几个组件：

**Shell 别名**（`zsh/.zsh_aliases`）：

| 别名 | 命令 |
|------|------|
| `jjl` | `jj log` |
| `jjs` | `jj status` |
| `jjd` | `jj diff` |
| `jjf` | `jj git fetch` |
| `jjb` | `jj bookmark list --all` |
| `jja` | `jjui -r 'all()'` |
| `jjnm` | `jj git fetch && jj new main@origin` |
| `jjt <bookmark> [remote]` | `jj bookmark track <bookmark> --remote=<remote>` |

**自定义 zsh 提示符**（`omz-custom/themes/jj.zsh-theme`）：两行提示符，优先检测 jj 仓库（回退到 git），显示 change id、描述、diff 统计、距 trunk 的 commit 数、冲突/空提交标记、活动 bookmark。还会显示 agent 上下文（CLAUDE.md、skills 数量）。

**Commit skill**（`skills/commit/`）：一个 Claude Code / klaude 的 [agent skill](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/claude-code-skills)，自动执行 `jj describe` / `jj split`，生成 Conventional Commit 格式的提交信息。它会检查工作区状态，推断出一个内聚的提交边界，干净地拆分变更。

### Karabiner 按键映射

`config/.config/karabiner/karabiner.json` 为外接键盘重映射修饰键：

| 物理按键 | 映射为 |
|---------|--------|
| Caps Lock | Left Command |
| Left Command | Left Control |
| Left Control | Caps Lock |

把 Command 放到 Caps Lock 的位置（本位行），方便触发快捷键。仅对外接键盘生效（通过 vendor/product ID 过滤），Mac 内置键盘不受影响。

### 其他别名和函数

| 命令 | 说明 |
|------|------|
| `port <n>` | 查看占用指定端口的进程 |
| `pid <name>` | 搜索正在运行的进程 |
| `ram` | 按应用名汇总内存占用排行 |
| `md <dir>` | mkdir + cd |
| `gclone <url>` | 克隆 GitHub 仓库到 `~/code/GITHUB/org-repo` 并进入目录 |
| `cwd` | 复制当前路径到剪贴板 |

### macOS 系统设置

`scripts/macos-defaults.sh` 通过 `defaults write` 配置：
- Dock：放在右侧、开启放大、隐藏最近使用和活动指示器
- 访达：显示路径栏和状态栏、默认搜索当前文件夹
- 键盘：F 键用作标准功能键、关闭自动大写/句号/智能引号/拼写纠正
- Spotlight：禁用 Cmd+Space（让给 Raycast）
- 台前调度：启用
- 文件关联：常见代码文件默认用 VSCode 打开（通过 `duti`）

### 代理 + Tunnel 共存

[docs/proxy-tunnel.md](docs/proxy-tunnel.md) 记录了 FlClash TUN 模式与 Cloudflare Tunnel、Tailscale、SSH 的共存方案。`scripts/setup-flclash.sh` 可以一键注入覆写规则。
