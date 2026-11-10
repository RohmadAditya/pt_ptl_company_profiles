#!/usr/bin/env python3
import os
import re
import sys
import json
import urllib.request
import urllib.parse
from pathlib import Path

BASE_URL = "https://popeye-logistik.com"
BASE_URL_HTTP = "http://popeye-logistik.com"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
}

PAGES = [
    {"slug": "index", "path": "/", "file": "index.html", "subfolder": ""},
    {"slug": "tentang-kami", "path": "/tentang-kami/", "file": "tentang-kami.html", "subfolder": "tentang-kami"},
    {"slug": "armada", "path": "/armada/", "file": "armada.html", "subfolder": "armada"},
    {"slug": "klien", "path": "/klien/", "file": "klien.html", "subfolder": "klien"},
    {"slug": "kontak", "path": "/kontak/", "file": "kontak.html", "subfolder": "kontak"},
    {"slug": "proyek", "path": "/proyek/", "file": "proyek.html", "subfolder": "proyek"},
    {"slug": "portfolio", "path": "/portfolio/", "file": "portfolio.html", "subfolder": "portfolio"},
    {"slug": "product-2", "path": "/product-2/", "file": "product-2.html", "subfolder": "product-2"},
    {"slug": "sample-page", "path": "/sample-page/", "file": "sample-page.html", "subfolder": "sample-page"},
]

downloaded_assets = set()
failed_assets = set()

def fetch_url(url, is_binary=False):
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            content = resp.read()
            if is_binary:
                return content
            try:
                return content.decode("utf-8")
            except UnicodeDecodeError:
                return content.decode("latin-1", errors="ignore")
    except Exception as e:
        print(f"  [!] Failed fetching {url}: {e}")
        return None

def save_file(rel_path, content, is_binary=False):
    # rel_path is relative to workspace root, e.g. "wp-content/themes/astra/..."
    # Clean query strings or invalid characters
    clean_path = rel_path.split("?")[0].split("#")[0]
    # Remove leading slash
    if clean_path.startswith("/"):
        clean_path = clean_path[1:]
    
    # Handle percent-encoded characters in filename
    clean_path = urllib.parse.unquote(clean_path)
    
    file_path = Path(clean_path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    if is_binary:
        with open(file_path, "wb") as f:
            f.write(content)
    else:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
    return clean_path

def download_asset(asset_url, referer=None):
    # Normalize url
    if not asset_url:
        return None
    asset_url = asset_url.strip()
    if asset_url.startswith("//"):
        asset_url = "https:" + asset_url
    elif asset_url.startswith("/"):
        asset_url = BASE_URL + asset_url
    elif not asset_url.startswith("http://") and not asset_url.startswith("https://"):
        if referer:
            asset_url = urllib.parse.urljoin(referer, asset_url)
        else:
            asset_url = BASE_URL + "/" + asset_url

    parsed = urllib.parse.urlparse(asset_url)
    
    # Only download assets from popeye-logistik.com or relative
    if parsed.netloc and "popeye-logistik.com" not in parsed.netloc:
        # Check if external font or script we want to save
        return asset_url

    clean_asset_path = parsed.path
    if not clean_asset_path or clean_asset_path == "/":
        return None

    # Check if already processed
    if clean_asset_path in downloaded_assets:
        return clean_asset_path

    # Rel path in workspace
    rel_path = clean_asset_path.lstrip("/")
    if not rel_path:
        return None

    print(f"Downloading asset: {clean_asset_path}")
    data = fetch_url(asset_url, is_binary=True)
    if data is not None:
        save_file(rel_path, data, is_binary=True)
        downloaded_assets.add(clean_asset_path)
        
        # If it's a CSS file, parse for url(...) and @import
        if clean_asset_path.endswith(".css"):
            try:
                css_text = data.decode("utf-8")
            except UnicodeDecodeError:
                css_text = data.decode("latin-1", errors="ignore")
            
            # Find url(...)
            url_matches = re.findall(r'url\s*\(\s*[\'"]?([^\'")]+)[\'"]?\s*\)', css_text)
            for sub_url in url_matches:
                sub_url = sub_url.strip()
                if sub_url.startswith("data:"):
                    continue
                # resolve relative to css file url
                full_sub_url = urllib.parse.urljoin(asset_url, sub_url)
                download_asset(full_sub_url, referer=asset_url)
                
            # Find @import
            import_matches = re.findall(r'@import\s+[\'"]([^\'"]+)[\'"]', css_text)
            for imp in import_matches:
                full_imp = urllib.parse.urljoin(asset_url, imp)
                download_asset(full_imp, referer=asset_url)
                
        return clean_asset_path
    else:
        failed_assets.add(asset_url)
        return None

def main():
    print("=== Step 1: Querying WordPress REST API for all Media Assets ===")
    media_url = f"{BASE_URL}/wp-json/wp/v2/media?per_page=100"
    media_json_str = fetch_url(media_url)
    if media_json_str:
        try:
            media_items = json.loads(media_json_str)
            print(f"Found {len(media_items)} media items in REST API")
            for item in media_items:
                source_url = item.get("source_url")
                if source_url:
                    download_asset(source_url)
                # Download sizes
                media_details = item.get("media_details", {})
                sizes = media_details.get("sizes", {})
                for size_name, size_info in sizes.items():
                    s_url = size_info.get("source_url")
                    if s_url:
                        download_asset(s_url)
        except Exception as e:
            print("Error parsing media json:", e)

    print("\n=== Step 2: Fetching HTML for All Pages ===")
    raw_pages = {}
    for p in PAGES:
        url = BASE_URL + p["path"]
        print(f"Fetching page: {p['slug']} ({url})")
        html = fetch_url(url)
        if html:
            raw_pages[p["slug"]] = html
        else:
            print(f"FAILED to fetch page {p['slug']}")

    print("\n=== Step 3: Discovering and Downloading Assets from HTML ===")
    for slug, html in raw_pages.items():
        # 1. CSS files: <link rel="stylesheet" ... href="...">
        css_links = re.findall(r'<link[^>]+rel=[\'"](?:stylesheet|preload)[\'"][^>]+href=[\'"]([^\'"]+)[\'"]', html, re.I)
        css_links += re.findall(r'<link[^>]+href=[\'"]([^\'"]+)[\'"][^>]+rel=[\'"](?:stylesheet|preload)[\'"]', html, re.I)
        for link in css_links:
            download_asset(link)

        # 2. Favicons / icons
        icon_links = re.findall(r'<link[^>]+rel=[\'"](?:icon|shortcut icon|apple-touch-icon)[\'"][^>]+href=[\'"]([^\'"]+)[\'"]', html, re.I)
        for link in icon_links:
            download_asset(link)

        # 3. JS scripts: <script ... src="...">
        js_scripts = re.findall(r'<script[^>]+src=[\'"]([^\'"]+)[\'"]', html, re.I)
        for src in js_scripts:
            download_asset(src)

        # 4. Images: <img ... src="..."> and <img ... srcset="...">
        img_srcs = re.findall(r'<img[^>]+src=[\'"]([^\'"]+)[\'"]', html, re.I)
        for src in img_srcs:
            if not src.startswith("data:"):
                download_asset(src)

        srcsets = re.findall(r'srcset=[\'"]([^\'"]+)[\'"]', html, re.I)
        for sset in srcsets:
            # Format: url 100w, url2 200w
            parts = sset.split(",")
            for part in parts:
                clean_part = part.strip().split(" ")[0]
                if clean_part and not clean_part.startswith("data:"):
                    download_asset(clean_part)

        # 5. Background images in style attributes or inline styles
        bg_urls = re.findall(r'url\s*\(\s*[\'"]?([^\'")]+)[\'"]?\s*\)', html)
        for b_url in bg_urls:
            if not b_url.startswith("data:"):
                download_asset(b_url)

        # 6. Any other wp-content or wp-includes URLs found in HTML
        wp_urls = re.findall(r'https?://popeye-logistik\.com/(wp-content/[^\s"\'<>]+|wp-includes/[^\s"\'<>]+)', html)
        for w_url in wp_urls:
            download_asset(BASE_URL + "/" + w_url)

    print(f"\nTotal assets downloaded: {len(downloaded_assets)}")
    if failed_assets:
        print(f"Failed assets ({len(failed_assets)}): {failed_assets}")

    print("\n=== Step 4: Rewriting and Saving HTML Pages ===")
    
    # URL Replacement map
    # Maps original page paths to local filenames
    page_link_replacements = [
        ("https://popeye-logistik.com/tentang-kami/", "tentang-kami.html"),
        ("http://popeye-logistik.com/tentang-kami/", "tentang-kami.html"),
        ("https://popeye-logistik.com/armada/", "armada.html"),
        ("http://popeye-logistik.com/armada/", "armada.html"),
        ("https://popeye-logistik.com/klien/", "klien.html"),
        ("http://popeye-logistik.com/klien/", "klien.html"),
        ("https://popeye-logistik.com/kontak/", "kontak.html"),
        ("http://popeye-logistik.com/kontak/", "kontak.html"),
        ("https://popeye-logistik.com/proyek/", "proyek.html"),
        ("http://popeye-logistik.com/proyek/", "proyek.html"),
        ("https://popeye-logistik.com/portfolio/", "portfolio.html"),
        ("http://popeye-logistik.com/portfolio/", "portfolio.html"),
        ("https://popeye-logistik.com/product-2/", "product-2.html"),
        ("http://popeye-logistik.com/product-2/", "product-2.html"),
        ("https://popeye-logistik.com/sample-page/", "sample-page.html"),
        ("http://popeye-logistik.com/sample-page/", "sample-page.html"),
        ("https://popeye-logistik.com/", "index.html"),
        ("http://popeye-logistik.com/", "index.html"),
        ("https://popeye-logistik.com", "index.html"),
        ("http://popeye-logistik.com", "index.html"),
    ]

    for p in PAGES:
        slug = p["slug"]
        if slug not in raw_pages:
            continue
        html = raw_pages[slug]

        # 1. Rewrite domain page links
        for orig, target in page_link_replacements:
            # Exact quoted links
            html = html.replace(f'"{orig}"', f'"{target}"')
            html = html.replace(f"'{orig}'", f"'{target}'")
            # Unquoted or inside json
            html = html.replace(f'{orig}', f'{target}')

        # 2. Rewrite root-relative page links
        for p_sub in PAGES:
            r_path = p_sub["path"]
            r_target = p_sub["file"]
            html = re.sub(r'href=([\'"])' + re.escape(r_path) + r'([\'"])', r'href=\1' + r_target + r'\2', html)

        # 3. Rewrite asset URLs: https://popeye-logistik.com/wp-content/ -> wp-content/
        # Also handle http://
        html = html.replace("https://popeye-logistik.com/wp-content/", "wp-content/")
        html = html.replace("http://popeye-logistik.com/wp-content/", "wp-content/")
        html = html.replace("https://popeye-logistik.com/wp-includes/", "wp-includes/")
        html = html.replace("http://popeye-logistik.com/wp-includes/", "wp-includes/")

        # In case there are "/wp-content/" or "/wp-includes/"
        html = re.sub(r'([\'"])/wp-content/', r'\1wp-content/', html)
        html = re.sub(r'([\'"])/wp-includes/', r'\1wp-includes/', html)
        html = re.sub(r'url\([\'"]?/wp-content/', r'url(wp-content/', html)
        html = re.sub(r'url\([\'"]?/wp-includes/', r'url(wp-includes/', html)

        # 4. Remove external analytics or tracker tags that slow down local loading or cause errors
        html = re.sub(r'<script[^>]*googletagmanager[^>]*>.*?</script>', '', html, flags=re.DOTALL)
        html = re.sub(r'<link[^>]*googletagmanager[^>]*>', '', html)

        # Save root HTML file (e.g. index.html, tentang-kami.html)
        root_file = p["file"]
        with open(root_file, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"Saved: {root_file}")

        # Also save subdirectory version (e.g. tentang-kami/index.html)
        if p["subfolder"]:
            sub_dir = Path(p["subfolder"])
            sub_dir.mkdir(parents=True, exist_ok=True)
            sub_html = html
            # Rewrite relative paths to prepend ../
            sub_html = sub_html.replace('wp-content/', '../wp-content/')
            sub_html = sub_html.replace('wp-includes/', '../wp-includes/')
            for _, t in page_link_replacements:
                sub_html = sub_html.replace(f'"{t}"', f'"../{t}"')
                sub_html = sub_html.replace(f"'{t}'", f"'../{t}'")
            with open(sub_dir / "index.html", "w", encoding="utf-8") as f:
                f.write(sub_html)
            print(f"Saved: {sub_dir}/index.html")

    print("\n=== Step 5: Fixing Asset URLs in Local CSS Files ===")
    css_files = list(Path(".").glob("**/*.css"))
    print(f"Scanning {len(css_files)} CSS files for external popeye-logistik.com URLs...")
    for css_p in css_files:
        try:
            with open(css_p, "r", encoding="utf-8") as f:
                content = f.read()
        except UnicodeDecodeError:
            with open(css_p, "r", encoding="latin-1") as f:
                content = f.read()
        
        modified = False
        if "popeye-logistik.com" in content:
            content = content.replace("https://popeye-logistik.com/wp-content/", "../../")
            content = content.replace("http://popeye-logistik.com/wp-content/", "../../")
            content = content.replace("https://popeye-logistik.com/wp-includes/", "../../../wp-includes/")
            content = content.replace("http://popeye-logistik.com/wp-includes/", "../../../wp-includes/")
            modified = True
            
        if modified:
            with open(css_p, "w", encoding="utf-8") as f:
                f.write(content)

    print("\n=== Cloning complete! ===")

if __name__ == "__main__":
    main()
