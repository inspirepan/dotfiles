# ZSH 选项
setopt AUTO_CD
setopt CORRECT
setopt INTERACTIVE_COMMENTS
setopt NO_BEEP

# OMZ
export ZSH="$HOME/.oh-my-zsh"
ZSH_THEME="jj"
ZSH_AUTOSUGGEST_STRATEGY=(history completion)
ZSH_AUTOSUGGEST_BUFFER_MAX_SIZE=20
plugins=(git zsh-autosuggestions zsh-syntax-highlighting globalias)
source $ZSH/oh-my-zsh.sh

# 终端标题（省略 username@host 前缀）
ZSH_THEME_TERM_TITLE_IDLE="%~"
ZSH_THEME_TERM_TAB_TITLE_IDLE="%15<..<%~%<<"

# PATH
typeset -U path
export GOPATH="$HOME/go"
path=(
  $HOME/.local/bin
  $HOME/.bun/bin
  $GOPATH/bin
  $path
)

# ZOXIDE
eval "$(zoxide init zsh)"

# BAT
export BAT_THEME=ansi

# 别名
alias ll="eza -l --group-directories-first --hyperlink --no-user"
alias la="eza -la --group-directories-first --hyperlink --no-user"
alias tree="tree --gitignore"
alias lg="lazygit"
alias kl="klaude"

# 密钥（token、API key，不会被 dotfiles 跟踪）
[[ -f ~/.zshenv.secret ]] && source ~/.zshenv.secret

# gclone：把 GitHub 仓库克隆到 ~/code/GITHUB 下的 org-repo 目录
gclone() {
  local url="$1"
  local cwd="$PWD"

  if [[ -z "$url" ]]; then
    echo "用法：gclone <git-url>"
    return 1
  fi

  # 从常见的 GitHub URL 格式中提取 org 和 repo
  if [[ "$url" =~ github\.com[:/]+([^/]+)/([^/.]+)(\.git)?$ ]]; then
    local org="${match[1]}"
    local repo="${match[2]}"
    local dir="${org}-${repo}"

    mkdir -p "$HOME/code/GITHUB" || return 1

    if git -C "$HOME/code/GITHUB" clone "$url" "$dir"; then
      cd "$HOME/code/GITHUB/$dir" || cd "$cwd"
    else
      cd "$cwd"
      return 1
    fi
  else
    if git clone "$url"; then
      local repo_name
      repo_name="${url##*/}"
      repo_name="${repo_name%.git}"
      if [[ -d "$repo_name" ]]; then
        cd "$repo_name" || cd "$cwd"
      fi
    else
      return 1
    fi
  fi
}

# try
eval "$(ruby ~/.local/try.rb init ~/code/try)"

# bun 补全
[ -s "$HOME/.bun/_bun" ] && source "$HOME/.bun/_bun"

# Anthropic
export DISABLE_TELEMETRY=1
alias cld="claude --dangerously-skip-permissions"
alias cldt="claude-trace --dangerously-skip-permissions"

# Homebrew 镜像（清华）
export HOMEBREW_BREW_GIT_REMOTE="https://mirrors.tuna.tsinghua.edu.cn/git/homebrew/brew.git"
export HOMEBREW_CORE_GIT_REMOTE="https://mirrors.tuna.tsinghua.edu.cn/git/homebrew/homebrew-core.git"
export HOMEBREW_BOTTLE_DOMAIN="https://mirrors.tuna.tsinghua.edu.cn/homebrew-bottles"
export HOMEBREW_API_DOMAIN="https://mirrors.tuna.tsinghua.edu.cn/homebrew-bottles/api"

# ripgrep 配置
export RIPGREP_CONFIG_PATH="$HOME/.config/ripgrep/config"

# mkdir + cd
unalias md 2>/dev/null
md() { mkdir -p "$1" && cd "$1"; }
