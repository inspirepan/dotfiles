#!/bin/bash
# Copy Ghostty terminfo to a remote host via SSH.
# Fixes duplicate character display when using Ghostty + SSH.
#
# Usage: ./setup-ghostty-terminfo.sh user@host [user@host2 ...]
set -e

if [[ $# -eq 0 ]]; then
  echo "用法: $0 user@host [user@host2 ...]"
  exit 1
fi

if ! infocmp -x xterm-ghostty &>/dev/null; then
  echo "错误: 本地没有 xterm-ghostty terminfo，请先安装 Ghostty"
  exit 1
fi

for host in "$@"; do
  echo ">>> 正在传输 xterm-ghostty terminfo 到 $host ..."
  infocmp -x xterm-ghostty | ssh "$host" 'tic -x -'
  echo ">>> $host 完成"
done
