"""
Validate and clean the raw GA4 event export, then load it into SQLite.

Checks (each one is reported in outputs/data_quality_report.md):
  - internal / test traffic (hostname != production domain)
  - duplicate purchase events (same transaction_id sent more than once)
  - item rows with item_category "(not set)" -> repaired from the product catalog
  - events with missing required fields
  - purchase value vs. sum of item prices (revenue reconciliation)

Output: data/piston_hub.db  (tables: events, event_items)
"""

import sqlite3
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
DB = ROOT / "data" / "piston_hub.db"
REPORT = ROOT / "outputs" / "data_quality_report.md"
PROD_HOST = "yuvrajbhagyedh.github.io"

REQUIRED = ["event_id", "event_timestamp", "user_pseudo_id", "ga_session_id", "event_name"]


def main():
    events = pd.read_csv(RAW / "events.csv", dtype={"transaction_id": str, "item_list_name": str})
    items = pd.read_csv(RAW / "event_items.csv")
    lines = ["# Data Quality Report", "",
             f"Raw input: **{len(events):,} events**, **{len(items):,} item rows**.", "",
             "| # | Check | Found | Action |", "|---|---|---|---|"]

    # 1. Internal / test traffic
    internal = events["hostname"] != PROD_HOST
    n_int = int(internal.sum())
    lines.append(f"| 1 | Internal / test traffic (hostname ≠ `{PROD_HOST}`) | {n_int:,} events "
                 f"({events.loc[internal, 'hostname'].unique().tolist()}) | Removed |")
    events = events[~internal]

    # 2. Duplicate purchases (same transaction_id)
    purchases = events[events["event_name"] == "purchase"]
    dup_mask = purchases.duplicated("transaction_id", keep="first")
    dup_ids = purchases.loc[dup_mask, "event_id"]
    dup_dates = sorted(purchases.loc[dup_mask, "event_date"].unique())
    dup_value = purchases.loc[dup_mask, "value"].sum()
    lines.append(f"| 2 | Duplicate `purchase` events (same transaction_id) | {len(dup_ids):,} duplicates on "
                 f"{', '.join(dup_dates) if dup_dates else '-'}; would double reported revenue for those days (+ ₹{dup_value:,.0f} "
                 f") | Kept first event per transaction |")
    events = events[~events["event_id"].isin(dup_ids)]

    # Keep only item rows that belong to surviving events
    items = items[items["event_id"].isin(events["event_id"])]

    # 3. item_category "(not set)" -> repair from catalog (item_id is always present)
    catalog = (items[items["item_category"] != "(not set)"]
               .drop_duplicates("item_id").set_index("item_id")["item_category"])
    not_set = items["item_category"] == "(not set)"
    n_not_set = int(not_set.sum())
    items.loc[not_set, "item_category"] = items.loc[not_set, "item_id"].map(catalog)
    still_missing = int(items["item_category"].isna().sum())
    lines.append(f"| 3 | `item_category` = \"(not set)\" | {n_not_set:,} item rows "
                 f"({n_not_set / len(items):.1%}) | Repaired from product catalog by item_id "
                 f"({still_missing} unresolved) |")

    # 4. Missing required fields
    missing = events[REQUIRED].isna().any(axis=1)
    lines.append(f"| 4 | Missing required fields ({', '.join(REQUIRED)}) | {int(missing.sum())} events | "
                 f"{'Removed' if missing.any() else 'None found'} |")
    events = events[~missing]

    # 5. Revenue reconciliation: purchase value must equal sum(price * qty)
    p = events[events["event_name"] == "purchase"][["event_id", "value"]]
    item_rev = (items.assign(line=items["price"] * items["quantity"])
                .groupby("event_id")["line"].sum())
    p = p.join(item_rev, on="event_id")
    mismatch = int((abs(p["value"] - p["line"]) > 0.5).sum())
    lines.append(f"| 5 | Purchase value ≠ Σ(item price × qty) | {mismatch} transactions | "
                 f"{'Investigate' if mismatch else 'Reconciled — no action'} |")

    lines += ["", f"Clean output: **{len(events):,} events**, **{len(items):,} item rows** "
              f"loaded into `data/piston_hub.db`.", "",
              "**Why it matters:** without step 2, reported revenue for 14–16 Sep would be "
              "doubled; without step 1, QA test orders (₹9,999 each) would pollute AOV and product rankings. "
              "In production, steps 1–2 should also be prevented at source: a GA4 internal-traffic filter "
              "and a GTM trigger exception / transaction_id de-duplication in the purchase tag."]

    DB.unlink(missing_ok=True)
    with sqlite3.connect(DB) as con:
        events.to_sql("events", con, index=False)
        items.to_sql("event_items", con, index=False)
        con.executescript("""
            CREATE INDEX idx_events_session ON events(ga_session_id);
            CREATE INDEX idx_events_name ON events(event_name);
            CREATE INDEX idx_events_user ON events(user_pseudo_id);
            CREATE INDEX idx_items_event ON event_items(event_id);
        """)

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
