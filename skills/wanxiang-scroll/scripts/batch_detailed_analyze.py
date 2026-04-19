import os
import re
import json
from pathlib import Path
from datetime import datetime
import time

NOVEL_DIR = r"d:\projects\novel_data\txt"
OUTPUT_DIR = r"d:\projects\wanxiang-scroll\references\chapter-12-book-analysis\reports"
PROGRESS_FILE = r"d:\projects\wanxiang-scroll\references\chapter-12-book-analysis\progress.json"

os.makedirs(OUTPUT_DIR, exist_ok=True)

def clean_novel_name(filename):
    name = filename.replace('.txt', '')
    name = re.sub(r'_\d+$', '', name)
    name = re.sub(r'_Unicode$', '', name)
    name = re.sub(r'_作者.*', '', name)
    name = re.sub(r'⊙.*', '', name)
    name = re.sub(r'_tags_.*', '', name)
    name = re.sub(r'\(\d+\)$', '', name)
    name = re.sub(r'（.*）$', '', name)
    name = re.sub(r'《|》', '', name)
    name = re.sub(r'【.*】', '', name)
    name = re.sub(r'_第.*章.*', '', name)
    return name.strip()

def extract_content(filepath, max_chars=10000):
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read(max_chars)
        return content
    except:
        return ''

def extract_chapters(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        chapter_patterns = [
            r'第[一二三四五六七八九十百千万零\d]+[章节回]',
            r'Chapter\s*\d+',
            r'CHAPTER\s*\d+',
            r'【第[一二三四五六七八九十百千万零\d]+[章节回]】',
        ]
        chapter_count = 0
        for pattern in chapter_patterns:
            matches = re.findall(pattern, content)
            chapter_count = max(chapter_count, len(matches))
        return chapter_count
    except:
        return 0

def analyze_novel_detailed(filepath, filename):
    content = extract_content(filepath)
    if not content:
        return None
    
    name = clean_novel_name(filename)
    file_size = os.path.getsize(filepath)
    word_count = file_size // 3
    chapter_count = extract_chapters(filepath)
    
    novel_type = "未知"
    type_keywords = {
        "变身文": ["变身", "男变女", "TS", "性转"],
        "穿越文": ["穿越", "重生", "转世"],
        "重生文": ["重生", "回到"],
        "转生文": ["转生", "异世界"]
    }
    for t, keywords in type_keywords.items():
        for kw in keywords:
            if kw in filename or kw in content[:2000]:
                novel_type = t
                break
        if novel_type != "未知":
            break
    
    transform_type = "未知"
    transform_keywords = {
        "男变女": ["男变女", "TS", "性转"],
        "变萝莉": ["萝莉", "萝", "幼女"],
        "变妖物": ["狐", "蛇", "妖", "兽", "龙"],
        "变萌妹": ["萌", "可爱", "美少女"]
    }
    for t, keywords in transform_keywords.items():
        for kw in keywords:
            if kw in filename:
                transform_type = t
                break
        if transform_type != "未知":
            break
    
    background = "未知"
    background_keywords = {
        "火影同人": ["火影", "忍者", "查克拉"],
        "海贼同人": ["海贼", "恶魔果实", "海军"],
        "漫威同人": ["漫威", "复仇者", "钢铁侠"],
        "异世界": ["异世界", "异界", "魔法"],
        "仙侠": ["仙侠", "修仙", "灵气"],
        "末世": ["末世", "丧尸", "废土"],
        "校园": ["校园", "学校", "学生"]
    }
    for t, keywords in background_keywords.items():
        for kw in keywords:
            if kw in filename or kw in content[:2000]:
                background = t
                break
        if background != "未知":
            break
    
    protagonist = "未知"
    protag_match = re.search(r'(主角|主人公|男主|女主)[：:]\s*([^\n，。]{2,10})', content[:5000])
    if protag_match:
        protagonist = protag_match.group(2).strip()
    
    core_setting = "未知"
    setting_patterns = [
        r'(变身|穿越|重生|转生)[^\n。]{5,50}',
        r'(设定|背景)[：:][^\n。]{10,100}'
    ]
    for pattern in setting_patterns:
        match = re.search(pattern, content[:3000])
        if match:
            core_setting = match.group(0)[:50]
            break
    
    return {
        "filename": filename,
        "name": name,
        "type": novel_type,
        "transform_type": transform_type,
        "background": background,
        "word_count": word_count,
        "chapter_count": chapter_count,
        "file_size": file_size,
        "protagonist": protagonist,
        "core_setting": core_setting,
        "analyzed_at": datetime.now().isoformat()
    }

def generate_report(novel_info):
    report = f"""# 《{novel_info['name']}》拆书分析报告

> 分析日期：{novel_info['analyzed_at'][:10]}
> 小说类型：{novel_info['type']}

---

## 一、基本信息

| 项目 | 内容 |
|------|------|
| **书名** | {novel_info['name']} |
| **类型** | {novel_info['type']} |
| **变身类型** | {novel_info['transform_type']} |
| **背景设定** | {novel_info['background']} |
| **字数** | {novel_info['word_count']}万 |
| **章节数** | {novel_info['chapter_count']}章 |
| **主角** | {novel_info['protagonist']} |

---

## 二、核心设定

{novel_info['core_setting']}

---

## 三、素材价值评估

| 维度 | 评分(1-10) | 说明 |
|------|------------|------|
| **设定创新性** | - | 待深度分析 |
| **人物塑造** | - | 待深度分析 |
| **情节张力** | - | 待深度分析 |
| **可借鉴度** | - | 待深度分析 |
| **综合评分** | - | 待深度分析 |

---

*本报告由批量分析脚本自动生成，待深度分析*
"""
    return report

def load_progress():
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"analyzed": [], "last_index": 0}

def save_progress(progress):
    with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
        json.dump(progress, f, ensure_ascii=False, indent=2)

def main():
    print("开始批量详细分析小说...")
    
    files = list(Path(NOVEL_DIR).glob("*.txt"))
    print(f"总文件数: {len(files)}")
    
    progress = load_progress()
    analyzed_files = set(progress.get("analyzed", []))
    start_index = progress.get("last_index", 0)
    
    print(f"已分析: {len(analyzed_files)}")
    print(f"从第 {start_index} 个文件继续...")
    
    results = []
    new_analyzed = 0
    
    for i, filepath in enumerate(files[start_index:], start=start_index):
        if filepath.name in analyzed_files:
            continue
        
        if i % 50 == 0:
            print(f"处理进度: {i}/{len(files)} ({i*100//len(files)}%)")
        
        try:
            info = analyze_novel_detailed(str(filepath), filepath.name)
            if info:
                results.append(info)
                analyzed_files.add(filepath.name)
                new_analyzed += 1
                
                safe_name = re.sub(r'[\\/:*?"<>|]', '_', info['name'][:50])
                report_file = os.path.join(OUTPUT_DIR, f"{i:04d}-{safe_name}.md")
                report = generate_report(info)
                with open(report_file, 'w', encoding='utf-8') as f:
                    f.write(report)
                
                if new_analyzed % 100 == 0:
                    progress["analyzed"] = list(analyzed_files)
                    progress["last_index"] = i
                    save_progress(progress)
                    
                    all_results_file = os.path.join(OUTPUT_DIR, "..", "all_novels_detailed.json")
                    with open(all_results_file, 'w', encoding='utf-8') as f:
                        json.dump(results, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"处理 {filepath.name} 时出错: {e}")
            continue
    
    progress["analyzed"] = list(analyzed_files)
    progress["last_index"] = len(files)
    save_progress(progress)
    
    all_results_file = os.path.join(OUTPUT_DIR, "..", "all_novels_detailed.json")
    with open(all_results_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n分析完成!")
    print(f"本次新分析: {new_analyzed}")
    print(f"总计已分析: {len(analyzed_files)}")
    print(f"结果保存到: {all_results_file}")

if __name__ == "__main__":
    main()
