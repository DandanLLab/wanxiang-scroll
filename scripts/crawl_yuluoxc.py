#!/usr/bin/env python3
"""
yuluoxc_eboos_download.zip 小说提取脚本
从 ZIP 压缩包中提取小说文件并整理到目标目录

⚠️ 学习用途声明：本脚本提取的所有小说文件仅供学习参考使用，不得用于任何商业用途或其他非学习目的。
"""
import os
import sys
import json
import zipfile
import argparse
import re
from pathlib import Path
from datetime import datetime

def extract_yuluoxc_zip(zip_path, output_dir):
    """
    从 yuluoxc_eboos_download.zip 提取小说文件
    
    Args:
        zip_path (str): ZIP 文件路径
        output_dir (str): 输出目录
    
    Returns:
        dict: 提取结果统计
    """
    stats = {
        "total_files": 0,
        "txt_files": 0,
        "other_files": 0,
        "skipped": 0,
        "errors": [],
        "novels": []
    }
    
    if not os.path.exists(zip_path):
        print(f"❌ ZIP 文件不存在: {zip_path}")
        return stats
    
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"📦 开始解压: {zip_path}")
    print(f"📁 输出目录: {output_dir}")
    
    try:
        with zipfile.ZipFile(zip_path, 'r') as zf:
            file_list = zf.namelist()
            stats["total_files"] = len(file_list)
            
            print(f"📄 共发现 {len(file_list)} 个文件")
            
            for i, filename in enumerate(file_list):
                try:
                    if filename.endswith('/'):
                        continue
                    
                    basename = os.path.basename(filename)
                    
                    if not basename:
                        continue
                    
                    if basename.lower().endswith('.txt'):
                        safe_name = re.sub(r'[<>:"/\\|?*]', '_', basename)
                        out_path = os.path.join(output_dir, safe_name)
                        
                        if os.path.exists(out_path):
                            stats["skipped"] += 1
                            continue
                        
                        with zf.open(filename) as source:
                            content = source.read()
                            try:
                                text = content.decode('utf-8')
                            except UnicodeDecodeError:
                                try:
                                    text = content.decode('gbk')
                                except UnicodeDecodeError:
                                    text = content.decode('utf-8', errors='ignore')
                            
                            with open(out_path, 'w', encoding='utf-8') as f:
                                f.write(text)
                            
                            stats["txt_files"] += 1
                            stats["novels"].append({
                                "name": safe_name,
                                "source": filename,
                                "size": len(text)
                            })
                    else:
                        stats["other_files"] += 1
                    
                    if (i + 1) % 100 == 0:
                        print(f"  进度: {i+1}/{len(file_list)} | txt: {stats['txt_files']} | skip: {stats['skipped']}")
                
                except Exception as e:
                    stats["errors"].append(f"{filename}: {str(e)}")
    
    except zipfile.BadZipFile:
        stats["errors"].append("ZIP 文件损坏或格式不正确")
    except Exception as e:
        stats["errors"].append(f"解压失败: {str(e)}")
    
    return stats

def save_index(output_dir, stats):
    """保存小说索引文件"""
    index_path = os.path.join(output_dir, "yuluoxc_index.json")
    
    index_data = {
        "source": "yuluoxc_eboos_download.zip",
        "extract_time": datetime.now().isoformat(),
        "stats": {
            "total_files": stats["total_files"],
            "txt_files": stats["txt_files"],
            "other_files": stats["other_files"],
            "skipped": stats["skipped"]
        },
        "novels": stats["novels"]
    }
    
    with open(index_path, 'w', encoding='utf-8') as f:
        json.dump(index_data, f, ensure_ascii=False, indent=2)
    
    print(f"📋 索引文件已保存: {index_path}")

def main():
    parser = argparse.ArgumentParser(
        description="从 yuluoxc_eboos_download.zip 提取小说文件",
        epilog="⚠️ 学习用途声明：本脚本提取的所有小说文件仅供学习参考使用"
    )
    parser.add_argument(
        "--zip", 
        default="d:/projects/yuluoxc_eboos_download.zip",
        help="ZIP 文件路径 (默认: d:/projects/yuluoxc_eboos_download.zip)"
    )
    parser.add_argument(
        "--output", 
        default="d:/projects/novel_data/yuluoxc",
        help="输出目录 (默认: d:/projects/novel_data/yuluoxc)"
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("📚 yuluoxc_eboos_download.zip 小说提取脚本")
    print("⚠️  学习用途声明：提取的小说文件仅供学习参考使用")
    print("=" * 60)
    
    start_time = datetime.now()
    print(f"⏰ 开始时间: {start_time}")
    
    stats = extract_yuluoxc_zip(args.zip, args.output)
    
    if stats["txt_files"] > 0:
        save_index(args.output, stats)
    
    end_time = datetime.now()
    duration = end_time - start_time
    
    print("\n" + "=" * 60)
    print("📊 提取完成统计")
    print("=" * 60)
    print(f"  总文件数: {stats['total_files']}")
    print(f"  TXT 小说: {stats['txt_files']}")
    print(f"  其他文件: {stats['other_files']}")
    print(f"  跳过文件: {stats['skipped']}")
    print(f"  错误数量: {len(stats['errors'])}")
    print(f"  耗时: {duration}")
    
    if stats["errors"]:
        print("\n❌ 错误列表:")
        for err in stats["errors"][:10]:
            print(f"  - {err}")
        if len(stats["errors"]) > 10:
            print(f"  ... 还有 {len(stats['errors']) - 10} 个错误")
    
    print("\n⚠️  提醒：所有提取的小说文件仅供学习参考使用，不得用于商业用途")
    print("=" * 60)

if __name__ == "__main__":
    main()
