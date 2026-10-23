# Simulated Data — What It Is and Why

**Honest framing:** the Piston Hub site is a real, live store with a working GTM + GA4 setup, but it has no customer traffic yet.
To demonstrate the analysis half of the job, [`src/generate_events.py`](../src/generate_events.py) simulates 90 days of shoppers.

What makes the simulation useful rather than random:

- **Same contract as production.** It emits the exact event names, parameters, item schema and product catalog that `analytics.js` sends on the live site, in a flattened version of the GA4 BigQuery export schema. Pointing the pipeline at a real export only means swapping the loader.
- **Deterministic.** Fixed random seed (`42`) → every run produces the same data, so every number in the report can be reproduced.
- **Behaviour is explicit.** Every assumption is a named constant at the top of the script, listed below. The analysis then has to *discover* these patterns from raw events — which is exactly what it would do on real data.

## Assumptions

| Area | Assumption | Constant |
|---|---|---|
| Period | 25 Jul – 22 Oct 2026 (90 days), 9,000 users | `START`, `DAYS`, `N_USERS` |
| Traffic curve | Slow organic growth; weekends +30%; festive sale (Navratri–Dussehra, 10–20 Oct) ×1.9 | `day_weight()`, `FESTIVE` |
| Devices | Mobile 68% · desktop 27% · tablet 5% | `DEVICES` |
| Mobile checkout | Mobile completes checkout far less often (long form, no autofill) | `CHECKOUT_COMPLETION` |
| Channels | Organic 30% · Instagram 25% · Direct 17% · Paid search 14% · WhatsApp 8% · Email 6% of new users, each with its own conversion quality and return frequency | `CHANNELS` |
| Products | Helmets attract the most views; gloves are cheap impulse buys with the highest add-to-cart rate; boots are expensive and convert least | `VIEW_WEIGHT`, `ATC_RATE` |
| Cities | Bengaluru 44%, then Hyderabad, Chennai, Mysuru, Mumbai, Pune | `CITIES` |
| Returning visitors | Come back mostly via direct and email; convert better | session loop in `main()` |

## Injected data-quality problems

Real GA4 data is never clean. Three realistic problems are injected so the cleaning step is tested on something real:

| Problem | Real-world cause | How it's caught |
|---|---|---|
| Duplicate `purchase` events on 14–16 Sep | Purchase tag fired twice after a GTM change (e.g. both a page-view and custom-event trigger) | Same `transaction_id` appears more than once |
| ~3% of items have `item_category = "(not set)"` | Item mapping gap in a tag/variable | Repaired from the catalog via `item_id` |
| QA test orders from `localhost` | Developers testing checkout against the production GA4 property | Hostname filter |

These are documented with their impact in [`outputs/data_quality_report.md`](../outputs/data_quality_report.md).

## Limits

- Conversion rates, prices and channel mix are plausible for a small Indian D2C accessories store, not benchmarks.
- Insights in the report are about *the method* — the same SQL and charts would surface the real patterns once live traffic accumulates.
