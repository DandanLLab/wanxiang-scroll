#!/usr/bin/env python3
"""
全量下载+大纲提取 - 兼容原索引格式
用法: python crawl_all.py [--delay 1.5] [--limit 0] [--skip-download]
"""
import json, os, sys, re, time, argparse
from urllib.request import urlopen, Request
from urllib.error import URLError
from pathlib import Path
from collections import Counter

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

def fetch(url, timeout=30, retries=3):
    for attempt in range(retries):
        try:
            req = Request(url, headers=HEADERS)
            with urlopen(req, timeout=timeout) as r:
                return r.read()
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(2 ** attempt)
            else:
                return None

def download_txt(url, filepath, timeout=60, retries=3):
    data = fetch(url, timeout, retries)
    if data and len(data) > 100:
        with open(filepath, "wb") as f:
            f.write(data)
        return len(data)
    return 0

def extract_outline(filepath, max_chars=500000):
    """从txt提取大纲"""
    text = None
    for enc in ["utf-8", "gbk", "gb18030", "big5"]:
        try:
            with open(filepath, "r", encoding=enc) as f:
                text = f.read(max_chars)
            break
        except (UnicodeDecodeError, UnicodeError):
            continue
    if not text or len(text) < 100:
        return None

    # 章节检测
    patterns = [
        re.compile(r'^第[零一二三四五六七八九十百千万\d]+[卷章集部篇回]\s*.{0,50}$', re.MULTILINE),
        re.compile(r'^[Cc]hapter\s+\d+.*$', re.MULTILINE),
        re.compile(r'^第\d+话\s*.{0,50}$', re.MULTILINE),
        re.compile(r'^【[^】]{1,50}】$', re.MULTILINE),
    ]
    
    best_pat, best_cnt = None, 0
    for pat in patterns:
        cnt = len(pat.findall(text[:50000]))
        if cnt > best_cnt:
            best_cnt = cnt
            best_pat = pat
    
    chapters = []
    if best_pat:
        for m in best_pat.finditer(text):
            chapters.append(m.group().strip())
    
    has_volume = any(re.match(r'^第[零一二三四五六七八九十百千万\d]+卷', c) for c in chapters)
    n_ch = len(chapters)
    
    if has_volume: stype = "卷章结构"
    elif n_ch > 100: stype = "长篇连载"
    elif n_ch > 30: stype = "中篇分章"
    elif n_ch > 5: stype = "短篇分章"
    else: stype = "短篇/无分章"
    
    # 关键词
    kws = ["穿越","变身","转生","重生","觉醒","突破","修炼","战斗","系统","任务",
           "魔法","异世界","校园","修仙","末世","圣女","公主","女王","魔王","勇者",
           "精灵","龙","恋爱","告白","结局","秘密","阴谋","复仇","伪娘","性转"]
    found = [{"keyword": k, "count": text.count(k)} for k in kws if text.count(k) > 0]
    found.sort(key=lambda x: x["count"], reverse=True)
    
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    opening = ' '.join(lines[:3])[:300] if lines else ""
    ending = ' '.join(lines[-3:])[-200:] if lines else ""
    
    return {
        "filename": os.path.basename(filepath),
        "title": Path(filepath).stem,
        "total_chars": len(text),
        "structure_type": stype,
        "chapter_count": n_ch,
        "has_volume": has_volume,
        "keywords": found[:15],
        "opening": opening,
        "ending": ending,
        "chapters": chapters[:100],
    }

def main():
    parser = argparse.ArgumentParser(description="全量下载+大纲提取")
    parser.add_argument("--index", default="D:/openclaw/.openclaw/workspace/novel_data/novel_index.json")
    parser.add_argument("--outdir", default="D:/openclaw/.openclaw/workspace/novel_data")
    parser.add_argument("--delay", type=float, default=1.5, help="下载间隔秒")
    parser.add_argument("--limit", type=int, default=0, help="限制数量(0=全部)")
    parser.add_argument("--skip-download", action="store_true")
    parser.add_argument("--skip-outline", action="store_true")
    args = parser.parse_args()
    
    txt_dir = os.path.join(args.outdir, "txt")
    os.makedirs(txt_dir, exist_ok=True)
    
    # 加载索引
    with open(args.index, "r", encoding="utf-8") as f:
        index = json.load(f)
    
    novels = index.get("novels", [])
    total = len(novels)
    if args.limit > 0:
        novels = novels[:args.limit]
    
    print(f"Index: {total} novels, processing {len(novels)}")
    
    # 下载
    if not args.skip_download:
        print(f"\n=== Downloading (delay={args.delay}s) ===")
        ok, fail, skip = 0, 0, 0
        
        for i, n in enumerate(novels):
            name = n.get("name", n.get("title", f"novel_{i}"))
            safe_name = re.sub(r'[<>:"/\\|?*]', '_', name)[:80]
            out_path = os.path.join(txt_dir, f"{safe_name}.txt")
            
            # 跳过已下载
            if os.path.exists(out_path) and os.path.getsize(out_path) > 100:
                skip += 1
                if (i + 1) % 100 == 0:
                    print(f"  [{i+1}/{len(novels)}] OK:{ok} FAIL:{fail} SKIP:{skip}")
                continue
            
            # 获取txt URL
            txt_url = n.get("txt_url", "")
            if not txt_url:
                # 从page_url推导
                page_url = n.get("page_url", "")
                if page_url:
                    txt_url = page_url.replace("_page/", "").rstrip("/") + ".txt"
            
            if not txt_url:
                fail += 1
                continue
            
            size = download_txt(txt_url, out_path)
            if size > 0:
                ok += 1
            else:
                fail += 1
                # 删除空文件
                if os.path.exists(out_path):
                    os.remove(out_path)
            
            if (i + 1) % 50 == 0:
                print(f"  [{i+1}/{len(novels)}] OK:{ok} FAIL:{fail} SKIP:{skip}")
            
            time.sleep(args.delay)
        
        print(f"\nDownload done: OK={ok} FAIL={fail} SKIP={skip}")
    
    # 大纲提取
    if not args.skip_outline:
        print(f"\n=== Extracting outlines ===")
        outlines = []
        txt_files = sorted(Path(txt_dir).glob("*.txt"))
        print(f"Found {len(txt_files)} txt files")
        
        for i, tf in enumerate(txt_files):
            outline = extract_outline(str(tf))
            if outline:
                outlines.append(outline)
            if (i + 1) % 100 == 0:
                print(f"  [{i+1}/{len(txt_files)}] outlines: {len(outlines)}")
        
        out_path = os.path.join(args.outdir, "novel_outlines.json")
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump({"total": len(outlines), "outlines": outlines}, f, ensure_ascii=False, indent=2)
        
        print(f"Outlines: {len(outlines)} -> {out_path}")
    
    # 统计
    txt_count = len(list(Path(txt_dir).glob("*.txt")))
    print(f"\n=== COMPLETE ===")
    print(f"  Index: {total}")
    print(f"  TXT files: {txt_count}")
    print(f"  Dir: {args.outdir}")

if __name__ == "__main__":
    main()
