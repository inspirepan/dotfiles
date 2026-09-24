# 新 Mac 设置指南

用于初始化一台全新 macOS 机器的有序清单。

Phase 0 需要手动完成（bootstrap agent）。从 Phase 1 开始，在 dotfiles 目录启动
`klaude`，让 agent 按本指南执行剩余步骤。标记为 `[manual]` 的项目需要人工介入。

## Phase 0：手动 Bootstrap

在新机器上打开终端，按顺序执行：

1. 登录 Apple 账户
2. 安装 WeChat 并登录
3. 安装微信输入法（从微信官网获取）
4. 安装 [FlClash](https://github.com/chen08209/FlClash/releases/)，导入订阅并配置代理
5. 安装 Chrome，登录并同步扩展 / 书签
6. 安装 Homebrew：

先运行 `xcode-select -p` 检查 Command Line Tools；尚未安装时执行 `xcode-select --install` 并完成系统对话框，再安装 Homebrew。

```bash
export https_proxy=http://localhost:7890
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
echo 'eval "$(/opt/homebrew/bin/brew shellenv zsh)"' >> ~/.zprofile
eval "$(/opt/homebrew/bin/brew shellenv zsh)"
brew completions link
```

7. 登录 GitHub 并克隆 dotfiles：

```bash
brew install gh
gh auth login          # 选 SSH，会自动生成 key 并上传

# 克隆前先关掉 FlClash 的 TUN（虚拟网卡）模式，否则 SSH 连接会被截断
mkdir -p ~/code
git clone git@github.com:inspirepan/dotfiles.git ~/code/dotfiles
# 克隆完成后可以重新开启 TUN
```

8. 安装 uv 和 klaude：

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
uv tool install klaude-code
```

9. 创建 `~/.zshenv.secret`，写入 API key：

```bash
export YOUTU_API_KEY="..."
```

这是当前 Klaude 主模型所需的密钥，文件不入库。首次 Stow 前 `.zshrc` 尚未加载它，启动前需显式 source。

10. 启动 agent：

```bash
source ~/.zshenv.secret
cd ~/code/dotfiles && klaude --model gpt-6.1-sol@youtu-openai
```

> 从此处开始，告诉 klaude "按 docs/setup-guide.md 从 Phase 1 开始执行"。

---

## Phase 1：Homebrew 全量安装

> 如果代理已开启可跳过镜像配置。否则在执行 `brew bundle` 前临时设置国内镜像，避免从官方 `formulae.brew.sh` 下载大 JSON / bottle 卡顿：
>
> ```bash
> export HOMEBREW_API_DOMAIN="https://mirrors.tuna.tsinghua.edu.cn/homebrew-bottles/api"
> export HOMEBREW_BOTTLE_DOMAIN="https://mirrors.tuna.tsinghua.edu.cn/homebrew-bottles"
> export HOMEBREW_AUTO_UPDATE_SECS=86400
> ```
>
> 这些变量已写在 `zsh/.zshrc` 中，Phase 3 stow 后永久生效。

```bash
brew bundle --file=~/code/dotfiles/Brewfile
```

其中也会安装 `fzf` 和 `neovim`，供 `fb` 做上下键交互选文件并直接进入只读查看；还会安装
`poppler`（PDF 查看 / 渲染）、`summarize` 和 `mole`。`terminal-notifier` 用于 Herdr 的可选系统通知，单独安装时使用：

```bash
brew install terminal-notifier
```

当前 Herdr 配置使用 `delivery = "terminal"`。若改为 `delivery = "system"` 却没有 `terminal-notifier`，
通知会回退到 `osascript`，可能显示为来自 Script Editor。

以下包需要 sudo 安装 pkg，agent 无法自动执行，需手动在终端运行：

```bash
brew install --cask karabiner-elements  # 键盘映射
brew install --cask tailscale-app       # VPN（必须用 cask，formula 只有 CLI 没有菜单栏 GUI）
brew install --cask font-sf-mono        # Apple 字体
brew install --cask font-sf-pro         # Apple 字体
```

## Phase 2：Oh-my-zsh + 插件

运行初始化脚本：

```bash
~/code/dotfiles/scripts/setup-omz.sh
```

这会安装：
- oh-my-zsh
- zsh-autosuggestions
- zsh-syntax-highlighting
- jj.zsh-theme（带 jj/git 支持的自定义提示符）

核对账户的登录 shell：`dscl . -read "/Users/$USER" UserShell`，正常应为 `/bin/zsh`。
只有当前不是 zsh 时才需要手动切换，不必改成 Homebrew zsh。

## Phase 3：Stow 配置文件

```bash
cd ~/code/dotfiles
stow --no-folding -t ~ zsh git config ssh claude klaude
```

这会创建以下符号链接：
- `~/.zshrc` -> `dotfiles/zsh/.zshrc`
- `~/.zsh_aliases` -> `dotfiles/zsh/.zsh_aliases`
- `~/.gitconfig` -> `dotfiles/git/.gitconfig`
- `~/.config/ghostty/config` -> `dotfiles/config/.config/ghostty/config`
- `~/.config/ghostty/themes/blue-light` -> `dotfiles/config/.config/ghostty/themes/blue-light`
- `~/.config/ghostty/themes/blue-light-dark` -> `dotfiles/config/.config/ghostty/themes/blue-light-dark`
- `~/.config/herdr/config.toml` -> `dotfiles/config/.config/herdr/config.toml`
- `~/.warp/themes/blue-light.yaml` -> `dotfiles/config/.warp/themes/blue-light.yaml`
- `~/.warp/themes/blue-light-dark.yaml` -> `dotfiles/config/.warp/themes/blue-light-dark.yaml`
- `~/.config/ripgrep/config` -> `dotfiles/config/.config/ripgrep/config`
- `~/.config/nvim/init.lua` -> `dotfiles/config/.config/nvim/init.lua`
- `~/.config/jj/config.toml` -> `dotfiles/config/.config/jj/config.toml`
- `~/.config/jjui/config.toml` -> `dotfiles/config/.config/jjui/config.toml`
- `~/.config/zed/settings.json` -> `dotfiles/config/.config/zed/settings.json`
- `~/.config/karabiner/karabiner.json` -> `dotfiles/config/.config/karabiner/karabiner.json`
- `~/.config/git/ignore` -> `dotfiles/config/.config/git/ignore`
- `~/.ssh/config` -> `dotfiles/ssh/.ssh/config`
- `~/.claude/statusline.sh` -> `dotfiles/claude/.claude/statusline.sh`
- `~/.claude/CLAUDE.md` -> `dotfiles/claude/.claude/CLAUDE.md`
- `~/.klaude/klaude-config.yaml` -> `dotfiles/klaude/.klaude/klaude-config.yaml`

若 Stow 提示现有文件冲突，先比较内容，不要直接使用 `--adopt`。本机的 `.zshrc` 和 Klaude YAML
可能是普通文件；合并需要保留的差异后，可先备份这些文件再重跑 Stow：

```bash
backup_dir="$(mktemp -d "$HOME/.dotfiles-migration-backup.XXXXXXXX")"
for file in .zshrc .klaude/klaude-config.yaml; do
  if [ -e "$HOME/$file" ] && [ ! -L "$HOME/$file" ]; then
    mkdir -p "$backup_dir/$(dirname "$file")"
    mv "$HOME/$file" "$backup_dir/$file"
  fi
done
stow --no-folding -t ~ zsh git config ssh claude klaude
```

Claude Code 的 `settings.json` 不入库（会被频繁改写）；Phase 4 从无凭证模板合并 statusline、模型和插件偏好。
Klaude YAML 仅保存模型选择与 provider 开关，禁止加入明文凭证。`/model` 修改可能同步到仓库，提交前检查差异。

安装 Ghostty terminfo（让其他设备 SSH 进来时终端渲染正常）：

```bash
~/code/dotfiles/scripts/setup-ghostty-config.sh
~/code/dotfiles/scripts/setup-ghostty-terminfo.sh
```

Ghostty 配置脚本同时处理 macOS 入口的 `config` 和新版 `config.ghostty`；若已有 XDG `config.ghostty`，
也会先备份再链接到仓库配置，避免另一份配置覆盖字体和主题。

`~/.zshrc` 会在远端缺少 `xterm-ghostty` terminfo 时自动退回 `TERM=xterm-256color`。

**注意**：Karabiner-Elements 第一次启动时可能不接受符号链接配置。
如果它覆盖了符号链接，就先改为直接复制文件，之后再重新 `stow`。

## Phase 4：开发工具

```bash
# Python
uv python install 3.14 --default

# bun（JavaScript）
curl -fsSL https://bun.com/install | bash

# Herdr terminal workspace manager
curl -fsSL https://herdr.dev/install.sh | sh
herdr --version

# jj-hunk for splitting mixed files in the commit skill
cargo install jj-hunk
jj-hunk --help

# try（一次性小项目工具）
mkdir -p ~/.local/lib
curl -sL https://raw.githubusercontent.com/tobi/try/refs/heads/main/try.rb > ~/.local/try.rb
curl -sL https://raw.githubusercontent.com/tobi/try/refs/heads/main/lib/tui.rb > ~/.local/lib/tui.rb
curl -sL https://raw.githubusercontent.com/tobi/try/refs/heads/main/lib/fuzzy.rb > ~/.local/lib/fuzzy.rb
chmod +x ~/.local/try.rb
```

### uv 全局工具

```bash
uv tool install ruff
uv tool install pyright
uv tool install ty
uv tool install llm
```

### npm 全局包

```bash
npm i -g pnpm
npm i -g @anthropic-ai/claude-code
npm i -g @mariozechner/claude-trace
npm i -g agent-browser
npm i -g wrangler
npm i -g pptxgenjs

# 首次安装 agent-browser 后执行一次，下载 Chrome for Testing
agent-browser install
```

### Klaude 与 Claude Code

Agent 配置仅维护这两个工具，不安装或迁移其他 agent 的配置。
Klaude 已在 Phase 0 安装，模型偏好由 Phase 3 的 Stow 管理。当前主模型需要 `YOUTU_API_KEY`，
回退模型需要 `OPENCODE_API_KEY`，放在 `~/.zshenv.secret` 中并加载；运行 `klaude agents` 确认可用。
`klaude auth login` 可交互配置受支持的认证，但不要把模型 provider 名直接当成登录参数；认证文件不入库。
配置中的 `opencode-go` 是 Klaude 的 provider 名称，不需要安装 OpenCode。

Claude 模板为 `templates/claude-settings.json`，记录当前 Bedrock 后端、模型映射、主题、推理强度、插件和状态栏。
这些模型 ID 必须在新机账号中可用；使用其他后端时调整非敏感设置，不要向模板写入凭证。
模板不包含自动授权、跳过权限提示、机器路径或生成 hooks。

先安装官方插件：

```bash
for plugin in pyright-lsp code-review frontend-design code-simplifier skill-creator; do
  claude plugin install "$plugin@claude-plugins-official"
done
```

合并模板，保留原有认证配置、hooks 和无关设置；备份保存在 `~/.claude/settings-backup.*`，含本机配置，不入库：

```bash
(
  set -e
  mkdir -p "$HOME/.claude"
  backup_dir="$(mktemp -d "$HOME/.claude/settings-backup.XXXXXXXX")"
  settings="$HOME/.claude/settings.json"
  if [ -f "$settings" ]; then
    cp -p "$settings" "$backup_dir/original.json"
  else
    printf '{}\n' > "$backup_dir/original.json"
  fi
  jq -s '.[0] * .[1]' "$backup_dir/original.json" \
    ~/code/dotfiles/templates/claude-settings.json > "$backup_dir/merged.json"
  cp "$backup_dir/merged.json" "$settings"
)
```

凭证准备好后运行 `claude`，确认 Bedrock 登录、状态栏和插件正常。
如果使用 Herdr，执行 `herdr integration install claude`，再用 `herdr integration status` 检查。
这会生成并维护 SessionStart hook，不复制旧机器的 hook 文件或绝对路径。
Klaude 在 Herdr 中无需复制 Claude hook；按实际支持情况检查侧栏状态。

可选恢复 GitHub CLI 别名：`gh alias set co 'pr checkout'`；认证仍由 `gh auth login` 管理。

## Phase 5：主题

字体由 Brewfile 安装，包括 Paper Mono 和 STIX Two Math。TX-02 / TX-02-Variable 需按个人授权手动安装，
来源和备用字体见 [fonts.md](fonts.md)。运行 `ghostty +list-fonts` 核对配置引用的 family name。

Ghostty 主题已通过 stow 管理（`config/.config/ghostty/themes/`），Phase 3 的 stow 会自动创建符号链接。

Warp 主题同样通过 stow 管理（`config/.warp/themes/`），Phase 3 的 stow 会链接到 `~/.warp/themes/`。在 Warp 中打开 **Settings -> Appearance -> Themes**（或快捷键 `Cmd+P` 搜索 `Open Theme Picker`）即可选用 `Blue Light` / `Blue Light Dark`。

VSCode 主题从 dotfiles 安装：

```bash
code --install-extension ~/code/dotfiles/themes/vscode-blue-light/blue-light-0.6.4.vsix
```

主题源文件维护在 `themes/vscode-blue-light/`，如需重新打包：

```bash
cd ~/code/dotfiles/themes/vscode-blue-light
npm i -g vsce
vsce package
```

## Phase 6：Agent Skills

```bash
~/code/dotfiles/scripts/setup-skills.sh
```

这会从 `Skillfile` 安装远程 skill，并从 dotfiles 链接本地 skill（如 commit）到 `~/.agents/skills/`。
脚本同时为清单中的 skills 创建 `~/.claude/skills/` 链接，避免 Claude 的旧副本覆盖仓库版本。
已有冲突文件或目录先备份到 `~/.local/state/dotfiles/skills-backups/`，可恢复；不会整目录替换 Claude skills。
远程 skill 默认存在就跳过。主动更新时运行：

```bash
~/code/dotfiles/scripts/setup-skills.sh --update
```

更新按远程默认分支获取最新版本，先下载并验证，再备份旧副本；清单不锁定版本。

## Phase 7：密钥（补充）

在 `~/.zshenv.secret` 中补充其余 API key（`YOUTU_API_KEY` 已在 Phase 0 设置）：

```bash
export OPENCODE_API_KEY="..."
# ... 其他密钥
```

当前 Claude 模板使用 AWS Bedrock，需要自行配置 AWS 凭证与模型访问权限；不能只设置 `ANTHROPIC_API_KEY`。
Klaude 的 provider 认证使用对应环境变量或支持该类型的 `klaude auth login`。不要复制认证 JSON 到 Stow 包，
也不要把 AWS 凭证、API key 或登录状态写入模板。

## Phase 8：应用登录与同步

- [ ] [manual] Notion：登录并同步 workspace
- [ ] [manual] Spotify：登录
- [ ] [manual] Tailscale：登录并授权网络扩展
- [ ] [manual] VSCode：用 GitHub 登录并同步设置 / 扩展
- [ ] [manual] VSCode：核对 Paper Mono、Blue Light 主题、JetBrains 图标主题，以及 Go、Ruff、ty、VisualJJ、Remote SSH 扩展

远端扩展不依赖本机 Settings Sync 自动恢复，连接目标机器后单独核对。


## Phase 9：macOS 偏好设置

运行 defaults 脚本：

```bash
~/code/dotfiles/scripts/macos-defaults.sh
```

这会配置：
- Dock：大小 51，放在右侧，开启放大，隐藏最近使用项目，不按最近使用自动重排 Spaces
- 触发角：左下角调度中心，右下角不分配动作
- 访达：显示路径栏和状态栏，默认搜索当前文件夹，关闭修改扩展名警告，新窗口打开个人目录，列表视图，显示隐藏文件和扩展名，文件夹置顶
- 键盘：F 键用作标准功能键、关闭自动大写、双空格句号、智能破折号 / 引号、拼写纠正
- 台前调度：关闭

剩余需要手动完成：
- [ ] 充电上限设为 80%：**系统设置 -> 电池 -> 充电 -> (i)** -> 设置限制为 80%（需 macOS Tahoe 26.4+；旧版可用 `brew install batt` 后 `sudo batt limit 80`）
- [ ] Karabiner-Elements：启动，授权辅助功能和输入监控权限，确认按键映射已正确加载
- [ ] Stats：启动，授权辅助功能权限，配置菜单栏显示项
- [ ] BetterDisplay：启动，授权辅助功能和屏幕录制权限，配置显示参数
- [ ] Mos：启动，授权辅助功能权限，配置鼠标滚轮平滑和方向
- [ ] Itsycal：启动，授权日历访问权限，配置日期格式
- [ ] Raycast：启动，授权辅助功能权限，导入设置备份
- [ ] [LongShot](https://longshot.chitaner.com/)：从 Mac App Store 安装，启动并授权屏幕录制权限

## Phase 10：Tailscale 与 SSH

Tailscale 在 Phase 1 通过 cask 安装，Phase 8 登录授权。本阶段配置设备名和远程登录。

1. 设置设备主机名（每台机器上各自执行）：

```bash
tailscale set --hostname=pan-mbp-16   # 按实际机器命名
```

2. [manual] 开启远程登录（macOS sshd），允许其他设备通过 SSH 连入：

   **系统设置 -> 通用 -> 共享 -> 远程登录** -> 打开

3. （可选）如果需要 SSH 到未跑过 dotfiles setup 的机器（如 Linux 服务器），传输 terminfo：

```bash
~/code/dotfiles/scripts/setup-ghostty-terminfo.sh user@remote-host
```

> 跑过 dotfiles setup 的机器已在 Phase 3 安装了 terminfo，不需要再传。

4. 验证：从另一台 Tailscale 设备 SSH 连入：

```bash
ssh panjx@pan-mbp-16
```

> MagicDNS 默认开启，可以直接用主机名。如果和 FlClash TUN 模式冲突，参考 [proxy-tunnel.md](proxy-tunnel.md) 关闭。

## Phase 11：可选 / 按需安装

- [ ] Cloudflare Wrangler：`npm i -g wrangler`
- [ ] OrbStack：`brew install --cask orbstack`，首次启动后完成初始化
  - 核对 `~/.zprofile` 是否按需加载 `~/.orbstack/shell/init.zsh`；保留 Phase 0 的 Homebrew 初始化
  - 运行 `docker context ls`，确认 OrbStack context 及 socket 正常；不复制旧机器的 context 或运行目录
  - 若需要代理，设置 `http://127.0.0.1:7890`，排除 `localhost`；与 FlClash 端口一致
- [ ] FlClash TUN 模式覆写规则（SSH / Cloudflare Tunnel / Tailscale 直连）：
  ```bash
  ~/code/dotfiles/scripts/setup-flclash.sh
  ```
  详细说明见 [proxy-tunnel.md](proxy-tunnel.md)
