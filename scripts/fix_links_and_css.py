#!/usr/bin/env python3
import os
import re
from pathlib import Path

# Mapping of page paths to filenames
PAGE_MAP = [
    ("/tentang-kami/", "tentang-kami.html"),
    ("/armada/", "armada.html"),
    ("/klien/", "klien.html"),
    ("/kontak/", "kontak.html"),
    ("/proyek/", "proyek.html"),
    ("/portfolio/", "portfolio.html"),
    ("/product-2/", "product-2.html"),
    ("/sample-page/", "sample-page.html"),
    ("/", "index.html"),
]

HTML_FILES = [
    "index.html",
    "tentang-kami.html",
    "armada.html",
    "klien.html",
    "kontak.html",
    "proyek.html",
    "portfolio.html",
    "product-2.html",
    "sample-page.html",
]

SUBDIRS = [
    "tentang-kami",
    "armada",
    "klien",
    "kontak",
    "proyek",
    "portfolio",
    "product-2",
    "sample-page",
]

def clean_html(content, is_subdir=False):
    prefix = "../" if is_subdir else ""

    # 1. Clean previous artifacts
    content = re.sub(r'index\.htmlwp-content/', 'wp-content/', content)
    content = re.sub(r'index\.htmlwp-includes/', 'wp-includes/', content)
    content = re.sub(r'index\.htmlwp-admin/[^\s"\'<>]*', '#', content)
    content = re.sub(r'index\.htmlwp-json/[^\s"\'<>]*', '#', content)
    content = re.sub(r'index\.htmlcomments/[^\s"\'<>]*', '#', content)
    content = re.sub(r'index\.htmlfeed/', '#', content)
    content = re.sub(r'index\.htmlxmlrpc\.php', '#', content)

    # 2. Remove obsolete WordPress and tracker meta tags
    content = re.sub(r'<link[^>]+type=[\'"]application/rss\+xml[\'"][^>]*>', '', content)
    content = re.sub(r'<link[^>]+rel=[\'"]https://api\.w\.org/[\'"][^>]*>', '', content)
    content = re.sub(r'<link[^>]+rel=[\'"]EditURI[\'"][^>]*>', '', content)
    content = re.sub(r'<link[^>]+rel=[\'"]wlwmanifest[\'"][^>]*>', '', content)
    content = re.sub(r'<link[^>]+rel=[\'"]shortlink[\'"][^>]*>', '', content)
    content = re.sub(r'<link[^>]+type=[\'"]application/json\+oembed[\'"][^>]*>', '', content)
    content = re.sub(r'<link[^>]+type=[\'"]text/xml\+oembed[\'"][^>]*>', '', content)
    content = re.sub(r'<link[^>]+href=[\'"]//fonts\.googleapis\.com[\'"][^>]*>', '', content)
    content = re.sub(r'<link[^>]+googletagmanager[^>]*>', '', content)

    # Remove Google Site Kit inline scripts & trackers
    content = re.sub(r'<script[^>]*google-site-kit[^>]*>.*?</script>', '', content, flags=re.DOTALL)
    content = re.sub(r'<script[^>]*googletagmanager[^>]*>.*?</script>', '', content, flags=re.DOTALL)
    content = re.sub(r'<script[^>]*>\s*\(function\(w,d,s,l,i\).*?googletagmanager.*?</script>', '', content, flags=re.DOTALL)
    content = re.sub(r'<script[^>]*id=[\'"]google_gtagjs-js-after[\'"][^>]*>.*?</script>', '', content, flags=re.DOTALL)

    # 3. Replace asset domains with relative path
    content = content.replace("https://popeye-logistik.com/wp-content/", prefix + "wp-content/")
    content = content.replace("http://popeye-logistik.com/wp-content/", prefix + "wp-content/")
    content = content.replace("https://popeye-logistik.com/wp-includes/", prefix + "wp-includes/")
    content = content.replace("http://popeye-logistik.com/wp-includes/", prefix + "wp-includes/")

    # Root-relative asset paths: /wp-content/ -> wp-content/
    content = re.sub(r'([\'"])/wp-content/', r'\1' + prefix + r'wp-content/', content)
    content = re.sub(r'([\'"])/wp-includes/', r'\1' + prefix + r'wp-includes/', content)
    content = re.sub(r'url\([\'"]?/wp-content/', r'url(' + prefix + r'wp-content/', content)
    content = re.sub(r'url\([\'"]?/wp-includes/', r'url(' + prefix + r'wp-includes/', content)

    # 4. Replace absolute page URLs
    for p_path, p_target in PAGE_MAP:
        target = prefix + p_target
        content = content.replace(f'https://popeye-logistik.com{p_path}', target)
        content = content.replace(f'http://popeye-logistik.com{p_path}', target)
        content = re.sub(r'href=([\'"])' + re.escape(p_path) + r'([\'"])', r'href=\1' + target + r'\2', content)

    # 5. Fix JSON configs like elementorFrontendConfig and HappyLocalize
    escaped_prefix = prefix.replace("/", r"\/")
    content = re.sub(
        r'https?:\\\/\\\/popeye-logistik\.com\\\/wp-content\\\/plugins\\\/elementor\\\/assets\\\/',
        escaped_prefix + r'wp-content\/plugins\/elementor\/assets\/',
        content
    )
    content = re.sub(
        r'https?:\\\/\\\/popeye-logistik\.com\\\/wp-content\\\/uploads',
        escaped_prefix + r'wp-content\/uploads',
        content
    )
    content = re.sub(
        r'https?:\\\/\\\/popeye-logistik\.com\\\/wp-admin\\\/admin-ajax\.php',
        '',
        content
    )
    content = re.sub(
        r'"ajax_url":\s*"[^"]*admin-ajax\.php"',
        '"ajax_url": ""',
        content
    )

    # 6. Ensure bare wp-content without prefix in subdirs gets prefix
    if is_subdir:
        content = re.sub(r'src=([\'"])wp-content/', r'src=\1../wp-content/', content)
        content = re.sub(r'href=([\'"])wp-content/', r'href=\1../wp-content/', content)
        content = re.sub(r'src=([\'"])wp-includes/', r'src=\1../wp-includes/', content)
        content = re.sub(r'href=([\'"])wp-includes/', r'href=\1../wp-includes/', content)
        content = re.sub(r'url\([\'"]?wp-content/', r'url(../wp-content/', content)
        content = re.sub(r'url\([\'"]?wp-includes/', r'url(../wp-includes/', content)
        for _, p_target in PAGE_MAP:
            content = re.sub(r'href=([\'"])' + re.escape(p_target) + r'([\'"])', r'href=\1../' + p_target + r'\2', content)

    return content

def fix_css_urls():
    css_files = list(Path("wp-content").glob("**/*.css")) + list(Path("wp-includes").glob("**/*.css"))
    print(f"Fixing URLs in {len(css_files)} CSS files...")
    
    for css_path in css_files:
        try:
            with open(css_path, "r", encoding="utf-8") as f:
                content = f.read()
        except UnicodeDecodeError:
            with open(css_path, "r", encoding="latin-1") as f:
                content = f.read()

        css_dir = css_path.parent

        def replace_url(match):
            raw_url = match.group(1).strip("'\"")
            if not raw_url or raw_url.startswith("data:"):
                return match.group(0)

            clean_url = raw_url.split("?")[0].split("#")[0]
            query_part = raw_url[len(clean_url):]

            target_rel = None
            if "popeye-logistik.com" in clean_url:
                if "/wp-content/" in clean_url:
                    idx = clean_url.find("wp-content/")
                    target_rel = clean_url[idx:]
                elif "/wp-includes/" in clean_url:
                    idx = clean_url.find("wp-includes/")
                    target_rel = clean_url[idx:]
            elif clean_url.startswith("/wp-content/") or clean_url.startswith("wp-content/"):
                target_rel = clean_url.lstrip("/")
            elif clean_url.startswith("/wp-includes/") or clean_url.startswith("wp-includes/"):
                target_rel = clean_url.lstrip("/")

            if target_rel:
                try:
                    rel = os.path.relpath(target_rel, css_dir)
                    return f"url({rel}{query_part})"
                except Exception:
                    pass

            return match.group(0)

        new_content = re.sub(r'url\s*\(\s*([^\)]+)\s*\)', replace_url, content)

        if new_content != content:
            with open(css_path, "w", encoding="utf-8") as f:
                f.write(new_content)

def main():
    print("Fixing root HTML files...")
    for hf in HTML_FILES:
        p = Path(hf)
        if not p.exists():
            continue
        with open(p, "r", encoding="utf-8") as f:
            content = f.read()
        cleaned = clean_html(content, is_subdir=False)
        with open(p, "w", encoding="utf-8") as f:
            f.write(cleaned)
        print(f"  Fixed {hf}")

    print("Fixing subdirectory HTML files...")
    for sdir in SUBDIRS:
        p = Path(sdir) / "index.html"
        root_base = Path(f"{sdir}.html")
        if root_base.exists():
            with open(root_base, "r", encoding="utf-8") as f:
                content = f.read()
            cleaned = clean_html(content, is_subdir=True)
            with open(p, "w", encoding="utf-8") as f:
                f.write(cleaned)
            print(f"  Fixed {p}")

    fix_css_urls()
    print("Done!")

if __name__ == "__main__":
    main()
