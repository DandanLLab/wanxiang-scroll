#!/usr/bin/env python3
"""
全量下载v4 - 双策略：优先下载txt，失败则从_page页面提取正文
用法: python crawl_all_v4.py [--delay 2] [--workers 5]

⚠️ 安全警告：
- 此脚本用于下载小说内容，请确保遵守相关法律法规
- 仅用于个人学习和研究目的
- 请勿用于商业用途或侵犯版权
"""
import json, os, sys, re, time, argparse
from urllib.request import urlopen, Request
from urllib.parse import unquote
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
sys.stdout.reconfigure(line_buffering=True)

def fetch(url, timeout=30, retries=3):
    for attempt in range(retries):
        try:
            req = Request(url, headers=HEADERS)
            with urlopen(req, timeout=timeout) as r:
                return r.read()
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(1.5 * (attempt + 1))
            else:
                return None

def fetch_text(url, **kw):
    data = fetch(url, **kw)
    if data:
        return data.decode("utf-8", errors="replace")
    return ""

def save_novel(name, content, txt_dir):
    """保存小说内容到txt"""
    safe_name = re.sub(r'[<>:"/\\|?*]', '_', name)[:80]
    out_path = os.path.join(txt_dir, f"{safe_name}.txt")
    if isinstance(content, str):
        content = content.encode("utf-8")
    with open(out_path, "wb") as f:
        f.write(content)
    return len(content)

def try_download_txt(novel, txt_dir):
    """策略1: 直接下载txt文件"""
    name = novel.get("name", novel.get("title", ""))
    txt_url = novel.get("txt_url", "")
    
    if txt_url:
        data = fetch(txt_url, timeout=60, retries=2)
        if data and len(data) > 200:
            return save_novel(name, data, txt_dir), "txt"
    return 0, "fail"

def try_scrape_page(novel, txt_dir):
    """策略2: 从_page页面提取小说正文"""
    name = novel.get("name", novel.get("title", ""))
    page_url = novel.get("page_url", "")
    if not page_url:
        return 0, "fail"
    
    html = fetch_text(page_url, timeout=30, retries=2)
    if not html:
        return 0, "fail"
    
    # 提取正文
    content = ""
    # 方法1: 找article标签
    m = re.search(r'<article[^>]*>([\s\S]*?)</article>', html, re.IGNORECASE)
    if m:
        content = m.group(1)
    else:
        # 方法2: 找main标签
        m = re.search(r'<main[^>]*>([\s\S]*?)</main>', html, re.IGNORECASE)
        if m:
            content = m.group(1)
    
    if not content:
        return 0, "fail"
    
    # 清理HTML
    for tag in ["script", "style", "nav", "header", "footer", "noscript", "aside"]:
        content = re.sub(f'<{tag}[^>]*>[\\s\\S]*?</{tag}>', '', content, flags=re.IGNORECASE)
    text = re.sub(r'<[^>]+>', '\n', content)
    text = text.replace('&nbsp;', ' ').replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
    text = re.sub(r'\n{3,}', '\n\n', text).strip()
    
    if len(text) < 200:
        return 0, "fail"
    
    return save_novel(name, text, txt_dir), "page"

def process_novel(novel, txt_dir, existing):
    """处理单部小说"""
    name = novel.get("name", novel.get("title", ""))
    safe_name = re.sub(r'[<>:"/\\|?*]', '_', name)[:80]
    out_file = f"{safe_name}.txt"
    
    # 已下载则跳过
    if out_file.lower() in existing:
        return "skip", name
    
    # 策略1: 下载txt
    size, method = try_download_txt(novel, txt_dir)
    if size > 0:
        return "ok_txt", name
    
    # 策略2: 爬取页面
    size, method = try_scrape_page(novel, txt_dir)
    if size > 0:
        return "ok_page", name
    
    return "fail", name

def main():
    parser = argparse.ArgumentParser(description="全量下载v4")
    parser.add_argument("--index", default="D:/openclaw/.openclaw/workspace/novel_data/novel_index.json")
    parser.add_argument("--outdir", default="D:/openclaw/.openclaw/workspace/novel_data")
    parser.add_argument("--delay", type=float, default=2)
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--skip-download", action="store_true")
    parser.add_argument("--skip-outline", action="store_true")
    args = parser.parse_args()
    
    txt_dir = os.path.join(args.outdir, "txt")
    os.makedirs(txt_dir, exist_ok=True)
    
    with open(args.index, "r", encoding="utf-8") as f:
        index = json.load(f)
    
    novels = index.get("novels", [])
    if args.limit > 0:
        novels = novels[:args.limit]
    
    # 已下载集合
    existing = set()
    for f in os.listdir(txt_dir):
        if f.endswith(".txt"):
            existing.add(f.lower())
    
    print(f"Index: {len(novels)} | Already: {len(existing)}")
    
    stats = {"ok_txt": 0, "ok_page": 0, "skip": 0, "fail": 0}
    
    if not args.skip_download:
        print(f"\n=== Downloading (delay={args.delay}s) ===")
        
        for i, novel in enumerate(novels):
            result, name = process_novel(novel, txt_dir, existing)
            stats[result] += 1
            
            if result.startswith("ok"):
                existing.add(f"{re.sub(r'[<>:\"/\\\\|?*]', '_', name)[:80]}.txt".lower())
            
            if (i + 1) % 100 == 0:
                print(f"  [{i+1}/{len(novels)}] txt:{stats['ok_txt']} page:{stats['ok_page']} skip:{stats['skip']} fail:{stats['fail']}")
            
            if result.startswith("ok"):
                time.sleep(args.delay)
            elif result == "fail":
                time.sleep(0.5)  # fail时也稍微等一下避免限流
        
        print(f"\nDownload done: {stats}")
    
    # 大纲提取
    if not args.skip_outline:
        print(f"\n=== Extracting outlines ===")
        outlines = []
        txt_files = sorted(Path(txt_dir).glob("*.txt"))
        print(f"Found {len(txt_files)} txt files")
        
        from crawl_all import extract_outline
        for i, tf in enumerate(txt_files):
            # 内联大纲提取
            try:
                text = None
                for enc in ["utf-8", "gbk", "gb18030"]:
                    try:
                        with open(tf, "r", encoding=enc) as f:
                            text = f.read(500000)
                        break
                    except: continue
                if text and len(text) > 100:
                    chaps = re.findall(r'^第[零一二三四五六七八九十百千万\d]+[卷章集部篇回]\s*.{0,50}$', text, re.MULTILINE)
                    outlines.append({"title": tf.stem, "chars": len(text), "chapters": len(chaps), "opening": text[:200].strip()})
            except: pass
            
            if (i + 1) % 500 == 0:
                print(f"  [{i+1}/{len(txt_files)}] outlines: {len(outlines)}")
        
        out_path = os.path.join(args.outdir, "novel_outlines.json")
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump({"total": len(outlines), "outlines": outlines}, f, ensure_ascii=False, indent=2)
        print(f"Outlines: {len(outlines)}")
    
    txt_count = len(list(Path(txt_dir).glob("*.txt")))
    print(f"\n=== DONE === TXT: {txt_count}")

if __name__ == "__main__":
    main()