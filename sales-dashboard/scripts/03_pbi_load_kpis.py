"""
03_pbi_load_kpis.py — Power BI Python Data Source (KPI Summary)
================================================================

HOW TO USE THIS IN POWER BI:
    1. Open Power BI Desktop
    2. Click "Get Data" → "Python Script"
    3. Copy-paste the code below into the script editor
    4. Click OK — Power BI will load the kpi_summary table

This gives you a single-row table with all executive KPIs:
    total_revenue, rev_yoy, net_profit, profit_yoy, margin_pct,
    total_orders, orders_yoy, aov, aov_yoy, rev_target, rev_attainment
"""

import pandas as pd

# ── UPDATE THIS PATH to match your project location ──
CSV_PATH = r"D:\future_interns\FUTURE_DS_1\sales-dashboard\exports\kpi_summary.csv"

kpi_summary = pd.read_csv(CSV_PATH)
