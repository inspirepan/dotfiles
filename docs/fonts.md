# 字体

## 可通过 Brew 安装（已写入 Brewfile）

以下字体都通过 `brew bundle` 安装：

- **Commit Mono** -- 等宽字体，VSCode 编辑器字体
- **Geist / Geist Mono** -- Vercel 字体，Ghostty + Zed 使用
- **IBM Plex Sans** -- 正文字体
- **Inter** -- UI 字体
- **JetBrains Mono** -- 等宽字体
- **JetBrains Mono Nerd Font** -- 带图标的等宽字体，Ghostty 备用
- **Lilex** -- 等宽字体
- **Roboto Mono** -- 等宽字体
- **Sarasa Gothic** -- 中日韩字体，Ghostty 的 CJK 备用字体
- **SF Mono / SF Pro** -- Apple 系统字体
- **Work Sans** -- 无衬线字体
- **Spectral** -- 衬线字体

## 手动安装

这些字体无法通过 Homebrew 安装，字体文件存放在 `dotfiles/fonts/` 中。

安装命令：

```bash
cp ~/code/dotfiles/fonts/* ~/Library/Fonts/
```

### TX-02

等宽字体。在 VSCode 中作为第二编辑器字体使用（`CommitMono, TX-02`）。
来源：zip 文件（建议保留一份备份，或从原始来源重新下载）。

### Anthropic 品牌字体

- **Anthropic Mono**（Italic、Roman）
- **Anthropic Sans**（Italic、Roman）
- **Anthropic Serif**（Italic、Roman）

未公开分发，需要内部获取。

### Styrene A

Anthropic 的品牌展示字体。字重包括：Thin、Light、Regular、Medium、Bold、Black（另含 Italic）。
商业授权，未公开分发。

### 中文字体（手动版本）

- **STHeiti**（Bold、Medium） -- 华文黑体
- **STKai**（Bold、Medium） -- 华文楷体
- **STSong**（Bold、Medium） -- 华文宋体
- **Inter-STHeiti-Regular-90** -- Inter + STHeiti 混合 / 合并字体
