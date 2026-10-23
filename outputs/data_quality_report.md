# Data Quality Report

Raw input: **65,635 events**, **131,526 item rows**.

| # | Check | Found | Action |
|---|---|---|---|
| 1 | Internal / test traffic (hostname ≠ `yuvrajbhagyedh.github.io`) | 280 events (['localhost']) | Removed |
| 2 | Duplicate `purchase` events (same transaction_id) | 11 duplicates on 2026-09-14, 2026-09-15, 2026-09-16; would double reported revenue for those days (+ ₹30,786 ) | Kept first event per transaction |
| 3 | `item_category` = "(not set)" | 3,877 item rows (3.0%) | Repaired from product catalog by item_id (0 unresolved) |
| 4 | Missing required fields (event_id, event_timestamp, user_pseudo_id, ga_session_id, event_name) | 0 events | None found |
| 5 | Purchase value ≠ Σ(item price × qty) | 0 transactions | Reconciled — no action |

Clean output: **65,344 events**, **131,233 item rows** loaded into `data/piston_hub.db`.

**Why it matters:** without step 2, reported revenue for 14–16 Sep would be doubled; without step 1, QA test orders (₹9,999 each) would pollute AOV and product rankings. In production, steps 1–2 should also be prevented at source: a GA4 internal-traffic filter and a GTM trigger exception / transaction_id de-duplication in the purchase tag.
