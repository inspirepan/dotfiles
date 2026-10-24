#!/usr/bin/env zsh
# Run the dotfiles entry point from any directory.
set -eu

DOTFILES="$(cd "$(dirname "$0")/.." && pwd)"
exec uv run --script "$DOTFILES/scripts/dotfiles.py" "$@"
