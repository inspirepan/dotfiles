# 每次配置变化新增一个可验证步骤

1. 新增 `YYYYMMDD-NNN-名称.py`，提供 `DESCRIPTION`、`check(repository, home)`、`apply(repository, home)`。
2. `check` 只检查；`apply` 可重复执行，保留个人内容；验证成功才写本机记录。
3. 已应用步骤不可改正文；下一次变化新增文件。步骤按文件名排序，失败立即停止。
4. 配置正文保持在 Stow 包或清单内。检查使用当前目标配置；入口漂移或清单升级会重新应用。
5. 已有同名个人 Skill 保留并报冲突；先比较、明确处理，再重试。不要标记冲突为完成。

记录：`~/.local/state/dotfiles/updates.json`，不入库。不自动回滚已成功的步骤。
