#!/usr/bin/env python3
"""Regenerate the static site from offers.json.

Usage:  python3 scripts/build.py
Writes index.html, category pages, legal pages, 404.html, sitemap.xml, robots.txt.
No dependencies beyond the Python 3 standard library. Commit the output.
"""
import json, os, sys, html
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://dailyclaimit.com"
CLARITY = "x6fjwt28zp"
CATS = {
    "sweepstakes": ("Sweepstakes", "💰", "Free-to-enter giveaways and cash sweepstakes from our partners."),
    "surveys-quizzes": ("Surveys & Quizzes", "📝", "Paid surveys, quizzes and reward apps that pay in cash or gift cards."),
    "free-stuff": ("Free Stuff", "🎁", "Free samples, product testing and freebie offers."),
}
SWEEPS_NOTE = "No purchase necessary. See official rules on offer page."
REQUIRED = ["id", "title", "category", "description", "cta", "url", "network", "active", "added"]
e = lambda s: html.escape(str(s or ""), quote=True)


def load_offers():
    with open(os.path.join(ROOT, "offers.json"), encoding="utf-8") as f:
        data = json.load(f)
    offers, ids, s1s = data["offers"], set(), set()
    for o in offers:
        missing = [k for k in REQUIRED if k not in o]
        if missing: sys.exit(f"offer {o.get('id')} missing {missing}")
        if o["category"] not in CATS: sys.exit(f"offer {o['id']} bad category {o['category']}")
        if o["id"] in ids: sys.exit(f"duplicate id {o['id']}")
        ids.add(o["id"])
        s1 = [p[3:] for p in o["url"].split("?", 1)[-1].split("&") if p.startswith("s1=")]
        if not s1: sys.exit(f"offer {o['id']} url has no s1 subID")
        if s1[0] in s1s: sys.exit(f"duplicate s1 {s1[0]}")
        s1s.add(s1[0])
    return [o for o in offers if o["active"]]


def card(o):
    label, icon, _ = CATS[o["category"]]
    c = e(o["category"])
    out = (f'<div class="offer-card" data-offer-id="{e(o["id"])}">'
           f'<div class="card-visual card-visual-{c}">{icon}<div class="card-tag tag-{c}">{e(label)}</div></div>'
           f'<div class="card-body"><h3 class="card-title">{e(o["title"])}</h3>')
    if o.get("payout_note"): out += f'<div class="card-payout">{e(o["payout_note"])}</div>'
    out += (f'<div class="card-desc">{e(o["description"])}</div>'
            f'<a href="{e(o["url"])}" class="card-cta cta-{c}" rel="sponsored noopener" target="_blank">{e(o["cta"])} →</a>')
    if o["category"] == "sweepstakes": out += f'<p class="card-legal">{SWEEPS_NOTE}</p>'
    out += '</div><div class="card-foot">Sponsored offer · See provider terms</div></div>'
    return out


AFF_NOTE = ('<p class="aff-note"><strong>Disclosure:</strong> Offers below are from affiliate partners. '
            'We may earn a commission when you complete an offer, at no cost to you. '
            '<a href="/disclosure/">Learn more</a>.</p>')


def grid(items, category=None, limit=0):
    attrs = f' data-category="{category}"' if category else ""
    if limit: attrs += f' data-limit="{limit}"'
    inner = "".join(card(o) for o in items) or '<p class="empty-note">No open offers in this category right now. Check back soon.</p>'
    return f'<div class="offer-grid" data-offers{attrs}>{inner}</div>'


def email_block(source):
    return f'''
  <section class="email-capture" id="daily-drop">
    <div class="email-capture-inner">
      <div class="email-capture-eyebrow">✉️ The Daily Drop</div>
      <h2>Get new <span>freebies &amp;&nbsp;giveaways</span> in your inbox</h2>
      <p class="email-capture-sub">We email a hand-picked freebie, giveaway, or reward offer. Free to join, unsubscribe any time.</p>
      <form class="email-form" id="email-form" data-source="{source}" novalidate>
        <label for="email-input" class="sr-only">Email address</label>
        <input type="email" id="email-input" name="email" placeholder="your@email.com" autocomplete="email" required />
        <button type="submit" id="email-submit-btn">Send Me Freebies →</button>
      </form>
      <div class="email-error" id="email-error" role="alert">Please enter a valid email address.</div>
      <div class="email-confirm" id="email-confirm" role="status">
        <span class="email-confirm-icon">✓</span><span>Thanks! Check your inbox.</span>
      </div>
      <p class="email-consent">By subscribing you agree to receive emails from DailyClaimIt, which may include sponsored offers. See our <a href="/privacy/">Privacy Policy</a>. Unsubscribe any time.</p>
    </div>
  </section>'''


def page(path, title, desc, body, current=None, noindex=False):
    canonical = SITE + path
    nav = "".join(
        f'<a class="nl" href="/{k}/"{" aria-current=\"page\"" if current == k else ""}>{e(v[0])}</a>'
        for k, v in CATS.items())
    robots = '\n  <meta name="robots" content="noindex" />' if noindex else ""
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{e(title)}</title>
  <meta name="description" content="{e(desc)}" />{robots}
  <link rel="canonical" href="{canonical}" />
  <meta property="og:site_name" content="DailyClaimIt" />
  <meta property="og:title" content="{e(title)}" />
  <meta property="og:description" content="{e(desc)}" />
  <meta property="og:type" content="website" />
  <meta property="og:url" content="{canonical}" />
  <meta name="twitter:card" content="summary" />
  <meta name="theme-color" content="#F7F5F0" />
  <script defer src="https://www.clarity.ms/tag/{CLARITY}"></script>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link rel="preload" as="style" href="https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=Inter:wght@400;500;600&display=swap" onload="this.onload=null;this.rel='stylesheet'" />
  <noscript><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=Inter:wght@400;500;600&display=swap" /></noscript>
  <link rel="stylesheet" href="/assets/site.css" />
</head>
<body>
  <nav>
    <a href="/" class="nav-logo">daily<span>claim</span>it</a>
    <div class="nav-links">{nav}<a href="/#offers" class="nav-pill"><span class="nav-dot"></span>Today's Offers</a></div>
  </nav>
{body}
  <footer>
    <div class="footer-logo">daily<span>claim</span>it</div>
    <p>
      <a href="/sweepstakes/">Sweepstakes</a> &nbsp;|&nbsp; <a href="/surveys-quizzes/">Surveys &amp; Quizzes</a> &nbsp;|&nbsp; <a href="/free-stuff/">Free Stuff</a>
    </p>
    <p>
      <a href="/disclosure/">Affiliate Disclosure</a> &nbsp;|&nbsp;
      <a href="/privacy/">Privacy Policy</a> &nbsp;|&nbsp;
      <a href="/terms/">Terms</a> &nbsp;|&nbsp;
      <a href="mailto:contact@dailyclaimit.com">Contact</a>
    </p>
    <p style="margin-top:8px;">© {date.today().year} DailyClaimIt &nbsp;·&nbsp; DailyClaimIt lists third-party offers and may earn a commission when you complete them. We are not the sponsor of any sweepstakes or offer. See individual offer terms for full details.</p>
  </footer>
  <script src="/assets/site.js" defer></script>
</body>
</html>
'''


def home(offers):
    featured = [o for o in offers if o.get("featured")] or offers
    cats = "".join(
        f'<a class="cat-card" href="/{k}/"><div class="ci">{v[1]}</div><h3>{e(v[0])}</h3>'
        f'<p>{e(v[2])}</p></a>' for k, v in CATS.items())
    body = f'''
  <section class="hero">
    <div class="hero-text">
      <div class="hero-kicker"><span class="kicker-icon">🎁</span>Offers reviewed &amp; updated regularly</div>
      <h1>Your daily<br><span class="accent">rewards</span><br><span class="accent-green">drop.</span></h1>
      <p class="hero-body">Sweepstakes, paid surveys and quizzes, and free stuff — collected in one place. Every listing links to the partner's own page and terms.</p>
      <div class="hero-actions">
        <a href="#offers" class="btn-primary">Browse Today's Offers →</a>
        <a href="#categories" class="btn-ghost">Browse categories ↓</a>
      </div>
    </div>
    <div class="hero-visual">
      <div class="stat-ring">
        <div class="stat-ring-inner">
          <div class="stat-number">$0</div>
          <div class="stat-label">to use DailyClaimIt</div>
        </div>
      </div>
      <div class="float-badge badge-a"><span class="badge-dot" style="background:var(--green)"></span>Free to join</div>
      <div class="float-badge badge-b">🎁 Giveaways &amp; freebies</div>
      <div class="float-badge badge-c"><span class="badge-dot" style="background:var(--gold)"></span>Offers vetted daily</div>
    </div>
  </section>

  <section class="offers" id="offers">
    <div class="offers-header">
      <div>
        <div class="section-label">Featured</div>
        <h2 class="offers-title">Today's <span>featured</span> offers</h2>
      </div>
      <div class="offers-meta">Sponsored · Availability varies</div>
    </div>
    {AFF_NOTE}
    {grid(featured, limit=6)}
  </section>

  <section class="how" id="categories">
    <div class="how-inner">
      <div class="section-label">Browse by category</div>
      <div class="cat-grid">{cats}</div>
    </div>
  </section>
{email_block("homepage")}

  <section class="how" id="how">
    <div class="how-inner">
      <div class="section-label">How DailyClaimIt works</div>
      <div class="how-steps">
        <div class="how-step"><div class="step-num">01</div><div class="step-title">Browse open offers</div><div class="step-body">We list active sweepstakes, survey and quiz rewards, and freebie offers from partner networks.</div></div>
        <div class="how-step"><div class="step-num">02</div><div class="step-title">Read the partner's terms</div><div class="step-body">Each offer opens on the partner's site. Eligibility, requirements and official rules are set by them.</div></div>
        <div class="how-step"><div class="step-num">03</div><div class="step-title">Complete the offer</div><div class="step-body">Follow the offer instructions. Rewards are provided by the offer sponsor, not DailyClaimIt.</div></div>
      </div>
    </div>
  </section>

  <div class="trust-strip">
    <div class="trust-inner">
      <div class="trust-item"><div class="trust-icon">🆓</div><span>Free to join</span></div>
      <div class="trust-item"><div class="trust-icon">✅</div><span>Offers vetted daily</span></div>
      <div class="trust-item"><div class="trust-icon">🔗</div><span>Links go to official partner pages</span></div>
      <div class="trust-item"><div class="trust-icon"><svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true" fill="none" stroke="#A8832A" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="9"/><path d="M12 11v6M12 7.5v.01"/></svg></div><span><a href="/disclosure/" style="color:inherit">Affiliate relationships disclosed</a></span></div>
    </div>
  </div>
'''
    return page("/", "DailyClaimIt — Sweepstakes, Paid Surveys & Free Stuff",
                "Browse free-to-enter sweepstakes, paid surveys and quizzes, and free stuff offers in one place. Free to use; offers are from affiliate partners.",
                body)


def category(slug, offers):
    label, icon, blurb = CATS[slug]
    items = [o for o in offers if o["category"] == slug]
    extra = (f'<p class="aff-note">{SWEEPS_NOTE} Sweepstakes are run by their sponsors; odds, eligibility and prizes are set in each sponsor\'s official rules.</p>'
             if slug == "sweepstakes" else "")
    body = f'''
  <header class="page-head">
    <div class="section-label">{icon} Category</div>
    <h1>{e(label)}</h1>
    <p>{e(blurb)} Every listing opens the partner's own page, where their terms apply.</p>
  </header>
  <section class="offers" style="padding-top:32px">
    {AFF_NOTE}
    {extra}
    {grid(items, category=slug)}
  </section>
{email_block(slug)}
'''
    titles = {
        "sweepstakes": ("Free Sweepstakes & Giveaways to Enter | DailyClaimIt",
                        "Enter free sweepstakes and cash giveaways from our partners. No purchase necessary; see official rules on each offer page."),
        "surveys-quizzes": ("Paid Surveys & Quizzes for Cash and Gift Cards | DailyClaimIt",
                            "Find paid surveys, quizzes and reward apps that pay in cash or gift cards. Requirements vary by offer."),
        "free-stuff": ("Free Stuff, Samples & Product Testing Offers | DailyClaimIt",
                       "Free samples, product testing and freebie offers from our partners. Availability and eligibility vary."),
    }
    t, d = titles[slug]
    return page(f"/{slug}/", t, d, body, current=slug)





def legal(path, title, desc, h1, content):
    body = f'''
  <main class="prose">
    <h1>{h1}</h1>
    <p class="updated">Last updated: {date.today().strftime("%B %-d, %Y")}</p>
    {content}
  </main>
'''
    return page(path, title, desc, body)


DISCLOSURE = '''
<p><strong>DailyClaimIt is an affiliate site.</strong> We earn commissions when users complete offers listed on this site. In plain terms: if you click an offer and then sign up, enter, complete a survey, or take another qualifying action, the advertiser (through an affiliate network such as MaxBounty or Glitchy) may pay us. This costs you nothing extra.</p>
<h2>How this affects what you see</h2>
<p>Every offer on DailyClaimIt is a sponsored/affiliate link, and links are marked as sponsored. Compensation may influence which offers we list and where they appear. We try to list only offers that look legitimate and clearly explain their requirements, but we do not guarantee any offer, prize, or reward.</p>
<h2>Who provides the offer</h2>
<p>Offers, sweepstakes, surveys and free products are provided by third-party advertisers, not by DailyClaimIt. Each offer's eligibility rules, official rules, privacy policy and terms are set by the advertiser and shown on their page. Sweepstakes: no purchase necessary; see official rules on the offer page.</p>
<h2>Questions</h2>
<p>Contact us at <a href="mailto:contact@dailyclaimit.com">contact@dailyclaimit.com</a>.</p>
<p>This disclosure is provided in line with the U.S. Federal Trade Commission's Endorsement Guides (16 CFR Part 255).</p>
'''

PRIVACY = '''
<p>This policy explains what information DailyClaimIt ("we", "us") collects on dailyclaimit.com and how it is used.</p>
<h2>Information we collect</h2>
<ul>
<li><strong>Email address</strong> — only if you subscribe to our email list. It is sent to and stored in a Google Sheet via Google Apps Script, with the time and the page you signed up from.</li>
<li><strong>Usage data</strong> — we use Microsoft Clarity to understand how visitors use the site. Clarity collects device and browser information, pages viewed, clicks, scrolls and session recordings, and uses cookies or similar technology. See the <a href="https://privacy.microsoft.com/privacystatement" rel="noopener" target="_blank">Microsoft Privacy Statement</a>.</li>
<li><strong>Hosting and security data</strong> — our hosting and CDN providers (GitHub Pages and Cloudflare) may process IP addresses and request logs to deliver and protect the site.</li>
</ul>
<h2>Affiliate partners</h2>
<p>Offers on this site are affiliate links through networks such as MaxBounty and Glitchy. When you click an offer you leave DailyClaimIt; the network and advertiser may set cookies and record your click (including a tracking ID that tells them the click came from us). Any information you submit on an advertiser's page is governed by <em>their</em> privacy policy, not ours. We do not receive the personal information you give to advertisers; we may receive aggregated reports of clicks and completed offers.</p>
<h2>How we use information</h2>
<ul><li>To send the emails you signed up for, which may include sponsored offers.</li><li>To understand and improve the site.</li><li>To track affiliate performance.</li></ul>
<h2>Sharing</h2>
<p><strong>We never sell or share your email address.</strong> It is stored only with the service provider we use to run our email list (Google) and is not given to advertisers or affiliate partners. Affiliate partners and advertisers receive personal information only if you submit it yourself on their offer page. We may disclose information where required by law.</p>
<h2>Your choices</h2>
<p>You can unsubscribe from emails at any time using the link in any email or by writing to us. You can ask us to delete your email address by contacting <a href="mailto:contact@dailyclaimit.com">contact@dailyclaimit.com</a>. You can block cookies in your browser settings. Depending on where you live (for example California or the EU/UK), you may have additional rights to access, correct or delete your data.</p>
<h2>Children</h2>
<p>This site is not directed to children under 13 (and many offers require users to be 18+). We do not knowingly collect information from children.</p>
<h2>Changes</h2>
<p>We may update this policy; the date above shows the latest version.</p>
<h2>Contact</h2>
<p><a href="mailto:contact@dailyclaimit.com">contact@dailyclaimit.com</a></p>
'''

TERMS = '''
<p>By using dailyclaimit.com (the "Site") you agree to these terms.</p>
<h2>What the Site is</h2>
<p>DailyClaimIt is a directory of third-party offers, including sweepstakes, paid surveys and quizzes, and free product offers. We do not run, sponsor, or fulfill any of the offers listed. We earn commissions from affiliate partners when users complete offers (see our <a href="/disclosure/">Affiliate Disclosure</a>).</p>
<h2>Third-party offers</h2>
<p>Each offer is provided by a third-party advertiser and is subject to that advertiser's own terms, official rules, eligibility requirements and privacy policy. Offers may change, end, or be unavailable in your area without notice. Prizes, rewards and products are the responsibility of the advertiser. Sweepstakes: no purchase necessary; see official rules on the offer page.</p>
<h2>No guarantees</h2>
<p>The Site is provided "as is". We do not guarantee that any offer is available, accurate, or that you will qualify for or receive any reward. Information on the Site is for general informational purposes only.</p>
<h2>Limitation of liability</h2>
<p>To the fullest extent permitted by law, DailyClaimIt is not liable for any loss or damage arising from your use of the Site or of any third-party offer.</p>
<h2>Email list</h2>
<p>If you subscribe, you agree to receive emails that may include sponsored offers. You can unsubscribe at any time.</p>
<h2>Eligibility</h2>
<p>Many offers are limited to U.S. residents aged 18 or older. You are responsible for checking each offer's eligibility.</p>
<h2>Changes</h2>
<p>We may update these terms at any time. Continued use of the Site means you accept the updated terms.</p>
<h2>Contact</h2>
<p><a href="mailto:contact@dailyclaimit.com">contact@dailyclaimit.com</a></p>
'''


def write(rel, content):
    p = os.path.join(ROOT, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f: f.write(content)
    print("wrote", rel)


def main():
    offers = load_offers()
    write("index.html", home(offers))
    for slug in CATS: write(f"{slug}/index.html", category(slug, offers))
    write("disclosure/index.html", legal("/disclosure/", "Affiliate Disclosure | DailyClaimIt",
          "DailyClaimIt earns commissions when users complete offers listed on the site. Read our FTC affiliate disclosure.",
          "Affiliate Disclosure", DISCLOSURE))
    write("privacy/index.html", legal("/privacy/", "Privacy Policy | DailyClaimIt",
          "How DailyClaimIt collects and uses information, including email signups, Microsoft Clarity analytics, and affiliate partner tracking.",
          "Privacy Policy", PRIVACY))
    write("terms/index.html", legal("/terms/", "Terms of Use | DailyClaimIt",
          "Terms of use for DailyClaimIt, a directory of third-party sweepstakes, survey and free stuff offers.",
          "Terms of Use", TERMS))
    write("404.html", page("/404.html", "Page Not Found | DailyClaimIt",
          "The page you were looking for could not be found.",
          '\n  <main class="prose"><h1>Page not found</h1><p>That page doesn\'t exist or has moved.</p>'
          '<p><a class="btn-primary" href="/">Back to today\'s offers →</a></p></main>\n', noindex=True))
    paths = ["/"] + [f"/{s}/" for s in CATS] + ["/disclosure/", "/privacy/", "/terms/"]
    today = date.today().isoformat()
    write("sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
          + "".join(f"  <url><loc>{SITE}{p}</loc><lastmod>{today}</lastmod></url>\n" for p in paths) + "</urlset>\n")
    write("robots.txt", f"User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n")


if __name__ == "__main__":
    main()
