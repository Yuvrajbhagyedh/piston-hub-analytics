"""
Run the full pipeline end to end:
  generate events -> validate & clean -> load SQLite -> run SQL -> build charts
"""

import generate_events
import clean_and_load
import run_sql
import make_charts

if __name__ == "__main__":
    print("1/4 Generating simulated GA4 events ...")
    generate_events.main()
    print("\n2/4 Validating, cleaning and loading into SQLite ...")
    clean_and_load.main()
    print("\n3/4 Running SQL analysis ...")
    run_sql.run_all(verbose=False)
    print("    results written to outputs/tables/")
    print("\n4/4 Building charts ...")
    make_charts.main()
    print("\nDone. Read REPORT.md for the findings.")
