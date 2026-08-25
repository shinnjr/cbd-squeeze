#!/usr/bin/env python3
"""Generate W3 SEO/GEO pages for Simple Tinctures (static HTML, shared design system)."""
import json
import os

SITE = "/Users/jamesshinn/projects/cbd-squeeze/site"
BASE = "https://www.simpletinctures.com"

CSS = """
:root { --dark-green:#1a3a3a; --cream:#f5f1e8; --accent-green:#4a6741; --text-dark:#2d2d2d; --text-light:#f5f1e8; }
*{margin:0;padding:0;box-sizing:border-box;}
body{font-family:'Inter',sans-serif;background:var(--cream);color:var(--text-dark);line-height:1.6;overflow-x:hidden;}
.container{max-width:1100px;margin:0 auto;padding:0 20px;}
header{background-color:var(--dark-green);padding:15px 0;position:sticky;top:0;z-index:1000;}
.header-content{display:flex;justify-content:space-between;align-items:center;}
.logo{color:var(--text-light);font-size:24px;font-weight:700;text-decoration:none;}
nav a{color:var(--text-light);text-decoration:none;font-weight:500;margin-left:30px;transition:opacity .3s;}
nav a:hover{opacity:.8;}
.hero{background:linear-gradient(135deg,var(--dark-green) 0%,var(--accent-green) 100%);padding:64px 0;text-align:center;color:var(--text-light);}
.hero h1{font-size:2.6rem;line-height:1.2;margin-bottom:16px;}
.hero p{font-size:1.15rem;max-width:700px;margin:0 auto 24px;opacity:.95;}
.btn{background-color:var(--accent-green);color:#fff;padding:15px 30px;border-radius:8px;font-size:1.05rem;font-weight:600;text-decoration:none;display:inline-block;border:none;cursor:pointer;}
.btn:hover{background-color:#3a5633;transform:translateY(-2px);}
main{padding:56px 0;}
h2{color:var(--dark-green);font-size:1.9rem;margin:2.2rem 0 .9rem;}
h3{color:var(--dark-green);font-size:1.25rem;margin:1.6rem 0 .5rem;}
p{margin-bottom:1rem;}
ul,ol{margin:0 0 1.2rem 1.4rem;}
li{margin-bottom:.45rem;}
.answer-box{background:#fff;border:2px solid var(--accent-green);border-left-width:10px;border-radius:12px;padding:24px 28px;margin:28px 0;box-shadow:0 2px 10px rgba(0,0,0,.06);}
.answer-box p:last-child{margin-bottom:0;}
.stat-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:1rem;margin:1.5rem 0;}
.stat-card{background:#fff;border:1px solid #e5e0d5;border-radius:12px;padding:1.25rem;text-align:center;}
.stat-num{font-size:1.7rem;font-weight:700;color:var(--accent-green);}
.stat-label{font-size:.85rem;color:#666;}
table.data{width:100%;border-collapse:collapse;margin:1.5rem 0;background:#fff;border-radius:12px;overflow:hidden;box-shadow:0 2px 8px rgba(0,0,0,.06);}
table.data th,table.data td{padding:14px 16px;text-align:left;border-bottom:1px solid #eee;}
table.data th{background:var(--dark-green);color:var(--text-light);font-weight:600;}
table.data tr:hover td{background:rgba(74,103,65,.06);}
tr.hl td{background:#f4faf5;font-weight:600;}
.step{display:flex;gap:1rem;margin-bottom:1.4rem;background:#fff;border:1px solid #e5e0d5;border-radius:12px;padding:1.25rem 1.5rem;}
.step-n{flex:0 0 auto;width:2.2rem;height:2.2rem;line-height:2.2rem;border-radius:50%;background:var(--dark-green);color:#fff;font-weight:700;text-align:center;}
.faq-item{border-bottom:1px solid #ddd;padding:20px 0;}
.faq-q{font-weight:600;font-size:1.08rem;color:var(--dark-green);}
.faq-a{margin-top:.5rem;color:#555;}
.cta-band{background:var(--dark-green);color:var(--text-light);text-align:center;padding:48px 20px;border-radius:14px;margin:2.5rem 0;}
.cta-band .price-line{font-size:1.35rem;font-weight:700;margin:.5rem 0 1.2rem;}
.age-badge{position:fixed;bottom:20px;right:20px;background:var(--accent-green);color:#fff;padding:8px 12px;border-radius:6px;font-size:12px;font-weight:600;z-index:100;}
footer{background-color:var(--dark-green);color:var(--text-light);padding:40px 0 20px;font-size:.9rem;margin-top:40px;}
.footer-links{display:flex;flex-wrap:wrap;gap:18px;margin-bottom:22px;}
.footer-links a{color:var(--text-light);opacity:.85;text-decoration:none;}
.footer-links a:hover{opacity:1;}
.footer-bottom{border-top:1px solid rgba(255,255,255,.2);padding-top:18px;text-align:center;opacity:.75;}
@media(max-width:768px){.hero h1{font-size:1.9rem;} nav a{margin-left:16px;} table.data{font-size:.85rem;display:block;overflow-x:auto;}}
"""

def page(slug, title, desc, body_html, faq):
    faq_ld = {"@context": "https://schema.org", "@type": "FAQPage",
              "mainEntity": [{"@type": "Question", "name": q,
                              "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq]}
    web_ld = {"@context": "https://schema.org", "@type": "WebPage", "url": f"{BASE}/{slug}",
              "name": title, "description": desc,
              "isPartOf": {"@type": "WebSite", "name": "Simple Tinctures", "url": BASE}}
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{BASE}/{slug}">
<meta property="og:type" content="article">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{BASE}/{slug}">
<meta property="og:site_name" content="Simple Tinctures">
<meta name="twitter:card" content="summary">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{desc}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>{CSS}</style>
<script type="application/ld+json">{json.dumps(web_ld)}</script>
<script type="application/ld+json">{json.dumps(faq_ld)}</script>
</head>
<body>
<header><div class="container"><div class="header-content">
<a href="/index.html" class="logo">Simple&nbsp;Tinctures</a>
<nav><a href="/best-value-cbd.html">Value Guide</a><a href="/faq.html">FAQ</a><a href="/index.html#checkout">Buy</a></nav>
</div></div></header>
<div class="hero"><div class="container">{body_html['hero']}</div></div>
<main class="container">{body_html['main']}</main>
<footer><div class="container">
<div class="footer-links">
<a href="/index.html">Home</a><a href="/best-value-cbd.html">Best Value CBD</a><a href="/why-is-cbd-so-expensive.html">Why Is CBD So Expensive</a><a href="/cbd-cost-breakdown.html">CBD Cost Breakdown</a><a href="/cheapest-way-to-buy-cbd.html">Cheapest Way to Buy CBD</a><a href="/diy-cbd-tincture-guide.html">DIY Tincture Guide</a><a href="/faq.html">FAQ</a>
</div>
<p>These statements have not been evaluated by the FDA. This product is not intended to diagnose, treat, cure, or prevent any disease. Not for use by or sale to persons under the age of 18. Consult a physician before use if you are pregnant, nursing, or taking medication.</p>
<div class="footer-bottom">&copy; 2026 Simple Tinctures &middot; <span style="background:var(--accent-green);padding:3px 8px;border-radius:4px;font-weight:600;">18+</span> &middot; Third-party lab tested &middot; 0% THC</div>
</div></footer>
<div class="age-badge">18+</div>
</body>
</html>"""

CTA = """
<div class="cta-band">
<h2 style="color:inherit;margin-top:0;">The Best-Value CBD on This Page Is Ours</h2>
<p class="price-line">10,000mg squeeze-pour concentrate &middot; $127 &middot; $0.0127/mg</p>
<a class="btn" href="/index.html#checkout">Get My Bottle &rarr;</a>
<p style="margin:14px 0 0;font-size:.85rem;opacity:.8;">Free shipping &middot; Batch CoA included &middot; 18+</p>
</div>"""

pages = {}

# ---------------- 1. PILLAR: best-value-cbd ----------------
pages["best-value-cbd.html"] = page(
    "best-value-cbd.html",
    "Best Value CBD Oil in 2026: Cost Per Milligram, Ranked | Simple Tinctures",
    "What 'best value CBD' actually means: cost per milligram. Compare retail tinctures ($0.03-$0.12+/mg) against a 10,000mg concentrate at $0.0127/mg you mix yourself.",
    {
      "hero": """<h1>The Best Value CBD Isn't a Bottle. It's a Math Problem.</h1>
<p>Retail CBD oil runs $0.03&ndash;$0.20+ per milligram. Our 10,000mg squeeze-pour concentrate costs <strong>$0.0127/mg</strong> &mdash; and this guide shows you exactly how to compare any CBD product by the number that matters.</p>
<a class="btn" href="/index.html#checkout">See the $127 Concentrate &rarr;</a>""",
      "main": f"""
<h2>TL;DR: How to Find the Best Value CBD</h2>
<div class="answer-box">
<p><strong>Value = price &divide; total milligrams of CBD.</strong> Most retail tinctures cost $0.03&ndash;$0.12 per mg of CBD. Anything above ~$0.17/mg is widely graded as pricey; under ~$0.08/mg counts as bargain tier. Simple Tinctures' 10,000mg squeeze-pour concentrate costs $127, which works out to <strong>$0.0127 per mg</strong> &mdash; roughly 60&ndash;90% below typical retail &mdash; because we sell the concentrate only and skip the carrier oil, bottling labor, and ad budget you'd otherwise pay for.</p>
</div>

<h2>Why Cost Per Milligram Is the Only Comparison That's Fair</h2>
<p>A "$60 bottle" tells you nothing: one $60 bottle may hold 500mg while another holds 5,000mg. Divide price by total CBD mg and every product becomes apples-to-apples:</p>
<ul>
<li><strong>$40 &divide; 500mg = $0.080/mg</strong> &mdash; looks cheap, mid-tier value</li>
<li><strong>$120 &divide; 1,000mg = $0.120/mg</strong> &mdash; premium pricing</li>
<li><strong>$127 &divide; 10,000mg = $0.0127/mg</strong> &mdash; concentrate-only pricing</li>
</ul>
<p>Published market guides put the normal range at roughly $0.05&ndash;$0.20 per mg, with bargain grades starting under about $0.077/mg. Independent calculators like LeafReport and CBD Oil Users use these same bands.</p>

<div class="stat-grid">
<div class="stat-card"><div class="stat-num">$0.0127</div><div class="stat-label">Simple Tinctures per mg</div></div>
<div class="stat-card"><div class="stat-num">$0.03&ndash;$0.12</div><div class="stat-label">Typical retail tincture per mg</div></div>
<div class="stat-card"><div class="stat-num">$0.077</div><div class="stat-label">Where "bargain" grading begins</div></div>
<div class="stat-card"><div class="stat-num">~200</div><div class="stat-label">Servings per $127 bottle (at 50mg)</div></div>
</div>

<h2>The Value Table: What $100 Buys You</h2>
<table class="data">
<thead><tr><th>Product type</th><th>Total CBD</th><th>Typical price</th><th>Per mg</th></tr></thead>
<tbody>
<tr><td>Boutique premixed tincture</td><td>500mg</td><td>$50&ndash;$70</td><td>$0.10&ndash;$0.14</td></tr>
<tr><td>Mainstream premixed tincture</td><td>3,000mg</td><td>$90&ndash;$130</td><td>$0.03&ndash;$0.043</td></tr>
<tr><td>Budget direct-to-consumer tincture</td><td>5,000mg</td><td>$80&ndash;$120</td><td>$0.016&ndash;$0.024</td></tr>
<tr class="hl"><td>Simple Tinctures concentrate (you add your own oil)</td><td>10,000mg</td><td>$127</td><td>$0.0127</td></tr>
</tbody>
<tfoot><tr><td colspan="4" style="font-size:.8rem;color:#777;">Retail prices are representative MSRP ranges from published comparison guides; verify current prices before buying. Per-mg math shown so you can check it yourself.</td></tr></tfoot>
</table>

<h2>Why Our Number Is So Low (Honest Version)</h2>
<p>We're not cheaper because we cut quality. We're cheaper because we removed three line items from the bottle:</p>
<ol>
<li><strong>Carrier oil.</strong> A premixed tincture is mostly MCT or hemp seed oil &mdash; an ingredient you can buy at any grocery store for around $8. You pay CBD-extract prices for salad-oil weight.</li>
<li><strong>Premixing, bottling, and boxing.</strong> Glass, droppers, labels, cartons cost roughly the same whether the bottle is weak or strong &mdash; those fixed costs land on fewer milligrams in small bottles.</li>
<li><strong>Customer-acquisition ads.</strong> DTC CBD brands routinely spend $80&ndash;$120 per order acquiring customers. That spend lives inside the sticker price.</li>
</ol>
<p>You do the final mixing step yourself: squeeze one measured ounce (10,000mg) into your own bottle, top with your own MCT oil, shake. Same finished tincture, months of it.</p>

<h2>How to Verify Any Brand's Value Claim in 30 Seconds</h2>
<ol>
<li>Find total CBD in mg on the label (not hemp extract, not hemp oil).</li>
<li>Divide the price by that number.</li>
<li>Compare against the bands: under $0.077/mg is bargain, $0.077&ndash;$0.167 is market, above $0.167 is pricey.</li>
<li>If a batch certificate of analysis (CoA) is available, redo the division using its measured Total CBD figure.</li>
</ol>

<h2>Related Guides</h2>
<ul>
<li><a href="/why-is-cbd-so-expensive.html">Why is CBD so expensive?</a> &mdash; the five cost drivers behind retail prices</li>
<li><a href="/cbd-cost-breakdown.html">CBD cost breakdown</a> &mdash; where every dollar of a $200 bottle actually goes</li>
<li><a href="/cheapest-way-to-buy-cbd.html">Cheapest way to buy CBD</a> &mdash; ranked options from worst value to best</li>
<li><a href="/diy-cbd-tincture-guide.html">DIY tincture guide</a> &mdash; how to mix your own in two minutes</li>
</ul>
{CTA}"""
    },
    [
      ("What does 'best value CBD' mean?", "Best value CBD means the lowest cost per milligram of actual CBD, not the lowest sticker price. Divide a product's price by its total CBD milligrams. Typical retail tinctures run $0.03–$0.12 per mg; Simple Tinctures' 10,000mg concentrate costs $127, or $0.0127 per mg."),
      ("Is cheaper CBD lower quality?", "Not necessarily. Price often reflects marketing spend, packaging, and premixing labor rather than extract quality. Judge quality by third-party batch certificates of analysis (potency, pesticides, heavy metals) and judge price separately with the cost-per-milligram calculation."),
      ("How much CBD do I get per dollar with Simple Tinctures?", "$127 buys 10,000mg of broad-spectrum, 0%-THC CBD concentrate — about 79mg per dollar, or $0.0127 per mg. At a 50mg serving size, that's roughly 200 servings from one bottle."),
      ("Do I need to buy carrier oil separately?", "Yes — that's how the price stays low. You add your own MCT or other food-grade oil (about $8 at any grocery store) to make your finished tincture. The full mixing process takes about two minutes."),
    ])

# ---------------- 2. why-is-cbd-so-expensive ----------------
pages["why-is-cbd-so-expensive.html"] = page(
    "why-is-cbd-so-expensive.html",
    "Why Is CBD So Expensive? 5 Real Reasons (and One Fix) | Simple Tinctures",
    "CBD oil costs $0.03–$0.20+ per mg because of farming, extraction, testing — and mostly advertising. See the real cost drivers and the workaround that skips most of them.",
    {
      "hero": """<h1>Why Is CBD So Expensive?</h1>
<p>Short answer: you're paying for farming, extraction, testing, packaging &mdash; and above all, advertising. Long answer below, with numbers.</p>""",
      "main": f"""
<div class="answer-box">
<p><strong>CBD is expensive because retail prices bundle five costs:</strong> (1) licensed hemp farming, (2) CO2 extraction and refinement, (3) third-party lab testing, (4) packaging, premixing and compliance, and (5) customer acquisition &mdash; which for DTC CBD brands can run $80&ndash;$120 per order due to advertising restrictions. Only the first two are unavoidable. Simple Tinctures removes the last three from what you pay for by selling 10,000mg of concentrate at $127 ($0.0127/mg) that you mix into your own bottle and oil.</p>
</div>

<h2>The 5 Cost Drivers Behind That Price Tag</h2>

<h3>1. Regulated hemp farming</h3>
<p>Hemp must be grown under license with THC kept below the 0.3% federal limit. That means monitored genetics, testing through the grow cycle, and crop destruction risk if a batch runs hot. Farming inputs and compliance are real costs &mdash; but they're also the smallest slice of the retail price.</p>

<h3>2. Extraction and refinement</h3>
<p>Clean CO2 extraction equipment is capital-intensive, and turning crude extract into broad-spectrum distillate adds filtration, remediation, and more lab time. This is the part worth paying for &mdash; it's where potency and purity come from.</p>

<h3>3. Testing and compliance</h3>
<p>Reputable brands test multiple times per batch (potency, pesticides, heavy metals, microbials) and publish certificates of analysis. Labels, state disclosures, and age-gate systems add more. Necessary, and relatively cheap per bottle.</p>

<h3>4. Packaging and premixing labor</h3>
<p>A bottle, cap, dropper, carton, label, and shipping box cost roughly the same whether the oil inside carries 500mg or 15,000mg. On small bottles those fixed costs land on very few milligrams &mdash; one big reason weak bottles look deceptively cheap and strong bottles look shocking.</p>

<h3>5. Customer acquisition (the big one)</h3>
<p>CBD ads are restricted on TV, Google, and major social platforms, so DTC brands pay premium rates for whatever channels remain &mdash; commonly estimated at $80&ndash;$120 in ad spend to acquire a single order. That marketing bill sits inside every retail bottle. It is the largest line item in most DTC CBD cost structures and the one that adds nothing to what's in the bottle.</p>

<h2>Illustrative: Where a $200 Premixed Bottle Goes</h2>
<table class="data">
<thead><tr><th>Cost component</th><th>Estimated share</th></tr></thead>
<tbody>
<tr><td>CBD extract itself</td><td>~$25</td></tr>
<tr><td>Carrier oil (MCT/hemp seed)</td><td>~$8</td></tr>
<tr><td>Bottle, label, box, shipping</td><td>~$14</td></tr>
<tr><td>Farming, extraction, testing (embedded)</td><td>included above</td></tr>
<tr><td>Marketing &amp; customer acquisition</td><td>~$80&ndash;$120</td></tr>
<tr><td>Brand margin</td><td>the remainder</td></tr>
</tbody>
<tfoot><tr><td colspan="2" style="font-size:.8rem;color:#777;">Illustrative breakdown based on typical DTC CBD cost structures discussed across industry sources. No specific competitor's books were reviewed.</td></tr></tfoot>
</table>

<h2>The Fix: Stop Buying the Parts You Don't Need</h2>
<p>You cannot farm hemp or run a CO2 extractor at home. But you absolutely can buy MCT oil for ~$8 and pour liquid into a bottle you already own. When you buy concentrate only:</p>
<ul>
<li>You fund extraction and testing (the parts that matter).</li>
<li>You skip carrier-oil markup, premixing labor, and packaging theater.</li>
<li>You refuse to finance anyone's ad budget.</li>
</ul>
<p>That's how a $0.03&ndash;$0.12/mg retail norm becomes <strong>$0.0127/mg</strong>: same finished tincture, fewer middlemen. See the full arithmetic in our <a href="/cbd-cost-breakdown.html">CBD cost breakdown</a>, or jump straight to the <a href="/index.html#checkout">10,000mg concentrate</a>.</p>
{CTA}"""
    },
    [
      ("Why is CBD oil so expensive compared to other supplements?", "Because retail prices bundle regulated hemp farming, capital-intensive CO2 extraction, repeated third-party lab testing, packaging and compliance — plus heavy customer-acquisition ad spend, often estimated at $80–$120 per DTC order due to advertising restrictions on CBD. Advertising is typically the largest component."),
      ("Does expensive CBD mean better CBD?", "Not reliably. Above the cost of extract, extraction, and testing, higher prices usually buy marketing and packaging, not quality. Verify quality with a batch certificate of analysis and evaluate price independently using cost per milligram."),
      ("What's the cheapest legitimate way to buy CBD?", "Buy high-potency concentrate and mix it yourself. Simple Tinctures sells a 10,000mg squeeze-pour concentrate for $127 ($0.0127/mg); you add your own carrier oil (~$8) and bottle. Finished cost per mg drops 60–90% below typical retail."),
      ("Are cheap CBD products unsafe?", "Suspiciously cheap products can be mislabeled or untested — always require a third-party CoA. But low cost per mg isn't inherently unsafe when the seller publishes batch test results; it usually reflects a leaner business model."),
    ])

# ---------------- 3. cbd-cost-breakdown ----------------
pages["cbd-cost-breakdown.html"] = page(
    "cbd-cost-breakdown.html",
    "CBD Cost Breakdown: Where Every Dollar of Your Tincture Goes | Simple Tinctures",
    "Line-by-line cost breakdown of a typical $200 CBD tincture vs. the concentrate-only model at $0.0127/mg. Interactive-style cost table with honest per-mg math.",
    {
      "hero": """<h1>CBD Cost Breakdown: Every Dollar, Accounted For</h1>
<p>What a $200 premixed bottle actually pays for &mdash; and what happens to the math when you remove the parts you don't need.</p>""",
      "main": f"""
<div class="answer-box">
<p><strong>In a typical ~$200 premixed 10,000mg-class tincture, the CBD extract accounts for only about $25.</strong> The rest is carrier oil (~$8), packaging and shipping (~$14), embedded production/testing costs, and &mdash; the biggest line &mdash; $80&ndash;$120 of marketing and customer acquisition. Buying concentrate only cuts the finished price to $127 per 10,000mg (<strong>$0.0127/mg</strong>) plus your own ~$8 oil.</p>
</div>

<h2>The Cost Table: Premixed vs. Concentrate-Only</h2>
<table class="data">
<thead><tr><th>Line item</th><th>Typical premixed bottle (~$200)</th><th>Simple Tinctures way</th></tr></thead>
<tbody>
<tr><td>CBD extract (10,000mg)</td><td>~$25</td><td>$127 <em>(that's all we sell &mdash; and it includes our margin, testing, and fulfillment)</em></td></tr>
<tr><td>Carrier oil (MCT)</td><td>~$8 (marked up inside the price)</td><td>~$8 &mdash; you buy it once at any grocery store</td></tr>
<tr><td>Bottle, dropper, label, box</td><td>~$6</td><td>$0 &mdash; reuse a bottle you own</td></tr>
<tr><td>Premixing labor</td><td>bundled</td><td>$0 &mdash; two minutes of shaking</td></tr>
<tr><td>Marketing &amp; customer acquisition</td><td>~$80&ndash;$120</td><td>$0 &mdash; no ad budget baked in</td></tr>
<tr><td>Shipping</td><td>~$8&ndash;$10</td><td>$0 &mdash; free shipping included</td></tr>
<tr class="hl"><td><strong>Effective cost per mg CBD</strong></td><td><strong>$0.02&ndash;$0.04+</strong></td><td><strong>$0.0127 (+ ~$0.0008/mg for your oil)</strong></td></tr>
</tbody>
<tfoot><tr><td colspan="3" style="font-size:.8rem;color:#777;">Premixed column is an illustrative reconstruction of typical DTC CBD cost structures from industry reporting; we have not audited any competitor. Our column is verifiable: $127 &divide; 10,000mg.</td></tr></tfoot>
</table>

<h2>Run the Numbers Yourself: Cost-Per-MG Reference Bands</h2>
<p>Independent price trackers grade CBD value in three tiers:</p>
<table class="data">
<thead><tr><th>Grade</th><th>Cost per mg</th><th>What a 1,000mg bottle would cost</th></tr></thead>
<tbody>
<tr class="hl"><td>Bargain</td><td>&lt; $0.077</td><td>&lt; $77 &mdash; ours: <strong>$12.70-equivalent rate</strong></td></tr>
<tr><td>Market average</td><td>$0.077 &ndash; $0.167</td><td>$77 &ndash; $167</td></tr>
<tr><td>Pricey</td><td>&gt; $0.167</td><td>&gt; $167</td></tr>
</tbody>
</table>
<p>At $0.0127/mg, our concentrate prices out at about <strong>six times below the bottom of the bargain band</strong>. That's not a discount &mdash; it's a different cost structure.</p>

<h2>Three Refinements Most Price Guides Skip</h2>
<ol>
<li><strong>Divide by mg, never ml.</strong> Bottle volume says nothing about CBD content; concentration varies up to 50x between bottles of identical size.</li>
<li><strong>Use the CoA, not just the label.</strong> Batch certificates of analysis report measured Total CBD. Dividing price by the verified number is the only lab-checked version of the math.</li>
<li><strong>Count servings you'll actually use.</strong> A bottle is only cheaper per used milligram if you finish it before it ages out.</li>
</ol>

<h2>What $127 Actually Yields</h2>
<div class="stat-grid">
<div class="stat-card"><div class="stat-num">10,000mg</div><div class="stat-label">Total CBD, 0% THC, batch CoA</div></div>
<div class="stat-card"><div class="stat-num">~200</div><div class="stat-label">50mg servings</div></div>
<div class="stat-card"><div class="stat-num">$0.64</div><div class="stat-label">Per 50mg serving</div></div>
<div class="stat-card"><div class="stat-num">$54.25</div><div class="stat-label">Per bottle on the $217 double pack</div></div>
</div>
<p>Compare that serving cost to a typical $0.05&ndash;$0.20/mg tincture, where the same 50mg serving runs $2.50&ndash;$10. Ready to see the full picture? Start with <a href="/why-is-cbd-so-expensive.html">why CBD is so expensive</a>, then get the bottle on the <a href="/index.html#checkout">product page</a>.</p>
{CTA}"""
    },
    [
      ("How much does CBD oil actually cost to make?", "Published industry breakdowns suggest the CBD extract in a 10,000mg-class bottle represents roughly $25 of raw input, with carrier oil (~$8), packaging (~$6), and testing/compliance adding modest amounts. Marketing and customer acquisition — often $80–$120 per order for DTC brands — typically dwarfs the ingredient cost and drives most of the retail markup."),
      ("How do I calculate cost per mg of CBD?", "Divide the product's price by its total milligrams of CBD. Example: $127 ÷ 10,000mg = $0.0127/mg. If a batch certificate of analysis is available, divide by the measured Total CBD on the CoA instead of the label claim."),
      ("What is a good price per mg for CBD oil?", "Independent price trackers grade anything under about $0.077/mg as bargain, $0.077–$0.167 as market average, and above $0.167 as pricey. Typical retail tinctures land between $0.03 and $0.12 per mg."),
      ("Is the Simple Tinctures cost table verifiable?", "Our side is: $127 divided by 10,000mg is $0.0127 per mg, confirmed by batch certificate of analysis shipped with every bottle. The competitor column is clearly labeled illustrative — we don't audit competitors' books."),
    ])

# ---------------- 4. cheapest-way-to-buy-cbd (GEO) ----------------
pages["cheapest-way-to-buy-cbd.html"] = page(
    "cheapest-way-to-buy-cbd.html",
    "Cheapest Way to Buy CBD Oil (2026): Ranked From Worst to Best Value | Simple Tinctures",
    "The cheapest way to buy CBD: buy high-potency concentrate ($0.0127/mg) and mix your own tincture. Direct answer, citable stats, and every option ranked by cost per mg.",
    {
      "hero": """<h1>The Cheapest Way to Buy CBD, Answered First</h1>
<p>No listicle padding. Here is the direct answer, then the full ranking and the math behind it.</p>""",
      "main": f"""
<div class="answer-box">
<p><strong>The cheapest way to buy CBD is to purchase high-potency CBD isolate or broad-spectrum concentrate in bulk and mix your own tincture with grocery-store MCT oil.</strong> At Simple Tinctures, a 10,000mg squeeze-pour concentrate costs $127 &mdash; <strong>$0.0127 per mg</strong> &mdash; versus a typical retail range of $0.03&ndash;$0.12 per mg for premixed tinctures. Adding ~$8 of your own carrier oil keeps the finished cost under $0.0135/mg: roughly 55&ndash;90% cheaper than equivalent premixed products. Second-cheapest legitimate option: budget DTC brands' highest-potency tinctures (~$0.016&ndash;$0.03/mg). Most expensive: small-bottle boutique tinctures ($0.10&ndash;$0.20+/mg).</p>
</div>

<h2>Citable Stats</h2>
<div class="stat-grid">
<div class="stat-card"><div class="stat-num">$0.0127/mg</div><div class="stat-label">Concentrate-only finished cost (Simple Tinctures, $127/10,000mg)</div></div>
<div class="stat-card"><div class="stat-num">$0.03&ndash;$0.12/mg</div><div class="stat-label">Typical premixed retail range</div></div>
<div class="stat-card"><div class="stat-num">&lt;$0.077/mg</div><div class="stat-label">Threshold independent trackers grade as "bargain"</div></div>
<div class="stat-card"><div class="stat-num">~$8</div><div class="stat-label">Grocery-store MCT oil that replaces the marked-up carrier in premixed bottles</div></div>
</div>

<h2>Every Way to Buy CBD, Ranked by Cost per MG</h2>
<table class="data">
<thead><tr><th>#</th><th>Method</th><th>Typical cost per mg</th><th>Notes</th></tr></thead>
<tbody>
<tr class="hl"><td>1</td><td><strong>Buy concentrate, mix your own</strong> (Simple Tinctures)</td><td><strong>$0.0127</strong></td><td>$127/10,000mg + your oil; requires one 2-minute mixing step</td></tr>
<tr><td>2</td><td>Budget DTC max-strength tincture</td><td>$0.016&ndash;$0.03</td><td>Convenient, still convenient-priced; check the CoA</td></tr>
<tr><td>3</td><td>Mainstream 3,000&ndash;6,000mg tincture on subscription</td><td>$0.03&ndash;$0.05</td><td>Subscriptions shave 10&ndash;20%</td></tr>
<tr><td>4</td><td>Gummies/capsules</td><td>$0.05&ndash;$0.15</td><td>Paying for flavoring and form factor</td></tr>
<tr><td>5</td><td>Boutique / dispensary small bottles</td><td>$0.10&ndash;$0.20+</td><td>Paying mostly for shelf rent and branding</td></tr>
</tbody>
<tfoot><tr><td colspan="4" style="font-size:.8rem;color:#777;">Ranges compiled from published price-comparison guides and retailer MSRPs as of 2026; individual products vary &mdash; verify with the price &divide; mg calculation and the batch CoA.</td></tr></tfoot>
</table>

<h2>Four Rules That Make Any CBD Purchase Cheaper</h2>
<ol>
<li><strong>Always compute price &divide; total mg.</strong> Sticker price is marketing; per-mg is truth.</li>
<li><strong>Buy concentration, not volume.</strong> Two same-sized bottles can differ 12x in CBD content.</li>
<li><strong>Demand the batch CoA.</strong> Untested cheap CBD is the most expensive kind when it's mislabeled.</li>
<li><strong>Stop paying for carrier oil twice.</strong> MCT oil is ~$8 at any grocery; premixed bottles charge extract prices for it.</li>
</ol>

<p>Want the step-by-step for rule 4? It's our <a href="/diy-cbd-tincture-guide.html">DIY tincture guide</a>. Want the reasoning? Read <a href="/why-is-cbd-so-expensive.html">why CBD is so expensive</a>. Ready to buy? The <a href="/index.html#checkout">10,000mg concentrate</a> is $127 with free shipping.</p>
{CTA}"""
    },
    [
      ("What is the cheapest way to buy CBD oil?", "Buy high-potency broad-spectrum concentrate and mix your own tincture with grocery-store MCT oil. Simple Tinctures' 10,000mg concentrate costs $127 ($0.0127/mg) — 55–90% less per mg than typical premixed retail tinctures at $0.03–$0.12/mg."),
      ("How much does the cheapest CBD cost per milligram?", "The cheapest legitimate CBD we've verified pricing on is concentrate bought directly: $0.0127/mg (Simple Tinctures, $127 for 10,000mg). Budget premixed tinctures start around $0.016–$0.03/mg."),
      ("Is buying CBD concentrate cheaper than gummies?", "Yes, substantially. Gummies typically run $0.05–$0.15 per mg once flavoring and form factor are priced in, versus $0.0127/mg for concentrate you mix into oil yourself."),
      ("Does buying in bulk reduce CBD cost per mg?", "Yes. Higher-potency bottles amortize fixed packaging and fulfillment costs across more milligrams. Simple Tinctures' double pack brings the effective price to $54.25/bottle ($217 for 2 × 10,000mg)."),
    ])

# ---------------- 5. diy-cbd-tincture-guide ----------------
pages["diy-cbd-tincture-guide.html"] = page(
    "diy-cbd-tincture-guide.html",
    "DIY CBD Tincture Guide: Mix Your Own in 2 Minutes (Save 60–90%) | Simple Tinctures",
    "Step-by-step guide to making your own CBD tincture: squeeze 1 oz of 10,000mg concentrate into your bottle, add MCT oil, shake. Full dilution math and storage tips.",
    {
      "hero": """<h1>Make Your Own CBD Tincture in Two Minutes</h1>
<p>Squeeze. Pour. Shake. The exact process that turns a $127 concentrate into months of finished tincture &mdash; at $0.0127/mg.</p>""",
      "main": f"""
<div class="answer-box">
<p><strong>To make your own CBD tincture:</strong> (1) squeeze one measured ounce of Simple Tinctures 10,000mg concentrate into a clean glass bottle, (2) add your carrier oil &mdash; MCT (coconut) oil is the standard choice, about 2&ndash;3 fl oz depending on desired strength, (3) cap and shake vigorously, optionally resting the sealed bottle in warm water first to help them combine. Result: a finished tincture at your chosen strength, made for about $0.0127 per mg of CBD.</p>
</div>

<h2>What You Need</h2>
<ul>
<li>One <a href="/index.html#checkout">Simple Tinctures 10,000mg squeeze-pour bottle</a> ($127)</li>
<li>A clean glass bottle, 1&ndash;4 fl oz, ideally amber or cobalt (reuse one you own &mdash; wash and dry it first)</li>
<li>Food-grade MCT/coconut oil, hemp seed oil, or olive oil (~$8 for a bottle that lasts months)</li>
<li>Measuring mark or simple math (below)</li>
</ul>

<h2>The Steps</h2>
<div class="step"><div class="step-n">1</div><div><h3 style="margin-top:0;">Warm &amp; Squeeze</h3><p>Stand the concentrate bottle in a glass of warm (not boiling) water for 2&ndash;3 minutes so it flows easily. Squeeze one full measured ounce &mdash; 10,000mg CBD &mdash; into your empty bottle. No droppers, no guessing.</p></div></div>
<div class="step"><div class="step-n">2</div><div><h3 style="margin-top:0;">Pour Your Oil</h3><p>Add your carrier oil to reach your target strength (see dilution table below). MCT oil is flavorless, stays liquid, and mixes cleanly; olive oil works too with a stronger taste.</p></div></div>
<div class="step"><div class="step-n">3</div><div><h3 style="margin-top:0;">Shake &amp; Store</h3><p>Cap tightly and shake hard for 30 seconds. Re-shake before each use &mdash; oil and extract naturally separate. Store away from heat and light; a cupboard is fine, refrigeration optional.</p></div></div>

<h2>Dilution Math: Pick Your Strength</h2>
<table class="data">
<thead><tr><th>Add carrier oil to 1 oz (10,000mg) concentrate</th><th>Finished strength</th><th>Per-drop estimate*</th></tr></thead>
<tbody>
<tr><td>+ 1 fl oz (total 2 fl oz / ~1,180 drops)</td><td>~8.5mg per drop</td><td>high strength</td></tr>
<tr><td>+ 2 fl oz (total 3 fl oz / ~1,770 drops)</td><td>~5.7mg per drop</td><td>medium</td></tr>
<tr><td>+ 3 fl oz (total 4 fl oz / ~2,360 drops)</td><td>~4.2mg per drop</td><td>gentle</td></tr>
</tbody>
<tfoot><tr><td colspan="3" style="font-size:.8rem;color:#777;">*Standard 1ml droppers hold ~20 drops. Estimates only &mdash; your dropper may differ; count drops into a teaspoon once to calibrate. These figures describe product concentration, not dosing advice.</td></tr></tfoot>
</table>

<h2>Cost Check</h2>
<p>Your finished bottle contains 10,000mg of CBD. Concentrate: $127 &rarr; $0.0127/mg. Add ~$8 of oil spread over the same milligrams and the true finished cost is still under <strong>$0.0135/mg</strong>. An equivalent premixed 10,000mg-class tincture typically retails for $180&ndash;$240+. The two minutes of shaking is where the savings live.</p>

<h2>Practical Notes</h2>
<ul>
<li><strong>Shelf life:</strong> finished tincture is generally best within 12 months; MCT-based mixes hold well refrigerated or in a cool cupboard.</li>
<li><strong>Label your bottle</strong> with the strength you mixed so nobody guesses.</li>
<li><strong>Start low, go slow:</strong> begin with a small amount and adjust over days. We make no health claims and recommend discussing any supplement with your physician, especially alongside medication.</li>
<li><strong>Keep the concentrate bottle:</strong> it doubles as a precise dispenser if you prefer to dose straight from it without diluting.</li>
</ul>
<p>For the economics behind this method, see the <a href="/cbd-cost-breakdown.html">cost breakdown</a> or the pillar guide to <a href="/best-value-cbd.html">best value CBD</a>.</p>
{CTA}"""
    },
    [
      ("How do I make my own CBD tincture at home?", "Squeeze one measured ounce (10,000mg) of Simple Tinctures concentrate into a clean glass bottle, add 1–3 fluid ounces of MCT or other food-grade oil for your target strength, cap, and shake for 30 seconds. Warm the concentrate bottle in water first so it pours easily. Total time: about two minutes."),
      ("What carrier oil should I use for DIY CBD tincture?", "MCT (fractionated coconut) oil is the standard choice: flavorless, stays liquid, and mixes cleanly. Hemp seed oil and olive oil also work. All cost around $8 at grocery stores — a fraction of what premixed brands effectively charge for the same ingredient."),
      ("What strength should I mix my DIY tincture at?", "Adding 2 fl oz of carrier oil to 1 oz of 10,000mg concentrate yields roughly 5.7mg per drop with a standard 1ml dropper. Adjust the oil amount for stronger or gentler mixes — the dilution table on this page shows all three options. Concentration figures are not dosing advice."),
      ("How long does homemade CBD tincture last?", "Generally about 12 months when stored away from heat and light in a sealed bottle. Shake before each use, as oil and extract naturally separate."),
    ])

# ---------------- 6. faq ----------------
pages["faq.html"] = page(
    "faq.html",
    "Simple Tinctures FAQ: Pricing, Potency, Mixing, Shipping | Simple Tinctures",
    "Answers about the 10,000mg squeeze-pour CBD concentrate: what's in the bottle, how mixing works, cost per mg, lab testing, shipping, and the 18+ policy.",
    {
      "hero": """<h1>Frequently Asked Questions</h1>
<p>Everything about the 10,000mg squeeze-pour concentrate &mdash; pricing, potency, mixing, testing, and shipping.</p>""",
      "main": """
<h2>The Product</h2>

<div class="faq-item"><div class="faq-q">What exactly am I buying?</div><div class="faq-a">A one-ounce squeeze-pour bottle containing 10,000mg of broad-spectrum, 0%-THC hemp-derived CBD concentrate. It is the concentrated part of a tincture &mdash; not premixed with carrier oil. You add your own oil at home (see the <a href="/diy-cbd-tincture-guide.html">DIY guide</a>), which is why it costs $0.0127/mg instead of retail's usual $0.03&ndash;$0.12/mg.</div></div>

<div class="faq-item"><div class="faq-q">Why is it so much cheaper than other CBD?</div><div class="faq-a">We removed carrier oil, premixing labor, fancy packaging, and ad-spend markup from what you pay for. The math is public: $127 &divide; 10,000mg = $0.0127/mg. Details in the <a href="/cbd-cost-breakdown.html">cost breakdown</a>.</div></div>

<div class="faq-item"><div class="faq-q">How much does it cost?</div><div class="faq-a">$127 for one bottle (10,000mg, ~200 fifty-mg servings). Double pack: $217 ($54.25/bottle). Monthly refill: $107/mo, cancel anytime. Free shipping on all orders.</div></div>

<h2>Mixing &amp; Use</h2>

<div class="faq-item"><div class="faq-q">Do I have to mix it, or can I take it straight?</div><div class="faq-a">You can use it either way. Many customers dilute it into their own bottle of MCT oil for a classic tincture (two minutes &mdash; steps in the <a href="/diy-cbd-tincture-guide.html">guide</a>); others dispense the concentrate directly since it's already a liquid. The choice doesn't change the CBD content per drop.</div></div>

<div class="faq-item"><div class="faq-q">What oil should I mix it with?</div><div class="faq-a">MCT (fractionated coconut) oil is the classic &mdash; flavorless and always liquid. Hemp seed or olive oil work too. Expect to spend about $8 at any grocery store, once.</div></div>

<div class="faq-item"><div class="faq-q">How many servings does one bottle make?</div><div class="faq-a">About 200 servings at 50mg each, whether diluted or taken straight. Diluted into a 3-fl-oz finished bottle, that's roughly 5.7mg per drop with a standard 1ml dropper.</div></div>

<h2>Quality &amp; Safety</h2>

<div class="faq-item"><div class="faq-q">Is it tested?</div><div class="faq-a">Every batch is third-party tested for potency, pesticides, heavy metals, and microbials. A batch Certificate of Analysis ships with every bottle, and the concentrate contains 0% THC.</div></div>

<div class="faq-item"><div class="faq-q">Will it get me high? Does it contain THC?</div><div class="faq-a">No. It is broad-spectrum hemp-derived CBD with 0% THC, confirmed on the batch CoA. Hemp-derived CBD with no detectable THC is federally compliant under the 2018 Farm Bill.</div></div>

<div class="faq-item"><div class="faq-q">Any medical claims?</div><div class="faq-a">None. We sell a hemp-derived consumable and publish its price and lab results. These statements have not been evaluated by the FDA and nothing on this site is intended to diagnose, treat, cure, or prevent any disease. Talk to your physician before combining any supplement with medication.</div></div>

<h2>Orders &amp; Policies</h2>

<div class="faq-item"><div class="faq-q">Who can buy?</div><div class="faq-a">Adults 18 and older. Age verification is required at checkout.</div></div>

<div class="faq-item"><div class="faq-q">How does shipping work?</div><div class="faq-a">Free shipping on every order within the US, dispatched promptly with tracking. Checkout is handled securely via Google Pay through Stripe; your card details never touch our servers.</div></div>

<div class="faq-item"><div class="faq-q">Can I cancel a subscription?</div><div class="faq-a">Yes &mdash; the monthly refill cancels anytime from your account or by emailing support. No lock-in.</div></div>

<p>Ready when you are: <a href="/index.html#checkout">get the 10,000mg bottle here</a>. Still comparing? Start with <a href="/cheapest-way-to-buy-cbd.html">the cheapest way to buy CBD</a>.</p>"""
    },
    [
      ("What comes in the Simple Tinctures bottle?", "One ounce of broad-spectrum, 0%-THC hemp-derived CBD concentrate measuring 10,000mg total, with a batch Certificate of Analysis included. Carrier oil is intentionally excluded — you add your own MCT or other food-grade oil at home."),
      ("How much does Simple Tinctures cost per mg?", "$127 for 10,000mg equals $0.0127 per mg. The double pack reduces it further to $54.25 per bottle ($108.50 per 10,000mg, about $0.0109/mg)."),
      ("How do I turn the concentrate into a tincture?", "Squeeze the measured ounce into a clean glass bottle, add 1–3 fl oz of MCT oil for your preferred strength, cap and shake 30 seconds. Full instructions are in our DIY tincture guide; takes about two minutes."),
      ("Is Simple Tinctures lab tested and THC-free?", "Yes. Each batch is third-party tested for potency, pesticides, heavy metals, and microbials, and the batch CoA ships with every bottle. THC content is 0%."),
      ("Do you need to be 18 to buy?", "Yes. Purchases are restricted to adults 18 and older, verified at checkout."),
      ("Is there free shipping?", "Yes — free US shipping on all orders, including single bottles, double packs, and monthly refills."),
    ])

os.makedirs(SITE, exist_ok=True)
for fname, html in pages.items():
    with open(os.path.join(SITE, fname), "w") as f:
        f.write(html)
    words = len(html.split())
    print(f"{fname}: written, ~{words} words")
