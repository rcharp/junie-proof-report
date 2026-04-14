#!/usr/bin/env python3
"""
Proof Report Generator for Junie Systems
Generates a personalized "digital presence audit" for a contractor prospect.
Usage: python3 proof_report.py "Business Name" "City" "trade"
"""

import sys
import os
import requests
import json
import re
from datetime import datetime

API_KEY = "NGUzNGRhY2FmNTMzNDk4MjljODIyZWNhMmFjNTI4MmN8MDQ4ZTI3ZTUzNg"

JOB_VALUES = {
    "handyman": 300, "painting": 1200, "plumbing": 600,
    "pressure washing": 350, "tree service": 800, "landscaping": 500,
    "flooring": 3000, "floor removal": 800, "tile": 1500,
    "junk removal": 250, "junk hauling": 250, "concrete": 2000,
    "hvac": 400, "electrical": 500, "pool": 300, "lawn care": 80, "default": 400
}

def get_job_value(trade):
    for key, val in JOB_VALUES.items():
        if key in trade.lower():
            return val
    return JOB_VALUES["default"]

def outscraper_search(query, limit=20, fields=None):
    params = {"query": query, "limit": limit, "async": "false"}
    if fields:
        params["fields"] = fields
    try:
        r = requests.get(
            "https://api.app.outscraper.com/maps/search-v3",
            params=params,
            headers={"X-API-KEY": API_KEY},
            timeout=30
        )
        data = r.json()
        items = data.get("data", [[]])
        if items and isinstance(items[0], list):
            return [i for i in items[0] if isinstance(i, dict)]
        return [i for i in items if isinstance(i, dict)]
    except Exception as e:
        print(f"  Outscraper error: {e}")
        return []

def lookup_business(business_name, city, trade):
    """Look up the specific business to get their reviews/rating"""
    print(f"  Looking up {business_name} in {city}...")
    query = f"{business_name} {city} FL"
    results = outscraper_search(query, limit=5, fields="name,reviews,rating,website,phone,place_id")
    
    # Find best match
    for r in results:
        name = (r.get("name") or "").lower()
        if business_name.lower()[:8] in name or name[:8] in business_name.lower():
            return r
    
    # Return first result if no close match
    return results[0] if results else {}

def fetch_competitors(trade, city, exclude_name=""):
    """Fetch competitors in same trade/city"""
    print(f"  Fetching {trade} competitors in {city}...")
    query = f"{trade} {city} FL"
    results = outscraper_search(query, limit=20, fields="name,website,reviews,rating,phone")
    
    # Filter out the business itself
    competitors = []
    for r in results:
        if exclude_name.lower() not in (r.get("name") or "").lower():
            competitors.append(r)
    
    return competitors

def generate_report(business_name, city, trade):
    job_value = get_job_value(trade)

    # Auto-lookup the business
    print(f"\nLooking up business data for {business_name}...")
    biz_data = lookup_business(business_name, city, trade)
    reviews = biz_data.get("reviews", 0) or 0
    rating = biz_data.get("rating", 0.0) or 0.0
    has_website = bool((biz_data.get("website") or "").strip())
    
    print(f"  Found: {reviews} reviews, {rating}★, website: {'yes' if has_website else 'no'}")

    # Fetch competitors
    all_competitors = fetch_competitors(trade, city, exclude_name=business_name)
    total_competitors = len(all_competitors)
    competitors_with_website = sum(1 for c in all_competitors if (c.get("website") or "").strip())
    website_pct = int((competitors_with_website / total_competitors * 100)) if total_competitors > 0 else 70

    # Top 3 competitors by reviews
    top_competitors = sorted(
        [c for c in all_competitors if c.get("reviews", 0) and c.get("name")],
        key=lambda x: x.get("reviews", 0) or 0,
        reverse=True
    )[:3]

    # Revenue math
    missed_calls_per_week = 3
    close_rate = 0.4
    weeks_per_month = 4.3
    monthly_lost = int(missed_calls_per_week * close_rate * job_value * weeks_per_month)
    annual_lost = monthly_lost * 12

    # Visibility score
    visibility_score = 15 if not has_website else 35
    if reviews > 10:
        visibility_score += 10
    if reviews > 30:
        visibility_score += 10

    # Build competitor rows HTML
    comp_rows_html = ""
    for i, comp in enumerate(top_competitors):
        comp_name = comp.get("name", "")[:28]
        comp_reviews = comp.get("reviews", 0) or 0
        comp_rating = comp.get("rating", 0.0) or 0.0
        comp_has_site = bool((comp.get("website") or "").strip())
        rank = i + 1
        comp_rows_html += f"""
        <tr>
          <td style="padding:10px 8px;color:#94a3b8;font-size:13px">#{rank}</td>
          <td style="padding:10px 8px;font-size:14px;font-weight:600">{comp_name}</td>
          <td style="padding:10px 8px;text-align:center">
            <span style="color:{'#22c55e' if comp_has_site else '#ef4444'};font-size:13px">
              {'✓ Yes' if comp_has_site else '✗ No'}
            </span>
          </td>
          <td style="padding:10px 8px;text-align:center;font-size:13px">
            <span style="color:#f59e0b">{'★' * int(comp_rating)}</span> {comp_reviews}
          </td>
        </tr>"""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Digital Presence Audit — {business_name}</title>
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #0f0f14; color: #fff; min-height: 100vh; }}
  .header {{ background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); padding: 40px 24px 30px; text-align: center; border-bottom: 1px solid #2a2a4a; }}
  .header .logo {{ color: #6366f1; font-size: 14px; font-weight: 600; letter-spacing: 2px; text-transform: uppercase; margin-bottom: 20px; }}
  .header h1 {{ font-size: 28px; font-weight: 700; margin-bottom: 8px; }}
  .header h1 span {{ color: #6366f1; }}
  .header p {{ color: #94a3b8; font-size: 15px; }}
  .badge {{ display: inline-block; background: #ef444420; color: #ef4444; border: 1px solid #ef444440; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 600; margin-top: 12px; }}
  .container {{ max-width: 680px; margin: 0 auto; padding: 24px 16px 60px; }}
  .score-card {{ background: #1a1a2e; border: 1px solid #2a2a4a; border-radius: 16px; padding: 28px; margin-bottom: 20px; text-align: center; }}
  .score-circle {{ width: 120px; height: 120px; border-radius: 50%; background: conic-gradient(#ef4444 0% {visibility_score}%, #2a2a4a {visibility_score}% 100%); display: flex; align-items: center; justify-content: center; margin: 0 auto 16px; }}
  .score-inner {{ width: 90px; height: 90px; background: #1a1a2e; border-radius: 50%; display: flex; flex-direction: column; align-items: center; justify-content: center; }}
  .score-number {{ font-size: 30px; font-weight: 800; color: #ef4444; }}
  .score-label {{ font-size: 9px; color: #64748b; text-transform: uppercase; letter-spacing: 1px; }}
  .score-card h2 {{ font-size: 18px; font-weight: 700; margin-bottom: 6px; }}
  .score-card p {{ color: #94a3b8; font-size: 14px; }}
  .metric-card {{ background: #1a1a2e; border: 1px solid #2a2a4a; border-radius: 16px; padding: 24px; margin-bottom: 16px; }}
  .metric-card .label {{ font-size: 11px; color: #64748b; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px; }}
  .metric-card .value.red {{ font-size: 32px; font-weight: 800; color: #ef4444; }}
  .metric-card .value.green {{ font-size: 32px; font-weight: 800; color: #22c55e; }}
  .metric-card .description {{ color: #94a3b8; font-size: 14px; margin-top: 10px; line-height: 1.5; }}
  .bar-row {{ display: flex; align-items: center; gap: 12px; margin-bottom: 8px; }}
  .bar-label {{ font-size: 13px; color: #94a3b8; width: 140px; flex-shrink: 0; }}
  .bar-track {{ flex: 1; background: #2a2a4a; border-radius: 4px; height: 8px; overflow: hidden; }}
  .bar-fill.red {{ height: 100%; border-radius: 4px; background: #ef4444; }}
  .bar-fill.green {{ height: 100%; border-radius: 4px; background: #22c55e; }}
  .bar-pct {{ font-size: 13px; font-weight: 600; width: 40px; text-align: right; }}
  .comp-table {{ width: 100%; border-collapse: collapse; margin-top: 16px; }}
  .comp-table th {{ padding: 8px; text-align: left; font-size: 11px; color: #64748b; text-transform: uppercase; letter-spacing: 1px; border-bottom: 1px solid #2a2a4a; }}
  .comp-table tr:not(:last-child) td {{ border-bottom: 1px solid #1e1e30; }}
  .you-row td {{ background: #1e1e30 !important; }}
  .lost-revenue {{ background: linear-gradient(135deg, #1f0a0a 0%, #2d0f0f 100%); border: 1px solid #ef444430; border-radius: 16px; padding: 28px; margin-bottom: 16px; text-align: center; }}
  .lost-revenue .amount {{ font-size: 52px; font-weight: 900; color: #ef4444; }}
  .lost-revenue .period {{ font-size: 16px; color: #94a3b8; margin-top: 4px; }}
  .lost-revenue .explanation {{ color: #94a3b8; font-size: 13px; margin-top: 16px; line-height: 1.6; background: #ffffff08; border-radius: 8px; padding: 12px; }}
  .cta {{ background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%); border-radius: 16px; padding: 32px 24px; text-align: center; margin-top: 24px; }}
  .cta h2 {{ font-size: 22px; font-weight: 800; margin-bottom: 8px; }}
  .cta p {{ color: #c7d2fe; font-size: 14px; margin-bottom: 20px; line-height: 1.5; }}
  .cta .price {{ font-size: 36px; font-weight: 900; margin-bottom: 4px; }}
  .cta .price-note {{ color: #c7d2fe; font-size: 13px; }}
  .cta .features {{ list-style: none; margin: 16px 0; text-align: left; display: inline-block; }}
  .cta .features li {{ padding: 4px 0; font-size: 14px; color: #e0e7ff; }}
  .cta .features li::before {{ content: "✓ "; color: #a5f3fc; font-weight: 700; }}
  .footer {{ text-align: center; color: #4b5563; font-size: 12px; padding: 20px; }}
</style>
</head>
<body>
<div class="header">
  <div class="logo">Junie Systems</div>
  <h1>Digital Presence Audit<br><span>{business_name}</span></h1>
  <p>{trade.title()} · {city}, Florida</p>
  <div class="badge">⚠ Critical Issues Found</div>
</div>
<div class="container">

  <div class="score-card">
    <div class="score-circle">
      <div class="score-inner">
        <div class="score-number">{visibility_score}</div>
        <div class="score-label">/ 100</div>
      </div>
    </div>
    <h2>Online Visibility Score</h2>
    <p>Your business is {'nearly invisible' if visibility_score < 40 else 'underperforming'} to customers searching online right now.</p>
  </div>

  <div class="metric-card">
    <div class="label">Website Status</div>
    <div class="value {'green' if has_website else 'red'}">{'Found ✓' if has_website else 'None Found ✗'}</div>
    <div class="description">
      {'You have a website, but without the right automations you\'re still losing jobs to missed calls and no follow-up system.' if has_website else f'When a potential customer Googles "{trade} near me" in {city}, you don\'t show up. They call your competitor instead — every single time.'}
    </div>
  </div>

  <div class="metric-card">
    <div class="label">Your Google Reviews</div>
    <div class="value {'red' if reviews < 10 else 'green'}">{reviews} reviews · {'★' * int(rating) if rating else '☆☆☆☆☆'} {f'{rating:.1f}' if rating else '0.0'}</div>
    <div class="description">
      {'You have almost no reviews. Customers trust businesses with reviews. Without them, they choose your competitor.' if reviews < 10 else f'You have {reviews} reviews which is a start, but your top competitors have far more — and they\'re getting found first.'}
    </div>
  </div>

  <div class="metric-card">
    <div class="label">Competitor Landscape in {city} — {total_competitors} businesses found</div>
    <div style="margin-top:12px">
      <div class="bar-row">
        <span class="bar-label">Have a website</span>
        <div class="bar-track"><div class="bar-fill green" style="width:{website_pct}%"></div></div>
        <span class="bar-pct" style="color:#22c55e">{website_pct}%</span>
      </div>
      <div class="bar-row">
        <span class="bar-label">No website</span>
        <div class="bar-track"><div class="bar-fill red" style="width:{100-website_pct}%"></div></div>
        <span class="bar-pct" style="color:#ef4444">{100-website_pct}%</span>
      </div>
    </div>
    <div style="margin-top:20px">
      <table class="comp-table">
        <thead>
          <tr>
            <th>#</th><th>Business</th><th>Website</th><th>Reviews</th>
          </tr>
        </thead>
        <tbody>
          <tr class="you-row">
            <td style="padding:10px 8px;color:#6366f1;font-size:13px">YOU</td>
            <td style="padding:10px 8px;font-size:14px;font-weight:600;color:#6366f1">{business_name[:28]}</td>
            <td style="padding:10px 8px;text-align:center"><span style="color:{'#22c55e' if has_website else '#ef4444'};font-size:13px">{'✓ Yes' if has_website else '✗ No'}</span></td>
            <td style="padding:10px 8px;text-align:center;font-size:13px"><span style="color:#f59e0b">{'★' * int(rating) if rating else ''}</span> {reviews}</td>
          </tr>
          {comp_rows_html}
        </tbody>
      </table>
    </div>
  </div>

  <div class="lost-revenue">
    <div class="label" style="color:#ef444480;margin-bottom:8px">ESTIMATED MONTHLY REVENUE LOST</div>
    <div class="amount">${monthly_lost:,}</div>
    <div class="period">every month · ${annual_lost:,} per year</div>
    <div class="explanation">
      Based on {missed_calls_per_week} missed calls/week × {int(close_rate*100)}% close rate × ${job_value:,} avg {trade} job.
      No website = no Google presence = no calls from new customers searching online.
    </div>
  </div>

  <div class="cta">
    <h2>Fix This This Week</h2>
    <p>We build you a professional website that shows up on Google, plus the systems to turn missed calls into booked jobs.</p>
    <div class="price">$297<span style="font-size:18px;font-weight:400">/mo</span></div>
    <div class="price-note">Less than one {trade} job per month</div>
    <ul class="features">
      <li>Professional website + domain + hosting</li>
      <li>Shows up on Google searches</li>
      <li>Missed call text back automation</li>
      <li>Automated Google review requests</li>
      <li>1-year customer follow-up sequence</li>
    </ul>
    <p style="color:#c7d2fe;font-size:13px">No contracts · No setup fees · Live within 48 hours</p>
  </div>

</div>
<div class="footer">
  Junie Systems · juniesystems.com · ricky@juniesystems.com<br>
  <span style="font-size:11px">Report generated {datetime.now().strftime("%B %d, %Y")} · {city}, Florida</span>
</div>
</body>
</html>"""

    return html

def main():
    if len(sys.argv) < 4:
        print("Usage: python3 proof_report.py \"Business Name\" \"City\" \"trade\"")
        print("Example: python3 proof_report.py \"Bob's Painting\" \"Tampa\" \"painting\"")
        sys.exit(1)

    business_name = sys.argv[1]
    city = sys.argv[2]
    trade = sys.argv[3]

    print(f"\n🔍 Generating proof report for {business_name} ({trade} in {city})...")
    html = generate_report(business_name, city, trade)

    safe_name = re.sub(r'[^a-z0-9]', '_', business_name.lower())
    filename = f"{safe_name}_proof_report.html"
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"\n✅ Report saved: {output_path}")
    import platform
    if platform.system() == 'Darwin':
        os.system(f"open '{output_path}'")
    elif platform.system() == 'Windows':
        os.startfile(output_path)
    else:
        os.system(f"xdg-open '{output_path}'")

if __name__ == "__main__":
    main()
