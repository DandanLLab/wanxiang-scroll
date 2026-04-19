# 万象绘卷版本更新日志

## v2.6.2 (2026-04-19)

### 文档改进
- **添加安装说明**：明确的 Python 版本要求（3.10+）和依赖安装步骤
- **添加安全检查清单**：安装前、运行前、代码审查要点
- **添加虚拟环境建议**：推荐使用 venv 隔离环境
- **添加依赖说明**：列出 requirements.txt 中的依赖及其用途

### 安全改进
- 明确声明脚本为可选操作
- 添加代码审查要点
- 添加网络活动监控建议
- 添加备份建议

---

## v2.6.1 (2026-04-19)

### 安全修复
- **移除自动安装依赖代码**：`crawl_all_v5.py` 不再自动执行 `pip install`
- **添加安全警告**：所有爬虫脚本添加版权和法律合规警告
- **依赖安装改为手动**：用户需手动执行 `pip install -r requirements.txt`

### 修复内容
- 移除 `subprocess.check_call([sys.executable, "-m", "pip", "install", ...])`
- 添加 ImportError 处理，提示用户手动安装依赖
- 更新 SKILL.md 安全说明

---

## v2.6.0 (2026-04-19)

### 新增功能
- **完整数据库系统**：26张数据表覆盖所有系统
- **存档模板系统**：17个模板文件（存档类/创作类/分析类）
- **AI自由创作指南**：模板仅供参考，AI可自由创作
- **存档导出工具**：JSON + Markdown 双格式输出

### 数据库结构
- 核心故事系统: stories, worlds, world_state
- 角色系统: characters, character_attributes/traits/skills, relationships
- 事件系统: events, event_chains
- 剧情管理: plot_arcs, hidden_floors, summaries
- 小说生成: novel_chapters, novel_sections
- 文风系统: style_configs (56种), style_history
- 代代相传: legacies, family_tree
- 物品系统: items
- 拆书融合: fusion_projects, source_novels, fusion_elements, fusion_outputs
- 质量控制: quality_checks, forbidden_words
- 模板系统: templates, character_templates
- 日志系统: command_logs, game_sessions

### 模板系统
- 存档类: life_simulation, interactive_story, minecraft_survival, fusion_project
- 创作类: world_gen, character, event, novel_outline, golden_three_chapters
- 分析类: book_analysis, quality_check
- 通用: generic_save, AI_CREATION_GUIDE

### 脚本工具
- `init_database.py` - 数据库初始化
- `data_manager.py` - 数据管理工具
- `save_exporter.py` - 存档导出工具

---

## v2.5.2 (2026-04-19)

### 修复
- 修复文档不一致问题
- 澄清存储行为说明

---

## v2.5.0 (2026-04-18)

### 新增
- 人生模拟系统文档
- 交互式故事协议
- 剧情管理系统

---

## v2.0.0 (2026-04-15)

### 重构
- 模块化文档结构
- 14章节系统文档
- 文风系统56种配置

---

## v1.0.0 (2026-04-01)

### 初始版本
- 核心系统协议
- 世界规则
- 命令系统
