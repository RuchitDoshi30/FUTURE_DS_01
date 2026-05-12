"""
02_pbi_load_sales.py — Power BI Python Data Source (Sales Transactions)
========================================================================

HOW TO USE THIS IN POWER BI:
    1. Open Power BI Desktop
    2. Click "Get Data" → "Python Script"
    3. Copy-paste the code below into the script editor
    4. Click OK — Power BI will load the sales_transactions table
    5. You can then build visuals on top of this table

NOTE: Make sure the CSV_PATH below points to your actual exports folder.
"""

import pandas as pd

# ── UPDATE THIS PATH to match your project location ──
CSV_PATH = r"D:\future_interns\FUTURE_DS_1\sales-dashboard\exports\sales_transactions.csv"

# Load the full transaction table
sales_transactions = pd.read_csv(CSV_PATH, parse_dates=["order_date"])

# Power BI will automatically detect the 'sales_transactions' DataFrame
# and offer it as a table to import
