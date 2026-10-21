#!/usr/bin/env python3
"""Generate the Paid Quiz & Survey Starter Kit PDF.

Usage (needs google-chrome or chromium for --print-to-pdf):
  python3 scripts/build_starter_kit.py          -> downloads/paid-quiz-survey-starter-kit.pdf
      Site version: "Where to start" uses tagged affiliate links (dc_pdf_kit_<offer>) from offers.json.
      Re-run whenever offers.json changes so those links stay current.
  python3 scripts/build_starter_kit.py --email  -> downloads/starter-kit-email.pdf
      EMAIL-SAFE version for the email sequence only. Our active offers don't allow email traffic,
      so this variant has NO hyperlinks at all: no offer/affiliate links, no links to dailyclaimit.com
      pages with offer buttons, no offer or brand names, no disclosure/tracker/earnings content.
      "Where to start" is replaced by a generic "How to pick a site" checklist.
      Do NOT link this file from any site page or the sitemap.
"""
import json, os, sys, subprocess, shutil, tempfile, html, base64
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build  # shared offer loading + per-placement tagging (dc_pdf_kit_<offer>)
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EMAIL = "--email" in sys.argv[1:]
OUT = os.path.join(ROOT, "downloads", "starter-kit-email.pdf" if EMAIL else "paid-quiz-survey-starter-kit.pdf")
e = lambda s: html.escape(str(s), quote=True)
logo = base64.b64encode(open(os.path.join(ROOT, "assets", "logo-full.png"), "rb").read()).decode()

def checklist(items):
    return "".join(f'<li><span class="box"></span><div><strong>{t}</strong> {d}</div></li>' for t, d in items)

routine = [("Pick one or two platforms.", "Fewer balances means you reach cash-out minimums sooner."),
           ("Use a dedicated email.", "Keeps survey invites organized and your main inbox clean."),
           ("Complete your profile fully.", "Profile surveys decide which studies you're matched with."),
           ("Check in for 10&ndash;20 minutes, once or twice a day.", "Quick polls and quizzes first, then longer surveys."),
           ("Judge tasks by time, not points.", "A short quiz can be worth more per minute than a long survey."),
           ("Cash out as soon as you hit the minimum.", "Note the threshold and redeem when you reach it.")]
mistakes = [("Letting balances sit.", "Some platforms expire inactive accounts or points."),
            ("Skipping offer terms.", "Miss a required step or time window and the reward may not credit."),
            ("No screenshots.", "Save proof of completion for bigger offers in case you need support."),
            ("Forgetting free trials.", "Set a reminder to cancel anything you don't want to keep."),
            ("Speeding or inconsistent answers.", "Both are common reasons for rejected responses."),
            ("Multiple accounts or location-hiding VPNs.", "Usually against the rules and can close your account.")]
flags = ["Paying to join or to &ldquo;unlock&rdquo; earnings", "Guaranteed big payouts for one quiz",
         "Requests for your SSN, bank login or card number for a small reward",
         "No company name, terms or support contact", "Quizzes asking security-question facts (first pet, mother's maiden name)",
         "A check for more than you're owed, plus a request to send money back"]
pick = [("Clear cash-out minimum.", "The threshold is stated up front and is low enough to reach in a few weeks."),
        ("PayPal or gift card options.", "Look for familiar payout methods, not just site credit or points."),
        ("Real terms and support.", "A named company, published terms, a privacy policy and a way to contact support."),
        ("No upfront fees.", "It should be free to join and free to cash out. Never pay to &ldquo;unlock&rdquo; earnings."),
        ("Reasonable data requests.", "Profile questions are normal; SSN, bank logins or card numbers for a small reward are not."),
        ("Recent payout reviews.", "Check independent reviews for people actually getting paid recently.")]

if EMAIL:
    # Email-safe: generic criteria instead of offers, plain-text site mention only (no <a> tags anywhere).
    p2_label = "Paid Quiz &amp; Survey Starter Kit"
    p2_body = f'''<div class="card"><h2>&#128269; How to pick a site</h2><p class="tip" style="margin-bottom:10px">Before you sign up anywhere, check for these. Pick one or two that pass, complete your profile, then follow the routine on page 1.</p><ul class="check">{checklist(pick)}</ul></div>
  <div class="card"><h2>&#128218; Keep learning</h2><p class="tip">More free guides on paid quizzes, surveys and sweepstakes at dailyclaimit.com</p></div>
  <div class="foot">Each platform's own terms apply. &middot; &copy; DailyClaimIt</div>'''
else:
    links = build.kit_links(build.load_offers())  # active surveys-quizzes offers, tagged dc_pdf_kit_<offer>
    start = "".join(f'<div class="offer"><a href="{e(url)}">{e(o["title"])} &rarr;</a><p>{e(o.get("reason", o["description"]))}</p></div>' for o, url in links)
    p2_label = "Paid Quiz &amp; Survey Starter Kit"
    p2_body = f'''<div class="card"><h2>&#128640; Where to start</h2><p class="tip" style="margin-bottom:10px">Pick one or two, complete your profile, then follow the routine on page 1.</p>{start}</div>
  <div class="card"><h2>&#128218; Keep learning</h2><p class="tip">Full guide: <a href="https://dailyclaimit.com/guides/how-to-make-money-with-paid-quizzes/" style="color:#A8832A">dailyclaimit.com/guides/how-to-make-money-with-paid-quizzes</a><br>More offers: <a href="https://dailyclaimit.com/surveys-quizzes/" style="color:#A8832A">dailyclaimit.com/surveys-quizzes</a></p></div>
  <div class="foot"><strong>Disclosure:</strong> Some links in this kit are affiliate links. If you sign up through them, DailyClaimIt may earn a commission at no cost to you. Rewards and earnings vary; each platform's own terms apply. Full disclosure: <a href="https://dailyclaimit.com/disclosure/">dailyclaimit.com/disclosure</a> &middot; &copy; DailyClaimIt</div>'''

doc = f'''<!DOCTYPE html><html><head><meta charset="utf-8"><title>Paid Quiz &amp; Survey Starter Kit | DailyClaimIt</title>
<link href="https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
@page {{ size: Letter; margin: 0; }}
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{ font-family: Inter, sans-serif; color: #141210; font-size: 10.6pt; line-height: 1.45; }}
.page {{ width: 8.5in; height: 11in; padding: .6in .65in .55in; background: #F7F5F0; position: relative; page-break-after: always; overflow: hidden; }}
.page:last-child {{ page-break-after: auto; }}
.top {{ display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #D4A843; padding-bottom: 12px; margin-bottom: 18px; }}
.top img {{ height: 34px; }} .top span {{ font-size: 9pt; color: #A8832A; font-weight: 600; letter-spacing: .08em; text-transform: uppercase; }}
h1 {{ font-family: Syne, sans-serif; font-weight: 800; font-size: 28pt; line-height: 1.05; letter-spacing: -.02em; margin-bottom: 6px; }}
h1 span {{ color: #D4A843; }}
.lede {{ color: #6B6560; margin-bottom: 18px; font-size: 11pt; }}
h2 {{ font-family: Syne, sans-serif; font-weight: 800; font-size: 15pt; margin: 0 0 10px; }}
.card {{ background: #fff; border-radius: 14px; padding: 16px 18px; margin-bottom: 14px; box-shadow: 0 2px 14px rgba(20,18,16,.07); border: 1px solid rgba(212,168,67,.35); }}
ul.check {{ list-style: none; }} ul.check li {{ display: flex; gap: 10px; margin-bottom: 8px; }}
.box {{ flex: 0 0 14px; height: 14px; border: 2px solid #D4A843; border-radius: 4px; margin-top: 2px; }}
ul.flags {{ list-style: none; columns: 2; column-gap: 22px; }} ul.flags li {{ break-inside: avoid; padding-left: 16px; position: relative; margin-bottom: 6px; }}
ul.flags li::before {{ content: "!"; position: absolute; left: 0; top: 0; color: #C2410C; font-weight: 800; }}
.offer {{ border-left: 4px solid #D4A843; padding: 6px 0 6px 12px; margin-bottom: 10px; }}
.offer a {{ font-family: Syne, sans-serif; font-weight: 800; font-size: 13pt; color: #A8832A; text-decoration: none; }}
.offer p {{ color: #2b2724; font-size: 10pt; }}
.tip {{ font-size: 10pt; color: #6B6560; }}
.foot {{ position: absolute; left: .65in; right: .65in; bottom: .45in; font-size: 8.6pt; color: #6B6560; border-top: 1px solid rgba(20,18,16,.15); padding-top: 8px; }}
.foot a {{ color: #A8832A; }}
</style></head><body>
<div class="page">
  <div class="top"><img src="data:image/png;base64,{logo}" alt="DailyClaimIt"><span>Free starter kit</span></div>
  <h1>Paid Quiz &amp; Survey <span>Starter Kit</span></h1>
  <p class="lede">A simple routine for earning small rewards with paid quizzes and surveys, plus the mistakes and red flags to watch for. Print it or keep it on your phone.</p>
  <div class="card"><h2>&#9989; Your daily routine</h2><ul class="check">{checklist(routine)}</ul></div>
  <div class="card"><h2>&#9888;&#65039; Mistakes that cost you rewards</h2><ul class="check">{checklist(mistakes)}</ul></div>
</div>
<div class="page">
  <div class="top"><img src="data:image/png;base64,{logo}" alt="DailyClaimIt"><span>{p2_label}</span></div>
  <div class="card"><h2>&#128681; Red flags: walk away if you see these</h2><ul class="flags">{"".join(f"<li>{f}</li>" for f in flags)}</ul></div>
  {p2_body}
</div>
</body></html>'''

chrome = shutil.which("google-chrome") or shutil.which("chromium") or shutil.which("chromium-browser")
with tempfile.TemporaryDirectory() as d:
    src = os.path.join(d, "kit.html"); open(src, "w", encoding="utf-8").write(doc)
    if EMAIL:
        assert "<a " not in doc and "href=\"http" not in doc.replace('href="https://fonts.googleapis.com', ''), "email kit must contain no links"
        for banned in ("BigCash", "InboxDollars", "Swagbucks", "DoorDash", "dc_pdf"):
            assert banned.lower() not in doc.lower(), f"email kit must not mention {banned}"
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    subprocess.run([chrome, "--headless", "--no-sandbox", "--disable-gpu", "--no-pdf-header-footer",
                    "--virtual-time-budget=8000", f"--print-to-pdf={OUT}", "file://" + src],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
print("wrote", os.path.relpath(OUT, ROOT))
