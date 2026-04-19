#!/usr/bin/env python3
"""
从小说TXT文件中提取章节大纲和结构
- 识别章节标题、卷结构
- 提取关键情节点
- 输出结构化大纲JSON

用法:
  python3 scripts/extract_novel_outline.py --input INPUT_TXT --output OUTPUT_JSON
  python3 scripts/extract_novel_outline.py --dir INPUT_DIR --output-dir OUTPUT_DIR

参数:
  --input       单个TXT文件路径
  --output      单个文件输出JSON路径
  --dir         批量处理目录
  --output-dir  批量输出目录
  --max-chars   最大读取字符数 (默认: 500000, 约50万字)
"""

import argparse
import json
import os
import re
import sys
from collections import Counter


# 章节标题匹配模式（按优先级排序）
CHAPTER_PATTERNS = [
    # 第X卷/第X章 格式
    re.compile(r'^第[零一二三四五六七八九十百千万\d]+[卷章集部篇回]\s*.{0,50}$', re.MULTILINE),
    # 卷X/章X 格式
    re.compile(r'^[卷章集部篇回]\s*[零一二三四五六七八九十百千万\d]+\s*.{0,50}$', re.MULTILINE),
    # Chapter X 格式
    re.compile(r'^[Cc]hapter\s+\d+.*$', re.MULTILINE),
    # 第X话 格式
    re.compile(r'^第\d+话\s*.{0,50}$', re.MULTILINE),
    # 纯数字章节 如 "1" "001"
    re.compile(r'^\d{1,5}\s*$', re.MULTILINE),
    # 【标题】格式
    re.compile(r'^【[^】]{1,50}】$', re.MULTILINE),
    # 章节标记+标题 如 "第一章 标题"
    re.compile(r'^[第][\d零一二三四五六七八九十百千万]+[章节]\s*\S+', re.MULTILINE),
]


def detect_chapter_pattern(text, sample_size=50000):
    """自动检测最适合的章节匹配模式"""
    sample = text[:sample_size]
    best_pattern = None
    best_count = 0

    for pattern in CHAPTER_PATTERNS:
        matches = pattern.findall(sample)
        if len(matches) > best_count:
            best_count = len(matches)
            best_pattern = pattern

    return best_pattern, best_count


def extract_chapters(text, pattern=None):
    """从文本中提取章节结构"""
    if pattern is None:
        pattern, _ = detect_chapter_pattern(text)
    
    if pattern is None:
        return []

    matches = list(pattern.finditer(text))
    chapters = []

    for i, match in enumerate(matches):
        start = match.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        title = match.group().strip()
        content = text[start:end]

        # 提取章节首段文字（取前200字作为摘要）
        content_body = content[len(title):].strip()
        # 跳过空行
        lines = [l.strip() for l in content_body.split('\n') if l.strip()]
        preview = ' '.join(lines[:3])[:200] if lines else ""

        # 统计字数
        char_count = len(content_body)

        chapters.append({
            "title": title,
            "char_count": char_count,
            "preview": preview,
            "position": start
        })

    return chapters


def detect_volume_structure(chapters):
    """检测卷结构"""
    volumes = []
    current_volume = {"name": "默认卷", "chapters": []}

    for ch in chapters:
        title = ch["title"]
        # 判断是否为"卷"标题
        if re.match(r'^第[零一二三四五六七八九十百千万\d]+卷', title):
            if current_volume["chapters"]:
                volumes.append(current_volume)
            current_volume = {
                "name": title,
                "chapters": []
            }
        else:
            current_volume["chapters"].append(ch)

    if current_volume["chapters"] or current_volume["name"] != "默认卷":
        volumes.append(current_volume)

    return volumes


def analyze_structure(chapters, text):
    """分析小说整体结构"""
    total_chars = len(text)
    total_chapters = len(chapters)

    if total_chapters == 0:
        return {
            "total_chars": total_chars,
            "total_chapters": 0,
            "avg_chapter_length": 0,
            "structure_type": "unknown"
        }

    char_counts = [ch["char_count"] for ch in chapters]
    avg_length = sum(char_counts) / len(char_counts) if char_counts else 0

    # 检测结构类型
    has_volume = any(re.match(r'^第[零一二三四五六七八九十百千万\d]+卷', ch["title"]) for ch in chapters)
    if has_volume:
        structure_type = "卷章结构"
    elif total_chapters > 100:
        structure_type = "长篇连载"
    elif total_chapters > 30:
        structure_type = "中篇分章"
    else:
        structure_type = "短篇/中篇"

    return {
        "total_chars": total_chars,
        "total_chapters": total_chapters,
        "avg_chapter_length": int(avg_length),
        "max_chapter_length": max(char_counts),
        "min_chapter_length": min(char_counts),
        "structure_type": structure_type,
        "has_volume": has_volume
    }


def extract_plot_keywords(text, top_n=20):
    """提取可能的情节点关键词（基于高频词模式）"""
    # 常见情节关键词
    plot_keywords = [
        "穿越", "变身", "转生", "重生", "觉醒", "突破", "升级", "修炼",
        "战斗", "对决", "决战", "危机", "背叛", "重逢", "离别", "死亡",
        "复活", "进化", "觉醒", "获得", "发现", "揭示", "秘密", "阴谋",
        "告白", "恋爱", "结婚", "分离", "回忆", "真相", "终章", "结局",
        "系统", "任务", "副本", "等级", "技能", "异能", "魔法", "武技",
        "圣女", "公主", "女王", "魔王", "勇者", "精灵", "龙", "恶魔",
        "变身", "性转", "变嫁", "百合", "伪娘", "魔法少女", "异世界",
        "校园", "都市", "修仙", "仙侠", "玄幻", "科幻", "末世", "游戏"
    ]

    found = []
    for kw in plot_keywords:
        count = text.count(kw)
        if count > 0:
            found.append({"keyword": kw, "count": count})

    found.sort(key=lambda x: x["count"], reverse=True)
    return found[:top_n]


def process_txt_file(filepath, max_chars=500000):
    """处理单个TXT文件，提取大纲"""
    try:
        # 尝试多种编码
        for encoding in ["utf-8", "gbk", "gb18030", "big5", "utf-16"]:
            try:
                with open(filepath, "r", encoding=encoding) as f:
                    text = f.read(max_chars)
                break
            except (UnicodeDecodeError, UnicodeError):
                continue
        else:
            return {"error": f"无法解码文件: {filepath}"}
    except Exception as e:
        return {"error": f"读取文件失败: {str(e)}"}

    if not text.strip():
        return {"error": "文件内容为空"}

    # 提取章节
    chapters = extract_chapters(text)

    # 检测卷结构
    volumes = detect_volume_structure(chapters)

    # 分析整体结构
    structure = analyze_structure(chapters, text)

    # 提取情节关键词
    keywords = extract_plot_keywords(text)

    # 提取开头和结尾
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    opening = ' '.join(lines[:5])[:300] if lines else ""
    ending = ' '.join(lines[-5:])[-300:] if lines else ""

    result = {
        "filename": os.path.basename(filepath),
        "structure": structure,
        "keywords": keywords,
        "opening": opening,
        "ending": ending,
        "chapters": chapters[:200],  # 最多保留200章
        "total_chapters_extracted": len(chapters),
        "volumes": []
    }

    if volumes and structure.get("has_volume"):
        for vol in volumes:
            result["volumes"].append({
                "name": vol["name"],
                "chapter_count": len(vol["chapters"]),
                "chapters": vol["chapters"][:50]  # 每卷最多50章
            })

    return result


def process_directory(input_dir, output_dir, max_chars=500000):
    """批量处理目录下所有TXT文件"""
    os.makedirs(output_dir, exist_ok=True)
    results = []

    for filename in sorted(os.listdir(input_dir)):
        if not filename.endswith('.txt'):
            continue

        filepath = os.path.join(input_dir, filename)
        print(f"  处理: {filename}", end=" ", flush=True)

        result = process_txt_file(filepath, max_chars)
        results.append(result)

        status = "OK" if "error" not in result else result["error"]
        ch_count = result.get("total_chapters_extracted", 0)
        print(f"[{status}] {ch_count}章")

        # 保存单个结果
        out_name = filename.replace('.txt', '_outline.json')
        out_path = os.path.join(output_dir, out_name)
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

    # 保存汇总
    summary = {
        "total_files": len(results),
        "successful": sum(1 for r in results if "error" not in r),
        "failed": sum(1 for r in results if "error" in r),
        "results": results
    }

    summary_path = os.path.join(output_dir, "_summary.json")
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    print(f"\n完成! 成功: {summary['successful']}, 失败: {summary['failed']}")
    print(f"汇总: {summary_path}")
    return summary


def main():
    parser = argparse.ArgumentParser(description="从小说TXT提取章节大纲")
    parser.add_argument("--input", help="单个TXT文件路径")
    parser.add_argument("--output", help="单个文件输出JSON路径")
    parser.add_argument("--dir", help="批量处理目录")
    parser.add_argument("--output-dir", help="批量输出目录")
    parser.add_argument("--max-chars", type=int, default=500000, help="最大读取字符数")
    args = parser.parse_args()

    if args.input:
        result = process_txt_file(args.input, args.max_chars)
        output_path = args.output or args.input.replace('.txt', '_outline.json')
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"大纲提取完成: {output_path}")
        print(f"  章节数: {result.get('total_chapters_extracted', 0)}")
        print(f"  结构类型: {result.get('structure', {}).get('structure_type', 'unknown')}")
    elif args.dir:
        process_directory(args.dir, args.output_dir or "./outlines", args.max_chars)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
