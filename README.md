# dailyclaimit-home

Static site for dailyclaimit.com. Edit `offers.json` / `content/guides/*.html`, then run
`python3 scripts/build.py` and commit the generated output. Push to `main` deploys via GitHub Pages.

## Offer compliance fields

Each offer in `offers.json` has:

- `allowed_traffic`: traffic types the network/advertiser permits (Contextual, Display, Search, Social, Native, Mobile Ads, Email).
- `restrictions`: short note on creative/traffic restrictions.

Everything on this site (cards, guide text links, CTA buttons) counts as **Contextual** traffic.
`build.py` refuses to build if an `active` offer's `allowed_traffic` does not include `Contextual`.
Do not use offers on Pinterest/social or email unless `allowed_traffic` includes Social / Email.

Current status (MaxBounty audit, 2026-10-18):

| Offer | Network / ID | Allowed | Notes |
|---|---|---|---|
| snackbox | MaxBounty 25012 | Display, Social, Native, Mobile Ads | **Inactive**: Contextual not allowed. No guaranteed box claims, no unverified health benefits. |
| bigcash | MaxBounty 32533 | Contextual, Display, Search, Social, Native, Mobile Ads | No email, no brand bidding, no misleading ads, no incentivized. |
| win25k | MaxBounty 30664 | All, incl. Social and Email | Inactive (offer down). |
| inboxdollars | MaxBounty 6365 | Contextual, Display, Search, Native, Mobile Ads | NO Social, NO Email, no brand bidding (keyword restriction list applies). |
| swagbucks | Impact | Unconfirmed | Treat Social and Email as not allowed until verified. |

## Pending

- **Surveys2Cash** (MaxBounty 15647): pending approval. Allows Contextual, Social, Email. No incentive traffic; 18+ US only; cap 10/day. Not in `offers.json` yet.
