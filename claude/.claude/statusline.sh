#!/bin/bash
# Claude Code statusline: model · dir · git branch · context% · cost · duration
# Plain single line; only the model name is blue (ANSI 34), no emoji.

input=$(cat)

model=$(echo "$input" | jq -r '.model.display_name // empty')

cwd=$(echo "$input" | jq -r '.workspace.current_dir // empty')
dir_name=""
if [ -n "$cwd" ]; then
  dir_name=$(basename "$cwd")
fi

branch=""
if [ -n "$cwd" ] && [ -d "$cwd" ]; then
  branch=$(git -C "$cwd" --no-optional-locks branch --show-current 2>/dev/null)
  if [ -z "$branch" ]; then
    branch=$(git -C "$cwd" --no-optional-locks symbolic-ref --short HEAD 2>/dev/null)
  fi
fi

used_pct=$(echo "$input" | jq -r '.context_window.used_percentage // empty')
used_tok=$(echo "$input" | jq -r '.context_window.total_input_tokens // empty')
size_tok=$(echo "$input" | jq -r '.context_window.context_window_size // empty')

# Format token count as compact k/M, e.g. 86k or 1.0M
fmt_tok() {
  local n
  n=$(printf "%.0f" "$1")
  if [ "$n" -ge 1000000 ]; then
    awk -v n="$n" 'BEGIN { printf "%.1fM", n / 1000000 }'
  else
    printf "%dk" $(( (n + 500) / 1000 ))
  fi
}

ctx=""
if [ -n "$used_pct" ]; then
  ctx=$(printf "%.0f%%" "$used_pct")
fi
if [ -n "$used_tok" ] && [ -n "$size_tok" ]; then
  abs="$(fmt_tok "$used_tok")/$(fmt_tok "$size_tok")"
  if [ -n "$ctx" ]; then
    ctx="$ctx $abs"
  else
    ctx="$abs"
  fi
fi

cost_val=$(echo "$input" | jq -r '.cost.total_cost_usd // empty')
cost=""
if [ -n "$cost_val" ]; then
  cost=$(printf "\$%.2f" "$cost_val")
fi

dur_ms_raw=$(echo "$input" | jq -r '.cost.total_duration_ms // empty')
dur=""
if [ -n "$dur_ms_raw" ]; then
  dur_ms=$(printf "%.0f" "$dur_ms_raw")
  total_sec=$(( dur_ms / 1000 ))
  hours=$(( total_sec / 3600 ))
  mins=$(( (total_sec % 3600) / 60 ))
  if [ "$hours" -gt 0 ]; then
    dur="${hours}h${mins}m"
  else
    dur="${mins}m"
  fi
fi

parts=()
[ -n "$model" ] && parts+=("$(printf "\033[34m%s\033[0m" "$model")")
[ -n "$dir_name" ] && parts+=("$dir_name")
[ -n "$branch" ] && parts+=("$branch")
[ -n "$ctx" ] && parts+=("$ctx")
[ -n "$cost" ] && parts+=("$cost")
[ -n "$dur" ] && parts+=("$dur")

line=""
for i in "${!parts[@]}"; do
  if [ "$i" -eq 0 ]; then
    line="${parts[$i]}"
  else
    line="$line · ${parts[$i]}"
  fi
done

printf "%s\n" "$line"
