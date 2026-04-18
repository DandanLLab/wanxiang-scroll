# wanxiang-scroll

万象绘卷（wanxiang-scroll）是一个面向网文创作与互动叙事实验的综合仓库，聚合了：

- 多文风创作参考（文风切换、风格对照）
- 创作流程方法（开书、黄金三章、细纲生成、质量控制）
- 拆书融合工作流（多源作品要素提取与重组）
- 小说资料处理脚本（索引抓取、文本下载、结构提取、批量分析）

本仓库既可作为**创作参考资料库**，也可作为**脚本工具箱**用于文本素材整理与分析。

---

## 1. 项目定位

### 1.1 适合谁使用

- 想搭建网文创作流程的作者
- 需要做文风实验/文风对照的创作者
- 想做小说拆解、融合创作研究的用户
- 需要批量采集和分析小说文本结构的研究者

### 1.2 你可以在这里做什么

- 阅读结构化参考文档，快速搭建创作 SOP
- 使用脚本生成小说索引并下载文本素材
- 提取章节大纲和关键词，辅助创作规划
- 对比不同文风模板，优化表达效果

---

## 2. 仓库结构说明

| 路径 | 作用 | 说明 |
|---|---|---|
| `assets/` | 核心配置与扩展配置 | 包含万象主配置及相关扩展 JSON 数据。 |
| `references/` | 章节化参考文档 | 按主题组织的创作、风格、质量与安全文档。 |
| `scripts/` | 自动化脚本工具 | 用于抓取索引、下载文本、抽取大纲与批处理分析。 |
| `SKILL.md` | 主技能导航文档 | 汇总核心能力、模式、章节入口与使用建议。 |

---

## 3. 快速开始

### 3.1 环境准备

建议使用 Python 3.10+（或更高版本），并在虚拟环境中运行脚本：

```bash
python -m venv .venv
source .venv/bin/activate  # Windows 可用 .venv\Scripts\activate
```

> 说明：本仓库未强制固定依赖文件，不同脚本可能依赖不同第三方库，请按脚本报错提示安装。

### 3.2 先读哪份文档

- 想看全景导航：先读 `SKILL.md`
- 想练习创作流程：看 `references/chapter-06-novel-creation/`
- 想做文风切换：看 `references/chapter-02-style-system/`
- 想做质量优化：看 `references/chapter-07-quality-control/`

### 3.3 常用脚本示例

```bash
# 1) 抓取分类索引
python scripts/crawl_novel_index.py --mode index --outdir ./novel_data

# 2) 按索引批量下载（示例下载 10 本）
python scripts/crawl_novel_index.py \
  --mode download \
  --index ./novel_data/novel_index.json \
  --outdir ./novel_data \
  --limit 10

# 3) 基于索引抽取提纲
python scripts/crawl_novel_index.py \
  --mode outline \
  --index ./novel_data/novel_index.json \
  --outdir ./novel_data
```

---

## 4. 常见工作流

### 工作流 A：创作前准备

1. 阅读章节文档，选定题材与文风。
2. 用角色/大纲工具形成设定草稿。
3. 用质量控制标准检查首章可读性。
4. 进入正文创作并持续迭代。

### 工作流 B：拆书融合创作

1. 选取 3~6 本参考作品。
2. 提取世界观、人物关系、爽点结构。
3. 执行“保留核心 + 替换关键要素”的融合设计。
4. 形成新大纲并做原创性自检。

### 工作流 C：素材库建设

1. 执行索引抓取。
2. 下载目标文本。
3. 抽取章节结构与关键词。
4. 建立你的题材/节奏/风格标签体系。

---


## 5. 互动系统（交互式故事）

仓库不仅支持创作资料与脚本工具，也提供“交互式故事”使用路径。

### 5.1 互动系统适用场景

- 希望以“角色行动 + 世界反馈”的方式推进剧情
- 想在对话中实时查看状态、探索场景、触发事件
- 需要从“写作模式”切换到“游玩/扮演模式”

### 5.2 建议阅读顺序

1. `references/chapter-01-core-system/index.md`（核心系统与协议）
2. `references/chapter-03-interactive-story/index.md`（互动故事快速开始）
3. `references/chapter-02-style-system/index.md`（互动中切换文风）

### 5.3 互动系统快速体验

```text
打开菜单
看看现在啥情况
探索附近区域
```

可选的 `#` 指令形式（兼容口语输入）：

```text
#主菜单
#状态
#探索
```

### 5.4 与创作模式的区别

- **创作模式**：侧重写作产出（大纲、正文、优化、拆书融合），一般不需要指令系统。
- **互动模式**：侧重即时交互体验（行动、状态、世界反馈），建议优先加载核心配置并按互动协议运行。

---

## 6. Git 指令（GitHub）

仓库地址：`https://github.com/DandanLLab/wanxiang-scroll`

### 6.1 首次克隆

```bash
git clone https://github.com/DandanLLab/wanxiang-scroll.git
cd wanxiang-scroll
```

### 6.2 本地已有目录，关联远程

```bash
git init
git remote add origin https://github.com/DandanLLab/wanxiang-scroll.git
```

### 6.3 提交并推送

```bash
git add .
git commit -m "docs: improve README details"
git push -u origin main
```

### 6.4 更新本地代码

```bash
git pull --rebase origin main
```

---

## 7. 使用与合规

- 本仓库中的小说分析与素材整理内容主要用于学习和研究用途。
- 使用抓取/下载类脚本时，请遵守目标站点协议、robots 规则与当地法律法规。
- 若用于公开发布，请自行确认内容来源与版权边界。

---

## 8. 开源协议

本项目采用 **MIT License** 开源，详见 [LICENSE](./LICENSE)。

你可以在 MIT 许可下使用、修改、分发本仓库代码；但对于你自行采集或处理的数据内容，仍需按对应来源的版权与使用条款执行。
