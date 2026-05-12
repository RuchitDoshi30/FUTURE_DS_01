"""
01_refresh_data.py -- Master Data Refresh Script (Real Data)
==============================================================

WHAT THIS FILE DOES:
    Loads the real UCI Online Retail II dataset (1,067,371 rows),
    runs a 10-step data cleaning pipeline, computes all business
    metrics, and exports everything as CSV files for Power BI.

HOW TO USE:
    1. Make sure online_retail_II.xlsx is in data/raw/
    2. Run: python scripts/01_refresh_data.py
    3. Check exports/ folder for 15 CSV files
    4. Open Power BI Desktop and refresh your data sources
"""

import sys
import os

# Add the project root to Python's path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

import pandas as pd
from datetime import datetime
from data.fetch_data import fetch_all_data
from processing.transform import (
    monthly_revenue, yearly_totals, category_summary, region_summary,
    country_summary, segment_summary, product_table, discount_analysis,
    shipping_analysis, heatmap_data, monthly_time_series, compute_kpis,
    pipeline_metrics, hourly_analysis, day_of_week_analysis,
)

try:
    from models.forecast import train_and_forecast
    HAS_PROPHET = True
except ImportError:
    HAS_PROPHET = False


def main():
    """Run the full data pipeline and export CSVs for Power BI."""

    print("=" * 65)
    print("  NexaRetail -- Real Data Pipeline (UCI Online Retail II)")
    print("  Started at: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("=" * 65)

    # Create exports folder
    exports_dir = os.path.join(project_root, "exports")
    os.makedirs(exports_dir, exist_ok=True)

    # ===== PHASE 1: Load and Clean =====
    print("\n[PHASE 1] Loading and cleaning raw data...")
    data = fetch_all_data()

    if data["errors"]:
        print("  ERRORS:")
        for e in data["errors"]:
            print(f"    - {e}")
        return

    df = data["sales_df"]

    # Print the cleaning log
    print("\n  --- Data Cleaning Log ---")
    for line in data["log"]:
        print(f"  {line}")

    print(f"\n  Dataset: {data['api_source']}")
    print(f"  Columns: {list(df.columns)}")
    years = sorted(df["year"].unique())
    print(f"  Years in data: {years}")
    print(f"  Categories: {sorted(df['category'].unique())}")
    print(f"  Regions: {sorted(df['region'].unique())}")
    print(f"  Segments: {sorted(df['segment'].unique())}")

    # ===== PHASE 2: Export Transactions =====
    print("\n[PHASE 2] Exporting transaction data...")
    df.to_csv(os.path.join(exports_dir, "sales_transactions.csv"), index=False)
    print(f"  [OK] sales_transactions.csv ({len(df):,} rows x {len(df.columns)} cols)")

    # ===== PHASE 3: Business Calculations =====
    print("\n[PHASE 3] Running business calculations...")

    # Use the most recent full year for current-year analyses
    current_year = max(years)

    # Monthly revenue by year (all years stacked)
    monthly_all = []
    for yr in years:
        m = monthly_revenue(df, yr)
        m["year"] = yr
        m.index.name = "month"
        monthly_all.append(m.reset_index())
    monthly_df = pd.concat(monthly_all, ignore_index=True)
    monthly_df.to_csv(os.path.join(exports_dir, "monthly_revenue.csv"), index=False)
    print(f"  [OK] monthly_revenue.csv ({len(monthly_df)} rows)")

    # Category summary
    cat = category_summary(df, year=current_year)
    cat.to_csv(os.path.join(exports_dir, "category_summary.csv"), index=False)
    print(f"  [OK] category_summary.csv ({len(cat)} categories)")

    # Region summary
    reg = region_summary(df, year=current_year)
    reg.to_csv(os.path.join(exports_dir, "region_summary.csv"), index=False)
    print(f"  [OK] region_summary.csv ({len(reg)} regions)")

    # Country summary (top 20)
    countries = country_summary(df, year=current_year, top_n=20)
    countries.to_csv(os.path.join(exports_dir, "country_summary.csv"), index=False)
    print(f"  [OK] country_summary.csv ({len(countries)} countries)")

    # Segment summary
    seg = segment_summary(df, year=current_year)
    seg.to_csv(os.path.join(exports_dir, "segment_summary.csv"), index=False)
    print(f"  [OK] segment_summary.csv ({len(seg)} segments)")

    # Product leaderboard (top 500)
    prods = product_table(df, year=current_year)
    prods_top = prods.head(500)
    prods_top.to_csv(os.path.join(exports_dir, "product_table.csv"), index=False)
    print(f"  [OK] product_table.csv ({len(prods_top)} products, {len(prods):,} total)")

    # Discount analysis
    disc = discount_analysis(df, year=current_year)
    disc.to_csv(os.path.join(exports_dir, "discount_analysis.csv"), index=False)
    print(f"  [OK] discount_analysis.csv ({len(disc)} bands)")

    # Shipping/region analysis
    ship = shipping_analysis(df, year=current_year)
    ship.to_csv(os.path.join(exports_dir, "shipping_analysis.csv"), index=False)
    print(f"  [OK] shipping_analysis.csv ({len(ship)} regions)")

    # Heatmap matrix
    hm = heatmap_data(df, year=current_year)
    hm.to_csv(os.path.join(exports_dir, "heatmap_data.csv"))
    print(f"  [OK] heatmap_data.csv ({len(hm)} categories x 12 months)")

    # Hourly analysis (NEW - unique to real data with timestamps)
    hourly = hourly_analysis(df, year=current_year)
    hourly.to_csv(os.path.join(exports_dir, "hourly_analysis.csv"), index=False)
    print(f"  [OK] hourly_analysis.csv ({len(hourly)} hours)")

    # Day-of-week analysis (NEW)
    dow = day_of_week_analysis(df, year=current_year)
    dow.to_csv(os.path.join(exports_dir, "day_of_week_analysis.csv"), index=False)
    print(f"  [OK] day_of_week_analysis.csv ({len(dow)} days)")

    # ===== PHASE 4: Forecast =====
    print("\n[PHASE 4] Running Prophet forecast...")
    if not HAS_PROPHET:
        print("  [!] Prophet not installed -- skipping. Run: pip install prophet")
    else:
        ts = monthly_time_series(df)
        fc_df, fc_summary, fc_err = train_and_forecast(ts, periods=6)

        if fc_err:
            print(f"  [!] Forecast error: {fc_err}")
        elif fc_df is not None:
            fc_df.to_csv(os.path.join(exports_dir, "forecast_results.csv"), index=False)
            print(f"  [OK] forecast_results.csv ({len(fc_df)} rows)")
            if fc_summary:
                print(f"       Projected total: ${fc_summary['projected_h1_total']:,.0f}")
                print(f"       Trend: {fc_summary['trend_direction']}")

    # ===== PHASE 5: KPIs and Pipeline =====
    print("\n[PHASE 5] Computing executive KPIs...")
    kpis = compute_kpis(df, year=current_year)
    kpi_df = pd.DataFrame([kpis])
    kpi_df.to_csv(os.path.join(exports_dir, "kpi_summary.csv"), index=False)
    print(f"  [OK] kpi_summary.csv ({len(kpis)} metrics)")
    print(f"       Revenue: ${kpis['total_revenue']:,.0f}")
    print(f"       Orders: {kpis['total_orders']:,}")
    print(f"       Customers: {kpis['unique_customers']:,}")
    print(f"       AOV: ${kpis['aov']:,.2f}")

    pipeline = pipeline_metrics(df, year=current_year)
    pipe_df = pd.DataFrame(pipeline)
    pipe_df.to_csv(os.path.join(exports_dir, "pipeline_metrics.csv"), index=False)
    print(f"  [OK] pipeline_metrics.csv ({len(pipe_df)} stages)")

    # ===== DONE =====
    csv_count = len([f for f in os.listdir(exports_dir) if f.endswith('.csv')])
    print("\n" + "=" * 65)
    print(f"  [OK] ALL DONE -- {csv_count} CSV files exported to exports/")
    print(f"  Finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 65)
    print("\n  Next steps:")
    print("  1. Open Power BI Desktop")
    print("  2. Get Data -> Text/CSV -> select files from exports/")
    print("  3. Apply NexaRetail_Theme.json")
    print("  4. Build your report pages!")


if __name__ == "__main__":
    main()
