#!/bin/bash
# Install Ghostty terminfo (xterm-ghostty) locally or on remote hosts.
# Fixes duplicate character display when using Ghostty + SSH.
#
# Usage:
#   ./setup-ghostty-terminfo.sh              # install locally
#   ./setup-ghostty-terminfo.sh user@host    # install on remote host(s)
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
TERMINFO_FILE="$SCRIPT_DIR/../config/.config/ghostty/xterm-ghostty.terminfo"

get_terminfo() {
  if [[ -f "$TERMINFO_FILE" ]]; then
    cat "$TERMINFO_FILE"
  elif infocmp -x xterm-ghostty &>/dev/null; then
    infocmp -x xterm-ghostty
  else
    echo "错误: 找不到 xterm-ghostty terminfo（$TERMINFO_FILE 不存在，本地也未安装）" >&2
    exit 1
  fi
}

if [[ $# -eq 0 ]]; then
  echo ">>> 正在本地安装 xterm-ghostty terminfo ..."
  get_terminfo | tic -x -
  echo ">>> 本地安装完成"
else
  for host in "$@"; do
    echo ">>> 正在传输 xterm-ghostty terminfo 到 $host ..."
    get_terminfo | ssh "$host" 'tic -x -'
    echo ">>> $host 完成"
  done
fi
