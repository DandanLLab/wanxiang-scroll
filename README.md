# wanxiang-scroll

万象绘卷（wanxiang-scroll）是一个面向网文与互动叙事创作的综合工具仓库，整合了文风系统、创作引擎、质量控制、拆书融合方法与小说分析脚本。

## 项目内容

- `assets/`：核心配置与扩展配置（如万象主配置、MoM、春茶、Apex 等）。
- `references/`：按章节组织的参考文档（核心系统、文风系统、创作流程、质量控制、安全防御等）。
- `scripts/`：小说索引爬取、文本下载、提纲抽取、批量分析等工具脚本。
- `SKILL.md`：主技能文档与完整功能导航。

## 快速开始

### 1) 查看技能说明

直接阅读根目录的 `SKILL.md`，按章节导航选择需要的工作流。

### 2) 运行示例脚本

```bash
python scripts/crawl_novel_index.py --mode index --outdir ./novel_data
python scripts/crawl_novel_index.py --mode download --index ./novel_data/novel_index.json --outdir ./novel_data --limit 10
python scripts/crawl_novel_index.py --mode outline --index ./novel_data/novel_index.json --outdir ./novel_data
```

## Git 指令

仓库地址：`https://github.com/DandanLLab/wanxiang-scroll`

### 1) 首次克隆仓库

```bash
git clone https://github.com/DandanLLab/wanxiang-scroll.git
cd wanxiang-scroll
```

### 2) 已有本地目录时关联远程仓库

```bash
git init
git remote add origin https://github.com/DandanLLab/wanxiang-scroll.git
```

### 3) 提交并推送到 GitHub

```bash
git add .
git commit -m "docs: update README and license notes"
git push -u origin main
```

## 使用与合规说明

- 本仓库中的小说分析与素材整理内容主要用于学习和研究用途。
- 请确保你在使用爬取与下载脚本时遵守目标站点服务条款和当地法律法规。

## 开源协议

本项目采用 **MIT License** 开源。详见 [LICENSE](./LICENSE)。
