#!/bin/bash
# 通过 defaults write 配置 macOS 系统偏好设置
# 在新机器上运行一次，然后注销或重启使其生效。
set -e

echo ">>> 正在配置 macOS defaults..."

# --- Dock ---
# 图标大小（像素）
defaults write com.apple.dock tilesize -int 58
# 悬停放大效果
defaults write com.apple.dock magnification -bool true
# 放大后最大图标尺寸（默认 128，太大）
defaults write com.apple.dock largesize -int 72
# Dock 位置：屏幕右侧
defaults write com.apple.dock orientation -string "right"
# 隐藏 Dock 中“最近使用的应用”区域
defaults write com.apple.dock show-recents -bool false
# 不显示正在运行应用的小圆点指示器
defaults write com.apple.dock show-process-indicators -bool false
# 不要根据最近使用情况自动重排 Spaces
defaults write com.apple.dock mru-spaces -bool false

# --- 触发角 ---
# 左下角：调度中心
defaults write com.apple.dock wvous-bl-corner -int 2
defaults write com.apple.dock wvous-bl-modifier -int 0
# 右下角：快速备忘录
defaults write com.apple.dock wvous-br-corner -int 14
defaults write com.apple.dock wvous-br-modifier -int 0

# --- 访达 ---
# 底部显示完整路径面包屑栏
defaults write com.apple.finder ShowPathbar -bool true
# 底部显示项目数量 / 磁盘空间状态栏
defaults write com.apple.finder ShowStatusBar -bool true
# 默认搜索当前文件夹（而不是“这台 Mac”）
defaults write com.apple.finder FXDefaultSearchScope -string "SCcf"
# 修改文件扩展名时不弹出警告
defaults write com.apple.finder FXEnableExtensionChangeWarning -bool false

# --- 键盘 ---
# F 键默认用作标准功能键（F1-F12），而非亮度/音量等特殊功能
defaults write NSGlobalDomain com.apple.keyboard.fnState -bool true
# 不自动将句首字母大写
defaults write -g NSAutomaticCapitalizationEnabled -bool false
# 双空格时不自动插入句号
defaults write -g NSAutomaticPeriodSubstitutionEnabled -bool false
# 不把 -- 转成长破折号
defaults write -g NSAutomaticDashSubstitutionEnabled -bool false
# 不把普通引号转换为弯引号
defaults write -g NSAutomaticQuoteSubstitutionEnabled -bool false
# 不自动进行拼写纠正
defaults write -g NSAutomaticSpellingCorrectionEnabled -bool false

# --- Spotlight ---
# 禁用 Spotlight 的 Cmd+Space 快捷键，给 Raycast 让路
defaults write com.apple.symbolichotkeys AppleSymbolicHotKeys -dict-add 64 '
<dict>
  <key>enabled</key>
  <false/>
  <key>value</key>
  <dict>
    <key>parameters</key>
    <array>
      <integer>65535</integer>
      <integer>49</integer>
      <integer>1048576</integer>
    </array>
    <key>type</key>
    <string>standard</string>
  </dict>
</dict>'

# --- 台前调度 ---
# 启用台前调度窗口管理
defaults write com.apple.WindowManager GloballyEnabled -bool true

# --- Spring Loading ---
# 将文件拖到文件夹上并停留时自动打开文件夹
defaults write -g com.apple.springing.enabled -bool true
# 文件夹自动弹开的延迟（秒）
defaults write -g com.apple.springing.delay -float 0.5

# --- 默认打开方式 ---
# 用 duti 将常见代码文件的默认打开方式设为 VSCode（html/svg 保持浏览器默认）
echo ">>> 正在设置代码文件默认打开方式为 VSCode..."
code_exts=(
  py rs go java kt swift c cpp h hpp cs
  js jsx ts tsx mjs cjs vue svelte astro
  json jsonc yaml yml toml ini cfg conf
  md mdx txt csv tsv log
  sh bash zsh fish
  rb pl lua
  css scss less
  xml xsl
  sql graphql proto
  dockerfile makefile cmake
  gitignore gitconfig editorconfig
  env env.local
  lock
)
for ext in "${code_exts[@]}"; do
  duti -s com.microsoft.VSCode ".$ext" all 2>/dev/null
done
# 无扩展名的纯文本文件
duti -s com.microsoft.VSCode public.plain-text all 2>/dev/null
duti -s com.microsoft.VSCode public.unix-executable all 2>/dev/null
duti -s com.microsoft.VSCode public.shell-script all 2>/dev/null

# --- 重启受影响的应用 ---
echo ">>> 正在重启 Dock 和访达..."
killall Dock
killall Finder

echo ">>> 完成。部分改动可能需要注销或重启后生效。"
