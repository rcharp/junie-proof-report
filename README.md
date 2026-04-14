# Junie Systems — Proof Report Generator

Generates a personalized digital presence audit for contractor prospects.

## Setup

```bash
git clone https://github.com/rcharp/junie-proof-report
cd junie-proof-report
pip install requests
```

## Usage

```bash
python3 proof_report.py "Business Name" "City" "trade"
```

## Examples

```bash
python3 proof_report.py "Bob's Painting" "Tampa" "painting"
python3 proof_report.py "K&C Stump Grinding" "Sarasota" "tree service"
python3 proof_report.py "Joe's Plumbing" "Orlando" "plumbing"
```

The report will auto-open in your browser. It includes:
- Online visibility score
- Auto-fetched reviews & rating for the business
- Competitor comparison table (top 3 by reviews)
- Website presence breakdown
- Estimated monthly revenue lost
- Junie Systems CTA

## Supported Trades
handyman, painting, plumbing, pressure washing, tree service, landscaping, flooring, tile, junk removal, concrete, hvac, electrical, pool, lawn care
