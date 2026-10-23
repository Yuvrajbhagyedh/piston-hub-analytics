"""
Build the report charts from the SQL result tables (outputs/tables/*.csv).
Output: outputs/charts/*.png
"""

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
TABLES = ROOT / "outputs" / "tables"
CHARTS = ROOT / "outputs" / "charts"

# Validated categorical palette (first three slots are CVD-safe as a set).
BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
SURFACE, INK, INK_2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df"
CATEGORY_COLORS = {"Helmets": BLUE, "Gloves": ORANGE, "Boots": AQUA}

plt.rcParams.update({
    "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE,
    "font.family": "DejaVu Sans", "font.size": 10,
    "axes.edgecolor": GRID, "axes.labelcolor": INK_2, "axes.titlesize": 13,
    "axes.titleweight": "bold", "axes.titlecolor": INK, "axes.titlelocation": "left",
    "xtick.color": INK_2, "ytick.color": INK_2, "axes.grid": True, "grid.color": GRID,
    "grid.linewidth": 0.8, "axes.spines.top": False, "axes.spines.right": False,
    "legend.frameon": False, "axes.axisbelow": True,
    "patch.edgecolor": SURFACE, "patch.linewidth": 1.2,  # 2px surface gap between adjacent fills
})


def t(name):
    return pd.read_csv(TABLES / f"{name}.csv")


def save(fig, name, note=None):
    if note:
        fig.text(0.01, 0.01, note, fontsize=8.5, color=INK_2, ha="left", va="bottom")
    fig.tight_layout(rect=(0, 0.04 if note else 0, 1, 1))
    fig.savefig(CHARTS / f"{name}.png", dpi=160)
    plt.close(fig)


def inr(x):
    return f"₹{x / 100000:.1f}L" if x >= 100000 else f"₹{x / 1000:.0f}K"


def funnel():
    df = t("02_funnel")
    fig, ax = plt.subplots(figsize=(9, 4.2))
    labels = df["stage"].str.replace("_", " ")
    bars = ax.barh(labels[::-1], df["sessions"][::-1], color=BLUE, height=0.62)
    ax.grid(axis="y", visible=False)
    for bar, (_, r) in zip(bars, df[::-1].iterrows()):
        step = "" if pd.isna(r["step_conversion_pct"]) else f"   ({r['step_conversion_pct']:.0f}% of previous step)"
        ax.text(bar.get_width() + 120, bar.get_y() + bar.get_height() / 2,
                f"{int(r['sessions']):,} sessions · {r['pct_of_all_sessions']:.1f}%{step}",
                va="center", fontsize=9, color=INK)
    ax.set_xlim(0, df["sessions"].max() * 1.6)
    ax.xaxis.set_major_formatter(matplotlib.ticker.StrMethodFormatter("{x:,.0f}"))
    ax.set_xlabel("Sessions")
    ax.set_title("Shopping funnel: the biggest drop is product view → add to cart")
    save(fig, "01_funnel", "Session-level funnel, 25 Jul – 22 Oct 2026. Source: sql/02_funnel.sql")


def device_checkout():
    df = t("03_funnel_by_device")
    fig, ax = plt.subplots(figsize=(8, 3.8))
    colors = [ORANGE if d == "mobile" else BLUE for d in df["device_category"]]
    bars = ax.bar(df["device_category"], df["checkout_to_purchase_pct"], color=colors, width=0.55)
    ax.grid(axis="x", visible=False)
    for bar, (_, r) in zip(bars, df.iterrows()):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1.5,
                f"{r['checkout_to_purchase_pct']:.0f}%", ha="center", fontsize=11, weight="bold", color=INK)
        ax.text(bar.get_x() + bar.get_width() / 2, 4, f"{int(r['sessions']):,}\nsessions",
                ha="center", fontsize=8.5, color="white")
    ax.set_ylim(0, 100)
    ax.set_ylabel("Checkout → purchase (%)")
    ax.set_title("Mobile shoppers abandon checkout far more than desktop")
    save(fig, "02_checkout_by_device", "Share of sessions that began checkout and completed purchase. Source: sql/03_funnel_by_device.sql")


def channels():
    df = t("04_channel_performance").sort_values("share_of_sessions_pct", ascending=True)
    fig, ax = plt.subplots(figsize=(9, 4.4))
    y = range(len(df))
    h = 0.36
    ax.barh([i + h / 2 for i in y], df["share_of_sessions_pct"], height=h, color=BLUE, label="Share of sessions")
    ax.barh([i - h / 2 for i in y], df["share_of_revenue_pct"], height=h, color=ORANGE, label="Share of revenue")
    ax.set_yticks(list(y))
    ax.set_yticklabels(df["channel"])
    ax.grid(axis="y", visible=False)
    for i, (_, r) in enumerate(df.iterrows()):
        ax.text(max(r["share_of_sessions_pct"], r["share_of_revenue_pct"]) + 0.6, i,
                f"conv. {r['conversion_pct']:.1f}%", va="center", fontsize=9, color=INK_2)
    ax.set_xlim(0, df[["share_of_sessions_pct", "share_of_revenue_pct"]].max().max() * 1.3)
    ax.set_xlabel("% of total")
    ax.legend(loc="lower right")
    ax.set_title("Instagram brings traffic, not buyers; email punches above its weight")
    save(fig, "03_channels", "Source: sql/04_channel_performance.sql")


def categories():
    df = t("06_category_summary")
    fig, ax = plt.subplots(figsize=(8, 3.8))
    x = range(len(df))
    w = 0.36
    ax.bar([i - w / 2 for i in x], df["share_of_views_pct"], width=w, color=BLUE, label="Share of product views")
    ax.bar([i + w / 2 for i in x], df["share_of_revenue_pct"], width=w, color=ORANGE, label="Share of revenue")
    for i, (_, r) in enumerate(df.iterrows()):
        ax.text(i - w / 2, r["share_of_views_pct"] + 1, f"{r['share_of_views_pct']:.0f}%", ha="center", fontsize=9)
        ax.text(i + w / 2, r["share_of_revenue_pct"] + 1, f"{r['share_of_revenue_pct']:.0f}%", ha="center", fontsize=9)
    ax.set_xticks(list(x))
    ax.set_xticklabels([f"{c}\nview→cart {v:.0f}%" for c, v in zip(df["item_category"], df["view_to_cart_pct"])])
    ax.set_ylim(0, 70)
    ax.grid(axis="x", visible=False)
    ax.legend(loc="upper right")
    ax.set_title("Helmets get the attention; gloves convert at 2× the rate")
    save(fig, "04_categories", "Source: sql/06_category_summary.sql")


def products():
    df = t("05_product_performance").sort_values("revenue_inr")
    fig, ax = plt.subplots(figsize=(9, 5))
    colors = [CATEGORY_COLORS[c] for c in df["item_category"]]
    bars = ax.barh(df["item_name"], df["revenue_inr"], color=colors, height=0.62)
    ax.grid(axis="y", visible=False)
    for bar, (_, r) in zip(bars, df.iterrows()):
        ax.text(bar.get_width() + 1500, bar.get_y() + bar.get_height() / 2,
                f"{inr(r['revenue_inr'])} · {int(r['views']):,} views · {r['view_to_cart_pct']:.0f}% to cart",
                va="center", fontsize=8.5, color=INK)
    ax.set_xlim(0, df["revenue_inr"].max() * 1.65)
    ax.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: inr(v) if v else "0"))
    handles = [plt.Rectangle((0, 0), 1, 1, color=c) for c in CATEGORY_COLORS.values()]
    ax.legend(handles, CATEGORY_COLORS.keys(), loc="lower right")
    ax.set_title("Revenue by product: Axor Gloves is the #1 earner")
    save(fig, "05_products", "Source: sql/05_product_performance.sql")


def daily():
    df = t("07_daily_trend")
    df["event_date"] = pd.to_datetime(df["event_date"])
    fig, axes = plt.subplots(2, 1, figsize=(10, 5.6), sharex=True)
    for ax, col, avg, label in ((axes[0], "sessions", "sessions_7d_avg", "Sessions / day"),
                                (axes[1], "revenue_inr", "revenue_7d_avg", "Revenue / day (₹)")):
        ax.axvspan(pd.Timestamp("2026-10-10"), pd.Timestamp("2026-10-20"), color=ORANGE, alpha=0.12, lw=0)
        ax.plot(df["event_date"], df[col], color=BLUE, alpha=0.35, lw=1.2, label="Daily")
        ax.plot(df["event_date"], df[avg], color=BLUE, lw=2.2, label="7-day average")
        ax.set_ylabel(label)
        ax.grid(axis="x", visible=False)
    axes[1].yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: inr(v) if v else "0"))
    axes[0].text(pd.Timestamp("2026-10-10"), axes[0].get_ylim()[1] * 0.92, " Festive sale\n 10–20 Oct",
                 fontsize=9, color=INK, va="top")
    axes[0].legend(loc="upper left")
    axes[1].xaxis.set_major_formatter(mdates.DateFormatter("%d %b"))
    axes[0].set_title("Daily traffic and revenue: festive sale ≈ 3× normal daily revenue")
    save(fig, "06_daily_trend", "Source: sql/07_daily_trend.sql")


def returning():
    df = t("10_new_vs_returning")
    fig, ax = plt.subplots(figsize=(7, 3.4))
    bars = ax.barh(df["visitor_type"], df["conversion_pct"], color=[BLUE, ORANGE], height=0.5)
    ax.grid(axis="y", visible=False)
    for bar, (_, r) in zip(bars, df.iterrows()):
        ax.text(bar.get_width() + 0.1, bar.get_y() + bar.get_height() / 2,
                f"{r['conversion_pct']:.1f}% conv. · ₹{r['revenue_per_session_inr']:.0f}/session · {int(r['sessions']):,} sessions",
                va="center", fontsize=9)
    ax.set_xlim(0, df["conversion_pct"].max() * 2.4)
    ax.set_xlabel("Session conversion (%)")
    ax.set_title("Returning visitors convert ~1.5× better than new ones")
    save(fig, "07_new_vs_returning", "Source: sql/10_new_vs_returning.sql")


def cohort():
    df = t("11_weekly_cohort_retention")
    m = df.pivot(index="cohort_week", columns="weeks_since_first", values="retention_pct")
    m = m.drop(columns=[0])
    fig, ax = plt.subplots(figsize=(8, 3.8))
    im = ax.imshow(m.values, cmap=matplotlib.colors.LinearSegmentedColormap.from_list(
        "blues", ["#eef4fc", "#86b6ef", "#2a78d6", "#104281"]), aspect="auto", vmin=0, vmax=15)
    ax.grid(False)
    ax.set_xticks(range(m.shape[1]))
    ax.set_xticklabels([f"+{c}w" for c in m.columns])
    ax.set_yticks(range(m.shape[0]))
    sizes = df[df["weeks_since_first"] == 0].set_index("cohort_week")["cohort_users"]
    ax.set_yticklabels([f"Week {w} ({sizes[w]} users)" for w in m.index])
    for i in range(m.shape[0]):
        for j in range(m.shape[1]):
            v = m.values[i, j]
            if pd.notna(v):
                ax.text(j, i, f"{v:.0f}%", ha="center", va="center", fontsize=9,
                        color="white" if v > 8 else INK)
    ax.set_xlabel("Weeks after first visit")
    ax.set_title("Weekly cohorts: only ~1 in 10 visitors returns the next week")
    save(fig, "08_cohort_retention", "Share of each first-visit cohort active again N weeks later. Source: sql/11_weekly_cohort_retention.sql")


def abandonment():
    df = t("08_cart_abandonment")
    fig, ax = plt.subplots(figsize=(8, 3.4))
    bars = ax.barh(df["device_category"][::-1], df["abandoned_at_checkout_value_inr"][::-1],
                   color=[ORANGE if d == "mobile" else BLUE for d in df["device_category"][::-1]], height=0.5)
    ax.grid(axis="y", visible=False)
    for bar, (_, r) in zip(bars, df[::-1].iterrows()):
        ax.text(bar.get_width() + 8000, bar.get_y() + bar.get_height() / 2,
                f"{inr(r['abandoned_at_checkout_value_inr'])} in {int(r['abandoned_at_checkout'])} checkouts",
                va="center", fontsize=9)
    ax.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: inr(v) if v else "0"))
    ax.set_xlim(0, df["abandoned_at_checkout_value_inr"].max() * 1.45)
    ax.set_title("Cart value abandoned after starting checkout")
    save(fig, "09_checkout_abandonment_value", "Peak cart value of sessions that began checkout but did not purchase. Source: sql/08_cart_abandonment.sql")


def main():
    CHARTS.mkdir(parents=True, exist_ok=True)
    for fn in (funnel, device_checkout, channels, categories, products, daily, returning, cohort, abandonment):
        fn()
    print("charts:", ", ".join(sorted(p.name for p in CHARTS.glob("*.png"))))


if __name__ == "__main__":
    main()
