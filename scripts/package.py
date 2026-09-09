#!/usr/bin/env python3
"""Assemble the publishable site into _site/.

    python3 scripts/package.py

Copies only what belongs on a web server — the generated HTML, the assets and
the crawler files — and leaves the sources, the build scripts and the project
notes behind. The GitHub Pages workflow uploads _site/ as its artifact, and
running this locally shows exactly what would be deployed.
"""

import pathlib
import shutil
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "_site"

# Everything a visitor may fetch. Anything not listed here is never published.
PUBLISH = [
    "index.html",
    "404.html",
    "robots.txt",
    "sitemap.xml",
    ".nojekyll",
    "CNAME",            # only exists once a custom domain is attached
    # Apache/LiteSpeed and Netlify/Cloudflare redirect tables. CLAUDE.md tells
    # the operator to upload _site/ to Hostinger, so leaving these out silently
    # dropped all 33 legacy 301s and the ErrorDocument line with them. Both are
    # inert on GitHub Pages, which reads neither.
    ".htaccess",
    "_redirects",
    "assets",
    "about-us",
    "business-loans",
    "contact-us",
    "cookies-policy",
    "privacy-policy",
    "terms-and-conditions",
]


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)

    copied, skipped = [], []
    for name in PUBLISH:
        src = ROOT / name
        if not src.exists():
            skipped.append(name)
            continue
        dest = OUT / name
        if src.is_dir():
            shutil.copytree(src, dest)
        else:
            shutil.copy2(src, dest)
        copied.append(name)

    # A missing index.html means the build never ran — fail loudly rather than
    # publishing an empty site.
    if not (OUT / "index.html").is_file():
        sys.exit("no index.html to publish — run scripts/build.py first")

    total = sum(f.stat().st_size for f in OUT.rglob("*") if f.is_file())
    files = sum(1 for f in OUT.rglob("*") if f.is_file())
    print(f"packaged {files} files ({total/1024:.0f} KB) into {OUT.relative_to(ROOT)}/")
    print("  included:", ", ".join(copied))
    if skipped:
        print("  not present:", ", ".join(skipped))


if __name__ == "__main__":
    main()
