#!/usr/bin/env python3
"""
格式化助手
用于修复挤在一起的 Python 文件
"""

import re
import sys
from pathlib import Path


def fix_imports(content):
    """修复挤在一起的 import 语句"""
    # 匹配 import xxximport yyy 这种模式
    patterns = [
        # import osimport re -> import os\nimport re
        (r'import\s+(\w+)import', r'import \1\nimport'),
        # from x import yimport -> from x import y\nimport
        (r'from\s+(\S+)\s+import\s+([^\n]+?)import', r'from \1 import \2\nimport'),
    ]
    
    for pattern, replacement in patterns:
        content = re.sub(pattern, replacement, content)
    
    return content


def add_newlines_after_imports(content):
    """在 import 语句后添加空行"""
    lines = content.split('\n')
    new_lines = []
    prev_was_import = False
    
    for line in lines:
        stripped = line.strip()
        is_import = stripped.startswith('import ') or stripped.startswith('from ')
        
        if prev_was_import and not is_import and stripped and not stripped.startswith('#'):
            new_lines.append('')
        
        new_lines.append(line)
        prev_was_import = is_import
    
    return '\n'.join(new_lines)


def format_file(filepath):
    """格式化单个文件"""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # 修复 import
        content = fix_imports(content)
        content = add_newlines_after_imports(content)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return True
    except Exception as e:
        print(f"Error formatting {filepath}: {e}")
        return False


def main():
    scripts_dir = Path(__file__).parent
    
    files_to_format = [
        'batch_detailed_analyze.py',
        'extract_character_book.py',
        'extract_novel_outline.py',
        'crawl_all.py',
        'crawl_all_v3.py',
        'crawl_all_v4.py',
        'crawl_novel_index.py',
    ]
    
    for filename in files_to_format:
        filepath = scripts_dir / filename
        if filepath.exists():
            print(f"Formatting {filename}...")
            if format_file(filepath):
                print(f"  ✓ Done")
            else:
                print(f"  ✗ Failed")
        else:
            print(f"File not found: {filename}")


if __name__ == '__main__':
    main()
