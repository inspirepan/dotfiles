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
export ANTHROPIC_API_KEY="..."
```

10. 配置 Homebrew 镜像（加速国内下载）：

```bash
export HOMEBREW_BREW_GIT_REMOTE="https://mirrors.tuna.tsinghua.edu.cn/git/homebrew/brew.git"
export HOMEBREW_CORE_GIT_REMOTE="https://mirrors.tuna.tsinghua.edu.cn/git/homebrew/homebrew-core.git"
export HOMEBREW_BOTTLE_DOMAIN="https://mirrors.tuna.tsinghua.edu.cn/homebrew-bottles"
export HOMEBREW_API_DOMAIN="https://mirrors.tuna.tsinghua.edu.cn/homebrew-bottles/api"
brew update
```

> 这些变量在 Phase 3 stow 后会由 `.zshrc` 永久生效，这里先手动 export 以加速 Phase 1。

11. 启动 agent：

```bash
cd ~/code/dotfiles && klaude
```

> 从此处开始，告诉 klaude "按 docs/setup-guide.md 从 Phase 1 开始执行"。

---

## Phase 1：Homebrew 全量安装

```bash
brew bundle --file=~/code/dotfiles/Brewfile
```

以下包需要 sudo 安装 pkg，agent 无法自动执行，需手动在终端运行：

```bash
brew install --cask karabiner-elements  # 键盘映射
brew install --cask tailscale           # VPN（必须用 cask，formula 只有 CLI 没有菜单栏 GUI）
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

## Phase 3：Stow 配置文件

```bash
cd ~/code/dotfiles
stow --no-folding -t ~ zsh git config ssh
```

这会创建以下符号链接：
- `~/.zshrc` -> `dotfiles/zsh/.zshrc`
- `~/.zsh_aliases` -> `dotfiles/zsh/.zsh_aliases`
- `~/.gitconfig` -> `dotfiles/git/.gitconfig`
- `~/.gitconfig-github` -> `dotfiles/git/.gitconfig-github`
- `~/.config/ghostty/config` -> `dotfiles/config/.config/ghostty/config`
- `~/.config/ghostty/themes/blue-light` -> `dotfiles/config/.config/ghostty/themes/blue-light`
- `~/.config/ghostty/themes/blue-light-dark` -> `dotfiles/config/.config/ghostty/themes/blue-light-dark`
- `~/.config/ripgrep/config` -> `dotfiles/config/.config/ripgrep/config`
- `~/.config/jj/config.toml` -> `dotfiles/config/.config/jj/config.toml`
- `~/.config/jjui/config.toml` -> `dotfiles/config/.config/jjui/config.toml`
- `~/.config/zed/settings.json` -> `dotfiles/config/.config/zed/settings.json`
- `~/.config/karabiner/karabiner.json` -> `dotfiles/config/.config/karabiner/karabiner.json`
- `~/.config/git/ignore` -> `dotfiles/config/.config/git/ignore`
- `~/.ssh/config` -> `dotfiles/ssh/.ssh/config`

安装 Ghostty terminfo（让其他设备 SSH 进来时终端渲染正常）：

```bash
~/code/dotfiles/scripts/setup-ghostty-terminfo.sh
```

**注意**：Karabiner-Elements 第一次启动时可能不接受符号链接配置。
如果它覆盖了符号链接，就先改为直接复制文件，之后再重新 `stow`。

## Phase 4：开发工具

```bash
# Python
uv python install 3.14 --default

# bun（JavaScript）
curl -fsSL https://bun.com/install | bash

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
npm i -g @mariozechner/pi-coding-agent
npm i -g wrangler
npm i -g pptxgenjs
```

## Phase 5：主题

Ghostty 主题已通过 stow 管理（`config/.config/ghostty/themes/`），Phase 3 的 stow 会自动创建符号链接。

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

## Phase 7：密钥（补充）

在 `~/.zshenv.secret` 中补充其余 API key（ANTHROPIC_API_KEY 已在 Phase 0 设置）：

```bash
export OPENAI_API_KEY="..."
# ... 其他密钥
```

## Phase 8：应用登录与同步

- [ ] [manual] Notion：登录并同步 workspace
- [ ] [manual] Spotify：登录
- [ ] [manual] Tailscale：登录并授权网络扩展
- [ ] [manual] VSCode：用 GitHub 登录并同步设置 / 扩展


## Phase 9：macOS 偏好设置

运行 defaults 脚本：

```bash
~/code/dotfiles/scripts/macos-defaults.sh
```

这会配置：
- Dock：大小 58，放在右侧，开启放大，隐藏最近使用项目，不按最近使用自动重排 Spaces
- 触发角：左下角调度中心，右下角快速备忘录
- 访达：显示路径栏和状态栏，默认搜索当前文件夹，关闭修改扩展名警告，新窗口打开个人目录，列表视图，显示隐藏文件和扩展名，文件夹置顶
- 键盘：F 键用作标准功能键、关闭自动大写、双空格句号、智能破折号 / 引号、拼写纠正
- 台前调度：启用

剩余需要手动完成：
- [ ] 充电上限设为 80%：**系统设置 -> 电池 -> 充电 -> (i)** -> 设置限制为 80%（需 macOS Tahoe 26.4+；旧版可用 `brew install batt` 后 `sudo batt limit 80`）
- [ ] Karabiner-Elements：启动，授权辅助功能和输入监控权限，确认按键映射已正确加载
- [ ] Stats：启动，授权辅助功能权限，配置菜单栏显示项
- [ ] BetterDisplay：启动，授权辅助功能和屏幕录制权限，配置显示参数
- [ ] Mos：启动，授权辅助功能权限，配置鼠标滚轮平滑和方向
- [ ] Itsycal：启动，授权日历访问权限，配置日期格式
- [ ] Raycast：启动，授权辅助功能权限，导入设置备份
- [ ] Snipaste：启动，授权屏幕录制权限

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
- [ ] OrbStack
- [ ] FlClash TUN 模式覆写规则（SSH / Cloudflare Tunnel / Tailscale 直连）：
  ```bash
  ~/code/dotfiles/scripts/setup-flclash.sh
  ```
  详细说明见 [proxy-tunnel.md](proxy-tunnel.md)
