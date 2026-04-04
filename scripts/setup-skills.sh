#!/bin/bash
# Install agent skills from Skillfile
set -e

DOTFILES="$(cd "$(dirname "$0")/.." && pwd)"
SKILLS_DIR="$HOME/.agents/skills"
SKILLFILE="$DOTFILES/Skillfile"
TMPDIR=$(mktemp -d)

mkdir -p "$SKILLS_DIR"

# Link local skills from dotfiles
echo ">>> Linking local skills"
for skill_dir in "$DOTFILES"/skills/*/; do
  name=$(basename "$skill_dir")
  if [[ -f "$skill_dir/SKILL.md" ]]; then
    ln -sfn "$skill_dir" "$SKILLS_DIR/$name"
    echo "    $name -> linked"
  fi
done

# Install remote skills from Skillfile
echo ">>> Installing remote skills from Skillfile"
declare -A cloned_repos

while IFS= read -r line; do
  # Skip comments and empty lines
  [[ "$line" =~ ^#.*$ || -z "$line" ]] && continue

  repo=$(echo "$line" | awk '{print $1}')
  skill_path=$(echo "$line" | awk '{print $2}')
  local_name=$(echo "$line" | awk '{print $3}')

  if [[ -d "$SKILLS_DIR/$local_name" ]]; then
    echo "    $local_name -> already exists, skipping"
    continue
  fi

  # Clone repo if not already cloned
  repo_dir="$TMPDIR/$(echo "$repo" | tr '/' '-')"
  if [[ -z "${cloned_repos[$repo]}" ]]; then
    echo "    Cloning $repo ..."
    git clone --depth 1 "https://github.com/$repo.git" "$repo_dir" 2>/dev/null
    cloned_repos[$repo]="$repo_dir"
  else
    repo_dir="${cloned_repos[$repo]}"
  fi

  # Copy skill to target
  if [[ -d "$repo_dir/$skill_path" ]]; then
    cp -r "$repo_dir/$skill_path" "$SKILLS_DIR/$local_name"
    echo "    $local_name -> installed from $repo"
  else
    echo "    $local_name -> ERROR: $skill_path not found in $repo"
  fi
done < "$SKILLFILE"

# Cleanup
rm -rf "$TMPDIR"
echo ">>> Done"
