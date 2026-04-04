#!/bin/bash
# 安装 oh-my-zsh 和插件
set -e

export ZSH="${ZSH:-$HOME/.oh-my-zsh}"

if [[ ! -d "$ZSH" ]]; then
  echo ">>> 正在安装 oh-my-zsh ..."
  export RUNZSH=no
  export CHSH=no
  sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"
else
  echo ">>> 已安装 oh-my-zsh，跳过"
fi

ZSH_CUSTOM="${ZSH_CUSTOM:-$ZSH/custom}"

echo ">>> 正在安装 zsh-autosuggestions"
if [[ ! -d "$ZSH_CUSTOM/plugins/zsh-autosuggestions" ]]; then
  git clone https://github.com/zsh-users/zsh-autosuggestions "$ZSH_CUSTOM/plugins/zsh-autosuggestions"
else
  echo "    已存在，跳过"
fi

echo ">>> 正在安装 zsh-syntax-highlighting"
if [[ ! -d "$ZSH_CUSTOM/plugins/zsh-syntax-highlighting" ]]; then
  git clone https://github.com/zsh-users/zsh-syntax-highlighting "$ZSH_CUSTOM/plugins/zsh-syntax-highlighting"
else
  echo "    已存在，跳过"
fi

echo ">>> globalias 已内置于 oh-my-zsh，只需在 plugins=() 中启用"

DOTFILES="$(cd "$(dirname "$0")/.." && pwd)"
echo ">>> 正在从 dotfiles 链接 jj.zsh-theme"
ln -sf "$DOTFILES/omz-custom/themes/jj.zsh-theme" "$ZSH_CUSTOM/themes/jj.zsh-theme"

echo ">>> 完成。请重启 shell，或执行：source ~/.zshrc"
