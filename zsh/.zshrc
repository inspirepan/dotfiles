# ZSH 选项
setopt AUTO_CD
setopt CORRECT
setopt INTERACTIVE_COMMENTS
setopt NO_BEEP
setopt SHARE_HISTORY
setopt HIST_IGNORE_ALL_DUPS
setopt HIST_REDUCE_BLANKS
HISTSIZE=50000
SAVEHIST=50000

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
  /opt/homebrew/opt/ruby/bin
  $HOME/.local/bin
  $HOME/.cargo/bin
  $HOME/.bun/bin
  $GOPATH/bin
  $path
)

bindkey '^[[Z' autosuggest-accept

# ZOXIDE
eval "$(zoxide init zsh)"

# EDITOR
export EDITOR="zed --wait --new"
export VISUAL="$EDITOR"

# BAT
export BAT_THEME=ansi

# 别名和函数
source ~/.zsh_aliases

# 密钥（token、API key，不会被 dotfiles 跟踪）
[[ -f ~/.zshenv.secret ]] && source ~/.zshenv.secret

# try
eval "$(ruby ~/.local/try.rb init ~/code/try)"

# bun 补全
[ -s "$HOME/.bun/_bun" ] && source "$HOME/.bun/_bun"

# Anthropic
export DISABLE_TELEMETRY=1

# ripgrep 配置
export RIPGREP_CONFIG_PATH="$HOME/.config/ripgrep/config"

# Added by LM Studio CLI (lms)
export PATH="$PATH:/Users/panjx/.lmstudio/bin"
# End of LM Studio CLI section

