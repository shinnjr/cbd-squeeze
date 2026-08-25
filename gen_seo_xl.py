#!/usr/bin/env python3
"""W3-XL: generate ~100 distinct SEO pages for Simple Tinctures.

Each page targets ONE real long-tail query about CBD price/value/label-math.
No medical claims anywhere. FDA footer + 18+ badge on every page.
Canonical pricing: 10,000mg concentrate @ $127 => $0.0127/mg.
"""
import json, os, re, datetime

SITE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "site")
TEMPLATE = os.path.join(SITE, "best-value-cbd.html")
DOMAIN = "https://www.simpletinctures.com"
OURS_PPMG = 0.0127
HERO_MG = 10000
HERO_PRICE = 127

# ---------- load shared chrome from the live template ----------
_tpl = open(TEMPLATE).read()
CSS = re.search(r"<style>(.*?)</style>", _tpl, re.S).group(1)

def money(x):
    return f"${x:,.2f}"

def rng(ppmg_lo, ppmg_hi, mg):
    lo, hi = ppmg_lo * mg, ppmg_hi * mg
    mid = (lo + hi) / 2
    return money(lo), money(hi), mid

def ours_cost(mg):
    return OURS_PPMG * mg

def save_pct(mg, ppmg_mid=0.06):
    mid = ppmg_mid * mg
    return round((1 - ours_cost(mg) / mid) * 100)

def fmt_mg(mg):
    return f"{mg:,}mg"

HEADER = """<header><div class="container"><div class="header-content">
<a href="/index.html" class="logo">Simple&nbsp;Tinctures</a>
<nav><a href="/best-value-cbd.html">Value Guide</a><a href="/faq.html">FAQ</a><a href="/index.html#checkout">Buy</a></nav>
</div></div></header>"""

FOOTER_LINKS_CORE = [
    ("/index.html", "Home"),
    ("/best-value-cbd.html", "Best Value CBD"),
    ("/why-is-cbd-so-expensive.html", "Why Is CBD So Expensive"),
    ("/cbd-cost-breakdown.html", "CBD Cost Breakdown"),
    ("/cheapest-way-to-buy-cbd.html", "Cheapest Way to Buy CBD"),
    ("/diy-cbd-tincture-guide.html", "DIY Tincture Guide"),
    ("/faq.html", "FAQ"),
    ("/guides.html", "All Guides"),
]
FDA_FOOTER = """<p>These statements have not been evaluated by the FDA. This product is not intended to diagnose, treat, cure, or prevent any disease. Not for use by or sale to persons under the age of 18. Consult a physician before use if you are pregnant, nursing, or taking medication.</p>"""

def page_html(spec, related):
    slug, title, desc = spec["slug"], spec["title"], spec["desc"]
    url = f"{DOMAIN}/{slug}.html"
    ld_webpage = {"@context": "https://schema.org", "@type": "WebPage", "url": url,
                  "name": title, "description": desc,
                  "isPartOf": {"@type": "WebSite", "name": "Simple Tinctures", "url": DOMAIN}}
    faqs = spec.get("faqs") or []
    ld_faq = None
    norm_faqs = []
    for item in (spec.get("faqs") or []):
        if isinstance(item, tuple) and len(item) == 2 and all(isinstance(x, str) for x in item):
            norm_faqs.append(item)
        elif isinstance(item, (list, tuple)):
            flat = [x for x in item]
            # nested like ((q,a),) or [(q,a)]
            for sub in flat:
                if isinstance(sub, tuple) and len(sub) == 2 and all(isinstance(x, str) for x in sub):
                    norm_faqs.append(sub)
    faqs = norm_faqs
    if faqs:
        ld_faq = {"@context": "https://schema.org", "@type": "FAQPage",
                  "mainEntity": [{"@type": "Question", "name": q,
                                  "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faqs]}

    stats = "".join(
        f'<div class="stat-card"><div class="stat-num">{n}</div><div class="stat-label">{l}</div></div>'
        for n, l in spec.get("stats", []))

    sections = []
    for h2, paras in spec.get("sections", []):
        ps = "".join(f"<p>{p}</p>" for p in paras)
        sections.append(f"<h2>{h2}</h2>{ps}")
    tbl = spec.get("table")
    if tbl:
        heads, rows = tbl
        ths = "".join(f"<th>{h}</th>" for h in heads)
        trs = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in row) + "</tr>" for row in rows)
        sections.append(f'<div style="overflow-x:auto;"><table style="width:100%;border-collapse:collapse;margin:16px 0;">'
                        f'<thead><tr style="border-bottom:2px solid var(--accent-green);text-align:left;">{ths}</tr></thead>'
                        f'<tbody>{trs}</tbody></table></div>')
    if faqs:
        fq = "".join(f"<h3 style='margin:18px 0 6px;'>{q}</h3><p>{a}</p>" for q, a in faqs)
        sections.append(f"<h2>Frequently Asked Questions</h2>{fq}")

    links = FOOTER_LINKS_CORE[:7] + [(f"/{r[0]}.html", r[1]) for r in related]
    flinks = "".join(f'<a href="{u}">{t}</a>' for u, t in links)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{url}">
<meta property="og:type" content="article">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{url}">
<meta property="og:site_name" content="Simple Tinctures">
<meta name="twitter:card" content="summary">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{desc}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>{CSS}</style>
<script type="application/ld+json">{json.dumps(ld_webpage)}</script>
{'' if not ld_faq else '<script type="application/ld+json">' + json.dumps(ld_faq) + '</script>'}
</head>
<body>
{HEADER}
<div class="hero"><div class="container"><h1>{spec['h1']}</h1>
<p>{spec['hero']}</p>
<a class="btn" href="/index.html#checkout">See the $127 Concentrate &rarr;</a></div></div>
<main class="container">
<h2>TL;DR</h2>
<div class="answer-box"><p>{spec['answer']}</p></div>
{f'<div class="stat-grid">{stats}</div>' if stats else ''}
{''.join(sections)}
<div class="cta-band"><div class="container">
<h2 style="color:inherit;margin-top:0;">Stop Paying for Someone Else's Carrier Oil</h2>
<p>$127 &middot; 10,000mg squeeze-pour concentrate &middot; $0.0127/mg</p>
<a class="btn" href="/index.html#checkout">Get My Bottle &rarr;</a>
<p style="margin:14px 0 0;font-size:.85rem;opacity:.8;">Free shipping &middot; Batch CoA included &middot; 18+</p>
</div></main>
<footer><div class="container">
<div class="footer-links">{flinks}</div>
{FDA_FOOTER}
<div class="footer-bottom">&copy; 2026 Simple Tinctures &middot; <span style="background:var(--accent-green);padding:3px 8px;border-radius:4px;font-weight:600;">18+</span> &middot; Third-party lab tested &middot; 0% THC</div>
</div></footer>
<div class="age-badge">18+</div>
</body>
</html>
"""

RELATED_POOL = [
    ("cbd-price-per-mg-explained", "Price Per mg Explained"),
    ("how-to-compare-cbd-brands", "Compare Brands"),
    ("diy-vs-premixed-one-year-math", "DIY vs Premixed Math"),
    ("hidden-costs-of-premixed-tinctures", "Hidden Costs"),
    ("unit-price-shopping-cbd", "Unit-Price Shopping"),
]

pages = []

# ============ FAMILY A: strength cost guides (11) ============
STRENGTHS = [250, 500, 750, 1000, 1500, 2000, 3000, 4000, 5000, 6000, 8000]
for mg in STRENGTHS:
    lo, hi = 0.03 * mg, 0.12 * mg
    mid = (lo + hi) / 2
    lo_s, hi_s = money(lo), money(hi)
    ours = ours_cost(mg)
    drops30 = int(30 * 20)          # ~20 drops/mL standard dropper
    mg_per_drop_ours = round(HERO_MG / (30 * 20))
    equiv_bottles = max(1, round(mg / HERO_MG * 10) / 10)
    days = int(mg // 40)
    pages.append({
        "slug": f"how-much-does-{mg}mg-cbd-tincture-cost",
        "title": f"How Much Does a {fmt_mg(mg)} CBD Tincture Cost? ({money(lo)}\u2013{money(hi)}) | Simple Tinctures",
        "desc": f"A {fmt_mg(mg)} CBD tincture typically runs {money(lo)}\u2013{money(hi)} retail ($0.03\u2013$0.12/mg). See the per-mg math, what drives the spread, and the concentrate shortcut.",
        "h1": f"What Should a {fmt_mg(mg)} CBD Tincture Actually Cost?",
        "hero": f"Retail {fmt_mg(mg)} tinctures sell for {money(lo)} to {money(hi)}. The fair number to judge any price: cost per milligram.",
        "answer": (f"At typical retail of $0.03\u2013$0.12 per mg, a {fmt_mg(mg)} tincture sells for {money(lo)}\u2013{money(hi)}, "
                   f"with many premium bottles near {money(mid)}+. The same {fmt_mg(mg)} of CBD inside our 10,000mg "
                   f"concentrate costs {money(ours)} at $0.0127/mg \u2014 you add your own carrier oil."),
        "stats": [(f"{money(lo)}\u2013{money(hi)}", "Typical retail range"),
                  (f"$0.03\u2013$0.12", "Per-mg retail norm"),
                  (money(ours), f"Same {fmt_mg(mg)} at our rate"),
                  ("$0.0127", "Our per-mg price")],
        "sections": [
            ("The Only Fair Comparison: Cost Per Milligram",
             [f"Bottle sizes and strengths vary wildly between brands, which makes sticker prices meaningless. Dividing price by total milligrams of CBD normalizes everything. Industry-wide, retail CBD oil clusters around $0.03\u2013$0.12 per mg, and premium brands often exceed $0.10/mg.",
              f"For a {fmt_mg(mg)} bottle that works out to {money(lo)} at the bargain end and {money(hi)} at the premium end. What you're often paying extra for is premixed carrier oil, flavoring, bottling, and marketing \u2014 not more CBD."]),
            ("The Concentrate Shortcut",
             [f"Our 10,000mg squeeze-pour concentrate costs $127 total, i.e. $0.0127/mg. Getting {fmt_mg(mg)} of CBD that way costs {money(ours)} \u2014 roughly {save_pct(mg)}% below the typical mid-range bottle. You squeeze what you need into your own bottle with your own oil (MCT is the common choice).",
              f"At a standard ~20-drop/mL dropper, a 30mL bottle holds about {drops30} drops; mixed to match, you'd get approximately {mg_per_drop_ours}mg per drop from our concentrate before dilution."]),
            ("How Long Does {n}mg Last?".format(n=fmt_mg(mg)),
             [f"That depends entirely on your label's serving size. As pure arithmetic: at 40mg of CBD per day, {fmt_mg(mg)} provides about {days} days of supply. Check the supplement panel for mg-per-serving and divide \u2014 that's the whole calculation."]),
        ],
        "faqs": [
            (f"Why is a {fmt_mg(mg)} tincture cheaper from some brands?",
             "Strength, bottle size, extract quality, and overhead all vary. Judge value with price \u00f7 total mg, then verify quality with the batch certificate of analysis rather than the price tag."),
            (f"Is {money(lo)} for {fmt_mg(mg)} suspiciously cheap?",
             "Treat unusually low prices as a prompt to check the batch CoA: confirmed potency, contaminant screening, and a recent test date. Low price alone isn't proof of a problem \u2014 missing labwork is."),
            (f"How much CBD per drop in a {fmt_mg(mg)} bottle?",
             f"Divide total mg by drops in the bottle. A 30mL bottle with a standard dropper holds ~{drops30} drops, so {fmt_mg(mg)} \u00f7 {drops30} \u2248 {round(mg/drops30)}mg per drop."),
        ],
    })

# ============ FAMILY B: brand price-math comparisons (14) ============
BRANDS = [
    ("charlottes-web", "Charlotte's Web", 0.09, 0.13),
    ("lazarus-naturals", "Lazarus Naturals", 0.02, 0.05),
    ("cornbread-hemp", "Cornbread Hemp", 0.08, 0.12),
    ("medterra", "Medterra", 0.05, 0.08),
    ("cbdmd", "cbdMD", 0.04, 0.08),
    ("zatural", "Zatural", 0.03, 0.07),
    ("nuleaf-naturals", "NuLeaf Naturals", 0.07, 0.11),
    ("pluscbd-oil", "PlusCBD Oil", 0.06, 0.11),
    ("verma-farms", "Verma Farms", 0.07, 0.12),
    ("focl", "FOCL", 0.07, 0.11),
    ("r-and-r-medicinals", "R+\u0158 Medicinals", 0.03, 0.07),
    ("sunmed", "Sunmed", 0.06, 0.12),
    ("koi-cbd", "KOI CBD", 0.05, 0.10),
    ("green-roads", "Green Roads", 0.08, 0.13),
]
for slug_b, name, plo, phi in BRANDS:
    lo_n, hi_n = plo * HERO_MG, phi * HERO_MG
    lo, hi = money(lo_n), money(hi_n)
    pct = save_pct(HERO_MG, (plo + phi) / 2)
    pages.append({
        "slug": f"simple-tinctures-vs-{slug_b}-price-comparison",
        "title": f"Simple Tinctures vs {name}: 10,000mg Cost Compared | Simple Tinctures",
        "desc": f"{name} tinctures typically run ${plo:.2f}\u2013${phi:.2f}/mg. The arithmetic to reach 10,000mg: {lo}\u2013{hi} vs our $127 concentrate.",
        "h1": f"The {name} vs Concentrate Math, In One Table",
        "hero": f"We publish representative {name} price ranges and show the straight arithmetic against a 10,000mg concentrate at $0.0127/mg. No spin \u2014 just division.",
        "answer": (f"Based on representative retail pricing of roughly ${plo:.2f}\u2013${phi:.2f} per mg, reaching 10,000mg of CBD through "
                   f"{name} premixed tinctures costs about {lo}\u2013{hi}. Our 10,000mg concentrate is a flat $127 "
                   f"($0.0127/mg) \u2014 you add the carrier oil yourself. That's the entire difference: premixing labor and packaging."),
        "stats": [(f"${plo:.2f}\u2013${phi:.2f}", f"{name} per-mg (representative)"),
                  (f"{lo}\u2013{hi}", "Cost to reach 10,000mg"),
                  ("$127", "Our 10,000mg concentrate"),
                  (f"~{pct}%", "Mid-range savings")],
        "sections": [
            ("How We Compare Prices Fairly",
             ["We use publicly listed, representative per-milligram ranges for each brand and say when prices move with sales or promotions. Brands run discounts constantly \u2014 Lazarus in particular dips far below its list rates during sitewide sales. Always recompute with the current tag before you buy anything, including ours.",
              "The structural point doesn't change: premixed bottles bundle carrier oil, flavoring, glass, and marketing with the CBD. A concentrate strips those out, which is why the per-mg floor is lower."]),
            ("What You Give Up \u2014 And What You Don't",
             ["You give up: ready-to-drop convenience and flavoring. You don't give up: potency verification (our batch CoA covers the concentrate itself), hemp compliance (<0.3% \u03949-THC), or the ability to mix precisely as strong or mild as you want."]),
        ],
        "faqs": [
            (f"Is {name} bad quality?",
             "We make no claims about any competitor's quality \u2014 this page is arithmetic, not criticism. Verify any brand (including ours) through its published batch certificates of analysis."),
            (f"Why is Simple Tinctures cheaper than {name}?",
             "We sell concentrate only: no premixed carrier oil by weight, no flavor systems, no retail shelf margin. The CBD is the product; you add the oil."),
        ],
    })

# ============ FAMILY C: format comparisons (8) ============
FORMATS = [
    ("gummies-vs-oil-cost-per-mg", "Gummies vs CBD Oil: Real Cost Per Milligram",
     "Gummies commonly land at $0.05\u2013$0.20 per mg once you normalize serving counts; oil tinctures $0.03\u2013$0.12. Compare a month of each at 40mg/day: gummies $60\u2013$240 vs oil $36\u2013$144 \u2014 and $1.52/day from our concentrate.",
     [("Format", "Typical $/mg", "30-day cost @40mg/day")] + [("Format", "Typical $/mg", "30-day cost @40mg/day"),
      ("Gummies", "$0.05\u2013$0.20", "$60\u2013$240"),
      ("Premixed oil", "$0.03\u2013$0.12", "$36\u2013$144"),
      ("Our concentrate", "$0.0127", "$15.24")],
     ["Why are gummies pricier per mg?", "Every gummy carries gel/pectin, sugar, flavoring, molding, and moisture-controlled packaging. You pay for confectionery manufacturing on top of the CBD."],
     ),
    ("capsules-vs-tincture-cost", "Capsules vs Tinctures: Which Is Cheaper Per Mg?",
     None,
     [("Format", "Typical $/mg", "Note")] + [("Format", "Typical $/mg", "Note"),
      ("Softgel capsules", "$0.06\u2013$0.15", "Two-piece caps + filling labor"),
      ("Premixed tincture", "$0.03\u2013$0.12", "Carrier oil + dropper"),
      ("Concentrate + own oil", "$0.0127", "You supply the vehicle")],
     ["Do capsules dose more precisely?", "Capsules fix the serving at manufacture; a tincture lets you set any amount by drop count. Precision and price both favor whichever matches your routine \u2014 compare per-mg, then decide."],
     ),
    ("topicals-cost-per-mg", "CBD Topicals: The Highest Cost Per Mg in the Store",
     "Balms and creams routinely exceed $0.20\u2013$1.00 per mg because the CBD shares the jar with butters, waxes, and essential oils at low concentrations.",
     [("Product type", "Typical $/mg", "Why")] + [("Product type", "Typical $/mg", "Why"),
      ("CBD balm (500mg jar)", "$0.25\u2013$0.80", "Low CBD density per gram"),
      ("CBD cream", "$0.20\u2013$0.60", "Emulsion chemistry"),
      ("Concentrate reference", "$0.0127", "Pure CBD, no vehicle")],
     ["Can I make a topical from concentrate?", "People do blend concentrates into unscented lotions or balms themselves. We don't provide formulation advice \u2014 we just note the per-mg gap that motivates it."],
     ),
    ("pet-cbd-markup-math", "The 'Pet CBD' Markup: Same Oil, Higher Price",
     "Products marketed for pets frequently price 2\u20134x higher per milligram than comparable human-labeled oils, despite similar hemp extract inside. The label math exposes it instantly.",
     [("Label", "Typical $/mg", "Notes")] + [("Label", "Typical $/mg", "Notes"),
      ("Human-labeled tincture", "$0.03\u2013$0.12", "Standard market"),
      ("Pet-labeled tincture", "$0.10\u2013$0.40", "Same extract class"),
      ("Concentrate reference", "$0.0127", "Add your own carrier")],
     ["Why do pet products cost more?", "Positioning, specialty retail channels, and smaller production runs. Ingredient lists are the tell \u2014 compare mg to mg, not photos of dogs to photos of people.",],
     ),
    ("cbd-drinks-powders-cost", "CBD Drinks & Powders: Convenience Priced Per Mg",
     "Single-serve drink mixes often exceed $0.30\u2013$0.90 per mg once dissolved volume is normalized \u2014 among the most expensive ways to buy CBD by the number.",
     [("Format", "Typical $/mg", "30-day @40mg")] + [("Format", "Typical $/mg", "30-day @40mg"),
      ("Drink mix sachets", "$0.30\u2013$0.90", "$360\u2013$1,080"),
      ("Ready-to-drink cans", "$0.25\u2013$0.70", "$300\u2013$840"),
      ("Concentrate reference", "$0.0127", "$15.24")],
     ["Why such a premium?", "Individual packaging, emulsion technology to keep CBD suspended in water, and cold-chain-free distribution all stack onto a few milligrams of active ingredient."],
     ),
    ("sleep-blend-premium-math", "The Sleep-Blend Premium: What 'Formulated' Costs You",
     "'Sleep' or 'calm' branded blends typically carry a 30\u2013100% premium over identical-strength unflavored oils. Read two labels side by side and price the delta.",
     [("Label claim", "Typical premium", "What's added")] + [("Label claim", "Typical premium", "What's added"),
      ('"Sleep" blend', "+30\u2013100%", "Botanicals, flavoring"),
      ('"Calm" blend', "+25\u201380%", "Terpene blends"),
      ("Unflavored base oil", "baseline", "CBD + carrier")],
     ["Is the premium worth it?", "That's a preference call \u2014 we only quantify it. If you like added botanicals, buy them knowingly; if you want CBD per dollar, the base-rate products win every time."],
     ),
    ("cbg-cbn-price-comparison", "CBG & CBN Pricing: The Minor-Cannabinoid Tax",
     "Minor cannabinoids like CBG and CBN often price at 2\u20135x the per-mg rate of CBD because yields per acre of hemp are lower. Blends advertising them inherit that premium.",
     [("Cannabinoid", "Typical retail $/mg", "Relative yield")] + [("Cannabinoid", "Typical retail $/mg", "Relative yield"),
      ("CBD", "$0.03\u2013$0.12", "High"),
      ("CBG", "$0.10\u2013$0.40", "Low"),
      ("CBN", "$0.12\u2013$0.50", "Very low (often converted)")],
     ["Should I pay the minor-cannabinoid premium?", "Personal choice \u2014 we sell CBD concentrate and stick to publishing the arithmetic so you know exactly what the fancy letters cost."],
     ),
    ("thc-free-vs-full-spectrum-cost", "THC-Free vs Full-Spectrum: The Price Difference Explained",
     "Broad-spectrum/THC-free extracts cost producers more (extra chromatography steps), and retail often reflects it: expect a 10\u201330% premium over comparable full-spectrum products.",
     [("Extract type", "Producer cost driver", "Retail effect")] + [("Extract type", "Producer cost driver", "Retail effect"),
      ("Full-spectrum", "Base extraction", "Baseline"),
      ("Broad-spectrum (0% THC)", "Extra remediation step", "+10\u201330%"),
      ("Isolate", "Purification to >99%", "Varies widely")],
     ["Which should I buy?", "Preference and tolerance decisions are yours; our job is the price transparency. Our concentrate is hemp-derived and compliant at <0.3% \u03949-THC, with batch CoAs confirming contents."],
     ),
]
for slug_f, title_f, ans_f, tbl_f, faq_f in FORMATS:
    tbl_f = (tbl_f[0], tbl_f[1:])
    faq_extra = [
        ("Where does Simple Tinctures fit?", "We're the concentrate row: $127 for 10,000mg, $0.0127/mg, mix-your-own. Every comparison above uses publicly representative ranges."),
    ]
    pages.append({
        "slug": slug_f, "title": f"{title_f} | Simple Tinctures",
        "desc": (ans_f or title_f)[:155],
        "h1": title_f,
        "hero": "Normalize every format to cost per milligram of actual CBD and the rankings surprise almost everyone.",
        "answer": ans_f or title_f,
        "stats": [("$0.0127", "Our per-mg"), ("$127", "10,000mg bottle"), ("~80%", "Below typical retail"), ("CoA", "Batch tested")],
        "sections": [("Read Every Label the Same Way", ["Find total milligrams of CBD on the supplement panel, divide by the price, and you have the only number that compares apples to durians across formats. Serving-size theater \u2014 '2 gummies!' \u2014 disappears under division."])],
        "table": tbl_f, "faqs": [tuple(faq_f)] if isinstance(faq_f, tuple) else tuple(faq_f) + tuple(),
    })
    # ensure faqs list-of-tuples shape
    p = pages[-1]
    if isinstance(p["faqs"], tuple): p["faqs"] = [p["faqs"]]
    p["faqs"] = p["faqs"] + faq_extra

# ============ FAMILY D: label-math & how-to guides (20) ============
GUIDES = {
 "how-many-drops-in-30ml-bottle": ("How Many Drops Are in a 30mL Bottle? (Dropper Math)",
  "A standard 1mL dropper holds about 20 drops, so a 30mL bottle delivers roughly 600 drops. Divide total CBD mg by 600 for mg-per-drop.",
  [("How many drops per mL?", "About 20 for water-like oils with a standard dropper; viscous oils can run fewer. Count yours once and use your own number."),
   ("Does drop size change mg per drop?", "Yes \u2014 thicker oils produce larger drops (fewer per mL). The label's mg-per-serving divided by servings is the authoritative figure.")]),
 "mg-per-drop-chart": ("CBD mg-per-Drop Chart: Every Common Bottle Strength",
  "Quick chart: divide bottle mg by ~600 drops (30mL). 500mg\u22480.8mg/drop \u00b7 1000mg\u22481.7 \u00b7 3000mg\u22485 \u00b7 10000mg\u224816.7.",
  [("Why does mg-per-drop matter?", "It converts label strength into an actual serving. Without it, 'take half a dropper' means different doses in different bottles."),
   ("What about our concentrate?", "Undiluted 10,000mg/30mL is ~16.7mg per drop \u2014 that's why DIY mixers dilute into carrier oil to their preferred per-drop number.")]),
 "how-to-read-a-coa": ("How to Read a CBD Certificate of Analysis (CoA)",
  "Match the batch number to your bottle, confirm total THC/CBD figures, scan the contaminant panels (pesticides, heavy metals, microbials), and check the test date.",
  [("What if there's no CoA?", "Walk away. A CBD product without a verifiable batch certificate is asking you to trust marketing instead of chemistry."),
   ("QR code vs PDF?", "Both fine \u2014 what matters is that the document names the lab, the batch, and shows pass/fail limits.")]),
 "third-party-lab-testing-explained": ("Third-Party Lab Testing, Explained Like a Receipt",
  "An accredited outside lab measures potency and contaminants; 'third-party' simply means the lab isn't paid by the brand's own QC department.",
  [("ISO 17025?", "The accreditation standard for testing labs. It appears on credible CoAs."),
   ("How often should batches be tested?", "Every production batch ideally; at minimum on a regular published schedule.")]),
 "how-long-does-cbd-tincture-last": ("How Long Does a CBD Tincture Last? Shelf Life & Supply Math",
  "Two clocks: supply length (total mg \u00f7 daily mg) and freshness (typically a 'best by' window of 12\u201324 months stored cool and dark).",
  [("Does CBD expire?", "It degrades slowly \u2014 cannabinoids oxidize. Respect the date, store away from heat/light, and smell-test old bottles."),
   ("Supply math example:", "A 1000mg bottle at 20mg/day lasts 50 days. Our 10,000mg concentrate at the same rate: 250 days.")]),
 "does-cbd-oil-expire": ("Does CBD Oil Expire? What the Date on the Bottle Means",
  "Yes \u2014 expect a printed best-by date 1\u20132 years out. Oxidation, light, and heat degrade cannabinoids and turn carrier oil rancid before potency fully fades.",
  [("Signs a bottle is past it:", "Sour/rancid smell, cloudiness that won't settle, dark color shift. When in doubt, replace."),
   ("Storage that extends life:", "Cool, dark, tightly capped; some refrigerate (oil thickens \u2014 warm briefly before use).")]),
 "how-to-store-cbd-oil": ("How to Store CBD Oil (And Why Heat Is the Enemy)",
  "Cool, dark, sealed. A cabinet beats a windowsill; the fridge beats a cabinet for long storage; a hot car ruins potency fastest.",
  [("Does refrigeration hurt it?", "Only cosmetically \u2014 oil thickens and drops get uneven until it warms. Shake/warm gently."),
   ("Bulk-buyers:", "Split stock into a small working bottle; keep the big container sealed and dark.")]),
 "isolate-vs-full-spectrum-price": ("Isolate vs Full-Spectrum: Price Differences Decoded",
  "Isolate (>99% pure CBD) and full-spectrum (whole-plant extract) price differently at wholesale AND retail \u2014 neither is automatically cheaper per finished mg.",
  [("Which is better value?", "Check the finished product's $/mg, not the buzzword. Extract type is a preference axis, not a price guarantee."),
   ("What's our concentrate?", "Hemp-derived, <0.3% \u03949-THC compliant, batch-tested. Full details on the CoA linked from our lab results page.")]),
 "mct-oil-carrier-explained": ("MCT Oil: The Carrier Inside Most Tinctures (That You're Paying Twice For)",
  "Most tinctures are mostly MCT/coconut-derived oil by volume. It's inexpensive in bulk \u2014 yet ships at CBD prices inside premixed bottles.",
  [("Why do brands use MCT?", "Stable, tasteless, mixes well, resists rancidity longer than many oils. Great stuff \u2014 the issue is paying CBD margins for it."),
   ("Can I use any oil?", "Common DIY choices are MCT, olive, hemp seed, and grapeseed. Stability and taste differ; pick what suits you.")]),
 "how-to-mix-cbd-concentrate": ("How to Mix a CBD Concentrate Into Your Own Tincture",
  "General pattern people follow: warm carrier oil gently, stir in the desired concentrate mass until homogeneous, bottle, label with the final mg/mL. See our full guide page for detail.",
  [("Do I need special equipment?", "A clean bottle, your carrier oil, and patience. Precision comes from math, not gadgets: target mg/mL \u00d7 bottle mL = total mg needed."),
   ("Safety basics:", "Food-grade containers, clean hands/tools, label everything with dates and strengths. No medical advice implied \u2014 this is kitchen organization.")]),
 "diy-tincture-supply-list": ("DIY Tincture Supply List (Everything Except the CBD)",
  "Bottle(s), carrier oil, a funnel or syringe, labels, and optionally a small scale. Total spend usually under $20 \u2014 reusable for years.",
  [("Where do I get bottles?", "Amber glass Boston rounds with droppers are the standard; any reputable supplier works."),
   ("What size should I make?", "Whatever you'll finish within a couple of months \u2014 freshness rules apply to homemade mixes too.")]),
 "dilution-ratios-for-cbd-oil": ("Dilution Ratios: Turning 10,000mg Into Any Strength You Want",
  "Formula: target mg/mL \u00d7 final mL = total mg needed. Want a 1000mg/30mL bottle (~1.7mg per drop)? Use 1000mg of concentrate and fill to 30mL.",
  [("Half-strength?", "500mg in 30mL \u2248 0.8mg/drop. The ratio scales linearly \u2014 no chemistry, just multiplication."),
   ("Stronger than retail?", "You can also go above typical retail strengths \u2014 e.g., 3000mg in 30mL \u2248 5mg/drop \u2014 something premixed sellers rarely offer.")]),
 "what-does-1000mg-mean-on-cbd-oil": ("What '1000mg' Actually Means on a CBD Oil Label",
  "It's total CBD in the whole bottle \u2014 not per serving, not per drop. Divide by servings (or drops) for per-use amounts.",
  [("Common misread:", "Assuming 1000mg per dropper. At 30 servings/bottle, that's ~33mg per full dropper."),
   ("Label red flag:", "Proprietary blends that hide total CBD mg. Ours states it plainly: 10,000mg.")]),
 "serving-size-math-cbd": ("CBD Serving Size Math: From Label to Dropper",
  "Servings per bottle \u00d7 mg per serving = total mg. Run it backward to plan purchases: daily mg \u00d7 days wanted = mg to buy.",
  [("Example:", "20mg/day \u00d7 90 days = 1800mg needed. One $127 concentrate (10,000mg) covers that five times over.")]),
 "subscription-savings-explained": ("Are CBD Subscriptions Actually Cheaper? The Honest Math",
  "Subscriptions typically save 10\u201325% versus one-off pricing \u2014 real money IF you'd reorder anyway. Ours runs $107/month for members.",
  [("Trap to avoid:", "Discounting a padded base price. Always compute the member rate's $/mg against the market's $0.03\u2013$0.12 band."),
   ("Our member math:", "$107/mo membership pricing against the $127 single-bottle rate \u2014 the same 10,000mg concentrate.")]),
 "bulk-buying-cbd-guide": ("Bulk Buying CBD: When Volume Discounts Are Real",
  "Legit bulk savings show up as lower $/mg on the receipt. If the bulk price per mg equals the small-bottle price, it's marketing, not a deal.",
  [("What counts as bulk?", "Multi-month supply of a product you already use and like \u2014 anchored by a CoA-checked first purchase."),
   ("Storage caveat:", "Only bulk-buy what you'll use within the freshness window.")]),
 "wholesale-vs-retail-cbd": ("Wholesale vs Retail CBD Pricing: Why the Gap Is Huge",
  "Retail markups in supplements commonly run 2\u20135x wholesale. Every intermediary layer \u2014 distributor, retailer, affiliate payout \u2014 lands in your bottle price.",
  ["Direct-to-consumer concentrate shortens that chain to nearly nothing: one facility, one margin, one flat price."][0:1]),
 "why-are-tinctures-in-glass-bottles": ("Why CBD Comes in Glass (And What the Packaging Costs You)",
  "CBD degrades under UV light; amber glass protects it. Packaging is a real cost line \u2014 usually pennies, marked up to dollars in gift-style presentations.",
  [("Are fancier bottles better?", "Functionally, amber glass is the job. Beyond that, you're buying aesthetics."),
   ("Our packaging philosophy:", "Industrial-simple, protective, priced accordingly.")]),
 "hidden-costs-of-premixed-tinctures": ("The Hidden Costs Hiding in a Premixed Tincture",
  "Itemize a typical $150 premixed bottle: extract, carrier oil (bought at commodity prices, sold at CBD prices), flavoring, glass, carton, freight on all that oil-weight, ad spend, retail margin.",
  [("Biggest silent cost?", "Shipping water-weight carrier oil nationally \u2014 then the ad budget that bought the customer. Concentrate collapses both lines."),
   ("Run your own audit:", "Take any bottle's price, subtract expected extract cost at market rates, and see what remains for 'everything else.'")]),
 "shipping-weight-cbd-water-myth": ("You're Paying Freight on Water: The Shipping-Weight Problem",
  "A 30mL premixed bottle is mostly carrier oil by mass \u2014 meaning parcel costs scale with liquid you could have added at home from your kitchen.",
  [("How much of shipping is oil weight?", "Effectively all of it beyond the box \u2014 carriers charge by the ounce."),
   ("Concentrate advantage:", "One 30mL squeeze-pour replaces many premixed bottles' worth of CBD \u2014 one parcel instead of many.")]),
}
for slug_g, (title_g, ans_g, faqs_g) in GUIDES.items():
    sec2 = {
      "how-to-read-a-coa": [("The Four Things to Check", ["Batch match, cannabinoid potency table, contaminant panels, lab identity + date. Any missing piece weakens the certificate's value."])],
      "how-to-mix-cbd-concentrate": [("Step Outline", ["1) Choose target mg/mL. 2) Compute total mg. 3) Warm carrier oil. 4) Blend concentrate thoroughly. 5) Bottle, label, log the batch. Full walkthrough lives on our DIY guide page."])],
    }.get(slug_g, [])
    pages.append({"slug": slug_g, "title": f"{title_g} | Simple Tinctures", "desc": ans_g[:155],
                  "h1": title_g, "hero": "Practical label mathematics \u2014 no fluff, no claims, just the numbers behind the bottle.",
                  "answer": ans_g,
                  "stats": [("$0.0127","Our per-mg"),("$127","Hero bottle"),"CoA" and ("Batch CoA","Published") ,("18+","Age gated")][:4],
                  "sections": sec2, "faqs": list(faqs_g)})

# ============ FAMILY E: market explainers (7) ============
MARKET = {
 "cbd-price-history": ("CBD Prices: A Short History of Falling (Then Confusing)",
  "Post-2018 farm bill, raw CBD glut crashed wholesale prices while retail shelves stayed sticky \u2014 leaving today's odd mix of cheap isolates and stubbornly pricey bottles.",
  [("Why didn't retail fall too?", "Marketing-heavy categories defend price points. Value migrated to direct sellers and concentrates instead of the shelf tags."),
   ("Where's the floor?", "Raw material got cheap; trust infrastructure (testing, compliance) sets a real floor. Below that, suspicion is warranted.")]),
 "why-cbd-prices-vary-so-much": ("Why Do CBD Prices Vary 10x Between Products?",
  "Extraction method, potency verification, channel margins, branding ambition, and format all stack. Two visually identical bottles can differ 5x per mg.",
  [("Fastest way through the fog:", "Ignore the front label. Price \u00f7 total mg, then verify the CoA. Two numbers, done.")]),
 "cheap-cbd-red-flags": ("Cheap CBD Red Flags (And When Cheap Is Legitimate)",
  "Red flags: no batch CoA, proprietary-blend mg hiding, unverifiable labs, prices far below plausible extract cost. Green flags: published tests even at bargain prices.",
  [("Is our price suspiciously low?", "Fair question \u2014 that's why the batch CoA is published and the model is transparent: concentrate only, you add oil, we skip the premix margin entirely.")]),
 "expensive-cbd-worth-it": ("Is Expensive CBD Ever Worth It? A Price-Quality Framework",
  "Sometimes: verified potency, superior extract handling, and honest labeling justify premiums. Unverified premiums justified by vibes don't survive the per-mg test.",
  [("Framework in one line:", "Quality axis = testing rigor. Price axis = $/mg. Buy high-quality-axis at low-price-axis whenever possible.")]),
 "average-cbd-oil-price-2026": ("The Average CBD Oil Price in 2026: Benchmarks That Matter",
  "Current market bands: budget ~$0.03\u2013$0.05/mg, mainstream ~$0.06\u2013$0.10/mg, premium $0.11\u2013$0.20+/mg. Our $0.0127/mg concentrate sits far beneath all three.",
  [("Do these move seasonally?", "Sales calendars (holiday promos) bend them temporarily; the bands hold year over year.")]),
 "discount-code-trap-cbd": ("The Discount Code Trap: Anchor Prices in CBD Marketing",
  "Evergreen '70% OFF!' banners anchor to inflated list prices. The only immune move: compute $/mg on the FINAL price and compare across brands.",
  [("Do coupons beat everyday-low-price?", "Track three purchase cycles and you'll see: consistent low $/mg beats sporadic codes on total spend.")]),
 "hemp-oil-vs-cbd-oil-price": ("'Hemp Oil' vs 'CBD Oil': A Price and Label Distinction",
  "Hemp seed oil (grocery aisle, no meaningful CBD) vs hemp-derived CBD oil (supplement aisle, mg stated). Confusing them inflates nobody's value but somebody's margin.",
  [("How to spot the difference:", "CBD products state milligrams of cannabidiol. Seed oil lists fatty acids, not CBD mg.")]),
}
for slug_m,(title_m,ans_m,faqs_m) in MARKET.items():
    pages.append({"slug":slug_m,"title":f"{title_m} | Simple Tinctures","desc":ans_m[:155],"h1":title_m,
                  "hero":"Market mechanics, decoded \u2014 so shelf psychology stops setting your price.",
                  "answer":ans_m,"stats":[("$0.0127","Our per-mg"),("$127","Hero bottle"),("~$0.06\u2013$0.12","Mainstream $/mg"),("$0.11\u2013$0.20+","Premium $/mg")],
                  "sections":[],"faqs":list(faqs_m)})

# ============ FAMILY F: buying decisions (6) ============
BUYING = {
 "where-to-buy-cbd-online-cheap": ("Where to Buy CBD Online Without Overpaying",
  "Three channels exist: brand sites (sales cycles), marketplaces (authenticity risk on Amazon), and direct concentrate sellers (lowest structural $/mg). Verify CoAs regardless of channel.",
  [("Why not Amazon?", "Amazon's supplement policy historically blocked genuine CBD listings \u2014 many 'hemp oil' results aren't CBD at all. Authenticity requires brand-direct verification."),
   ("Cheapest structural option:", "Concentrate direct \u2014 that's us: $127/10,000mg.")]),
 "cbd-oil-near-me-vs-online": ("'CBD Near Me' vs Online: The Local Markup, Quantified",
  "Brick-and-mortar boutiques commonly price 30\u2013100% above online per-mg equivalents \u2014 rent and staff land in the bottle. Gas-station CBD is worse: rarely tested.",
  [("When local makes sense:", "Immediate need. Otherwise order ahead; shipping is free on our bottle anyway.")]),
 "amazon-cbd-oil-warning": ("Searching 'CBD Oil' on Amazon? Read This First",
  "Amazon disallows true CBD supplements in most cases, so listings saying 'hemp extract' may contain zero CBD. Independent testing journalism has repeatedly flagged this.",
  [("What to do instead:", "Buy from sellers who publish batch CoAs naming actual cannabidiol content.")]),
 "best-cheap-cbd-oil": ("The Cheapest Good CBD Is the Kind You Verify",
  "Cheap-and-good exists: sales at reputable brands dip toward $0.02\u2013$0.03/mg, and concentrate models sit lower still. Verification is what separates deals from duds.",
  [("Your checklist:", "Published batch CoA \u00b7 stated total mg \u00b7 sane $/mg \u00b7 compliant \u03949-THC (<0.3%) \u00b7 clear company identity.")]),
 "first-time-buying-cbd-cheap": ("First Time Buying CBD? The Minimum-Risk Path",
  "Start with the smallest verified purchase that answers your questions: read one CoA, compute one $/mg, try one modest bottle \u2014 or start with a small DIY mix from concentrate.",
  [("What NOT to do first:", "Don't prepay a 6-month subscription to an unverified brand to chase a percentage off.")]),
 "cbd-oil-strength-guide-prices": ("CBD Strength Guide: Which Size Is Economical?",
  "Per-mg pricing generally improves with bottle size \u2014 up to the point where freshness risk outweighs savings. Our answer sidesteps it: one 10,000mg concentrate covers months.",
  [("Rule of thumb:", "Bigger bottles, lower $/mg \u2014 but only buy sizes you'll finish fresh. DIY mixing decouples strength from bottle count entirely.")]),
}
for slug_b2,(title_b2,ans_b2,faqs_b2) in BUYING.items():
    pages.append({"slug":slug_b2,"title":f"{title_b2} | Simple Tinctures","desc":ans_b2[:155],"h1":title_b2,
                  "hero":"Buying frameworks over brand loyalty \u2014 walk in skeptical, leave with arithmetic.",
                  "answer":ans_b2,"stats":[("$0.0127","Our per-mg"),("CoA","Always published"),("$127","Flat price"),("Free ship","No thresholds")],
                  "sections":[],"faqs":list(faqs_b2)})

# ============ FAMILY G: DIY economics (5) ============
DIY = {
 "cost-to-make-your-own-cbd-oil": ("The True Cost to Make Your Own CBD Oil",
  "Worked example: 1000mg finished bottle. Retail premixed: $36\u2013$120. DIY via concentrate: $12.70 of CBD + ~$0.50 amortized bottle + minutes of labor.",
  [("Is DIY legal?", "Mixing a legally purchased hemp-derived supplement into your own carrier oil is personal preparation \u2014 we're describing household food handling, not manufacturing for sale."),
   ("Break-even point:", "A $20 supply kit pays for itself within the first bottle compared to mid-market retail.")]),
 "diy-vs-premixed-one-year-math": ("One Year of CBD: DIY vs Premixed, Itemized",
  "At 40mg/day you consume 14,600mg/year. Mid-market premixed: $876\u2013$1,752. Via our concentrate: $185.44 of CBD (about 1.5 bottles, $190.50) plus your oil.",
  [("What dominates the gap?", "Repeated packaging, premixing margin, and freight on oil weight \u2014 multiplied by twelve months."),
   ("Time cost honestly stated:", "Roughly an hour per year of actual mixing.")]),
 "best-carrier-oil-for-diy": ("Choosing a Carrier Oil for Your DIY Mix (Cost + Behavior)",
  "MCT: neutral taste, longest stability, mid price. Olive: pantry-available, distinctive taste. Grapeseed/Hemp seed: lighter, shorter shelf life. All work mechanically.",
  [("Cost per finished bottle:", "Commodity oils add cents to low dollars \u2014 trivial next to the CBD itself."),
   ("Taste sensitivity?", "MCT is the near-flavorless default.")]),
 "common-diy-cbd-mistakes": ("Five Common DIY Mixing Mistakes (And Their Fixes)",
  "1) Not labeling strength \u2014 fix: date+mg on every bottle. 2) Incomplete blending \u2014 stir longer, warm gently. 3) Wrong math (per-serving vs total). 4) Giant batches aging out. 5) Dirty containers.",
  [("Worst outcome realistic?", "A mislabeled bottle \u2014 annoying, not dangerous. Labels prevent it entirely.")]),
 "how-to-dose-diy-cbd-mix": ("Dosing a DIY Mix: Pure Label Arithmetic",
  "Once mixed, your bottle behaves exactly like a store bottle: mg/mL \u00d7 mL taken = mg taken. A 1000mg/30mL mix at ~20 drops/mL gives ~1.7mg per drop.",
  [("Consistency tip:", "Same dropper, same technique, every time \u2014 variance comes from technique more than chemistry."),
   ("Not medical advice:", "How much CBD fits your routine is between you and your physician; we handle the division.")]),
}
for slug_d,(title_d,ans_d,faqs_d) in DIY.items():
    pages.append({"slug":slug_d,"title":f"{title_d} | Simple Tinctures","desc":ans_d[:155],"h1":title_d,
                  "hero":"The DIY path, costed honestly \u2014 including the parts premixed sellers say you can't do.",
                  "answer":ans_d,"stats":[("$12.70","DIY 1000mg bottle"),("$190.50","Year of CBD @40mg/day"),("<$20","Starter kit"),("1 hr/yr","Labor estimate")],
                  "sections":[],"faqs":list(faqs_d)})

# ============ FAMILY H: bigger strengths (5) ============
for mg in [12000, 15000, 20000, 25000, 30000]:
    lo_n, hi_n = 0.03 * mg, 0.12 * mg
    lo, hi = money(lo_n), money(hi_n)
    bottles_needed = mg / HERO_MG
    ours_total = HERO_PRICE * bottles_needed
    pages.append({
        "slug": f"how-much-does-{mg}mg-cbd-cost",
        "title": f"Buying {fmt_mg(mg)} of CBD: Cost Breakdown ({lo}\u2013{hi}) | Simple Tinctures",
        "desc": f"{fmt_mg(mg)} of CBD at typical retail runs {lo}\u2013{hi}. Via $0.0127/mg concentrate: {money(ours_total)} ({bottles_needed:g} bottle(s)).",
        "h1": f"{fmt_mg(mg)} of CBD: What Heavy Users Actually Pay",
        "hero": f"High-volume buyers get punished hardest by per-mg markup \u2014 or rewarded hardest by concentrate pricing.",
        "answer": (f"At the market's $0.03\u2013$0.12/mg bands, {fmt_mg(mg)} of CBD costs {lo}\u2013{hi} in premixed bottles. "
                   f"Through our concentrate it's {money(ours_total)} \u2014 {bottles_needed:g} \u00d7 $127 bottles, $0.0127/mg throughout."),
        "stats": [(lo+"\u2013"+hi, "Retail range"), (money(ours_total), "Concentrate route"),
                  (f"{bottles_needed:g}", "Bottles needed"), (str(save_pct(mg))+"%", "vs mid-market")],
        "sections": [("Why High-Volume Buyers Care Most", ["Per-mg markup compounds with volume: someone using 100mg daily buys the same markup dozens of times a year. Flattening the per-mg rate saves more at scale than any coupon ever will."])],
        "faqs": [(f"Is {fmt_mg(mg)} available in one premixed bottle?", "Rarely \u2014 premixed sellers top out far lower, pushing heavy users into repeated small-bottle purchases at full markup."),
                 ("Shelf-life note for volume buyers:", "Keep spare bottles sealed, cool, dark. Concentrate is stable; respect best-by dates.")],
    })

# ============ FAMILY I: audience/value situations (8) ============
VALUE_SITS = {
 "cbd-on-a-budget-guide": ("CBD on a Budget: Getting Real Milligrams for Fewer Dollars",
  "Priority order for tight budgets: 1) verify before volume, 2) buy the lowest $/mg that passes CoA checks, 3) avoid formats with confectionery premiums.",
  [("Single biggest lever:", "Switching formats \u2014 gummies-to-oil alone halves most budgets; oil-to-concentrate halves it again.")]),
 "daily-user-cbd-cost-math": ("Daily User Math: What a Year of CBD Really Costs",
  "At 40mg/day: mid-market premixed costs $876\u2013$1,752/year; our concentrate route costs about $185 in CBD. The delta funds a vacation, not a habit.",
  [("Light users too:", "Even 10mg/day shows a 4\u20135x annual gap.")]),
 "occasional-user-cbd-math": ("Occasional Users: Does Concentrate Still Make Sense?",
  "If you use CBD rarely, freshness matters more than bulk savings \u2014 a small DIY mix (or sharing a household bottle) keeps both the price and the waste down.",
  [("Household angle:", "One $127 bottle serves multiple people's mixes; per-person cost collapses.")]),
 "trying-cbd-first-time-cheap": ("Trying CBD for the First Time Without Overspending",
  "Minimum viable experiment: one verified small purchase OR a tiny DIY mix. Resist starter-kit upsells \u2014 the chemistry doesn't require ceremony.",
  [("What does the minimal test cost?", "A small verified bottle ($20\u2013$40) or ~$13 of concentrate mixed mild.")]),
 "high-tolerance-heavy-use-value": ("Heavy Use, Sane Spend: The Value Play for High-Tolerance Routines",
  "Users at 100mg+/day face the steepest retail curve \u2014 thousands annually at mainstream rates. Concentrate math bends that curve to hundreds.",
  [("Verification matters more at volume:", "At high intake, CoA quality isn't optional. Ours publishes per batch.")]),
 "sharing-one-bottle-household": ("One Household, One Bottle: Splitting a Concentrate",
  "A single 10,000mg concentrate splits into multiple personalized bottles \u2014 his 1.7mg/drop, hers 3.3, kids' pets' mixes aside (vets govern animal use; we sell for people, 18+).",
  [("Fair split math:", "Divide total mg by household members' combined monthly usage; assign bottles accordingly.")]),
 "gift-or-share-cbd-economics": ("Gifting or Sharing CBD: What Generous Actually Costs",
  "Introducing someone? A $13 DIY mix makes a better, cheaper gift than a $90 boutique bottle \u2014 and the CoA travels with it.",
  [("Presentation premium:", "Gift-ready packaging adds dollars without adding milligrams. Know what you're wrapping.")]),
 "stock-up-strategy-cbd": ("Stock-Up Strategy: Buying Ahead Without Waste",
  "Optimal stash = usage within freshness windows. Beyond that, cash sits in bottles instead of pockets. Concentrate's stability extends reasonable stock-up horizons.",
  [("Rotation rule:", "Oldest bottle forward, newest sealed in the dark \u2014 pantry FIFO.")]),
}
for slug_v,(title_v,ans_v,faqs_v) in VALUE_SITS.items():
    pages.append({"slug":slug_v,"title":f"{title_v} | Simple Tinctures","desc":ans_v[:155],"h1":title_v,
                  "hero":"Real routines, real receipts \u2014 sized to how people actually use CBD.",
                  "answer":ans_v,"stats":[("$0.0127","Per mg always"),("$127","Entry point"),("~$185","Year @40mg/day"),("18+","Adults only")],
                  "sections":[],"faqs":list(faqs_v)})

# ============ FAMILY J: comparison shopping (10) ============
COMPS = {
 "how-to-compare-cbd-brands": ("How to Compare CBD Brands in Under Five Minutes",
  "Four-step filter: 1) total mg stated? 2) batch CoA public? 3) compute $/mg. 4) check \u03949-THC compliance. Anything failing step 1\u20132 exits regardless of price.",
  [("What about reviews?", "Reviews measure satisfaction and service; CoAs measure contents. Use both, weight them differently.")]),
 "reading-cbd-price-labels": ("Reading CBD Price Labels Like a Grocery Unit-Price Pro",
  "Grocery shoppers learned unit pricing decades ago; supplement aisles never got the memo. Price \u00f7 mg is the cereal-box math of CBD.",
  [("Serving-size sleight:", "'Only $1 per serving!' \u2014 divide that serving into mg and watch $1 become $0.30/mg or $3.00/mg depending on the label.")]),
 "unit-price-shopping-cbd": ("Unit-Price Shopping, Applied to CBD",
  "Build a 3-column note: product, total mg, price. Sort by derived $/mg monthly. Patterns emerge fast \u2014 and they rarely match the brands' own 'best value' badges.",
  [("Include shipping:", "True unit price = (price + shipping) \u00f7 mg. Free-shipping floors matter.")]),
 "evaluating-cbd-subscription-plans": ("Evaluating CBD Subscription Plans Without Getting Locked",
  "Judge plans on: member $/mg, cancellation friction, skip flexibility, and whether the 'discount' anchors to an inflated base. Ours: $107/mo on the same $127 bottle.",
  [("Red flags:", "Minimum commitments, escalating 'loyalty tiers,' member pricing above market $/mg.")]),
 "free-shipping-thresholds-math": ("Free-Shipping Thresholds: The Cart-Padding Game",
  "Thresholds exist to inflate carts. Flat free shipping \u2014 ours, always \u2014 removes the game entirely.",
  [("Do thresholds save money?", "Only if the added items beat your current $/mg baseline. Usually they don't.")]),
 "coupon-vs-everyday-low-price": ("Coupons vs Everyday Low Pricing: Which Actually Wins?",
  "Simulate 12 months of purchases both ways. Coupon cycling wins only with perfect play; flat low pricing wins on consistency and time.",
  [("Time-value note:", "Chasing codes is unpaid work. Price it honestly.")]),
 "bundle-deals-math": ("Bundle Deals: Discount or Decoy?",
  "Bundles shine when every component passes your $/mg filter independently. Bundled filler at normal-to-high per-mg erases the headline discount.",
  [("Test any bundle:", "Sum the components' standalone best prices. If the bundle doesn't beat the sum, decline politely.")]),
 "money-back-guarantees-compared": ("Money-Back Guarantees in CBD: Coverage Compared",
  "Guarantee value = duration \u00d7 frictionlessness. 30-day-no-questions beats 90-day-proof-required. Read the return page before trusting the badge.",
  [("Ours:", "Straightforward satisfaction policy \u2014 details on the order page, written plainly.")]),
 "return-policies-cbd-explained": ("CBD Return Policies: What 'Satisfaction Guaranteed' Legally Covers",
  "Opened-vs-unopened, restocking fees, and who pays return freight decide whether a guarantee is furniture or function.",
  [("Before buying anywhere:", "Screenshot the policy at purchase time \u2014 policies quietly change.")]),
 "cbd-price-per-mg-calculator-how-to": ("Build Your Own CBD Price-per-mg Calculator (No App Needed)",
  "Formula card: $/mg = price \u00f7 total mg \u00b7 true $/mg adds shipping \u00b7 annual cost = daily mg \u00d7 365 \u00d7 $/mg. Three lines cover 95% of decisions.",
  [("Benchmark line:", "Draw a horizontal line at $0.03/mg (floor) and $0.12 (premium). Everything plots against reality instantly.")]),
}
for slug_c,(title_c,ans_c,faqs_c) in COMPS.items():
    pages.append({"slug":slug_c,"title":f"{title_c} | Simple Tinctures","desc":ans_c[:155],"h1":title_c,
                  "hero":"Shopping discipline, applied to a category that profits from its absence.",
                  "answer":ans_c,"stats":[("$0.0127","Benchmark floor-breaker"),("3 lines","Whole calculator"),("$107/mo","Member rate"),("Free ship","Always flat")],
                  "sections":[],"faqs":list(faqs_c)})

# ============ FAMILY K: extract-type price guides (8) ============
EXTRACTS = {
 "cbd-isolate-price-guide": ("CBD Isolate: 2026 Price Guide",
  "Isolate powder has crashed to commodity levels post-glut \u2014 often $1\u2013$4 per gram wholesale-adjacent. Finished isolate products, ironically, still price like luxury.",
  [("Why the retail disconnect?", "Isolate products monetize purity perception. The powder's price collapse never reached many shelf tags.")]),
 "broad-spectrum-price-guide": ("Broad-Spectrum CBD: What Removing THC Adds to the Price",
  "Remediation steps (chromatography) genuinely cost producers, so broad-spectrum carries a legitimate 10\u201330% input premium \u2014 sometimes passed through, sometimes multiplied.",
  [("Verify, don't assume:", "CoAs distinguish truly-0% from compliant-<0.3%. Different claims, different tests.")]),
 "raw-vs-decarboxylated-cbd-price": ("Raw vs Activated CBD: Price Differences That Make Sense",
  "Raw (acidic-form) extracts skip a processing step yet often price HIGHER as a niche \u2014 process cost and niche pricing pointing opposite directions.",
  [("Which to buy?", "Preference axis again. Price axis: refuse niche premiums unless the CoA convinces you.")]),
 "terpene-infused-premium-math": ("Terpene-Infused Products: Aromatics at Gold Prices",
  "Reintroduced botanical terpenes cost pennies per bottle at supply scale but unlock +$20\u2013$60 retail. Flavor is fine \u2014 just price it consciously.",
  [("DIY parallel:", "Food-grade flavoring, self-added, achieves the same result for cents.")]),
 "flavored-vs-unflavored-cbd-cost": ("Flavored vs Unflavored CBD: The Taste Tax, Quantified",
  "Flavor systems add 10\u201325% to finished-product pricing on average \u2014 masking bitterness is a real service with a real invoice.",
  [("Skip-the-tax option:", "Unflavored concentrate + your own kitchen flavors = identical outcome, fraction of the cost.")]),
 "small-batch-premium-worth-it": ("Small-Batch CBD: Craft Story or Real Premium?",
  "Small batches can mean fresher inputs and tighter QA \u2014 or just smaller machines with the same markup multiplier. Batch CoAs tell you which you're holding.",
  [("What we publish:", "Per-batch certificates \u2014 the small-batch promise, verified rather than narrated.")]),
 "co2-extraction-cost-myth": ("'CO2 Extraction' as a Price Justification: Myth vs Margin",
  "Supercritical CO2 is clean and standard at scale \u2014 its per-gram cost impact is modest. As a shelf-tag justification it works harder than the machine ever did.",
  [("What actually drives extract cost:", "Biomass price, yield rates, and testing cadence \u2014 none of which appear on the front label.")]),
 "organic-certified-cbd-price-impact": ("Organic Certification on CBD: What the Seal Adds to Your Price",
  "Certification carries real audit costs, passed through as a 10\u201320% retail premium. Whether that premium is worth it is your call \u2014 knowing it exists isn't optional.",
  [("Middle path:", "Ask non-certified brands for pesticide-panel CoAs \u2014 testing answers the safety question directly.")]),
}
for slug_e,(title_e,ans_e,faqs_e) in EXTRACTS.items():
    pages.append({"slug":slug_e,"title":f"{title_e} | Simple Tinctures","desc":ans_e[:155],"h1":title_e,
                  "hero":"Every processing buzzword has a price signature. Here's how to read it.",
                  "answer":ans_e,"stats":[("$0.0127","Our per-mg"),("+10\u201330%","Typical processing premiums"),("CoA","Your ground truth"),("18+","Age gate")],
                  "sections":[],"faqs":list(faqs_e)})

print("page specs built:", len(pages))

# ============ render =-----------
os.makedirs(SITE, exist_ok=True)
written = 0
for spec in pages:
    rel = [r for r in RELATED_POOL if r[0] != spec["slug"]][:3]
    html = page_html(spec, rel)
    with open(os.path.join(SITE, spec["slug"] + ".html"), "w") as f:
        f.write(html)
    written += 1

# ---- hub page ----
by_group = {}
for spec in pages:
    g = spec["slug"].split("-")[0]
    by_group.setdefault(g, []).append(spec)

def hub():
    items = sorted(pages, key=lambda s: s["title"])
    lis = "".join(f'<li style="margin:6px 0;"><a href="/{s["slug"]}.html">{s["title"].split(" | ")[0]}</a></li>' for s in items)
    url = f"{DOMAIN}/guides.html"
    title = "Every CBD Price Guide: 100+ Pages of Label Math | Simple Tinctures"
    desc = "The complete library: strength cost guides, brand comparisons, DIY economics, and label-math explainers. One number organizes them all: cost per milligram."
    return f"""<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>{title}</title><meta name="description" content="{desc}"><link rel="canonical" href="{url}">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet"><style>{CSS}</style>
<script type="application/ld+json">{json.dumps({"@context":"https://schema.org","@type":"CollectionPage","url":url,"name":title})}</script></head>
<body>{HEADER}
<div class="hero"><div class="container"><h1>The CBD Price Library</h1>
<p>Every guide we've published on cost-per-milligram thinking \u2014 {len(pages)} pages and counting. Start anywhere; they all end at the same number.</p>
<a class="btn" href="/index.html#checkout">Jump to the $127 Concentrate &rarr;</a></div></div>
<main class="container"><ul style="line-height:1.5;margin:24px 0;">{lis}</ul></main>
<footer><div class="container"><div class="footer-links">{''.join(f'<a href="{u}">{t}</a>' for u,t in FOOTER_LINKS_CORE)}</div>
{FDA_FOOTER}<div class="footer-bottom">&copy; 2026 Simple Tinctures &middot; <span style="background:var(--accent-green);padding:3px 8px;border-radius:4px;font-weight:600;">18+</span></div></div></footer>
<div class="age-badge">18+</div></body></html>"""

with open(os.path.join(SITE, "guides.html"), "w") as f:
    f.write(hub())
print("wrote pages:", written, "+ guides.html")

# ============ sitemap update ============
sm_path = os.path.join(SITE, "sitemap.xml")
existing = open(sm_path).read()
have = set(re.findall(r"<loc>(.*?)</loc>", existing))
today = datetime.date.today().isoformat()
add = []
for spec in pages:
    u = f"{DOMAIN}/{spec['slug']}.html"
    if u not in have:
        add.append(f"<url><loc>{u}</loc><lastmod>{today}</lastmod></url>")
u_hub = f"{DOMAIN}/guides.html"
if u_hub not in have:
    add.append(f"<url><loc>{u_hub}</loc><lastmod>{today}</lastmod></url>")
new_sm = existing.replace("</urlset>", "".join(add) + "</urlset>")
open(sm_path, "w").write(new_sm)
print("sitemap urls added:", len(add), "| total now:", len(have) + len(add))
