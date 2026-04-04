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
# Dock 位置：屏幕右侧
defaults write com.apple.dock orientation -string "right"
# 隐藏 Dock 中“最近使用的应用”区域
defaults write com.apple.dock show-recents -bool false
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

# --- 台前调度 ---
# 启用台前调度窗口管理
defaults write com.apple.WindowManager GloballyEnabled -bool true

# --- Spring Loading ---
# 将文件拖到文件夹上并停留时自动打开文件夹
defaults write -g com.apple.springing.enabled -bool true
# 文件夹自动弹开的延迟（秒）
defaults write -g com.apple.springing.delay -float 0.5

# --- 重启受影响的应用 ---
echo ">>> 正在重启 Dock 和访达..."
killall Dock
killall Finder

echo ">>> 完成。部分改动可能需要注销或重启后生效。"
