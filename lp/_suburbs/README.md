# ANKS suburb landing-page sources

Each `*.json` here is one suburb. `python3 .build/lp_render.py` (run from the site root)
turns each into four pages and refreshes the `<!-- LP -->` block in `sitemap.xml`:

- `landscaping-<slug>.html`          - suburb hub (overview + links to the 3 service pages)
- `custom-homes-<slug>.html`         - Architectural / custom homes x suburb
- `commercial-<slug>.html`           - Commercial landscaping x suburb
- `builders-developers-<slug>.html`  - Builders & developers x suburb

Do not hand-edit the generated HTML. Edit the JSON (or the shared chrome/copy in
`.build/lp_render.py`) and re-run.

## Content rule (hard)

Service-area framing only. Never claim a completed project in a suburb where ANKS has not
worked. The "Real projects" strip shows genuine ANKS work labelled with its TRUE location
(North Balwyn, Sunbury, Mernda Hills, St James Vermont) as proof of capability. No fabricated
reviews, no invented stats, no budget figures, no internal tier language. Editorial ANKS
voice (see the site CLAUDE.md banned-phrases list). Em dashes are auto-normalised to hyphens.

## Schema

```json
{
  "name": "Camberwell",                         // display name
  "slug": "camberwell",                         // url-safe, no spaces
  "postcode": "3124",
  "lat": "-37.8323",                            // for geo meta + schema
  "lng": "145.0585",
  "lastmod": "2026-07-22",                      // sitemap lastmod (YYYY-MM-DD)
  "neighbours": ["Canterbury", "Balwyn", "..."], // shown in the "Around <suburb>" list
  "hub_hero_lede": "1-2 sentence hero lede for the suburb hub, locally specific.",
  "character_title": "Section heading for the hub intro.",
  "character": ["Para 1 about the suburb's homes/streets.", "Para 2 on how ANKS delivers there."],
  "where_lede": "1-2 sentences for the 'Where we work' band.",
  "service_angle": {                            // 1-2 sentence local opener per service page
    "custom-homes": "...",
    "commercial": "...",
    "builders-developers": "..."
  },
  "faqs": [                                     // suburb-specific FAQs (0-2), shown on every page for the suburb
    { "q": "...", "a": "..." }
  ]
}
```

Write real, differentiated copy per suburb (homes, streets, constraints, neighbouring areas).
Near-identical pages with only the suburb name swapped read as doorway pages and will not rank.

## Rollout

See `../SUBURB-ROLLOUT-PLAN.md` for the suburb queue, cadence, and per-week batch.
After generating, run `python3 .build/linkify_footer_suburbs.py` so the sitewide footer
"Service areas" band links each suburb that now has a hub page.
