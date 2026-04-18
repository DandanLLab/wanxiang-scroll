#!/usr/bin/env python3
"""
全量下载v5 - 使用requests+session+自动重试
"""
import json, os, sys, re, time, argparse
from pathlib import Path

try:
    import requests
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
except ImportError:
    print("Installing requests...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests", "-q"])
    import requests
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry

# Session with retry
def make_session():
    s = requests.Session()
    retries = Retry(total=5, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
    s.mount('http://', HTTPAdapter(max_retries=retries))
    s.mount('https://', HTTPAdapter(max_retries=retries))
    s.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"})
    return s

SESSION = make_session()

def normalize_url(url):
    """规范化URL，处理../和重复路径"""
    # 处理 ../
    while '/../' in url:
        old = url
        url = re.sub(r'/[^/]+/\.\./', '/', url)
        if url == old:
            break
    return url

def download_txt(url, filepath, timeout=60):
    url = normalize_url(url)
    try:
        r = SESSION.get(url, timeout=timeout)
        if r.status_code == 200 and len(r.content) > 100:
            with open(filepath, "wb") as f:
                f.write(r.content)
            return len(r.content)
    except Exception as e:
        pass
    return 0

def scrape_page(page_url):
    """从_page页面提取小说正文"""
    try:
        r = SESSION.get(page_url, timeout=30)
        if r.status_code != 200:
            return ""
        html = r.text
        
        # 找article或main
        m = re.search(r'<article[^>]*>([\s\S]*?)</article>', html, re.IGNORECASE)
        if m:
            content = m.group(1)
        else:
            m = re.search(r'<main[^>]*>([\s\S]*?)</main>', html, re.IGNORECASE)
            if m:
                content = m.group(1)
            else:
                content = html
        
        # 清理HTML
        for tag in ["script", "style", "nav", "header", "footer", "noscript", "aside"]:
            content = re.sub(f'<{tag}[^>]*>[\\s\\S]*?</{tag}>', '', content, flags=re.IGNORECASE)
        text = re.sub(r'<[^>]+>', '\n', content)
        text = text.replace('&nbsp;', ' ').replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
        text = re.sub(r'\n{3,}', '\n\n', text).strip()
        
        return text if len(text) > 200 else ""
    except:
        return ""

def main():
    parser = argparse.ArgumentParser(description="全量下载v5")
    parser.add_argument("--index", default="D:/openclaw/.openclaw/workspace/novel_data/novel_index.json")
    parser.add_argument("--outdir", default="D:/openclaw/.openclaw/workspace/novel_data")
    parser.add_argument("--delay", type=float, default=1.5)
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--skip-download", action="store_true")
    args = parser.parse_args()
    
    txt_dir = os.path.join(args.outdir, "txt")
    os.makedirs(txt_dir, exist_ok=True)
    
    with open(args.index, "r", encoding="utf-8") as f:
        index = json.load(f)
    
    novels = index.get("novels", [])
    if args.limit > 0:
        novels = novels[:args.limit]
    
    existing = {f.lower() for f in os.listdir(txt_dir) if f.endswith('.txt')}
    
    print(f"Index: {len(novels)} | Already: {len(existing)}")
    
    stats = {"ok_txt": 0, "ok_page": 0, "skip": 0, "fail": 0}
    
    if not args.skip_download:
        print(f"\n=== Downloading (delay={args.delay}s) ===")
        
        for i, n in enumerate(novels):
            name = n.get("name", n.get("title", f"novel_{i}"))
            safe_name = re.sub(r'[<>:"/\\|?*]', '_', name)[:80]
            out_file = f"{safe_name}.txt"
            out_path = os.path.join(txt_dir, out_file)
            
            if out_file.lower() in existing:
                stats["skip"] += 1
                continue
            
            # 策略1: 下载txt
            txt_url = n.get("txt_url", "")
            if txt_url:
                size = download_txt(txt_url, out_path)
                if size > 0:
                    stats["ok_txt"] += 1
                    existing.add(out_file.lower())
                    if (i + 1) % 50 == 0:
                        print(f"  [{i+1}/{len(novels)}] txt:{stats['ok_txt']} page:{stats['ok_page']} skip:{stats['skip']} fail:{stats['fail']}")
                    time.sleep(args.delay)
                    continue
            
            # 策略2: 爬取页面
            page_url = n.get("page_url", "")
            if page_url:
                text = scrape_page(page_url)
                if text:
                    with open(out_path, "w", encoding="utf-8") as f:
                        f.write(text)
                    stats["ok_page"] += 1
                    existing.add(out_file.lower())
                    if (i + 1) % 50 == 0:
                        print(f"  [{i+1}/{len(novels)}] txt:{stats['ok_txt']} page:{stats['ok_page']} skip:{stats['skip']} fail:{stats['fail']}")
                    time.sleep(args.delay)
                    continue
            
            stats["fail"] += 1
            
            if (i + 1) % 50 == 0:
                print(f"  [{i+1}/{len(novels)}] txt:{stats['ok_txt']} page:{stats['ok_page']} skip:{stats['skip']} fail:{stats['fail']}")
        
        print(f"\nDone: {stats}")
    
    txt_count = len(list(Path(txt_dir).glob("*.txt")))
    print(f"Total: {txt_count} files")

if __name__ == "__main__":
    main()