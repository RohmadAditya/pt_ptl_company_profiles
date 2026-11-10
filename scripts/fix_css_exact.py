#!/usr/bin/env python3
import os
import re
from pathlib import Path

def resolve_target(raw_url, css_file):
    # Strip quotes and query/fragment
    clean_url = raw_url.strip("'\"")
    clean_no_hash = clean_url.split("?")[0].split("#")[0]
    
    # Already exists relative to css_file?
    p = (css_file.parent / clean_no_hash).resolve()
    if p.exists() and p.is_file():
        return None  # Already valid, no fix needed!
        
    # Check if it was malformed like ../../uploads/...
    # which actually means wp-content/uploads/...
    candidates = []
    
    if "uploads/" in clean_no_hash:
        idx = clean_no_hash.find("uploads/")
        candidates.append("wp-content/" + clean_no_hash[idx:])
        
    if "wp-content/" in clean_no_hash:
        idx = clean_no_hash.find("wp-content/")
        candidates.append(clean_no_hash[idx:])
        
    if "wp-includes/" in clean_no_hash:
        idx = clean_no_hash.find("wp-includes/")
        candidates.append(clean_no_hash[idx:])
        
    # Also check basename in whole workspace
    basename = Path(clean_no_hash).name
    if basename:
        for found in Path("wp-content").glob(f"**/{basename}"):
            candidates.append(str(found))
            
    for cand in candidates:
        cand_p = Path(cand).resolve()
        if cand_p.exists() and cand_p.is_file():
            # Found the target file!
            return str(cand_p.relative_to(Path.cwd()))
            
    return None

def main():
    css_files = list(Path("wp-content").glob("**/*.css")) + list(Path("wp-includes").glob("**/*.css"))
    print(f"Checking {len(css_files)} CSS files...")
    
    fixed_count = 0
    total_urls = 0
    
    for css_p in css_files:
        try:
            with open(css_p, "r", encoding="utf-8") as f:
                content = f.read()
        except UnicodeDecodeError:
            with open(css_p, "r", encoding="latin-1") as f:
                content = f.read()
                
        css_dir = css_p.parent
        modified = False
        
        def repl(match):
            nonlocal fixed_count, total_urls, modified
            total_urls += 1
            raw_url = match.group(1).strip("'\" ")
            if not raw_url or raw_url.startswith("data:"):
                return match.group(0)
                
            clean_no_hash = raw_url.split("?")[0].split("#")[0]
            query_part = raw_url[len(clean_no_hash):]
            
            target_rel = resolve_target(raw_url, css_p)
            if target_rel:
                rel = os.path.relpath(target_rel, css_dir)
                fixed_count += 1
                modified = True
                return f"url({rel}{query_part})"
                
            return match.group(0)
            
        new_content = re.sub(r'url\s*\(\s*([^\)]+)\s*\)', repl, content)
        if modified:
            with open(css_p, "w", encoding="utf-8") as f:
                f.write(new_content)
                
    print(f"Total url() processed: {total_urls}")
    print(f"Fixed: {fixed_count}")

if __name__ == "__main__":
    main()
