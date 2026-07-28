#!/usr/bin/env python3
"""seo_100_patch.py - idempotent on-page SEO patcher for the ANKS site.

Brings the 24 pages listed in sitemap.xml (12 core + 12 suburb landing pages) to
a clean pass on the machine-checkable checks in Apps/sutera-seo/checklist.py.
Safe to re-run; every insertion is guarded by a presence check.

Applies the MECHANICAL fixes only. Title + meta-description copy is rewritten by
hand in a separate pass (those need editorial judgement, not truncation):

  - twitter card + image (all pages; normalises any partial block)
  - canonical + og:url            (core pages missing them)
  - JSON-LD @graph: GeneralContractor + BreadcrumbList (core pages with no JSON-LD)
  - BreadcrumbList-only block      (pages that have JSON-LD but no crumb: privacy)
  - visible breadcrumb nav below the hero (interior pages, not the homepage)
  - skip-to-content link + <main id="main">   (all pages)
  - explicit width/height on <img> read from the real asset file (no distortion)

Deliberately NOT touched:
  - architectural-landscaping.html - paid-ads LP, not in sitemap, left as-is
  - the homepage gets no breadcrumb (design: fixed header floats over full-bleed
    hero; a homepage crumb is pointless UX). That single check stays a WARN.
"""

import json
import os
import re
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://anks.com.au"

# filename -> clean slug (matches sitemap.xml; "" == homepage)
CORE = {
    "index.html": "",
    "about.html": "about",
    "services.html": "services",
    "custom-homes.html": "custom-homes",
    "commercial.html": "commercial",
    "builders-developers.html": "builders-developers",
    "process.html": "process",
    "projects.html": "projects",
    "testimonials.html": "testimonials",
    "faq.html": "faq",
    "contact.html": "contact",
    "privacy.html": "privacy",
}
SUBURBS = {"balwyn": "Balwyn", "camberwell": "Camberwell", "canterbury": "Canterbury"}
SERVICES = {
    "landscaping": "Landscaping",
    "custom-homes": "Custom Homes",
    "commercial": "Commercial",
    "builders-developers": "Builders & Developers",
}
SUBURB_FILES = {f"{svc}-{sub}.html": (SERVICES[svc], name)
                for svc in SERVICES for sub, name in SUBURBS.items()}

# Visible + schema breadcrumb trail per page: [(name, slug_or_None)].
# slug "" -> homepage, None -> current page (no link, aria-current).
CRUMBS = {
    "about.html": [("Home", ""), ("About", None)],
    "services.html": [("Home", ""), ("Services", None)],
    "custom-homes.html": [("Home", ""), ("Services", "services"), ("Custom Homes", None)],
    "commercial.html": [("Home", ""), ("Services", "services"), ("Commercial", None)],
    "builders-developers.html": [("Home", ""), ("Services", "services"), ("Builders & Developers", None)],
    "process.html": [("Home", ""), ("Process", None)],
    "projects.html": [("Home", ""), ("Projects", None)],
    "testimonials.html": [("Home", ""), ("Testimonials", None)],
    "faq.html": [("Home", ""), ("FAQ", None)],
    "contact.html": [("Home", ""), ("Contact", None)],
    "privacy.html": [("Home", ""), ("Privacy", None)],
}
# suburb pages: match the existing JSON-LD trail (Home / Suburb)
for fn, (_svc, sub_name) in SUBURB_FILES.items():
    CRUMBS[fn] = [("Home", ""), (sub_name, None)]

# The business entity, mirrored from index.html so rich-results stay consistent.
BUSINESS_NODE = {
    "@type": "GeneralContractor",
    "name": "ANKS Construction and Landscaping",
    "url": SITE + "/",
    "image": SITE + "/assets/brand/anks-logo-transparent.png",
    "telephone": "+61401500778",
    "email": "info@anks.com.au",
    "address": {
        "@type": "PostalAddress",
        "streetAddress": "South Mountain Road",
        "addressLocality": "Upper Plenty",
        "addressRegion": "VIC",
        "postalCode": "3756",
        "addressCountry": "AU",
    },
    "areaServed": ["Camberwell", "Canterbury", "Balwyn", "Balwyn North", "Kew",
                   "Hawthorn", "Glen Iris", "Brighton", "Brighton East", "Toorak",
                   "Malvern", "South Yarra", "Melbourne", "Regional Victoria"],
    "aggregateRating": {"@type": "AggregateRating", "ratingValue": "5.0", "reviewCount": "28"},
}

_DIM_CACHE = {}


def img_dims(src):
    """Return (w, h) ints for a local asset src, or None. Cached."""
    src = src.split("?")[0].split("#")[0]
    if src.startswith(("http://", "https://", "data:", "//")):
        return None
    if src in _DIM_CACHE:
        return _DIM_CACHE[src]
    path = os.path.normpath(os.path.join(ROOT, src.lstrip("/")))
    if not path.startswith(ROOT) or not os.path.isfile(path):
        _DIM_CACHE[src] = None
        return None
    try:
        out = subprocess.run(["sips", "-g", "pixelWidth", "-g", "pixelHeight", path],
                             capture_output=True, text=True, timeout=20).stdout
        w = re.search(r"pixelWidth:\s*(\d+)", out)
        h = re.search(r"pixelHeight:\s*(\d+)", out)
        dims = (int(w.group(1)), int(h.group(1))) if w and h else None
    except Exception:
        dims = None
    _DIM_CACHE[src] = dims
    return dims


def abs_url(u):
    if not u:
        return u
    if u.startswith(("http://", "https://")):
        return u
    return SITE + "/" + u.lstrip("/")


def canonical_for(slug):
    return SITE + "/" if slug == "" else f"{SITE}/{slug}"


def crumb_html(trail):
    lis = []
    for name, slug in trail:
        if slug is None:
            lis.append(f'      <li aria-current="page">{name}</li>')
        else:
            href = "/" if slug == "" else "/" + slug
            lis.append(f'      <li><a href="{href}">{name}</a></li>')
    return ('<nav class="breadcrumb" aria-label="Breadcrumb">\n'
            '  <div class="container">\n'
            '    <ol>\n' + "\n".join(lis) + "\n    </ol>\n"
            "  </div>\n</nav>\n")


def crumb_node(trail):
    items = []
    for i, (name, slug) in enumerate(trail, 1):
        it = {"@type": "ListItem", "position": i, "name": name}
        if slug is not None:
            it["item"] = canonical_for(slug)
        items.append(it)
    return {"@type": "BreadcrumbList", "itemListElement": items}


def jsonld_block(payload):
    body = json.dumps(payload, indent=2, ensure_ascii=False)
    return f'<script type="application/ld+json">\n{body}\n</script>\n'


def meta_content(html, pattern):
    m = re.search(pattern, html)
    return m.group(1).strip() if m else ""


def patch(fn, slug):
    path = os.path.join(ROOT, fn)
    html = open(path, encoding="utf-8").read()
    orig = html
    did = []

    title = meta_content(html, r"<title>(.*?)</title>")
    desc = meta_content(html, r'name="description"\s+content="([^"]*)"')
    ogtitle = meta_content(html, r'property="og:title"\s+content="([^"]*)"') or title
    ogdesc = meta_content(html, r'property="og:description"\s+content="([^"]*)"') or desc
    ogimg = abs_url(meta_content(html, r'property="og:image"\s+content="([^"]*)"'))
    canonical = canonical_for(slug)

    # --- canonical (after </title>) ---
    if 'rel="canonical"' not in html:
        html = html.replace("</title>",
                            f'</title>\n<link rel="canonical" href="{canonical}" />', 1)
        did.append("canonical")

    # --- og:url (after og:image line) ---
    if "og:url" not in html:
        html = re.sub(r'(<meta property="og:image"[^>]*/>)',
                      rf'\1\n<meta property="og:url" content="{canonical}" />', html, count=1)
        did.append("og:url")

    # --- twitter card (normalise: drop any existing twitter:* then insert full block) ---
    if 'name="twitter:image"' not in html:
        html = re.sub(r'\s*<meta name="twitter:[^"]*"[^>]*/>', "", html)
        tw = (f'<meta name="twitter:card" content="summary_large_image" />\n'
              f'<meta name="twitter:title" content="{ogtitle}" />\n'
              f'<meta name="twitter:description" content="{ogdesc}" />\n'
              f'<meta name="twitter:image" content="{ogimg}" />')
        anchor = re.search(r'<meta property="og:url"[^>]*/>', html)
        if anchor:
            html = html[:anchor.end()] + "\n" + tw + html[anchor.end():]
        else:
            html = html.replace("</title>", f"</title>\n{tw}", 1)
        did.append("twitter")

    # --- JSON-LD (business + breadcrumb) / breadcrumb-only top-up ---
    has_ld = "application/ld+json" in html
    has_crumb_schema = "BreadcrumbList" in html
    trail = CRUMBS.get(fn)
    if not has_ld:
        graph = {"@context": "https://schema.org", "@graph": [BUSINESS_NODE]}
        if trail:
            graph["@graph"].append(crumb_node(trail))
        block = jsonld_block(graph)
        html = html.replace('<link rel="stylesheet" href="styles.css" />',
                            block + '<link rel="stylesheet" href="styles.css" />', 1)
        did.append("jsonld")
    elif trail and not has_crumb_schema:
        block = jsonld_block({"@context": "https://schema.org", **crumb_node(trail)})
        html = html.replace('<link rel="stylesheet" href="styles.css" />',
                            block + '<link rel="stylesheet" href="styles.css" />', 1)
        did.append("breadcrumb-schema")

    # --- skip-to-content link + <main id="main"> ---
    if "skip-link" not in html:
        html = html.replace("<body>",
                            '<body>\n<a class="skip-link" href="#main">Skip to content</a>', 1)
        did.append("skip-link")
    if not re.search(r"<main\b[^>]*\bid=", html):
        html = re.sub(r"<main\b([^>]*)>", r'<main id="main"\1>', html, count=1)
        did.append("main-id")

    # --- visible breadcrumb nav (interior pages only), below the hero ---
    if trail and 'class="breadcrumb"' not in html:
        nav = crumb_html(trail)
        mo = re.search(r'<main\b[^>]*>', html)
        if mo:
            # first </section> after <main> == end of hero; place crumb right after it
            sec = html.find("</section>", mo.end())
            if 0 <= sec <= mo.end() + 6000:
                pt = sec + len("</section>")
                html = html[:pt] + "\n" + nav + html[pt:]
            else:
                html = html[:mo.end()] + "\n" + nav + html[mo.end():]
            did.append("breadcrumb-nav")

    # --- explicit width/height on <img> ---
    def add_dims(m):
        tag = m.group(0)
        if re.search(r"\bwidth=", tag) and re.search(r"\bheight=", tag):
            return tag
        s = re.search(r'\bsrc="([^"]+)"', tag)
        if not s:
            return tag
        d = img_dims(s.group(1))
        if not d:
            return tag
        return re.sub(r"<img\b", f'<img width="{d[0]}" height="{d[1]}"', tag, count=1)

    new_html = re.sub(r"<img\b[^>]*?/?>", add_dims, html)
    if new_html != html:
        did.append("img-dims")
        html = new_html

    if html != orig:
        open(path, "w", encoding="utf-8").write(html)
    return did


def main():
    files = {**CORE, **{fn: slug for fn, slug in
                        [(f, f[:-5]) for f in SUBURB_FILES]}}
    print(f"Patching {len(files)} pages under {ROOT}\n")
    for fn in sorted(files):
        slug = files[fn]
        changed = patch(fn, slug)
        print(f"  {fn:38s} {', '.join(changed) if changed else 'no change (already compliant)'}")
    print("\nDone. Re-run any time; it is idempotent.")


if __name__ == "__main__":
    main()
