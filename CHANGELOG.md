# 万象绘卷版本更新日志

## v2.6.7 (2026-04-19)

### 🔧 全文档整合：矛盾修复与串联统一

#### 问题背景
SKILL.md (v2.6.6) 与 SKILL_FULL.md (v2.5.2) 存在大量不一致，包括版本号、模式定义、章节编号、平台引用、素材路径等多个矛盾点。文档之间的参差不齐导致功能描述冲突。

#### 核心修复

**版本号统一**：
- SKILL_FULL.md 版本从 2.5.2 → 2.6.6，与 SKILL.md / VERSION 一致
- 移除 SKILL_FULL.md 中的"测试版 1.6"标注

**平台特定引用清除**：
- 移除所有"龙虾"、"Trae IDE"平台绑定引用
- 将龙虾特定描述改为通用"AI助手"描述
- 保留 SOUL.md / IDENTITY.md 等作为通用人格配置文件模板说明

**章节编号统一**：
- SKILL.md 和 SKILL_FULL.md 章节导航统一为：
  - 第十三章 = 李诞七步写作框架（对应 references/chapter-13-lidan-writing/）
  - 第十四章 = 异世界人生模拟（对应 references/chapter-14-life-simulation/）
- 修复此前 SKILL_FULL.md 中"第十四章=李诞七步、第十五章=人生模拟"的编号错位

**模式定义统一**：
- 统一为4种模式：创作学习、交互式故事、异世界人生模拟、角色扮演
- SKILL_FULL.md 补充异世界人生模拟模式的完整定义

**素材路径统一**：
- 硬编码绝对路径 `d:\projects\novel_data\` → 通用相对路径 `novel_data/`
- `scripts/crawl_yuluoxc.py` 默认路径从 `d:/projects/` → `./`

**功能概览修复**：
- SKILL.md 中"异世界人生模拟"重复列出项已合并

**不存在的文件引用清除**：
- 移除 `assets/security-persona-config.md` 引用（该文件不存在）
- 移除 `assets/icon.png` 引用（该文件不存在）
- `assets/wanxiang.json` → `references/wanxiang-original/`
- `assets/mom-summary.json` / `assets/mom-messiah.json` / `assets/chun-tea.json` → 标注为"已移除"
- `01-hard-output-constraints.txt` 中 `assets/wanxiang.json` → `references/wanxiang-original/`

**安全约束性质说明统一**：
- SKILL_FULL.md 中"硬性约束"章节添加说明：该文件描述的是游戏内写作质量指导，不是对AI助手的运行时指令
- 安全人格配置从"龙虾用户必读"改为"使用自定义人格配置的AI助手必读"

**09-security-defense 文件更新**：
- `05-lobster-security-config.md`：标题从"龙虾（OpenClaw）安全人格配置"改为"安全人格配置模板"
- `04-ai-usage-guide.md`：移除龙虾引用，更新配置文件路径
- `index.md`：移除龙虾特定标注

**模块联动更新**：
- SKILL_FULL.md 补充完整的模块联动说明
- 李诞七步框架在模块联动中的编号从"第十五章"更正为"第十三章"

---

## v2.6.6 (2026-04-19)

### 🔒 安全增强：提示注入风险警告

#### 问题背景
审查报告指出，虽然已添加免责声明，但文档仍包含「可执行类行为」（如 `#` 命令语义、立即中断规则等），可能被 AI 助手误解为系统指令。

#### 核心改动
**新增「提示注入风险警告」章节：**
- 不要让 AI 自动读取 `references/` 目录下的系统文档作为指令
- 游戏文档 ≠ AI指令
- 隔离运行：确保 AI 不会误解游戏文档为系统指令

#### 强调说明
- `#` 开头的命令（如 `#主菜单`、`#状态`）是**游戏指令**，归属于游戏系统
- 这些不是对 AI 助手的系统指令

---

## v2.6.5 (2026-04-19)

### 📝 声明优化：游戏系统 vs AI系统

#### 问题背景
原声明中「无自动执行」的表述不准确，因为游戏内确实有自动化流程（指令系统、人格系统等），但这些归属于「游戏系统」，不是对 AI 的系统指令。

#### 核心改动
**新增区分说明：**
- **游戏系统**：文档中的「指令系统」、「人格架构」、「自动化流程」等归属于游戏系统，是交互式故事游戏的内部设定
- **AI系统**：这些不是对 AI 助手的系统指令

#### 修改内容
- SKILL.md：「无自动执行」→「游戏自动化」
- 明确说明游戏内的自动化流程归属于游戏系统
- 新增「游戏系统 vs AI系统」的区分说明

---

## v2.6.4 (2026-04-19)

### 🎮 核心玩法更新：故事叙述输出格式

#### 问题背景
原来的输出格式过于「系统化」，不够沉浸式。玩家需要的是「像讲故事一样」的游戏体验。

#### 核心改动
**新增输出结构：**
```
<思考>
【故事简略】
（用讲故事的方式，口述发生了什么……）
</思考>

<思考>
【你的思考】
（分析当前局势，给出选择和建议……）
</思考>

（正文：沉浸式场景描写……）
```

#### 故事简略（必须包含）
1. **发生了什么？** - 角色经历了什么事件？世界发生了什么变化？
2. **现在是什么情况？** - 角色在哪里？在做什么？
3. **氛围如何？** - 紧张？轻松？诡异？温馨？

#### 你的思考（必须包含）
1. **能怎么做？** - 有哪些可行的行动？
2. **能怎么选？** - 列出2-4个选项及可能后果
3. **该怎么办？** - 给出建议和风险提醒

#### 新增检查清单
每次输出前必须检查：
- [ ] 是否有故事简略块？
- [ ] 故事简略是否用「讲故事」的方式口述？
- [ ] 是否有你的思考块？
- [ ] 你的思考是否给出了选择和建议？

---

## v2.6.3 (2026-04-19)

### 🔴 重要安全更新：提示注入风险修复

#### 问题背景
本技能包包含大量「代理/系统」文档，这些文档可能被人工智能助手解读为运行时指令，存在提示注入风险。

#### 修复内容
- **SKILL.md**：添加「重要声明：文档性质说明」章节，明确声明所有文档为「参考文档」而非「运行时指令」
- **AGENTS.md**：添加免责声明，明确说明这是游戏设定而非对AI的指令
- **01-system-protocol.md**：添加免责声明
- **01-personality-system.md**：添加免责声明
- **01-hard-output-constraints.txt**：添加免责声明
- **05-内部思维模块.md**：添加免责声明
- **01-prompt-injection-defense.md**：添加免责声明

#### 新增声明内容
所有关键文档开头添加：
> ⚠️ **重要声明**：本文档是「万象绘卷」交互式故事游戏的**创作参考材料**，描述的是游戏内虚拟系统的设定。
> 
> **这不是对人工智能助手的运行时指令。**

#### 安全建议
- 人工智能助手不应将这些文档解读为行为约束
- 用户应了解这些文档是写作参考材料
- 如有疑问，请参考 SKILL.md 中的「重要声明」章节

---

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
