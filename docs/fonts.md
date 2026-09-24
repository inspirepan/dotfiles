# 字体

## 当前配置依赖的字体

- **Paper Mono** -- Ghostty、Zed 和 VSCode 的主要等宽字体；由 `font-paper-mono` 安装。
- **TX-02 / TX-02-Variable** -- Ghostty 的备用字体，需从已购买的 [Berkeley Mono](https://usgraphics.com/products/berkeley-mono) 下载并手动安装。
- **STIX Two Math** -- Ghostty 数学符号备用字体；由 `font-stix-two-math` 安装。
- **JetBrains Mono Nerd Font** -- Ghostty 备用等宽字体与图标。
- **Sarasa Gothic** -- Ghostty 斜体的 CJK 备用字体；常规文字也使用 macOS 自带的苹方。
- **Geist** -- Zed UI 字体。

Paper Mono 使用 SIL Open Font License，官方来源为 [paper-design/paper-mono](https://github.com/paper-design/paper-mono)。
商业字体不入库；从个人授权来源获取 OTF/TTF，用字体册安装。不同下载版本的 family name 可能不同，
安装后用 `ghostty +list-fonts` 核对 `Paper Mono`、`TX-02` 和 `TX-02-Variable`。
未购买 TX-02 时可跳过，Ghostty 会使用列表中的其他字体；Zed 和 VSCode 应确保 Paper Mono 已安装。

## Homebrew 字体清单

以下字体通过 `brew bundle` 安装（已写入 Brewfile）：

- **Paper Mono** -- 主要编辑器与终端字体
- **STIX Two Math** -- 数学符号
- **Noto Serif CJK SC** -- 简体中文衬线字体
- **Commit Mono** -- 备用等宽字体
- **Geist / Geist Mono** -- UI / 等宽字体
- **IBM Plex Sans** -- 正文字体
- **Inter** -- UI 字体
- **JetBrains Mono** -- 等宽字体
- **JetBrains Mono Nerd Font** -- 带图标的等宽字体，Ghostty 备用
- **Lilex** -- 等宽字体
- **Roboto Mono** -- 等宽字体
- **Sarasa Gothic** -- 中日韩字体，Ghostty 的 CJK 备用字体
- **SF Mono / SF Pro** -- Apple 字体，按 setup guide 手动通过 cask 安装
- **Work Sans** -- 无衬线字体
- **Spectral** -- 衬线字体
