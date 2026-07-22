#!/usr/bin/env python3
"""
Idempotent: turn each suburb in the sitewide footer "Service areas" band into a link to its
hub page, but only for suburbs that actually have a generated `landscaping-<slug>.html`.
Suburbs without a hub yet stay as plain text. Run after `.build/lp_render.py`.

Run from the site root:  python3 .build/linkify_footer_suburbs.py
"""

import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEP = " &middot; "
BAND_RE = re.compile(r'(<p class="footer-areas-list">)(.*?)(</p>)', re.DOTALL)


def slugify(name):
    return name.strip().lower().replace(" ", "-")


def linkify_band(inner):
    tokens = inner.split(SEP)
    out = []
    for tok in tokens:
        raw = tok.strip()
        if raw.startswith("<a "):            # already a link -> leave it
            out.append(tok)
            continue
        slug = slugify(raw)
        hub = os.path.join(ROOT, f"landscaping-{slug}.html")
        if os.path.exists(hub):
            out.append(f'<a href="landscaping-{slug}.html">{raw}</a>')
        else:
            out.append(tok)
    return SEP.join(out)


def main():
    changed = 0
    for fn in sorted(os.listdir(ROOT)):
        if not fn.endswith(".html"):
            continue
        path = os.path.join(ROOT, fn)
        with open(path, encoding="utf-8") as f:
            content = f.read()
        m = BAND_RE.search(content)
        if not m:
            continue
        new_inner = linkify_band(m.group(2))
        if new_inner == m.group(2):
            continue
        new_content = content[:m.start(2)] + new_inner + content[m.end(2):]
        with open(path, "w", encoding="utf-8") as f:
            f.write(new_content)
        changed += 1
        print(f"[linkify] {fn}")
    print(f"\n[linkify] updated {changed} file(s)")


if __name__ == "__main__":
    main()
