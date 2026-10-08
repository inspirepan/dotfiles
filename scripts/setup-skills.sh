#!/usr/bin/env zsh
# Link local skills and install declared remote skills with the Skills CLI.
set -e

for arg in "$@"; do
  case "$arg" in
    --update) ;; # Compatibility alias: every run refreshes remote skills.
    --help|-h)
      echo "Usage: setup-skills.sh [--update]"
      echo "Install skills and link them to ~/.agents/skills and ~/.claude/skills."
      echo "Every run refreshes remote skills with npx skills, targeting Claude Code only."
      echo "--update  Alias for the default install-and-refresh operation."
      exit 0
      ;;
    *) echo "Unknown argument: $arg" >&2; exit 1 ;;
  esac
done

DOTFILES="$(cd "$(dirname "$0")/.." && pwd)"
SKILLS_DIR="$HOME/.agents/skills"
CLAUDE_SKILLS_DIR="${CLAUDE_CONFIG_DIR:-$HOME/.claude}/skills"
SKILLFILE="$DOTFILES/Skillfile"

if ! command -v npx >/dev/null 2>&1; then
  echo "npx is required; install Node.js from Brewfile first." >&2
  exit 1
fi

# Move link conflicts; copy snapshots before CLI-managed replacements.
backup() {
  local target="$1" mode="${2:-move}" backup_dir
  if [[ -e "$target" || -L "$target" ]]; then
    mkdir -p "$HOME/.local/state/dotfiles/skills-backups"
    backup_dir=$(mktemp -d "$HOME/.local/state/dotfiles/skills-backups/backup.XXXXXXXX")
    if [[ "$mode" == copy ]]; then
      cp -RP "$target" "$backup_dir/"
    else
      mv "$target" "$backup_dir/"
    fi
    echo "    $target -> backed up to $backup_dir"
  fi
}

# Leave shared entries untouched, including directory-level links.
link_skill() {
  local source="$1" target="$2"
  if [[ -e "$target" && "${target:A}" == "${source:A}" ]]; then
    return
  fi
  backup "$target"
  ln -s "$source" "$target"
  echo "    $target -> linked"
}

mkdir -p "$SKILLS_DIR" "$CLAUDE_SKILLS_DIR"

# Link local skills from dotfiles
echo ">>> Linking local skills"
for skill_dir in "$DOTFILES"/skills/*(N/); do
  name=$(basename "$skill_dir")
  if [[ -f "$skill_dir/SKILL.md" ]]; then
    link_skill "$skill_dir" "$SKILLS_DIR/$name"
    link_skill "$SKILLS_DIR/$name" "$CLAUDE_SKILLS_DIR/$name"
  fi
done

# Delegate remote installation and metadata tracking to the Skills CLI.
echo ">>> Installing remote skills from Skillfile"
backup "$HOME/.agents/.skill-lock.json" copy

while IFS= read -r line || [[ -n "$line" ]]; do
  # Skip comments and empty lines
  [[ "$line" =~ '^[[:space:]]*(#|$)' ]] && continue

  read -r repo skill_name extra <<< "$line"
  if [[ ! "$repo" =~ '^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$' ||
        ! "$skill_name" =~ '^[a-z0-9]+(-[a-z0-9]+)*$' || -n "$extra" ]]; then
    echo "Invalid Skillfile entry: $line" >&2
    exit 1
  fi

  if [[ -f "$DOTFILES/skills/$skill_name/SKILL.md" ]]; then
    echo "Refusing to replace a local skill: $skill_name" >&2
    exit 1
  fi

  backup "$SKILLS_DIR/$skill_name" copy
  if [[ "${CLAUDE_SKILLS_DIR:A}" != "${SKILLS_DIR:A}" ]]; then
    backup "$CLAUDE_SKILLS_DIR/$skill_name" copy
  fi
  echo "    $skill_name -> installing from $repo"
  npx --yes skills add "$repo" --skill "$skill_name" --global --agent claude-code --yes --json </dev/null
  if [[ ! -f "$CLAUDE_SKILLS_DIR/$skill_name/SKILL.md" ]]; then
    echo "Skill not installed for Claude Code: $skill_name" >&2
    exit 1
  fi
  link_skill "$CLAUDE_SKILLS_DIR/$skill_name" "$SKILLS_DIR/$skill_name"
done < "$SKILLFILE"

echo ">>> Done"
