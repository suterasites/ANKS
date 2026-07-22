# ANKS Suburb Landing-Page Rollout

Local-SEO buildout: each target suburb gets **4 pages** - a suburb hub plus 3 service pages
(Custom Homes, Commercial, Builders & Developers). Generated from `lp/_suburbs/<slug>.json`
via `python3 .build/lp_render.py`, then `python3 .build/linkify_footer_suburbs.py`.

**Status (2026-07-22):** Template APPROVED by James. Camberwell, Canterbury and Balwyn live
(3 suburbs, 12 pages). Remaining 9 suburbs batching per the cadence below. Suburb LPs sit in
the Premium tier of ANKS's original quote (beyond the base $1,500) - billing to confirm.

## Rules (hard)

- **Service-area framing only.** Never claim a completed project in a suburb where ANKS has not
  worked. The "Real projects" strip shows genuine ANKS work at its TRUE location (North Balwyn,
  Sunbury, Mernda Hills, St James Vermont) as proof of capability.
- No fabricated reviews or stats, no budget/$ figures, no internal Tier 1/2/3 language on the site.
- Editorial ANKS voice; honour the banned-phrases list in the site CLAUDE.md.
- Every suburb JSON must carry genuinely unique local copy (homes, streets, constraints,
  neighbours). Near-duplicate pages read as doorway pages and will not rank.

## Cadence

Target: **2 suburb hubs + 3 service pages per week**, working down the priority order and
finishing each suburb's 3 service pages as you go. At that rate the 11 remaining suburbs
(44 pages) land over roughly 10-12 weeks. Adjust once the template is approved.

## Per-week workflow

1. Pick the next 1-2 suburbs from the queue below.
2. Write `lp/_suburbs/<slug>.json` with real local copy (schema in `_suburbs/README.md`).
3. `python3 .build/lp_render.py` then `python3 .build/linkify_footer_suburbs.py` from the site root.
4. Spot-check: pages serve, no em dashes, no banned phrases, no fabricated local project, images resolve.
5. Move the suburb to the Built log below.
6. `git add` the new pages + edited page footers + sitemap.xml + `lp/`, commit, push (Cloudflare deploys).

## Built log

| Date | Suburb | Pages |
|------|--------|-------|
| 2026-07-22 | Camberwell | hub + custom-homes + commercial + builders-developers (approved template) |
| 2026-07-22 | Canterbury | hub + custom-homes + commercial + builders-developers |
| 2026-07-22 | Balwyn | hub + custom-homes + commercial + builders-developers |

## Queue (priority order - sweet-spot core first)

| # | Suburb | Slug | Notes |
|---|--------|------|-------|
| 1 | Kew | kew | Core six. |
| 2 | Hawthorn | hawthorn | Core six. |
| 3 | Brighton | brighton | Core six. Bayside, distinct character from the eastern suburbs. |
| 4 | Balwyn North | balwyn-north | Has a real ANKS project - use the honest local-proof block here. |
| 5 | Brighton East | brighton-east | Bayside. |
| 6 | Glen Iris | glen-iris | |
| 7 | Malvern | malvern | |
| 8 | South Yarra | south-yarra | Denser, more apartment/townhouse - weight commercial/builders angle. |
| 9 | Toorak | toorak | Premium, but NOT the ultra-mega segment; keep to the $2m-$8m register. |

Note: Balwyn North (#6) is the one suburb with a documented ANKS project (North Balwyn). When
building it, add a genuine local-project block rather than the generic service-area framing.
