import os
import re
import json
from pathlib import Path
from collections import defaultdict

REPORTS_DIR = r"d:\projects\wanxiang-scroll\references\chapter-12-book-analysis\reports"
NOVEL_LIST_FILE = r"d:\projects\wanxiang-scroll\references\chapter-12-book-analysis\novel_list.json"

def clean_novel_name(filename):
    name = filename.replace('.md', '')
    name = re.sub(r'^\d{4}-', '', name)
    name = re.sub(r'_\d+$', '', name)
    name = re.sub(r'_Unicode$', '', name)
    name = re.sub(r'_作者.*', '', name)
    name = re.sub(r'⊙.*', '', name)
    name = re.sub(r'_tags_.*', '', name)
    return name.strip()

def main():
    print("开始删除重复的分析文件...")
    
    files = list(Path(REPORTS_DIR).glob("*.md"))
    print(f"总报告数: {len(files)}")
    
    name_to_files = defaultdict(list)
    for f in files:
        name = clean_novel_name(f.name)
        name_to_files[name].append(f)
    
    duplicates = {k: v for k, v in name_to_files.items() if len(v) > 1}
    print(f"重复的小说名: {len(duplicates)}")
    
    deleted_count = 0
    for name, file_list in duplicates.items():
        file_list.sort(key=lambda x: os.path.getsize(str(x)), reverse=True)
        keep_file = file_list[0]
        for f in file_list[1:]:
            try:
                os.remove(str(f))
                deleted_count += 1
            except Exception as e:
                print(f"删除失败: {f.name} - {e}")
    
    print(f"\n删除完成!")
    print(f"删除重复文件: {deleted_count}")
    
    remaining = list(Path(REPORTS_DIR).glob("*.md"))
    print(f"剩余报告数: {len(remaining)}")
    
    unique_names = set()
    for f in remaining:
        name = clean_novel_name(f.name)
        unique_names.add(name)
    print(f"去重后小说数: {len(unique_names)}")

if __name__ == "__main__":
    main()
