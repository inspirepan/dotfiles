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
    change_id=$(jj log -r @ --no-graph -T 'change_id.shortest(8)' 2>/dev/null)
    desc=$(jj log -r @ --no-graph -T 'description.first_line()' 2>/dev/null)
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
      desc_part=" %F{8}${desc}%f"
    else
      desc_part=" %F{8}(无描述)%f"
    fi

    echo " %F{magenta}jj:${change_id}%f%F{yellow}(${change_count})%f %F{cyan}${local_bookmark}%f${desc_part}${stat}${git_user}"
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

    echo " %F{cyan}git:${branch}%f${stat}${git_user}"
    return
  fi
}

setopt PROMPT_SUBST

PROMPT='
%F{blue}%~%f$(_jj_theme_vcs_info)
%F{magenta}➜%f '
