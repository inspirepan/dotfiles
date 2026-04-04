# 新 Mac 设置指南

用于初始化一台全新 macOS 机器的有序清单。

标记为 `[stow]` 的项目由本仓库中的配置文件管理。
标记为 `[manual]` 的项目需要手动操作。

## 第一阶段：基础项

- [ ] [manual] 登录 Apple 账户
- [ ] [manual] 安装 WeChat 并登录
- [ ] [manual] 安装微信输入法（从微信官网获取）
- [ ] [manual] 安装 Clash Verge，导入订阅并配置代理
- [ ] [manual] 安装 Chrome，登录并同步扩展 / 书签

## 第二阶段：Homebrew

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
eval "$(/opt/homebrew/bin/brew shellenv)"

brew completions link
```

通过 Brewfile 安装全部内容：

```bash
brew bundle --file=~/code/dotfiles/Brewfile
```

## 第三阶段：GitHub

```bash
gh auth login
```

克隆当前 dotfiles 仓库：

```bash
mkdir -p ~/code
git clone git@github.com:inspirepan/dotfiles.git ~/code/dotfiles
```

## 第四阶段：Oh-my-zsh + 插件

运行初始化脚本：

```bash
~/code/dotfiles/scripts/setup-omz.sh
```

这会安装：
- oh-my-zsh
- zsh-autosuggestions
- zsh-syntax-highlighting
- jj.zsh-theme（带 jj/git 支持的自定义提示符）

## 第五阶段：Stow 配置文件

```bash
cd ~/code/dotfiles
brew install stow
stow zsh git config ssh
```

这会创建以下符号链接：
- `~/.zshrc` -> `dotfiles/zsh/.zshrc`
- `~/.gitconfig` -> `dotfiles/git/.gitconfig`
- `~/.gitconfig-github` -> `dotfiles/git/.gitconfig-github`
- `~/.config/ghostty/config` -> `dotfiles/config/.config/ghostty/config`
- `~/.config/ghostty/themes/blue-light.theme` -> `dotfiles/config/.config/ghostty/themes/blue-light.theme`
- `~/.config/ghostty/themes/blue-light-dark.theme` -> `dotfiles/config/.config/ghostty/themes/blue-light-dark.theme`
- `~/.config/ripgrep/config` -> `dotfiles/config/.config/ripgrep/config`
- `~/.config/jj/config.toml` -> `dotfiles/config/.config/jj/config.toml`
- `~/.config/jjui/config.toml` -> `dotfiles/config/.config/jjui/config.toml`
- `~/.config/zed/settings.json` -> `dotfiles/config/.config/zed/settings.json`
- `~/.config/karabiner/karabiner.json` -> `dotfiles/config/.config/karabiner/karabiner.json`
- `~/.config/git/ignore` -> `dotfiles/config/.config/git/ignore`
- `~/.ssh/config` -> `dotfiles/ssh/.ssh/config`

**注意**：Karabiner-Elements 第一次启动时可能不接受符号链接配置。
如果它覆盖了符号链接，就先改为直接复制文件，之后再重新 `stow`。

## 第六阶段：额外开发工具

```bash
# uv（Python）
curl -LsSf https://astral.sh/uv/install.sh | sh
uv python install 3.14 --default

# bun（JavaScript）
curl -fsSL https://bun.com/install | bash

# try（一次性小项目工具）
mkdir -p ~/.local
curl -sL https://raw.githubusercontent.com/tobi/try/refs/heads/main/try.rb > ~/.local/try.rb
chmod +x ~/.local/try.rb
```

### uv 全局工具

```bash
uv tool install ruff
uv tool install pyright
uv tool install ty
uv tool install llm
uv tool install klaude-code
```

### npm 全局包

```bash
npm i -g @anthropic-ai/claude-code
npm i -g @mariozechner/claude-trace
npm i -g @mariozechner/pi-coding-agent
npm i -g wrangler
npm i -g pptxgenjs
```

## 第七阶段：主题

Ghostty 主题已通过 stow 管理（`config/.config/ghostty/themes/`），第五阶段的 `stow config` 会自动创建符号链接。

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

## 第八阶段：密钥

创建 `~/.zshenv.secret`，写入 API key 和 token。这个文件会被 `.zshrc`
加载，但不会被 dotfiles 跟踪。

```bash
# 模板：
export OPENAI_API_KEY="..."
export ANTHROPIC_API_KEY="..."
# ... 其他密钥
```

## 第九阶段：手动安装（不在 brew 中）

- [ ] 字体：`cp ~/code/dotfiles/fonts/* ~/Library/Fonts/`（见 [fonts.md](fonts.md)）

## 第十阶段：应用登录与同步

- [ ] [manual] Notion：登录并同步 workspace
- [ ] [manual] Spotify：登录
- [ ] [manual] Tailscale：登录并授权网络扩展
- [ ] [manual] VSCode：用 GitHub 登录并同步设置 / 扩展
- [ ] [manual] Raycast：导入设置备份
- [ ] [manual] BetterDisplay：配置显示参数
- [ ] [manual] Itsycal：配置日期格式

## 第十一阶段：macOS 偏好设置

运行 defaults 脚本：

```bash
~/code/dotfiles/scripts/macos-defaults.sh
```

这会配置：
- Dock：大小 58，放在右侧，开启放大，隐藏最近使用项目，不按最近使用自动重排 Spaces
- 触发角：左下角调度中心，右下角快速备忘录
- 访达：显示路径栏和状态栏，默认搜索当前文件夹，关闭修改扩展名警告
- 键盘：关闭自动大写、双空格句号、智能破折号 / 引号、拼写纠正
- 台前调度：启用

剩余需要手动完成：
- [ ] Karabiner-Elements：配置已通过 stow 链接，确认按键映射已正确加载

## 第十二阶段：可选 / 按需安装

- [ ] Cloudflare Wrangler：`npm i -g wrangler`
- [ ] OrbStack
- [ ] 代理 + Tunnel / VPN 共存（见 [proxy-tunnel.md](proxy-tunnel.md)）
