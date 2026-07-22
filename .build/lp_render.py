#!/usr/bin/env python3
"""
ANKS Construction and Landscaping - suburb landing-page generator.

Deterministic. Reads one JSON per suburb from lp/_suburbs/*.json and renders, per suburb:
  - landscaping-<slug>.html            (suburb hub: overview + links to the 3 service pages)
  - custom-homes-<slug>.html           (Architectural / custom homes x suburb)
  - commercial-<slug>.html             (Commercial landscaping x suburb)
  - builders-developers-<slug>.html    (Builders & developers x suburb)
Then refreshes the LP block in sitemap.xml.

Run from the site root:  python3 .build/lp_render.py

WHY a generator: pages roll out weekly and must share ANKS's exact chrome (header, footer,
styles.css classes) and stay on-brand. Structure is locked here; the per-suburb JSON carries
the UNIQUE local copy so pages are genuinely differentiated, not doorway clones.

CONTENT RULE (hard): service-area framing only. Never claim a completed project in a suburb
where ANKS has not worked. Real project case studies shown on these pages (North Balwyn,
Sunbury, Mernda Hills, St James Vermont) are labelled with their TRUE locations as proof of
capability. Em dashes are auto-normalised to hyphens. No fabricated reviews or stats.

See lp/_suburbs/README.md for the JSON schema and lp/SUBURB-ROLLOUT-PLAN.md for the programme.
"""

import html
import json
import os
import re

SITE = "https://anks.com.au"
PHONE_DISPLAY = "0401 500 778"
PHONE_TEL = "+61401500778"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SUBURBS_DIR = os.path.join(ROOT, "lp", "_suburbs")
SITEMAP = os.path.join(ROOT, "sitemap.xml")


def nd(s):
    return s.replace("—", " - ").replace("–", "-")


def esc(s):
    return html.escape(nd(s), quote=True)


# --------------------------------------------------------------------------- service configs
# Copy is faithful to the live service pages (custom-homes.html, commercial.html,
# builders-developers.html). {S} is substituted with the suburb name at render time.

SERVICES = {
    "custom-homes": {
        "short": "Custom homes",
        "nav_label": "Architectural, luxury and custom homes",
        "hero_eyebrow": "Residential",
        "hero_headline": "Landscape Construction,<br />Resolved With The Architecture",
        "hero_img": "assets/pages/north-balwyn/photos/north-balwyn-modern-house-rear-garden.jpeg",
        "intro_eyebrow": "The brief",
        "intro_title": "A garden that reads as part of the build, not after it.",
        "intro_media": "assets/pages/north-balwyn/photos/north-balwyn-aerial-paving-around-house.jpeg",
        "intro_media_alt": "Aerial of an architectural home with crazy paving wrapping the perimeter",
        "intro_p": [
            "On premium custom homes, the landscape is the last thing to start and the first thing people see. Architecturally ambitious projects deserve a landscape contractor who can carry that ambition through every stage of the work, not one who arrives at practical completion to lay turf around someone else's mistakes.",
            "ANKS delivers landscape construction the way the build was drawn. Levels, drainage and structure are resolved against the architecture from day one. Hardscape, planting and lighting are detailed against the materials of the home. Handover happens once, and the landscape is established alongside the residents.",
        ],
        "caps_title": "What we deliver on a custom home.",
        "caps": [
            ("Excavation &amp; site preparation", "Site set-out, bulk and detail excavation, sub-base preparation and earthworks coordinated against the architectural levels.", "assets/pages/sunbury-mansion/photos/process/sunbury-process-aerial-twin-excavators-earthworks.jpeg"),
            ("Structure &amp; retaining", "Boulder, sandstone, masonry and concrete retaining. Pool surrounds, terraces and structural elements that anchor the landscape to the site.", "assets/pages/sunbury-mansion/photos/project/sunbury-project-boulder-wall-side-path-steps.jpeg"),
            ("Hardscape &amp; paving", "Crazy paving, bluestone, aggregate driveways, brick paths, corten and timber edging. Detailed against the materiality of the home.", "assets/pages/north-balwyn/photos/north-balwyn-crazy-paving-stone-detail.jpeg"),
            ("Soft landscape &amp; planting", "Hedging, feature trees, layered beds and turf. Planting palettes selected for the way they age, not just how they look on day one.", "assets/pages/north-balwyn/photos/north-balwyn-boundary-hedge-planting.jpeg"),
            ("Lighting &amp; finishing", "Garden uplights, path lighting and architectural fixtures. Final finishing details that bring the landscape into focus at dusk.", "assets/pages/north-balwyn/photos/north-balwyn-tree-uplighting-night.jpeg"),
            ("Handover &amp; establishment", "Walk-through inspections, maintenance guidance and establishment-period check-ins so the landscape settles in the way it was drawn.", "assets/pages/north-balwyn/photos/north-balwyn-modern-house-rear-garden.jpeg"),
        ],
        "tracks_title": "Three ways into the same standard of work.",
        "tracks": [
            ("For homeowners", "Direct engagement on your home.", "Some clients come to us before there's an architect on the project, others after the build is well underway. Either way we run the landscape as a coordinated piece of work and communicate directly through every stage.", ["Free on-site consultation", "Tailored scope and budget conversation", "Weekly updates during the build", "Maintenance and establishment guidance"]),
            ("For architects &amp; designers", "A delivery partner for the landscape plans.", "We collaborate with architects, landscape designers and consultants to translate drawings into the built result. Materials are specified against the architecture, methodology is resolved before excavation, and the finished work reads as intended.", ["Coordination on drawings and specifications", "Construction methodology resolved before site start", "Materials sourced and detailed against the design", "Single point of contact through delivery"]),
            ("For custom builders", "A landscape contractor inside your programme.", "We run to builder programmes and resolve external works without becoming the reason a build slips. Earthworks and infrastructure can start while the home is being framed; planting and finishing land on practical completion week.", ["Programme integration and milestone tracking", "Authority approvals and compliance handling", "Practical completion and defects coordination", "Establishment maintenance during the handover window"]),
        ],
        "projects": [
            ("Residential &middot; North Balwyn", "North Balwyn residence", "An architectural rebuild reframed by considered hardscape, restrained planting and bespoke lighting detail.", "assets/pages/north-balwyn/cover.jpeg", "projects.html#north-balwyn"),
            ("Residential &middot; Sunbury", "Sunbury estate", "A premium estate landscape resolved end-to-end - boulder retaining, aggregate drives, corten and olive.", "assets/pages/sunbury-mansion/cover.jpeg", "projects.html#sunbury"),
        ],
        "faq": [
            ("When in the build should we engage you for a {S} project?", "The earlier the better. If we are involved during design we can coordinate levels, drainage and structural landscape elements against the architecture. We also work happily on projects we inherit later, once the build is underway or approaching practical completion."),
            ("Do you work directly with our architect or landscape designer?", "Yes. We collaborate with architects, landscape architects, designers and consultants throughout. Specifications, methodology and material selections are resolved with the design team before the first excavator arrives."),
            ("Who is on site during the build?", "Our in-house team. Landscape, construction and earthworks all sit under one company with a single line of accountability. We do not subcontract the structural or earthworks portions to a separate firm and then arrive later to plant around their work."),
        ],
        "seo_service": "Architectural landscape construction",
    },
    "commercial": {
        "short": "Commercial",
        "nav_label": "Commercial landscaping",
        "hero_eyebrow": "Commercial",
        "hero_headline": "Landscape Construction,<br />Delivered Through Active Sites",
        "hero_img": "assets/pages/commercial/photos/st-james-vermont/st-james-vermont-building-hero.jpeg",
        "intro_eyebrow": "The brief",
        "intro_title": "Active sites, fixed programmes, multiple stakeholders.",
        "intro_media": "assets/pages/commercial/photos/mernda-hills-primary/mernda-hills-aerial-courts-and-elc.jpeg",
        "intro_media_alt": "Aerial of a completed school landscape with courts and early learning centre",
        "intro_p": [
            "Commercial landscape construction is rarely just about the landscape. School grounds work runs through term breaks while classrooms operate next door. Public realm and childcare sites carry safety, compliance and stakeholder demands that a residential job never sees.",
            "ANKS is built for this. We run programmes against fixed completion dates, coordinate with principals, business managers and project consultants, and deliver the external works package safely on active and sensitive sites.",
        ],
        "caps_title": "What we deliver on a commercial site.",
        "caps": [
            ("Site safety &amp; WHS", "Fenced compounds, traffic management plans and SWMS documentation. Working alongside active classrooms, public users and live commercial operations.", "assets/pages/commercial/photos/st-james-vermont/st-james-vermont-aerial-site-overview-mulch-sandstone.jpeg"),
            ("Civil &amp; infrastructure", "Bulk and detail excavation, drainage, sub-base, paving, kerbs and driveways. The infrastructure that carries the finished landscape.", "assets/pages/commercial/photos/st-james-vermont/st-james-vermont-roller-compacting-driveway.jpeg"),
            ("Structural &amp; retaining", "Sandstone, boulder, timber and concrete retaining. Tiered beds, embankments and structural elements that shape graded sites.", "assets/pages/commercial/photos/st-james-vermont/st-james-vermont-sandstone-boulder-retaining-wall.jpeg"),
            ("Planting &amp; soft landscape", "Shade trees, hedging, garden beds, ground cover and turf. Planting selected for the way it establishes in commercial settings.", "assets/pages/commercial/photos/mernda-hills-primary/mernda-hills-strelitzia-bed-classroom-wall.jpeg"),
            ("Finishing &amp; site furniture", "Shade sails, fencing, signage, bollards, edging and finishing details. The final layer that brings the commercial site into use.", "assets/pages/commercial/photos/mernda-hills-primary/mernda-hills-shade-sails-playground-perimeter.jpeg"),
            ("Programme delivery &amp; handover", "Milestones tracked to the day, defects and snag resolution before handover, and warranty documentation aligned with consultant requirements.", "assets/pages/commercial/photos/st-james-vermont/st-james-vermont-aerial-school-complex-wide.jpeg"),
        ],
        "tracks_title": "Three ways into the same standard of work.",
        "tracks": [
            ("For schools &amp; education", "Grounds works delivered around the school day.", "Grounds and external works staged around term dates and daily operations, with the documentation and site controls that education projects require. Safe delivery alongside a live campus.", ["Works staged around terms and school hours", "Traffic management and fenced compounds", "SWMS and compliance documentation", "Principal and business-manager coordination"]),
            ("For councils &amp; public realm", "Streetscapes and public spaces, delivered in service.", "Streetscape, park and public-space construction delivered with the public still using the space. Programme, safety and finish held to the standard the brief was written to.", ["Public-access safety management", "Consultant and council coordination", "Streetscape, park and civic works", "Defects and handover documentation"]),
            ("For commercial developers", "External works packages on complex sites.", "The external works package on childcare, medium-density and mixed-use sites, run against your programme with a single point of accountability from earthworks to establishment.", ["Programme integration and milestone tracking", "Earthworks through to soft landscape", "Practical completion and defects", "Establishment during the handover window"]),
        ],
        "projects": [
            ("Commercial &middot; Mernda", "Mernda Hills school grounds", "A school landscape delivered around live classrooms - embankments, planting, shade and finishing to programme.", "assets/pages/commercial/photos/mernda-hills-primary/mernda-hills-aerial-courts-and-elc.jpeg", "projects.html"),
            ("Commercial &middot; Vermont", "St James, Vermont", "Graded driveway, sandstone retaining, tiered beds and grounds delivered across an active education site.", "assets/pages/commercial/photos/st-james-vermont/st-james-vermont-building-hero.jpeg", "projects.html"),
        ],
        "faq": [
            ("Do you deliver commercial landscape works around {S}?", "Yes. Commercial work takes us across metropolitan Melbourne, and we deliver school, childcare, public-realm and medium-density external works in and around {S} and the surrounding suburbs."),
            ("Can you work on an active school or public site?", "Yes. We run fenced compounds, traffic management plans and SWMS documentation, and stage the works around term dates, school hours and public access so the site stays safe while it stays open."),
            ("Who holds accountability for the external works package?", "One in-house team, from earthworks through to planting and finishing. A single line of accountability against your programme, not a chain of subcontractors handing off between trades."),
        ],
        "seo_service": "Commercial landscape construction",
    },
    "builders-developers": {
        "short": "Builders &amp; developers",
        "nav_label": "Builders &amp; developers",
        "hero_eyebrow": "Builders &amp; developers",
        "hero_headline": "External Works Packages,<br />Delivered To Programme",
        "hero_img": "assets/pages/sunbury-mansion/photos/process/sunbury-process-aerial-twin-excavators-earthworks.jpeg",
        "intro_eyebrow": "The brief",
        "intro_title": "A landscape contractor inside your programme, not on top of it.",
        "intro_media": "assets/pages/sunbury-mansion/photos/process/sunbury-process-excavators-boulder-wall-build.jpeg",
        "intro_media_alt": "Excavators building a boulder retaining wall during the earthworks stage",
        "intro_p": [
            "Builders and developers run to programmes. Slipped external works mean slipped practical completion, which means slipped settlement, which means stress at the wrong end of a build. Most landscape subcontractors are the reason that happens.",
            "ANKS works differently. Earthworks and infrastructure can start while the home is being framed. Hardscape and structure resolve alongside the construction sequence, and planting and finishing land on practical completion week, ready to settle.",
        ],
        "caps_title": "What we deliver on a builder programme.",
        "caps": [
            ("Programme integration", "Milestones tracked against your build programme. Earthworks and infrastructure that start in parallel with framing, not after lock-up.", "assets/pages/sunbury-mansion/photos/process/sunbury-process-aerial-twin-excavators-earthworks.jpeg"),
            ("Earthworks &amp; site preparation", "Bulk and detail excavation, cut and fill, levels resolved against the architectural drawings. Sub-base preparation ready for civil works.", "assets/pages/sunbury-mansion/photos/process/sunbury-process-excavator-boulder.jpeg"),
            ("Civil &amp; infrastructure", "Driveways, paths, services trenches, drainage and sub-base. The infrastructure that carries the landscape and the home's external presentation.", "assets/pages/sunbury-mansion/photos/process/sunbury-process-concrete-driveway-pour-aerial.jpeg"),
            ("Structural &amp; retaining", "Boulder, sandstone, masonry and concrete retaining. Structural elements that handle difficult sites, sloping blocks and graded levels.", "assets/pages/sunbury-mansion/photos/project/sunbury-project-boulder-wall-side-path-steps.jpeg"),
            ("Soft landscape &amp; finishing", "Planting, turf, hedging, garden beds and feature trees. Finishing details that present the home at handover and establish well after.", "assets/pages/north-balwyn/photos/north-balwyn-boundary-hedge-planting.jpeg"),
            ("Practical completion &amp; defects", "Walk-through inspection, snag-list resolution before PC, warranty documentation and defects period support. Handover ready to settle.", "assets/pages/north-balwyn/photos/north-balwyn-modern-house-rear-garden.jpeg"),
        ],
        "tracks_title": "Three ways into the same standard of work.",
        "tracks": [
            ("For custom builders", "External works on architect-led custom homes.", "The full external works package on architect-led custom homes, resolved against your programme so the landscape lands with the build rather than chasing it.", ["Programme integration and milestone tracking", "Earthworks through to planting", "Authority approvals and compliance", "Practical completion and defects support"]),
            ("For volume &amp; project builders", "Repeatable scopes delivered on programme.", "Repeatable external works scopes across multiple lots and stages, delivered to fixed programmes with consistent quality and a single point of contact.", ["Repeatable scopes across lots and stages", "Fixed programmes and predictable delivery", "Consistent finish standard", "One point of accountability"]),
            ("For developers", "External works on medium-density and estates.", "External works on medium-density and estate projects, from bulk earthworks and civil through to landscape and establishment, coordinated with your consultant team.", ["Bulk earthworks and civil infrastructure", "Retaining and structural landscape", "Landscape and establishment", "Consultant and authority coordination"]),
        ],
        "projects": [
            ("Residential &middot; Sunbury", "Sunbury estate", "Earthworks, boulder retaining, aggregate driveway and landscape delivered end-to-end on a substantial residential build.", "assets/pages/sunbury-mansion/cover.jpeg", "projects.html#sunbury"),
            ("Residential &middot; North Balwyn", "North Balwyn residence", "External works on an architectural rebuild - hardscape, planting and lighting resolved against the build programme.", "assets/pages/north-balwyn/cover.jpeg", "projects.html#north-balwyn"),
        ],
        "faq": [
            ("Can you start external works before the {S} build is finished?", "Yes, and it is usually the point. Earthworks and infrastructure can start while the home is being framed, so the external works resolve alongside the build instead of compressing into the weeks before practical completion."),
            ("How do you keep external works off the critical path?", "We integrate with your build programme and track milestones against it. Earthworks, civil and structure sequence with the trades ahead of us so planting and finishing land on practical completion week."),
            ("Who is accountable for the whole external package?", "One in-house team across earthworks, civil, structure, landscape and finishing. A single point of accountability, so there is no subcontractor stitching and no scope drift at handover."),
        ],
        "seo_service": "Landscape and external works for builders and developers",
    },
}

SERVICE_ORDER = ["custom-homes", "commercial", "builders-developers"]


# --------------------------------------------------------------------------- chrome

def head(*, title, description, canonical, geo, schema):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<meta name="description" content="{esc(description)}" />
<meta property="og:title" content="{esc(title)}" />
<meta property="og:description" content="{esc(description)}" />
<meta property="og:type" content="website" />
<meta property="og:image" content="{SITE}/assets/pages/north-balwyn/cover.jpeg" />
<meta property="og:url" content="{canonical}" />
<title>{esc(title)}</title>
<link rel="canonical" href="{canonical}" />

<meta name="geo.region" content="AU-VIC" />
<meta name="geo.placename" content="{esc(geo['name'])}, Victoria" />
<meta name="geo.position" content="{geo['lat']};{geo['lng']}" />
<meta name="ICBM" content="{geo['lat']}, {geo['lng']}" />

<link rel="icon" type="image/png" sizes="192x192" href="assets/brand/favicon-192.png" />
<link rel="icon" type="image/png" sizes="32x32" href="assets/brand/favicon-32.png" />
<link rel="alternate icon" href="assets/brand/favicon.ico" />
<link rel="apple-touch-icon" sizes="180x180" href="assets/brand/favicon-180.png" />
<meta name="theme-color" content="#C99404" />

<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet" />

<script type="application/ld+json">
{schema}
</script>

<link rel="stylesheet" href="styles.css" />
</head>
<body>
"""


NAV = """
<header class="site-header" id="site-header">
  <div class="container header-row">
    <a href="index.html" class="brand" aria-label="ANKS Construction and Landscaping - home">
      <img src="assets/brand/anks-logo-transparent.png" alt="" class="brand-mark" width="46" height="46" />
      <span class="brand-text">
        <span class="brand-name">ANKS</span>
        <span class="brand-sub">Construction &amp; Landscaping</span>
      </span>
    </a>

    <nav class="primary-nav" aria-label="Primary">
      <ul>
        <li class="has-mega">
          <a href="/services" aria-haspopup="true">Services<svg class="nav-caret" viewBox="0 0 24 24" width="12" height="12" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="6 9 12 15 18 9"/></svg></a>
          <div class="mega-panel" role="region" aria-label="Services">
            <div class="mega-grid mega-grid-services">
              <a class="mega-cap" href="custom-homes.html">
                <p class="mega-eyebrow">Residential</p>
                <h3 class="mega-cap-title">Architectural, luxury and custom homes</h3>
                <p class="mega-cap-desc">Architecturally integrated outdoor environments delivered alongside homeowners, architects and builders.</p>
                <span class="mega-cap-more">Excavation &middot; Infrastructure &middot; Planting &middot; Handover</span>
              </a>
              <a class="mega-cap" href="commercial.html">
                <p class="mega-eyebrow">Commercial</p>
                <h3 class="mega-cap-title">Commercial landscaping</h3>
                <p class="mega-cap-desc">Schools, childcare, public spaces, streetscapes and complex commercial environments.</p>
                <span class="mega-cap-more">Safety &middot; Compliance &middot; Stakeholder management &middot; Programme delivery</span>
              </a>
              <a class="mega-cap" href="builders-developers.html">
                <p class="mega-eyebrow">Builders &amp; developers</p>
                <h3 class="mega-cap-title">Builders &amp; developers</h3>
                <p class="mega-cap-desc">Reliable delivery for custom builders, volume builders, medium-density and large residential projects.</p>
                <span class="mega-cap-more">Programmes &middot; Approvals &middot; Practical completion &middot; Establishment</span>
              </a>
            </div>
          </div>
        </li>
        <li><a href="process.html">Process</a></li>
        <li><a href="projects.html">Projects</a></li>
        <li><a href="faq.html">FAQ</a></li>
        <li><a href="/contact">Contact</a></li>
      </ul>
    </nav>

    <div class="header-actions">
      <a href="index.html#contact" class="btn btn-pill header-cta">Book a Consultation</a>
      <a href="index.html#contact" class="header-arrow" aria-label="Book a consultation">
        <svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><line x1="7" y1="17" x2="17" y2="7"/><polyline points="8 7 17 7 17 16"/></svg>
      </a>
    </div>

    <button class="nav-toggle" id="nav-toggle" aria-label="Open menu" aria-expanded="false" aria-controls="mobile-nav">
      <span></span><span></span><span></span>
    </button>
  </div>

  <nav class="mobile-nav" id="mobile-nav" aria-label="Mobile">
    <ul>
      <li><a href="/services">Services</a></li>
      <li><a href="process.html">Process</a></li>
      <li><a href="projects.html">Projects</a></li>
      <li><a href="faq.html">FAQ</a></li>
      <li><a href="/contact">Contact</a></li>
      <li><a href="index.html#contact" class="mobile-cta">Book a Consultation</a></li>
    </ul>
  </nav>
</header>
"""


FOOTER = """
<footer class="site-footer">
  <div class="container">
    <div class="footer-top">
      <div class="footer-brand-col">
        <a href="index.html" class="footer-brand" aria-label="ANKS Construction and Landscaping - home">
          <img src="assets/brand/anks-logo-transparent.png" alt="" class="footer-logo-mark" width="48" height="48" />
          <span class="footer-wordmark">ANKS</span>
        </a>
        <div class="footer-socials">
          <a href="https://www.instagram.com/anksconstruction/" target="_blank" rel="noopener" aria-label="Instagram">
            <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="2" width="20" height="20" rx="5"/><circle cx="12" cy="12" r="4"/><line x1="17.5" y1="6.5" x2="17.5" y2="6.5"/></svg>
          </a>
          <a href="https://www.facebook.com/anksconstruction" target="_blank" rel="noopener" aria-label="Facebook">
            <svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor" aria-hidden="true"><path d="M14 13.5h2.5l1-4H14v-2c0-1.03 0-2 2-2h1.5V2.14c-.326-.043-1.557-.14-2.857-.14C11.928 2 10 3.657 10 6.7v2.8H7v4h3V22h4z"/></svg>
          </a>
        </div>
      </div>

      <nav class="footer-cols" aria-label="Footer">
        <div class="footer-col">
          <p class="footer-col-title">Services</p>
          <ul>
            <li><a href="custom-homes.html">Custom homes</a></li>
            <li><a href="commercial.html">Commercial</a></li>
            <li><a href="builders-developers.html">Builders &amp; developers</a></li>
          </ul>
        </div>
        <div class="footer-col">
          <p class="footer-col-title">Studio</p>
          <ul>
            <li><a href="about.html">About</a></li>
            <li><a href="process.html">Our process</a></li>
            <li><a href="projects.html">Featured projects</a></li>
            <li><a href="testimonials.html">Testimonials</a></li>
            <li><a href="faq.html">FAQ</a></li>
          </ul>
        </div>
        <div class="footer-col">
          <p class="footer-col-title">Contact</p>
          <ul>
            <li><a href="index.html#contact">Book a Consultation</a></li>
            <li><a href="tel:+61401500778">0401 500 778</a></li>
            <li><a href="mailto:info@anks.com.au">info@anks.com.au</a></li>
          </ul>
        </div>
      </nav>
    </div>

    <div class="footer-areas">
      <p class="footer-areas-title">Service areas</p>
      <p class="footer-areas-list">Balwyn &middot; Balwyn North &middot; Brighton &middot; Brighton East &middot; Camberwell &middot; Canterbury &middot; Glen Iris &middot; Hawthorn &middot; Kew &middot; Malvern &middot; South Yarra &middot; Toorak</p>
    </div>

    <div class="footer-base">
      <p class="footer-copyright">&copy; <span id="year">2026</span> ANKS Construction and Landscaping</p>
      <p class="footer-base-right">
        <span>South Mountain Road, Upper Plenty VIC 3756 &middot; Moama NSW 2731</span>
        <span><a href="privacy.html">Privacy Policy</a></span>
        <span>Website by <a href="https://suterasites.com.au" target="_blank" rel="noopener">Sutera Sites</a></span>
      </p>
    </div>
  </div>
</footer>

<script src="script.js"></script>
</body>
</html>
"""


def breadcrumb(trail):
    # trail: list of (label, href-or-None)
    parts = []
    for label, href in trail:
        if href:
            parts.append(f'<a href="{href}">{esc(label)}</a>')
        else:
            parts.append(f'<span aria-current="page">{esc(label)}</span>')
    inner = '<span class="crumb-sep" aria-hidden="true">/</span>'.join(parts)
    return f"""
  <nav class="lp-breadcrumb" aria-label="Breadcrumb">
    <div class="container">{inner}</div>
  </nav>
"""


# --------------------------------------------------------------------------- shared sections

def caps_section(cfg, note):
    cards = []
    for i, (title, desc, img) in enumerate(cfg["caps"], 1):
        cards.append(f"""        <article class="cap-card">
          <div class="cap-media"><img src="{img}" alt="{esc(nd(re.sub('&amp;','and',title)))}" loading="lazy" /></div>
          <div class="cap-body">
            <span class="cap-num" aria-hidden="true">{i:02d}</span>
            <h3 class="cap-title">{title}</h3>
            <p class="cap-desc">{desc}</p>
          </div>
        </article>""")
    return f"""
  <section class="sector-caps section section-warm">
    <div class="container">
      <header class="credentials-head">
        <p class="eyebrow">Scope</p>
        <h2 class="credentials-title">{esc(note)}</h2>
      </header>
      <div class="cap-grid">
{chr(10).join(cards)}
      </div>
    </div>
  </section>
"""


def tracks_section(cfg):
    cards = []
    for eyebrow, title, desc, bullets in cfg["tracks"]:
        lis = "".join(f"<li>{esc(b)}</li>" for b in bullets)
        cards.append(f"""        <article class="track-card">
          <p class="track-eyebrow">{eyebrow}</p>
          <h3 class="track-title">{esc(title)}</h3>
          <p class="track-desc">{esc(desc)}</p>
          <ul class="track-list">{lis}</ul>
        </article>""")
    return f"""
  <section class="tracks section">
    <div class="container">
      <header class="credentials-head">
        <p class="eyebrow">Who we work with</p>
        <h2 class="credentials-title">{esc(cfg['tracks_title'])}</h2>
      </header>
      <div class="tracks-grid">
{chr(10).join(cards)}
      </div>
    </div>
  </section>
"""


def projects_section(cfg, heading):
    cards = []
    for eyebrow, title, desc, img, href in cfg["projects"]:
        cards.append(f"""        <a href="{href}" class="pi-card">
          <div class="pi-card-media"><img src="{img}" alt="{esc(title)}" loading="lazy" /></div>
          <div class="pi-card-meta">
            <span class="pi-card-eyebrow">{eyebrow}</span>
            <h2 class="pi-card-title">{esc(title)}</h2>
            <p class="pi-card-desc">{esc(desc)}</p>
          </div>
        </a>""")
    return f"""
  <section class="signature section section-warm">
    <div class="container">
      <header class="credentials-head">
        <p class="eyebrow">Real projects</p>
        <h2 class="credentials-title">{esc(heading)}</h2>
      </header>
      <div class="pi-grid pi-grid-pair">
{chr(10).join(cards)}
      </div>
      <p class="signature-link"><a href="projects.html" class="link-arrow">View the full portfolio</a></p>
    </div>
  </section>
"""


def where_section(sub, lede):
    neighbours = sub.get("neighbours", [])
    chips = "".join(f"<li>{esc(n)}</li>" for n in [sub["name"]] + neighbours)
    return f"""
  <section class="suburbs section">
    <div class="container suburbs-grid">
      <div class="suburbs-text">
        <p class="eyebrow">Where we work</p>
        <h2 class="suburbs-title">Around {esc(sub['name'])}.</h2>
        <p class="suburbs-lede">{esc(lede)}</p>
      </div>
      <div class="suburbs-list-wrap">
        <p class="suburbs-list-title">{esc(sub['name'])} and nearby</p>
        <ul class="suburbs-list">{chips}</ul>
        <p class="suburbs-extra">Part of our core eastern and south-eastern service area. See the <a href="index.html">full picture of how we work</a>.</p>
      </div>
    </div>
  </section>
"""


def faq_section(items, heading):
    rows = []
    for q, a in items:
        rows.append(f"""        <details class="sfaq-item">
          <summary><span>{esc(q)}</span><span class="sfaq-icon" aria-hidden="true"></span></summary>
          <div class="sfaq-body"><p>{esc(a)}</p></div>
        </details>""")
    return f"""
  <section class="sector-faq section section-warm">
    <div class="container">
      <header class="credentials-head">
        <p class="eyebrow">Common questions</p>
        <h2 class="credentials-title">{esc(heading)}</h2>
      </header>
      <div class="sfaq-list">
{chr(10).join(rows)}
      </div>
    </div>
  </section>
"""


def cta_section(sub):
    return f"""
  <section class="cta-banner" id="contact">
    <div class="cta-banner-media" aria-hidden="true">
      <img src="assets/pages/north-balwyn/photos/north-balwyn-aerial-driveway-paving-car.jpeg" alt="" loading="lazy" />
      <div class="cta-banner-veil"></div>
    </div>
    <div class="container cta-banner-inner">
      <p class="eyebrow">Book a consultation</p>
      <h2 class="cta-banner-title">Start with a site walk in {esc(sub['name'])}.</h2>
      <p class="cta-banner-lede">Every project begins with a free on-site consultation. Bring the plans, the architect, the brief, or just the vision. We will walk the site and talk through what is possible.</p>
      <div class="cta-banner-actions">
        <a href="contact.html#contact-form" class="btn btn-primary cta-banner-btn">Book a Consultation</a>
        <a href="tel:{PHONE_TEL}" class="btn btn-ghost-light cta-banner-btn">Call {PHONE_DISPLAY}</a>
      </div>
    </div>
  </section>
"""


# --------------------------------------------------------------------------- schema

def faq_schema(items):
    return {
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": nd(q),
             "acceptedAnswer": {"@type": "Answer", "text": nd(a)}}
            for q, a in items
        ],
    }


def service_schema(name, description, sub, canonical, crumbs):
    graph = [
        {
            "@type": "Service",
            "name": name,
            "description": nd(description),
            "serviceType": name,
            "provider": {
                "@type": "GeneralContractor",
                "name": "ANKS Construction and Landscaping",
                "telephone": PHONE_TEL,
                "url": SITE + "/",
                "image": SITE + "/assets/pages/north-balwyn/cover.jpeg",
            },
            "areaServed": {"@type": "Place", "name": f"{sub['name']}, Victoria, Australia"},
            "url": canonical,
        },
        {
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": i + 1, "name": nd(lbl),
                 **({"item": SITE + href} if href else {})}
                for i, (lbl, href) in enumerate(crumbs)
            ],
        },
    ]
    return graph


def dump_schema(graph):
    obj = {"@context": "https://schema.org", "@graph": graph}
    return json.dumps(obj, indent=2)


# --------------------------------------------------------------------------- page builders

def render_service_page(service_key, sub):
    cfg = SERVICES[service_key]
    slug = f"{service_key}-{sub['slug']}"
    canonical = f"{SITE}/{slug}"
    name = sub["name"]
    label = nd(re.sub("&amp;", "and", cfg["nav_label"]))
    title = f"{label} in {name} - ANKS Construction and Landscaping"
    description = f"{cfg['seo_service']} in {name} and Melbourne's east. {cfg['short'].replace('&amp;','and')} delivered by one in-house team, from excavation through to handover."

    angle = sub.get("service_angle", {}).get(service_key, "")
    hero_lede_extra = f'<p class="hero-lede">{esc(angle)}</p>' if angle else ""

    faqs = [(q.replace("{S}", name), a.replace("{S}", name)) for q, a in cfg["faq"]]
    faqs = sub_local_faqs(sub, service_key) + faqs

    crumbs = [("Home", "/"), ("Services", "/services"),
              (label, f"/{service_key}"), (name, None)]
    schema = dump_schema(service_schema(f"{cfg['seo_service']} in {name}", description, sub,
                                        canonical, crumbs) + [faq_schema(faqs)])

    doc = head(title=title, description=description, canonical=canonical,
               geo=sub, schema=schema)
    doc += NAV
    doc += "\n<main>\n"
    doc += breadcrumb([("Home", "index.html"), (cfg["short"].replace("&amp;", "and"), f"{service_key}.html"), (name, None)])
    # hero
    doc += f"""
  <section class="hero">
    <div class="hero-media" aria-hidden="true"><img src="{cfg['hero_img']}" alt="" /><div class="hero-veil"></div></div>
    <div class="container hero-inner">
      <div class="hero-copy">
        <p class="hero-eyebrow">{cfg['hero_eyebrow']} &middot; {esc(name)}</p>
        <h1 class="hero-headline">{cfg['hero_headline']}</h1>
        {hero_lede_extra}
        <p class="hero-lede">One in-house team from first consultation to final handover. Not three trades stitched together at the end.</p>
        <div class="hero-ctas">
          <a href="index.html#contact" class="btn btn-pill btn-pill-lg">Book a Consultation</a>
          <a href="tel:{PHONE_TEL}" class="hero-arrow" aria-label="Call {PHONE_DISPLAY}"><svg viewBox="0 0 24 24" width="22" height="22" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><line x1="7" y1="17" x2="17" y2="7"/><polyline points="8 7 17 7 17 16"/></svg></a>
        </div>
      </div>
    </div>
  </section>
"""
    # intro
    intro_p = "".join(f'<p class="sector-intro-lede">{esc(p)}</p>' for p in cfg["intro_p"])
    doc += f"""
  <section class="sector-intro section">
    <div class="container sector-intro-grid">
      <div class="sector-intro-text">
        <p class="eyebrow">{cfg['intro_eyebrow']}</p>
        <h2 class="sector-intro-title">{esc(cfg['intro_title'])}</h2>
        {intro_p}
      </div>
      <div class="sector-intro-media"><img src="{cfg['intro_media']}" alt="{esc(cfg['intro_media_alt'])}" loading="lazy" /></div>
    </div>
  </section>
"""
    doc += caps_section(cfg, cfg["caps_title"])
    doc += tracks_section(cfg)
    doc += projects_section(cfg, "Real ANKS projects.")
    doc += where_section(sub, sub.get("where_lede", f"We deliver across {name} and the surrounding eastern and south-eastern suburbs."))
    doc += faq_section(faqs, f"{label} in {name}.")
    doc += cta_section(sub)
    doc += "\n</main>\n"
    doc += FOOTER
    return nd(doc)


def render_hub_page(sub):
    slug = f"landscaping-{sub['slug']}"
    canonical = f"{SITE}/{slug}"
    name = sub["name"]
    title = f"Landscape Construction in {name} - ANKS Construction and Landscaping"
    description = f"Architectural landscape construction in {name}. One in-house team across landscape, construction and earthworks, from first excavation to final planting and handover."

    hero_lede = sub.get("hub_hero_lede",
                        f"Architectural landscape construction across {name} and Melbourne's east. Excavation, structure, hardscape, planting and lighting delivered as one considered piece of work.")
    character = sub.get("character", [])
    intro_p = "".join(f'<p class="sector-intro-lede">{esc(p)}</p>' for p in character)

    # three service cards linking to the service x suburb pages
    cards = []
    for sk in SERVICE_ORDER:
        c = SERVICES[sk]
        cards.append(f"""        <a class="track-card lp-service-card" href="{sk}-{sub['slug']}.html">
          <p class="track-eyebrow">{c['hero_eyebrow']}</p>
          <h3 class="track-title">{c['nav_label']}</h3>
          <p class="track-desc">{esc(sub.get('service_angle', {}).get(sk, ''))}</p>
          <span class="link-arrow">Explore {c['short']} in {esc(name)}</span>
        </a>""")

    faqs = sub_local_faqs(sub, None) + [
        (f"Do you work across {name}?", f"Yes. {name} sits inside our core eastern and south-eastern service area. We deliver architectural landscape construction, commercial works and builder external-works packages across {name} and the surrounding suburbs."),
        ("Is it one team or subcontractors?", "One in-house team. Landscape, construction and earthworks all sit under one company with a single line of accountability, so the work resolves as a single piece rather than three trades stitched together at the end."),
        ("Where can we see your work?", "Our portfolio includes recent residential work in North Balwyn and Sunbury and commercial grounds at Mernda Hills and St James, Vermont. Every project shown is real ANKS work."),
    ]

    crumbs = [("Home", "/"), ("Service areas", None), (name, None)]
    graph = service_schema(f"Landscape construction in {name}", description, sub, canonical,
                           [("Home", "/"), (name, None)])
    schema = dump_schema(graph + [faq_schema(faqs)])

    doc = head(title=title, description=description, canonical=canonical, geo=sub, schema=schema)
    doc += NAV
    doc += "\n<main>\n"
    doc += breadcrumb([("Home", "index.html"), ("Service areas", None), (name, None)])
    doc += f"""
  <section class="hero">
    <div class="hero-media" aria-hidden="true"><img src="assets/pages/north-balwyn/cover.jpeg" alt="" /><div class="hero-veil"></div></div>
    <div class="container hero-inner">
      <div class="hero-copy">
        <p class="hero-eyebrow">{esc(name)} &middot; Landscape, construction &amp; earthworks</p>
        <h1 class="hero-headline">Architectural Landscape<br />Construction in {esc(name)}</h1>
        <p class="hero-lede">{esc(hero_lede)}</p>
        <p class="hero-lede">One in-house team from first consultation to final handover. Not three trades stitched together at the end.</p>
        <div class="hero-ctas">
          <a href="index.html#contact" class="btn btn-pill btn-pill-lg">Book a Consultation</a>
          <a href="tel:{PHONE_TEL}" class="hero-arrow" aria-label="Call {PHONE_DISPLAY}"><svg viewBox="0 0 24 24" width="22" height="22" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><line x1="7" y1="17" x2="17" y2="7"/><polyline points="8 7 17 7 17 16"/></svg></a>
        </div>
      </div>
    </div>
  </section>
"""
    doc += f"""
  <section class="sector-intro section">
    <div class="container sector-intro-grid">
      <div class="sector-intro-text">
        <p class="eyebrow">In {esc(name)}</p>
        <h2 class="sector-intro-title">{esc(sub.get('character_title', f'Landscape that reads as part of the {name} home.'))}</h2>
        {intro_p}
      </div>
      <div class="sector-intro-media"><img src="assets/pages/north-balwyn/photos/north-balwyn-crazy-paving-lamp-garden-edge.jpeg" alt="Crazy paving terrace and lamp post on an architectural residence" loading="lazy" /></div>
    </div>
  </section>
"""
    doc += f"""
  <section class="tracks section section-warm">
    <div class="container">
      <header class="credentials-head">
        <p class="eyebrow">How we can help in {esc(name)}</p>
        <h2 class="credentials-title">Three ways into the same standard of work.</h2>
      </header>
      <div class="tracks-grid">
{chr(10).join(cards)}
      </div>
    </div>
  </section>
"""
    doc += projects_section(SERVICES["custom-homes"], "Recent work near you.")
    doc += where_section(sub, sub.get("where_lede", f"We deliver across {name} and the surrounding eastern and south-eastern suburbs."))
    doc += faq_section(faqs, f"Landscape construction in {name}.")
    doc += cta_section(sub)
    doc += "\n</main>\n"
    doc += FOOTER
    return nd(doc)


def sub_local_faqs(sub, service_key):
    """Suburb-specific FAQs from the JSON (shared across that suburb's pages)."""
    out = []
    for item in sub.get("faqs", []):
        out.append((item["q"], item["a"]))
    return out


# --------------------------------------------------------------------------- sitemap

def update_sitemap(pages):
    with open(SITEMAP, encoding="utf-8") as f:
        xml = f.read()
    xml = re.sub(r"\n  <!-- LP:START -->.*?<!-- LP:END -->", "", xml, flags=re.DOTALL)
    lines = ["\n  <!-- LP:START -->"]
    for slug, lastmod, priority in pages:
        lines.append(f"  <url>\n    <loc>{SITE}/{slug}</loc>\n    <lastmod>{lastmod}</lastmod>\n    <priority>{priority}</priority>\n  </url>")
    lines.append("  <!-- LP:END -->")
    xml = xml.replace("</urlset>", "\n".join(lines) + "\n</urlset>")
    with open(SITEMAP, "w", encoding="utf-8") as f:
        f.write(xml)


# --------------------------------------------------------------------------- main

def main():
    subs = []
    if os.path.isdir(SUBURBS_DIR):
        for fn in sorted(os.listdir(SUBURBS_DIR)):
            if fn.endswith(".json"):
                with open(os.path.join(SUBURBS_DIR, fn), encoding="utf-8") as f:
                    subs.append(json.load(f))

    sitemap_pages = []
    for sub in subs:
        for key, fn in [("hub", f"landscaping-{sub['slug']}.html")] + \
                       [(sk, f"{sk}-{sub['slug']}.html") for sk in SERVICE_ORDER]:
            html_doc = render_hub_page(sub) if key == "hub" else render_service_page(key, sub)
            with open(os.path.join(ROOT, fn), "w", encoding="utf-8") as f:
                f.write(html_doc)
            print(f"[lp_render] wrote {fn}")
            slug = fn[:-5]
            sitemap_pages.append((slug, sub.get("lastmod", "2026-07-22"),
                                  "0.75" if key == "hub" else "0.7"))

    update_sitemap(sitemap_pages)
    print(f"[lp_render] updated sitemap.xml ({len(sitemap_pages)} LP url(s))")


if __name__ == "__main__":
    main()
