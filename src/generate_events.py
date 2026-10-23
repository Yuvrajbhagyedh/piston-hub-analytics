"""
Generate 90 days of simulated GA4 event data for the Piston Hub store.

The live site (yuvrajbhagyedh.github.io/Piston-hub-Bike-accessory-website) is
instrumented with GTM + GA4, but has no real customer traffic yet. This script
simulates realistic shopper behaviour using the *same event names, parameters
and product catalog* the live dataLayer sends, so the analysis pipeline is
identical to what would run on a real GA4 BigQuery export.

Behaviour assumptions baked into the simulation are documented in
docs/simulation-assumptions.md. Three data-quality problems are injected on
purpose so the cleaning step has real work to do:
  1. Duplicate purchase events (GTM tag double-firing, 14-16 Sep)
  2. item_category "(not set)" on ~3% of item rows
  3. Internal QA traffic from hostname "localhost"

Output: data/raw/events.csv, data/raw/event_items.csv
"""

import csv
import random
from datetime import date, datetime, timedelta
from pathlib import Path

SEED = 42
START = date(2026, 7, 25)
DAYS = 90  # 25 Jul - 22 Oct 2026
N_USERS = 9000
HOSTNAME = "yuvrajbhagyedh.github.io"

OUT = Path(__file__).resolve().parent.parent / "data" / "raw"

# Same catalog as script.js on the live site (prices in INR).
CATALOG = {
    "apex-venom-gloves":        ("Apex Venom Gloves",        "Apex",  "Gloves",  1299),
    "apex-marvel-gloves":       ("Apex Marvel Gloves",       "Apex",  "Gloves",  1499),
    "axor-gloves":              ("Axor Gloves",              "Axor",  "Gloves",  1799),
    "apex-boots":               ("Apex Boots",               "Apex",  "Boots",   3499),
    "apex-marvel-boots":        ("Apex Marvel Boots",        "Apex",  "Boots",   4299),
    "apex-marvel-venom-helmet": ("Apex Marvel Venom Helmet", "Apex",  "Helmets", 3299),
    "apex-hunter-boots":        ("Apex Hunter Boots",        "Apex",  "Boots",   4999),
    "apex-solid-boots":         ("Apex Solid Boots",         "Apex",  "Boots",   3999),
    "apex-dynamo-helmet":       ("Apex Dynamo Helmet",       "Apex",  "Helmets", 2799),
    "retro-jet-west-helmet":    ("Retro Jet West Helmet",    "Retro", "Helmets", 2499),
    "vega-max":                 ("Vega Max",                 "Vega",  "Helmets", 1899),
    "apex-solid-helmet":        ("Apex Solid Helmet",        "Apex",  "Helmets", 2299),
}

# How strongly each product attracts views (helmets get browsed most).
VIEW_WEIGHT = {
    "apex-venom-gloves": 7, "apex-marvel-gloves": 6, "axor-gloves": 8,
    "apex-boots": 5, "apex-marvel-boots": 4, "apex-hunter-boots": 6, "apex-solid-boots": 3,
    "apex-marvel-venom-helmet": 12, "apex-dynamo-helmet": 10, "retro-jet-west-helmet": 11,
    "vega-max": 9, "apex-solid-helmet": 8,
}

# Probability a product view leads to add_to_cart, by category.
ATC_RATE = {"Gloves": 0.24, "Helmets": 0.11, "Boots": 0.09}

DEVICES = [("mobile", 0.68), ("desktop", 0.27), ("tablet", 0.05)]
# Checkout completion (begin_checkout -> purchase) by device: the mobile
# checkout form is long and has no autofill, so mobile completes far less.
CHECKOUT_COMPLETION = {"mobile": 0.34, "desktop": 0.63, "tablet": 0.50}

# (source, medium, share of new users, conversion multiplier, avg sessions/user)
CHANNELS = [
    ("google",    "organic",  0.30, 1.15, 1.9),
    ("instagram", "social",   0.25, 0.60, 1.4),
    ("(direct)",  "(none)",   0.17, 1.10, 2.3),
    ("google",    "cpc",      0.14, 0.95, 1.5),
    ("whatsapp",  "referral", 0.08, 1.45, 1.8),
    ("newsletter", "email",   0.06, 1.30, 2.8),
]

CITIES = [("Bengaluru", 0.44), ("Hyderabad", 0.13), ("Chennai", 0.12),
          ("Mumbai", 0.10), ("Pune", 0.10), ("Mysuru", 0.11)]

LISTS = [("slider", "All Products", 0.52), ("royalenfield", "Bike - Royal Enfield", 0.16),
         ("pulsar", "Bike - Pulsar", 0.09), ("yamaha", "Bike - Yamaha", 0.08),
         ("triumph", "Bike - Triumph", 0.04), ("AXOR", "Brand - Axor", 0.06),
         ("steelbird", "Brand - Steelbird", 0.05)]

FESTIVE = (date(2026, 10, 10), date(2026, 10, 20))   # Navratri-Dussehra sale
DUPLICATE_BUG = (date(2026, 9, 14), date(2026, 9, 16))


def pick(rng, options):
    """Weighted choice from [(value..., weight)] where weight is the last element."""
    r, acc = rng.random(), 0.0
    total = sum(o[-1] for o in options)
    for o in options:
        acc += o[-1] / total
        if r <= acc:
            return o
    return options[-1]


def day_weight(d):
    w = 1.0 + 0.004 * (d - START).days          # slow organic growth
    if d.weekday() >= 5:
        w *= 1.30                                # weekend riders browse more
    if FESTIVE[0] <= d <= FESTIVE[1]:
        w *= 1.9                                 # festive sale traffic
    return w


class Writer:
    def __init__(self):
        self.events, self.items, self.next_id, self.orders = [], [], 1, 0

    def event(self, ts, user, session, name, page, value=None, txn=None, list_name=None, items=(), host=HOSTNAME):
        eid = self.next_id
        self.next_id += 1
        self.events.append({
            "event_id": eid,
            "event_date": ts.date().isoformat(),
            "event_timestamp": ts.isoformat(timespec="seconds"),
            "user_pseudo_id": user["id"],
            "ga_session_id": session["id"],
            "session_number": session["number"],
            "event_name": name,
            "page": page,
            "hostname": host,
            "device_category": user["device"],
            "source": session["source"],
            "medium": session["medium"],
            "city": user["city"],
            "transaction_id": txn or "",
            "value": "" if value is None else value,
            "item_list_name": list_name or "",
        })
        for item_id, qty in items:
            name_, brand, cat, price = CATALOG[item_id]
            self.items.append({"event_id": eid, "item_id": item_id, "item_name": name_,
                               "item_brand": brand, "item_category": cat,
                               "price": price, "quantity": qty})
        return eid


def simulate_session(rng, w, user, session, start_ts, festive):
    ts = start_ts
    step = lambda lo=8, hi=90: ts + timedelta(seconds=rng.randint(lo, hi))

    landing = "index" if rng.random() < 0.55 else "slider"
    w.event(ts, user, session, "page_view", landing)
    if rng.random() < 0.06:
        ts = step()
        w.event(ts, user, session, "page_view", "contact-us-page")
        if rng.random() < 0.45:
            ts = step(30, 180)
            w.event(ts, user, session, "generate_lead", "contact-us-page")

    if rng.random() > 0.78:          # bounced / browsed home only
        return
    list_slug, list_name, _ = pick(rng, LISTS)
    if landing == "index" and list_slug != "slider" and rng.random() < 0.7:
        w.event(ts, user, session, "select_content", "index")
    ts = step()
    w.event(ts, user, session, "page_view", list_slug)
    w.event(ts, user, session, "view_item_list", list_slug, list_name=list_name,
            items=[(i, 1) for i in CATALOG])

    if rng.random() > 0.68:
        return
    cart = {}
    n_views = 1 + min(int(rng.expovariate(0.9)), 4)
    viewed = set()
    for _ in range(n_views):
        item = pick(rng, [(k, v) for k, v in VIEW_WEIGHT.items()])[0]
        if item in viewed:
            continue
        viewed.add(item)
        ts = step()
        if list_slug == "slider":
            w.event(ts, user, session, "select_item", list_slug, list_name=list_name, items=[(item, 1)])
        w.event(ts, user, session, "page_view", item)
        w.event(ts, user, session, "view_item", item, value=CATALOG[item][3], items=[(item, 1)])
        atc = ATC_RATE[CATALOG[item][2]] * (1.25 if festive else 1.0) * (1.2 if session["number"] > 1 else 1.0)
        if rng.random() < atc * 1.25:
            qty = 2 if (CATALOG[item][2] == "Gloves" and rng.random() < 0.15) else 1
            ts = step(5, 40)
            w.event(ts, user, session, "add_to_cart", item, value=CATALOG[item][3] * qty, items=[(item, qty)])
            cart[item] = cart.get(item, 0) + qty

    if not cart:
        return
    cart_value = lambda: sum(CATALOG[i][3] * q for i, q in cart.items())
    if rng.random() > 0.82:
        return
    ts = step()
    w.event(ts, user, session, "page_view", "cart")
    w.event(ts, user, session, "view_cart", "cart", value=cart_value(), items=list(cart.items()))
    if len(cart) > 1 and rng.random() < 0.18:
        removed = rng.choice(list(cart))
        ts = step(5, 30)
        w.event(ts, user, session, "remove_from_cart", "cart", value=CATALOG[removed][3] * cart[removed],
                items=[(removed, cart[removed])])
        del cart[removed]

    # Checkout start: high-value carts hesitate more (sticker shock on boots).
    p_checkout = 0.60 - 0.04 * (cart_value() // 2500)
    if rng.random() > max(p_checkout, 0.3):
        return
    if not user["signed_up"] and rng.random() < 0.55:
        ts = step(20, 90)
        w.event(ts, user, session, "page_view", "signup")
        w.event(ts, user, session, "sign_up", "signup")
        user["signed_up"] = True
    elif user["signed_up"]:
        w.event(ts, user, session, "login", "login")
    ts = step()
    w.event(ts, user, session, "page_view", "checkout")
    w.event(ts, user, session, "begin_checkout", "checkout", value=cart_value(), items=list(cart.items()))

    p_buy = CHECKOUT_COMPLETION[user["device"]] * session["conv_mult"]
    p_buy *= 1.15 if festive else 1.0
    p_buy *= 1.25 if session["number"] > 1 else 1.0
    if rng.random() < min(p_buy, 0.92):
        ts = step(60, 300)
        w.orders += 1
        txn = "PH-%06d" % (100000 + w.orders)
        w.event(ts, user, session, "purchase", "checkout", value=cart_value(), txn=txn, items=list(cart.items()))
        user["purchases"] += 1
        if DUPLICATE_BUG[0] <= ts.date() <= DUPLICATE_BUG[1]:
            # Injected issue 1: tag fired twice for the same transaction
            w.event(ts + timedelta(seconds=1), user, session, "purchase", "checkout",
                    value=cart_value(), txn=txn, items=list(cart.items()))


def main():
    rng = random.Random(SEED)
    w = Writer()
    days = [START + timedelta(days=i) for i in range(DAYS)]
    weights = [day_weight(d) for d in days]
    total_w = sum(weights)

    session_counter = 0
    for u in range(N_USERS):
        source, medium, _, conv_mult, avg_sessions = pick(rng, [c + (c[2],) for c in CHANNELS])[:5]
        user = {
            "id": "%010d.%d" % (rng.randint(10**8, 10**9), 1_700_000_000 + u),
            "device": pick(rng, DEVICES)[0],
            "city": pick(rng, CITIES)[0],
            "signed_up": False,
            "purchases": 0,
        }
        # First visit day follows the traffic curve.
        r, acc, first = rng.random() * total_w, 0.0, days[-1]
        for d, wt in zip(days, weights):
            acc += wt
            if r <= acc:
                first = d
                break
        n_sessions = 1 + int(rng.expovariate(1 / (avg_sessions - 1)))
        day = first
        for s in range(1, n_sessions + 1):
            if day > days[-1]:
                break
            session_counter += 1
            # Returning visits mostly come back direct or via email.
            if s == 1:
                src, med, cm = source, medium, conv_mult
            else:
                src, med, _, cm, _ = pick(rng, [CHANNELS[2][:4] + (0.6,), CHANNELS[5][:4] + (0.25,), CHANNELS[0][:4] + (0.15,)])
            session = {"id": 1_760_000_000 + session_counter, "number": s,
                       "source": src, "medium": med, "conv_mult": cm}
            hour = rng.choice([8, 9, 12, 13, 18, 19, 20, 21, 22, 21, 20, 14, 11, 23])
            start_ts = datetime(day.year, day.month, day.day, hour, rng.randint(0, 59), rng.randint(0, 59))
            simulate_session(rng, w, user, session, start_ts, FESTIVE[0] <= day <= FESTIVE[1])
            day = day + timedelta(days=1 + int(rng.expovariate(1 / 9)))

    # Injected issue 3: internal QA traffic from localhost (developer testing)
    qa = {"id": "0000000001.1700000000", "device": "desktop", "city": "Bengaluru", "signed_up": True, "purchases": 0}
    for i in range(40):
        d = days[rng.randint(0, DAYS - 1)]
        sess = {"id": 1_769_000_000 + i, "number": i + 1, "source": "(direct)", "medium": "(none)", "conv_mult": 1}
        ts = datetime(d.year, d.month, d.day, 11, 0, 0)
        for item in rng.sample(list(CATALOG), 3):
            w.event(ts, qa, sess, "view_item", item, value=CATALOG[item][3], items=[(item, 1)], host="localhost")
            w.event(ts, qa, sess, "add_to_cart", item, value=CATALOG[item][3], items=[(item, 1)], host="localhost")
        w.event(ts, qa, sess, "purchase", "checkout", value=9999, txn="DEMO-QA%03d" % i,
                items=[(item, 1)], host="localhost")

    # Injected issue 2: ~3% of item rows lose their category (tag mapping gap)
    for row in w.items:
        if rng.random() < 0.03:
            row["item_category"] = "(not set)"

    w.events.sort(key=lambda e: (e["event_timestamp"], e["event_id"]))
    OUT.mkdir(parents=True, exist_ok=True)
    for name, rows in (("events.csv", w.events), ("event_items.csv", w.items)):
        with open(OUT / name, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)
    print(f"events: {len(w.events):,}  item rows: {len(w.items):,}  sessions: {session_counter:,}  users: {N_USERS:,}")


if __name__ == "__main__":
    main()
