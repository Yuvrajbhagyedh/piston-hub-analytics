# Piston Hub Analytics

A GTM + GA4 + Python + SQL case study I built on my own online store, Piston Hub (bike helmets, gloves and boots).

- Store: https://yuvrajbhagyedh.github.io/Piston-hub-Bike-accessory-website/
- Full write-up: [REPORT.md](REPORT.md)

## What I did

I set up Google Tag Manager and GA4 on the store and added e-commerce tracking (product views, add to cart, checkout, purchase and a few more). While doing this I found some bugs on the site, like prices showing in dollars on some pages and Add to Cart not working on most product pages, and fixed them.

The store doesn't have real customers yet, so I wrote a Python script that creates 90 days of shopper data in the same format the site sends to GA4. I then cleaned it, loaded it into SQLite and analysed it with SQL.

The main thing I found: people on mobile drop out of checkout much more than people on desktop (41% complete vs 75%). Fixing that alone could bring in around 25% more revenue. The other findings and my recommendations are in the report.

## Folders

- `docs/` – tracking plan, GTM/GA4 setup steps and screenshots
- `gtm/` – the GTM container export
- `src/` – Python scripts
- `sql/` – the SQL queries
- `outputs/` – charts, query results and the data quality report

## Running it

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python src/run_pipeline.py
```

— Yuvraj K
