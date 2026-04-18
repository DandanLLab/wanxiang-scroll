# 技能调用测试记录

> 日期：2026-04-18（UTC）

本次按仓库 `AGENTS.md` 的“技能加载规则”执行技能调用测试，使用会话中可用的系统技能：`skill-installer`。

## 测试目标

- 验证技能文档可读取（`/opt/codex/skills/.system/skill-installer/SKILL.md`）。
- 验证技能辅助脚本可被调用（`list-skills.py`）。

## 执行命令

```bash
python /opt/codex/skills/.system/skill-installer/scripts/list-skills.py --format json
```

## 执行结果

- 命令已成功发起，但因网络隧道返回 `403 Forbidden`，无法访问 GitHub API。
- 该结果说明：
  - **技能调用流程已触发**（脚本执行成功进入联网请求阶段）；
  - **失败原因是环境网络限制**，非仓库代码错误。

## 建议复测方式

在可访问 GitHub API 的网络环境中，重新执行上述命令即可得到可安装技能列表（JSON 格式）。
