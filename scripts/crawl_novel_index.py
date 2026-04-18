#!/usr/bin/env python3
"""
爬取 transchinese.org 三个档案馆的小说目录和内容
- 单页全量抓取目录索引
- 下载代表性小说txt
- 提取章节大纲

用法:
  python3 scripts/crawl_novel_index.py --mode index  [--output OUTPUT]
  python3 scripts/crawl_novel_index.py --mode download --index INDEX_JSON --outdir OUTDIR --limit LIMIT
  python3 scripts/crawl_novel_index.py --mode outline  --txt-dir TXT_DIR --outdir OUTDIR

参数:
  --mode     index=仅抓索引, download=下载txt, outline=提取大纲, full=全部
  --output   索引输出路径 (默认: ./novel_index.json)
  --index    索引JSON路径 (download模式使用)
  --outdir   输出目录 (默认: ./novel_data)
  --limit    下载/大纲数量限制 (默认: 30)
"""

import argparse
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request
import urllib.error


def fetch_url(url, timeout=30, retries=3):
    """获取URL内容"""
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={
                "User-Agent": "Mozilla/5.0 (compatible; NovelBot/1.0)"
            })
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return resp.read().decode("utf-8", errors="replace")
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(2 ** attempt)
            else:
                print(f"  [WARN] Failed: {url} - {e}", file=sys.stderr)
                return ""


def download_file(url, filepath, timeout=60, retries=3):
    """下载文件到本地"""
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={
                "User-Agent": "Mozilla/5.0 (compatible; NovelBot/1.0)"
            })
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                data = resp.read()
                with open(filepath, "wb") as f:
                    f.write(data)
                return len(data)
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(2 ** attempt)
            else:
                print(f"  [WARN] Download failed: {url} - {e}", file=sys.stderr)
                return 0


def parse_novel_links(html, base_url, category_path):
    """从HTML中解析小说链接"""
    novels = []
    # 匹配 _page 结尾的链接
    pattern = r'href="([^"]*_page/)"'
    matches = re.findall(pattern, html)

    seen = set()
    for href in matches:
        # 构建完整URL
        if href.startswith("http"):
            page_url = href
        elif href.startswith("/"):
            page_url = base_url.rstrip("/") + href
        else:
            page_url = f"{base_url}/{category_path}/{href}"

        # 提取小说名称
        name = href.split("/")[-2] if href.endswith("/") else href.split("/")[-1]
        name = urllib.parse.unquote(name).replace("_page", "").strip()
        name = re.sub(r'_+$', '', name).strip()

        if not name or name in seen:
            continue
        seen.add(name)

        # 构建txt下载URL
        txt_url = page_url.replace("_page/", "").rstrip("/") + ".txt"

        novels.append({
            "name": name,
            "page_url": page_url,
            "txt_url": txt_url
        })

    return novels


def crawl_index(output_path):
    """爬取三个档案馆的目录索引"""
    archives = [
        {
            "name": "档案馆一(剧情向)",
            "base_url": "https://novel.transchinese.org",
            "categories": [
                ("未分类长篇", "%E6%9C%AA%E5%88%86%E7%B1%BB%E9%95%BF%E7%AF%87"),
                ("未分类中短篇", "%E6%9C%AA%E5%88%86%E7%B1%BB%E4%B8%AD%E7%9F%AD%E7%AF%87"),
            ]
        },
        {
            "name": "档案馆二(变嫁/变百)",
            "base_url": "https://xnovel.transchinese.org",
            "categories": [
                ("百合向变身小说", "%E7%99%BE%E5%90%88%E5%90%91%E5%8F%98%E8%BA%AB%E5%B0%8F%E8%AF%B4%E5%90%88%E9%9B%86"),
                ("变嫁小说", "%E5%8F%98%E5%AB%81%E5%B0%8F%E8%AF%B4%E5%90%88%E9%9B%86"),
                ("未分类(更新)", "%E6%9C%AA%E5%88%86%E7%B1%BB%EF%BC%88%E6%9B%B4%E6%96%B0%EF%BC%89"),
            ]
        },
        {
            "name": "档案馆三(epub/txt)",
            "base_url": "https://unovel.transchinese.org",
            "categories": [
                ("epub小说下载", "epub%E5%B0%8F%E8%AF%B4%E4%B8%8B%E8%BD%BD%EF%BC%88%E6%9B%B4%E6%96%B0%EF%BC%89"),
                ("txt小说下载", "txt%E5%B0%8F%E8%AF%B4%E4%B8%8B%E8%BD%BD%EF%BC%88%E6%9B%B4%E6%96%B0%EF%BC%89"),
            ]
        },
    ]

    all_novels = []

    for archive in archives:
        print(f"\n爬取: {archive['name']}")
        for cat_name, cat_path in archive["categories"]:
            print(f"  分类: {cat_name}")
            url = f"{archive['base_url']}/{cat_path}/"
            html = fetch_url(url)
            if not html:
                print(f"    [FAIL] 无法获取页面")
                continue

            novels = parse_novel_links(html, archive["base_url"], cat_path)
            for n in novels:
                n["archive"] = archive["name"]
                n["category"] = cat_name

            all_novels.extend(novels)
            print(f"    获取 {len(novels)} 部小说")

    # 去重
    seen = set()
    unique = []
    for n in all_novels:
        key = n["name"]
        if key not in seen:
            seen.add(key)
            unique.append(n)

    result = {
        "total": len(unique),
        "archives": [a["name"] for a in archives],
        "novels": unique
    }

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"\n索引完成: {len(unique)} 部小说 -> {output_path}")
    return result


def download_novels(index_path, outdir, limit):
    """从索引下载txt文件"""
    with open(index_path, "r", encoding="utf-8") as f:
        index = json.load(f)

    novels = index["novels"]
    # 优先选择标题中带章数信息的（说明是长篇）
    long_novels = [n for n in novels if re.search(r'\d{2,}', n["name"])]
    short_novels = [n for n in novels if n not in long_novels]
    selected = (long_novels + short_novels)[:limit]

    txt_dir = os.path.join(outdir, "txt")
    os.makedirs(txt_dir, exist_ok=True)

    downloaded = []
    for i, n in enumerate(selected):
        name_safe = re.sub(r'[\\/:*?"<>|]', '_', n["name"])[:80]
        filepath = os.path.join(txt_dir, f"{name_safe}.txt")

        print(f"  [{i+1}/{len(selected)}] {n['name'][:40]}...", end=" ", flush=True)
        size = download_file(n["txt_url"], filepath)
        if size > 0:
            downloaded.append({**n, "local_path": filepath, "size": size})
            print(f"OK ({size//1024}KB)")
        else:
            print("FAIL")
        time.sleep(0.5)

    # 保存下载记录
    dl_path = os.path.join(outdir, "download_log.json")
    with open(dl_path, "w", encoding="utf-8") as f:
        json.dump({"downloaded": downloaded, "count": len(downloaded)}, f, ensure_ascii=False, indent=2)

    print(f"\n下载完成: {len(downloaded)}/{len(selected)}")
    return downloaded


# ===== 大纲提取 =====

CHAPTER_PATTERNS = [
    re.compile(r'^第[零一二三四五六七八九十百千万\d]+[卷章集部篇回]\s*.{0,50}$', re.MULTILINE),
    re.compile(r'^[Cc]hapter\s+\d+.*$', re.MULTILINE),
    re.compile(r'^第\d+话\s*.{0,50}$', re.MULTILINE),
    re.compile(r'^【[^】]{1,50}】$', re.MULTILINE),
    re.compile(r'^[第][\d零一二三四五六七八九十百千万]+[章节]\s*\S+', re.MULTILINE),
]


def extract_outline(filepath, max_chars=500000):
    """从txt文件提取大纲"""
    # 读取
    text = None
    for enc in ["utf-8", "gbk", "gb18030", "big5"]:
        try:
            with open(filepath, "r", encoding=enc) as f:
                text = f.read(max_chars)
            break
        except (UnicodeDecodeError, UnicodeError):
            continue
    if text is None:
        return {"error": f"无法解码: {filepath}"}
    if not text.strip():
        return {"error": "文件为空"}

    # 检测章节模式
    best_pattern = None
    best_count = 0
    for pat in CHAPTER_PATTERNS:
        cnt = len(pat.findall(text[:50000]))
        if cnt > best_count:
            best_count = cnt
            best_pattern = pat

    chapters = []
    if best_pattern:
        matches = list(best_pattern.finditer(text))
        for i, m in enumerate(matches):
            start = m.start()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            title = m.group().strip()
            content = text[start:end]
            body = content[len(title):].strip()
            lines = [l.strip() for l in body.split('\n') if l.strip()]
            preview = ' '.join(lines[:2])[:150] if lines else ""

            chapters.append({
                "title": title,
                "chars": len(body),
                "preview": preview
            })

    # 卷结构
    has_volume = any(re.match(r'^第[零一二三四五六七八九十百千万\d]+卷', c["title"]) for c in chapters)
    volumes = []
    if has_volume:
        cur_vol = {"name": "默认卷", "chapters": []}
        for ch in chapters:
            if re.match(r'^第[零一二三四五六七八九十百千万\d]+卷', ch["title"]):
                if cur_vol["chapters"]:
                    volumes.append(cur_vol)
                cur_vol = {"name": ch["title"], "chapters": []}
            else:
                cur_vol["chapters"].append(ch["title"])
        if cur_vol["chapters"]:
            volumes.append(cur_vol)

    # 结构类型
    n_ch = len(chapters)
    if has_volume:
        stype = "卷章结构"
    elif n_ch > 100:
        stype = "长篇连载"
    elif n_ch > 30:
        stype = "中篇分章"
    elif n_ch > 5:
        stype = "短篇分章"
    else:
        stype = "短篇/无分章"

    # 情节关键词
    kws = ["穿越", "变身", "转生", "重生", "觉醒", "突破", "修炼", "战斗",
           "系统", "任务", "魔法", "异世界", "校园", "修仙", "末世",
           "圣女", "公主", "女王", "魔王", "勇者", "精灵", "龙",
           "恋爱", "告白", "结局", "秘密", "阴谋", "复仇"]
    found_kws = [{"keyword": k, "count": text.count(k)} for k in kws if text.count(k) > 0]
    found_kws.sort(key=lambda x: x["count"], reverse=True)

    # 开头/结尾
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    opening = ' '.join(lines[:3])[:200] if lines else ""
    ending = ' '.join(lines[-3:])[-200:] if lines else ""

    return {
        "filename": os.path.basename(filepath),
        "total_chars": len(text),
        "structure_type": stype,
        "chapter_count": n_ch,
        "has_volume": has_volume,
        "keywords": found_kws[:15],
        "opening": opening,
        "ending": ending,
        "chapters": [c["title"] for c in chapters[:200]],
        "volumes": volumes if has_volume else [],
        "chapter_previews": chapters[:30]
    }


def extract_outlines(txt_dir, outdir, limit):
    """批量提取大纲"""
    os.makedirs(outdir, exist_ok=True)
    outlines = []

    txt_files = sorted([f for f in os.listdir(txt_dir) if f.endswith('.txt')])[:limit]

    for i, fname in enumerate(txt_files):
        fpath = os.path.join(txt_dir, fname)
        print(f"  [{i+1}/{len(txt_files)}] {fname[:50]}...", end=" ", flush=True)
        outline = extract_outline(fpath)
        outlines.append(outline)
        ch = outline.get("chapter_count", 0)
        st = outline.get("structure_type", "?")
        print(f"{ch}章 [{st}]")

    # 保存
    out_path = os.path.join(outdir, "novel_outlines.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({"total": len(outlines), "outlines": outlines}, f, ensure_ascii=False, indent=2)

    print(f"\n大纲提取完成: {out_path}")
    return outlines


def main():
    parser = argparse.ArgumentParser(description="爬取transchinese小说索引和大纲")
    parser.add_argument("--mode", default="full", choices=["index", "download", "outline", "full"],
                        help="运行模式")
    parser.add_argument("--output", default="./novel_data/novel_index.json", help="索引输出路径")
    parser.add_argument("--index", default="./novel_data/novel_index.json", help="索引JSON路径")
    parser.add_argument("--outdir", default="./novel_data", help="输出目录")
    parser.add_argument("--limit", type=int, default=50, help="下载/大纲数量限制")
    args = parser.parse_args()

    os.makedirs(args.outdir, exist_ok=True)

    if args.mode in ("index", "full"):
        index = crawl_index(args.output)
    else:
        with open(args.index, "r", encoding="utf-8") as f:
            index = json.load(f)

    if args.mode in ("download", "full"):
        download_novels(args.index, args.outdir, args.limit)

    if args.mode in ("outline", "full"):
        txt_dir = os.path.join(args.outdir, "txt")
        if os.path.isdir(txt_dir):
            extract_outlines(txt_dir, args.outdir, args.limit)
        else:
            print(f"[WARN] txt目录不存在: {txt_dir}", file=sys.stderr)


if __name__ == "__main__":
    main()
