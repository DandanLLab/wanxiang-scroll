#!/usr/bin/env python3
"""
全量下载+大纲提取 v3 - 正确获取txt下载链接
用法: python crawl_all_v3.py [--delay 1.5] [--skip-download] [--skip-outline]

⚠️ 安全警告：
- 此脚本用于下载小说内容，请确保遵守相关法律法规
- 仅用于个人学习和研究目的
- 请勿用于商业用途或侵犯版权
"""
import json, os, sys, re, time, argparse, hashlib
from urllib.request import urlopen, Request
from urllib.parse import unquote, quote
from pathlib import Path

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
                time.sleep(2 ** attempt)
            else:
                return None

def fetch_text(url, **kw):
    data = fetch(url, **kw)
    if data:
        return data.decode("utf-8", errors="replace")
    return ""

def find_txt_link(page_url, base_url):
    """从_page页面找到.txt下载链接"""
    html = fetch_text(page_url)
    if not html:
        return None
    
    # 找 href="xxx.txt" 链接
    for m in re.finditer(r'href="([^"]*\.txt)"', html):
        link = m.group(1)
        if link.startswith("http"):
            return link
        elif link.startswith("/"):
            return base_url + link
        else:
            # 相对路径
            return page_url.rsplit("/", 1)[0] + "/" + link
    
    # 尝试 .txt 在上级目录
    # page_url: .../分类/名字_page/
    # txt应该在: .../分类/名字.txt
    parent = page_url.replace("_page/", "").rstrip("/")
    if not parent.endswith(".txt"):
        candidate = parent + ".txt"
        # 验证
        data = fetch(candidate, timeout=10, retries=1)
        if data and len(data) > 100:
            return candidate
    
    return None

def download_txt(url, filepath, timeout=120, retries=3):
    data = fetch(url, timeout, retries)
    if data and len(data) > 100:
        with open(filepath, "wb") as f:
            f.write(data)
        return len(data)
    return 0

# ===== Outline =====
CHAPTER_PATTERNS = [
    re.compile(r'^第[零一二三四五六七八九十百千万\d]+[卷章集部篇回]\s*.{0,50}$', re.MULTILINE),
    re.compile(r'^[Cc]hapter\s+\d+.*$', re.MULTILINE),
    re.compile(r'^第\d+话\s*.{0,50}$', re.MULTILINE),
    re.compile(r'^【[^】]{1,50}】$', re.MULTILINE),
]

def extract_outline(filepath, max_chars=500000):
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
    
    best_pat, best_cnt = None, 0
    for pat in CHAPTER_PATTERNS:
        cnt = len(pat.findall(text[:50000]))
        if cnt > best_cnt:
            best_cnt = cnt
            best_pat = pat
    
    chapters = [m.group().strip() for m in best_pat.finditer(text)] if best_pat else []
    has_volume = any(re.match(r'^第[零一二三四五六七八九十百千万\d]+卷', c) for c in chapters)
    n_ch = len(chapters)
    
    if has_volume: stype = "卷章结构"
    elif n_ch > 100: stype = "长篇连载"
    elif n_ch > 30: stype = "中篇分章"
    elif n_ch > 5: stype = "短篇分章"
    else: stype = "短篇/无分章"
    
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
    parser = argparse.ArgumentParser(description="全量下载v3")
    parser.add_argument("--index", default="D:/openclaw/.openclaw/workspace/novel_data/novel_index.json")
    parser.add_argument("--outdir", default="D:/openclaw/.openclaw/workspace/novel_data")
    parser.add_argument("--delay", type=float, default=1.5)
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--skip-download", action="store_true")
    parser.add_argument("--skip-outline", action="store_true")
    parser.add_argument("--resume", action="store_true", help="只下载未完成的")
    args = parser.parse_args()
    
    txt_dir = os.path.join(args.outdir, "txt")
    os.makedirs(txt_dir, exist_ok=True)
    
    with open(args.index, "r", encoding="utf-8") as f:
        index = json.load(f)
    
    novels = index.get("novels", [])
    total = len(novels)
    if args.limit > 0:
        novels = novels[:args.limit]
    
    print(f"Index: {total} novels")
    
    # 构建已下载集合
    existing = set()
    for f in os.listdir(txt_dir):
        if f.endswith(".txt"):
            existing.add(f.lower())
    
    print(f"Already downloaded: {len(existing)}")
    
    # Download
    if not args.skip_download:
        print(f"\n=== Downloading (delay={args.delay}s) ===")
        ok, fail, skip, not_found = 0, 0, 0, 0
        
        for i, n in enumerate(novels):
            name = n.get("name", n.get("title", f"novel_{i}"))
            safe_name = re.sub(r'[<>:"/\\|?*]', '_', name)[:80]
            out_file = f"{safe_name}.txt"
            out_path = os.path.join(txt_dir, out_file)
            
            # Skip already downloaded
            if out_file.lower() in existing:
                skip += 1
                continue
            
            page_url = n.get("page_url", "")
            base_url = n.get("base_url", "")
            if not base_url and page_url:
                base_url = re.match(r'https?://[^/]+', page_url).group(0)
            
            # Step 1: 找txt链接
            txt_url = n.get("txt_url", "")
            
            # 验证txt_url是否可用
            if txt_url:
                test = fetch(txt_url, timeout=10, retries=1)
                if not test or len(test) < 100:
                    txt_url = ""  # 不可用，重新找
            
            if not txt_url and page_url:
                txt_url = find_txt_link(page_url, base_url)
                if txt_url:
                    n["txt_url"] = txt_url  # 更新索引
            
            if not txt_url:
                not_found += 1
                if (i + 1) % 100 == 0:
                    print(f"  [{i+1}/{len(novels)}] OK:{ok} FAIL:{fail} SKIP:{skip} NO_TXT:{not_found}")
                continue
            
            # Step 2: 下载
            size = download_txt(txt_url, out_path)
            if size > 0:
                ok += 1
                existing.add(out_file.lower())
            else:
                fail += 1
                if os.path.exists(out_path) and os.path.getsize(out_path) < 100:
                    os.remove(out_path)
            
            if (i + 1) % 100 == 0:
                print(f"  [{i+1}/{len(novels)}] OK:{ok} FAIL:{fail} SKIP:{skip} NO_TXT:{not_found}")
            
            time.sleep(args.delay)
        
        # 保存更新后的索引
        with open(args.index, "w", encoding="utf-8") as f:
            json.dump(index, f, ensure_ascii=False, indent=2)
        
        print(f"\nDownload done: OK={ok} FAIL={fail} SKIP={skip} NO_TXT={not_found}")
    
    # Outline
    if not args.skip_outline:
        print(f"\n=== Extracting outlines ===")
        outlines = []
        txt_files = sorted(Path(txt_dir).glob("*.txt"))
        print(f"Found {len(txt_files)} txt files")
        
        for i, tf in enumerate(txt_files):
            outline = extract_outline(str(tf))
            if outline:
                outlines.append(outline)
            if (i + 1) % 500 == 0:
                print(f"  [{i+1}/{len(txt_files)}] outlines: {len(outlines)}")
        
        out_path = os.path.join(args.outdir, "novel_outlines.json")
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump({"total": len(outlines), "outlines": outlines}, f, ensure_ascii=False, indent=2)
        
        print(f"Outlines: {len(outlines)}")
    
    txt_count = len(list(Path(txt_dir).glob("*.txt")))
    print(f"\n=== DONE === Total TXT: {txt_count} | Dir: {args.outdir}")

if __name__ == "__main__":
    main()