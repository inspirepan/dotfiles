#!/bin/bash
# Link Ghostty's macOS app config to the dotfiles-managed config.
set -euo pipefail

DOTFILES="$(cd "$(dirname "$0")/.." && pwd)"
SOURCE="$DOTFILES/config/.config/ghostty/config"
TARGET_DIR="$HOME/Library/Application Support/com.mitchellh.ghostty"
TARGET="$TARGET_DIR/config"

mkdir -p "$TARGET_DIR"

if [[ -L "$TARGET" && "$(readlink "$TARGET")" == "$SOURCE" ]]; then
  echo ">>> Ghostty config already linked"
  exit 0
fi

if [[ -e "$TARGET" || -L "$TARGET" ]]; then
  BACKUP_DIR="$HOME/.dotfiles-migration-backup-$(date +%Y%m%d-%H%M%S)/Library/Application Support/com.mitchellh.ghostty"
  mkdir -p "$BACKUP_DIR"
  mv "$TARGET" "$BACKUP_DIR/config"
  echo ">>> Backed up existing Ghostty config to $BACKUP_DIR/config"
fi

ln -sfn "$SOURCE" "$TARGET"
echo ">>> Linked Ghostty config to $SOURCE"
