#!/bin/bash
# Link Ghostty's macOS app config to the dotfiles-managed config.
set -euo pipefail

DOTFILES="$(cd "$(dirname "$0")/.." && pwd)"
SOURCE="$DOTFILES/config/.config/ghostty/config"
TARGET_DIR="$HOME/Library/Application Support/com.mitchellh.ghostty"

if [[ ! -f "$SOURCE" ]]; then
  echo ">>> Ghostty source config not found: $SOURCE" >&2
  exit 1
fi

# Support both the current filename and pre-1.2.3 Ghostty releases.
TARGETS=("$TARGET_DIR/config" "$TARGET_DIR/config.ghostty")
if [[ -e "$HOME/.config/ghostty/config.ghostty" || -L "$HOME/.config/ghostty/config.ghostty" ]]; then
  TARGETS+=("$HOME/.config/ghostty/config.ghostty")
fi

for TARGET in "${TARGETS[@]}"; do
  mkdir -p "$(dirname "$TARGET")"
  if [[ -L "$TARGET" && "$(readlink "$TARGET")" == "$SOURCE" ]]; then
    echo ">>> Ghostty config already linked: $TARGET"
    continue
  fi
  if [[ -e "$TARGET" || -L "$TARGET" ]]; then
    BACKUP_DIR="$(mktemp -d "$HOME/.dotfiles-migration-backup.XXXXXXXX")"
    mv "$TARGET" "$BACKUP_DIR/$(basename "$TARGET")"
    echo ">>> Backed up existing Ghostty config to $BACKUP_DIR"
  fi
  ln -s "$SOURCE" "$TARGET"
  echo ">>> Linked $TARGET to $SOURCE"
done
