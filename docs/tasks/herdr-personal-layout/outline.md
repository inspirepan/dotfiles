# Herdr 个人布局修复交接

1. 已确认
   - 内置 `main` 每次启动会被替换；改用本机个人 `layouts/klaude.json`。
   - 不修改已应用的 001/002、内置 mods、Klaude YAML 或 space/tab/pane 运行内容。
   - 003 只迁移布局文件；布局选择由运行中的 app 原生命令完成，不直接写 `shared.json`。
2. 已实现
   - `updates/20261030-003-personal-herdr-layout.py`：匹配 002 备份的替换后语义，复制个人布局，逐字节恢复 main；冲突拒绝、原子替换、迁移前备份、幂等检查。
   - `scripts/dotfiles.py`：已登记的 003 通过 `SUPERSEDES` 取代 002，避免后续更新重新修改 main；已应用正文哈希仍全部校验。
   - `updates/20261030-004-personal-herdr-mods.py` 接管个人 mod 链接检查及备份修复，防止取代 002 后漏检链接漂移。
   - 安装指南及 fake home 初始化流程已更新。
3. 已验证
   - `uv run --no-project python -m unittest discover -s tests -v`：39 项通过。
   - 覆盖原文字节恢复、保留布局其他字段、重复执行无新备份、个人布局冲突、main 额外修改、写入期间 main 变化、shared 原文不变，以及后续 app 升级和个人布局编辑不重复迁移。
   - 已在本机应用 003；`cmp` 确认 main 与 002 备份逐字节一致。
   - 原生命令切换后 `herdr-app status` 显示 `layout: klaude`、`errors: []`；重复 update 无新操作，002 已取代、003 已完成。
   - 004 已在本机登记完成；测试确认本机 mod 普通文件会备份后恢复链接，内置 main 不变。
   - 本机迁移前备份：`~/.local/state/dotfiles/backups/personal-herdr-layout-33f93ui0/`；未重启、提交或推送。
4. 审查与剩余事项
   - 两轮正确性审查确认的内置布局恢复、mod 链接漂移遗漏均已修复并回归验证；维护性审查无发现。
   - 实际重启保留效果未验证（遵守不重启约束）。
   - 另一台机器拉取后须执行指南中的更新及布局切换命令。
5. 当前阶段：通用终端标题已实现并验证
   - 已确认：基于官方 Agents / pane，仅调整标题优先级；保留 menu、tabs 与个人 layout 引用，不改官方原件、不重启。
   - `config/.config/herdr-app/mods/klaude-agents/main.js`：自身 pane 标题 trim → cwd 末级目录 → program.name → `-`；保留标点和状态符号，不依赖 tab 名称或其他 pane。
   - Agents 恢复官方 flex 滚动容器、时间与 pin 行为，移除 `on_size_change`、`this.width` 和手算列表宽度。
   - `config/.config/herdr-app/mods/klaude-pane/main.js`：相对官方仅增加所有 `program.agent` 的终端标题优先级，非 agent shell 沿用官方逻辑。
   - `updates/20261030-011-agent-session-title.py` 检查两份 mod symlink，仅取代 009；旧步骤不变，未在本机登记 011。
   - 已验证：`uv run --no-project python -m unittest discover -s tests -v`，46 项通过；本机两份 mod 均为指向仓库的 symlink。
   - 原生验证：两份 mod 的 `herdr-app check` 通过；触发 symlink 入口热重载后，在 zoom 1.1、侧栏 180 / 440 设计像素下截图确认标题展示、窄栏截断及 spinner 完整可见；已通过 `layout.resize` 恢复原宽度 204，`herdr-app status` 的 `errors` 为空。
   - 独立正确性审查无新增问题，并复跑 46 项测试通过；hover 仅有 mock 覆盖，未做原生鼠标验证，未重启。
   - 下一步：其他设备拉取本次提交后运行设备更新；本次未执行全量 update，避免触发无关待执行步骤。