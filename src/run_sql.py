"""
Run every query in sql/ against data/piston_hub.db and save each result
to outputs/tables/<query>.csv. Prints the results so they can be reviewed.
"""

import sqlite3
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "data" / "piston_hub.db"
SQL_DIR = ROOT / "sql"
OUT = ROOT / "outputs" / "tables"


def run_all(verbose=True):
    OUT.mkdir(parents=True, exist_ok=True)
    results = {}
    with sqlite3.connect(DB) as con:
        for path in sorted(SQL_DIR.glob("*.sql")):
            df = pd.read_sql_query(path.read_text(), con)
            df.to_csv(OUT / f"{path.stem}.csv", index=False)
            results[path.stem] = df
            if verbose:
                question = path.read_text().splitlines()[0].lstrip("- ")
                print(f"\n=== {path.stem}: {question}")
                print(df.head(15).to_string(index=False))
    return results


if __name__ == "__main__":
    pd.set_option("display.width", 200)
    run_all()
