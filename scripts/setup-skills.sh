#!/usr/bin/env zsh
# Install agent skills from Skillfile
set -e

UPDATE=false
for arg in "$@"; do
  case "$arg" in
    --update) UPDATE=true ;;
    --help|-h)
      echo "Usage: setup-skills.sh [--update]"
      echo "Install skills and link them to ~/.agents/skills and ~/.claude/skills."
      echo "--update  Refresh existing remote skills, keeping recoverable backups."
      exit 0
      ;;
    *) echo "Unknown argument: $arg" >&2; exit 1 ;;
  esac
done

DOTFILES="$(cd "$(dirname "$0")/.." && pwd)"
SKILLS_DIR="$HOME/.agents/skills"
CLAUDE_SKILLS_DIR="$HOME/.claude/skills"
SKILLFILE="$DOTFILES/Skillfile"
WORK_DIR=$(mktemp -d "${TMPDIR:-/tmp}/setup-skills.XXXXXXXX")
if command -v trash >/dev/null 2>&1; then
  trap 'trash "$WORK_DIR" || echo "Temporary files kept at $WORK_DIR" >&2' EXIT
fi

# Preserve conflicting entries in unique, recoverable directories.
backup() {
  local target="$1" backup_dir
  if [[ -e "$target" || -L "$target" ]]; then
    mkdir -p "$HOME/.local/state/dotfiles/skills-backups"
    backup_dir=$(mktemp -d "$HOME/.local/state/dotfiles/skills-backups/backup.XXXXXXXX")
    mv "$target" "$backup_dir/"
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

# Install remote skills from Skillfile
echo ">>> Installing remote skills from Skillfile"
declare -A cloned_repos

while IFS= read -r line || [[ -n "$line" ]]; do
  # Skip comments and empty lines
  [[ "$line" =~ '^[[:space:]]*(#|$)' ]] && continue

  read -r repo skill_path local_name extra <<< "$line"
  if [[ -z "$repo" || -z "$skill_path" || -z "$local_name" || -n "$extra" ||
        "$local_name" == */* || "$local_name" == . || "$local_name" == .. ||
        "$skill_path" == /* || "/$skill_path/" == */../* ]]; then
    echo "Invalid Skillfile entry: $line" >&2
    exit 1
  fi

  if [[ -d "$SKILLS_DIR/$local_name" && ! -L "$SKILLS_DIR/$local_name" && "$UPDATE" == false ]]; then
    echo "    $local_name -> already exists, skipping"
    link_skill "$SKILLS_DIR/$local_name" "$CLAUDE_SKILLS_DIR/$local_name"
    continue
  fi

  # Clone repo if not already cloned
  if [[ -z "${cloned_repos[$repo]}" ]]; then
    repo_dir=$(mktemp -d "$WORK_DIR/repo.XXXXXXXX")
    echo "    Cloning $repo ..."
    git clone --depth 1 "https://github.com/$repo.git" "$repo_dir" 2>/dev/null
    cloned_repos[$repo]="$repo_dir"
  else
    repo_dir="${cloned_repos[$repo]}"
  fi

  # Validate and stage the complete replacement before moving old data.
  if [[ ! -d "$repo_dir/$skill_path" || ! -f "$repo_dir/$skill_path/SKILL.md" ]]; then
    echo "    $local_name -> ERROR: $skill_path/SKILL.md not found in $repo" >&2
    exit 1
  fi
  staging_dir=$(mktemp -d "$WORK_DIR/skill.XXXXXXXX")
  cp -R "$repo_dir/$skill_path" "$staging_dir/$local_name"
  backup "$SKILLS_DIR/$local_name"
  mv "$staging_dir/$local_name" "$SKILLS_DIR/$local_name"
  link_skill "$SKILLS_DIR/$local_name" "$CLAUDE_SKILLS_DIR/$local_name"
  echo "    $local_name -> installed from $repo"
done < "$SKILLFILE"

echo ">>> Done"
