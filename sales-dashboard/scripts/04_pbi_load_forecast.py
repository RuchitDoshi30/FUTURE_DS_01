"""
04_pbi_load_forecast.py — Power BI Python Data Source (Forecast Results)
=========================================================================

HOW TO USE THIS IN POWER BI:
    1. Open Power BI Desktop
    2. Click "Get Data" → "Python Script"
    3. Copy-paste the code below into the script editor
    4. Click OK — Power BI will load the forecast_results table

The table contains both historical "actual" rows and future "forecast" rows.
Use the 'type' column to filter/color-code actual vs. projected data.
"""

import pandas as pd

# ── UPDATE THIS PATH to match your project location ──
CSV_PATH = r"D:\future_interns\FUTURE_DS_1\sales-dashboard\exports\forecast_results.csv"

forecast_results = pd.read_csv(CSV_PATH, parse_dates=["date"])
