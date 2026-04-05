# jj.zsh-theme - 一个支持 jj/git 的极简提示符
#
# 特性：
# - 第 1 行：路径 + 版本控制信息（优先 jj，回退到 git）
# - 第 2 行：提示符字符
# - 显示 change_id、描述、+/- 统计、git 用户

_jj_theme_vcs_info() {
  local git_user=""
  if git rev-parse --is-inside-work-tree &>/dev/null; then
    git_user=" %F{green}$(git config user.name)%f"
  fi

  # 优先尝试 jj
  if jj root &>/dev/null; then
    local change_id desc ins del stat_line change_count trunk_bookmark
    change_id=$(jj log -r @ --no-graph -T 'change_id.shortest()' 2>/dev/null)
    desc=$(jj log -r @ --no-graph -T 'description.first_line()' 2>/dev/null)
    local flags=$(jj log -r @ --no-graph -T 'if(conflict, "conflict") ++ " " ++ if(empty, "empty")' 2>/dev/null)
    change_count=$(jj log -r 'trunk()..@' --no-graph -T '"x\n"' 2>/dev/null | wc -l | tr -d ' ')
    local_bookmark=$(jj log -r '@' --no-graph -T 'bookmarks.join(" ")' 2>/dev/null)
    [[ -z "$local_bookmark" ]] && local_bookmark=$(jj log -r '@-' --no-graph -T 'bookmarks.join(" ")' 2>/dev/null)
    stat_line=$(jj diff --stat -r @ 2>/dev/null | tail -1)
    files=$(echo "$stat_line" | grep -oE '^[0-9]+' | head -1)
    ins=$(echo "$stat_line" | grep -oE '[0-9]+ insertion' | grep -oE '[0-9]+')
    del=$(echo "$stat_line" | grep -oE '[0-9]+ deletion' | grep -oE '[0-9]+')

    local stat="" desc_part=""
    [[ -n "$files" && "$files" -gt 0 ]] && stat=" %F{yellow}*${files}%f %F{green}+${ins:-0}%f %F{red}-${del:-0}%f"
    if [[ -n "$desc" ]]; then
      [[ ${#desc} -gt 40 ]] && desc="${desc:0:40}…"
      desc_part=" %F{8}${desc}%f"
    else
      desc_part=" %F{8}(无描述)%f"
    fi

    local count_part="" flag_part=""
    [[ -n "$change_count" && "$change_count" -gt 1 ]] && count_part="%F{yellow}(${change_count})%f"
    [[ "$flags" == *conflict* ]] && flag_part+=" %F{red}CONFLICT%f"
    [[ "$flags" == *empty* ]] && flag_part+=" %F{green}EMPTY%f"
    echo " %F{magenta}jj:${change_id}%f${count_part} %F{cyan}${local_bookmark}%f${desc_part}${stat}${flag_part}${git_user}"
    return
  fi

  # 回退到 git
  if git rev-parse --is-inside-work-tree &>/dev/null; then
    local branch ins del stat_line
    branch=$(git branch --show-current 2>/dev/null)
    [[ -z "$branch" ]] && branch=$(git rev-parse --short HEAD 2>/dev/null)
    stat_line=$(git diff --stat HEAD 2>/dev/null | tail -1)
    files=$(echo "$stat_line" | grep -oE '^[0-9]+' | head -1)
    ins=$(echo "$stat_line" | grep -oE '[0-9]+ insertion' | grep -oE '[0-9]+')
    del=$(echo "$stat_line" | grep -oE '[0-9]+ deletion' | grep -oE '[0-9]+')

    local stat=""
    [[ -n "$files" && "$files" -gt 0 ]] && stat=" %F{yellow}*${files}%f %F{green}+${ins:-0}%f %F{red}-${del:-0}%f"

    # ahead/behind
    local ab_part=""
    local ab=$(git rev-list --left-right --count HEAD...@{upstream} 2>/dev/null)
    if [[ -n "$ab" ]]; then
      local ahead=$(echo "$ab" | cut -f1) behind=$(echo "$ab" | cut -f2)
      [[ "$ahead" -gt 0 ]] && ab_part+=" %F{green}↑${ahead}%f"
      [[ "$behind" -gt 0 ]] && ab_part+=" %F{red}↓${behind}%f"
    fi

    # staged
    local staged_part=""
    local staged_count=$(git diff --cached --numstat 2>/dev/null | wc -l | tr -d ' ')
    [[ "$staged_count" -gt 0 ]] && staged_part=" %F{green}●${staged_count}%f"

    # stash
    local stash_part=""
    local stash_count=$(git stash list 2>/dev/null | wc -l | tr -d ' ')
    [[ "$stash_count" -gt 0 ]] && stash_part=" %F{yellow}⚑${stash_count}%f"

    echo " %F{cyan}git:${branch}%f${ab_part}${staged_part}${stat}${stash_part}${git_user}"
    return
  fi
}

_jj_theme_agent_info() {
  local parts=()
  [[ -f CLAUDE.md ]] && parts+=("CLAUDE.md")
  [[ -f AGENTS.md ]] && parts+=("AGENTS.md")
  local skill_count=0
  [[ -d .agents/skills ]] && (( skill_count += $(find .agents/skills -maxdepth 1 -mindepth 1 -type d 2>/dev/null | wc -l) ))
  [[ -d .claude/skills ]] && (( skill_count += $(find .claude/skills -maxdepth 1 -mindepth 1 -type d 2>/dev/null | wc -l) ))
  [[ "$skill_count" -gt 0 ]] && parts+=("${skill_count} skills")
  [[ ${#parts[@]} -gt 0 ]] && echo " %F{8}(${(j:, :)parts})%f"
}

# Resolve Tailscale hostname once at load time (falls back to system hostname)
_jj_theme_hostname="%m"
if command -v tailscale &>/dev/null; then
  _ts_name=$(tailscale status --self --json 2>/dev/null | command grep -o '"HostName": *"[^"]*"' | head -1 | cut -d'"' -f4)
  [[ -n "$_ts_name" ]] && _jj_theme_hostname="$_ts_name"
  unset _ts_name
else
  _ts_ip=$(ifconfig utun5 2>/dev/null | grep 'inet ' | awk '{print $2}')
  if [[ -n "$_ts_ip" ]]; then
    _ts_name=$(dscacheutil -q host -a ip_address "$_ts_ip" 2>/dev/null | awk -F'\\.' '/^name:.*\.ts\.net/{print $1}' | sed 's/^name: //')
    [[ -n "$_ts_name" ]] && _jj_theme_hostname="$_ts_name"
    unset _ts_name _ts_ip
  fi
fi

# Cache VCS info in precmd so Ctrl-C won't break the prompt
_jj_theme_cached_vcs=""
_jj_theme_cached_agent=""
_jj_theme_cached_host=""
_jj_theme_precmd() {
  _jj_theme_cached_vcs="$(_jj_theme_vcs_info)"
  _jj_theme_cached_agent="$(_jj_theme_agent_info)"
  [[ -n "$SSH_CONNECTION" ]] && _jj_theme_cached_host="%F{yellow}${_jj_theme_hostname}%f " || _jj_theme_cached_host=""
}
precmd_functions+=(_jj_theme_precmd)

setopt PROMPT_SUBST

PROMPT='
${_jj_theme_cached_host}%F{blue}%~%f${_jj_theme_cached_vcs}${_jj_theme_cached_agent}
%F{magenta}➜%f '
