"""
transform.py -- Retail KPI Engine (Real Data)
===============================================

WHAT THIS FILE DOES:
    Takes the cleaned UCI Online Retail II data (~800K rows) and crunches
    it into business metrics. Each function answers a specific question
    like "What's our revenue by month?" or "Which category is most profitable?"

    All functions accept an optional 'year' filter so you can analyze
    a single year (2010, 2011) or all years at once.

HOW POWER BI USES THIS:
    The refresh script (scripts/01_refresh_data.py) calls these functions
    and saves results as CSVs in exports/. Power BI reads those CSVs.

COLUMN REFERENCE (after cleaning):
    order_id, order_date, stock_code, product_name, quantity, unit_price,
    customer_id, country, revenue, profit, year, month, quarter,
    day_of_week, hour, category, region, segment, discount, shipping_cost
"""

import pandas as pd
import numpy as np


def monthly_revenue(df, year=None):
    """
    Calculate total revenue, profit, and order count for each month.
    Missing months are filled with zeros.
    """
    if year:
        df = df[df["year"] == year]
    monthly = df.groupby("month").agg(
        revenue=("revenue", "sum"),
        profit=("profit", "sum"),
        orders=("order_id", "nunique"),
    ).reindex(range(1, 13), fill_value=0)
    return monthly


def yearly_totals(df):
    """
    Calculate total revenue, profit, and orders for each year.
    Returns a dict like: {2010: {revenue: ..., profit: ..., orders: ...}, ...}
    """
    return df.groupby("year").agg(
        revenue=("revenue", "sum"),
        profit=("profit", "sum"),
        orders=("order_id", "nunique"),
    ).to_dict("index")


def category_summary(df, year=None):
    """
    Break down revenue, profit, orders, margin %, and revenue share by category.

    Categories (engineered from product descriptions):
      Seasonal & Christmas, Kitchen & Dining, Home Decor,
      Storage & Organization, Stationery & Gifts, Garden & Outdoor,
      General Merchandise
    """
    if year:
        df = df[df["year"] == year]
    summary = df.groupby("category").agg(
        revenue=("revenue", "sum"),
        profit=("profit", "sum"),
        orders=("order_id", "nunique"),
    ).reset_index()
    summary["margin_pct"] = (summary["profit"] / summary["revenue"] * 100).round(1)
    total_rev = summary["revenue"].sum()
    summary["rev_share"] = (summary["revenue"] / total_rev * 100).round(1)
    return summary.sort_values("revenue", ascending=False).reset_index(drop=True)


def region_summary(df, year=None):
    """
    Break down performance by geographic region.

    Regions (mapped from 40 countries):
      United Kingdom, Western Europe, Northern Europe,
      Southern Europe, Asia-Pacific, Americas,
      Middle East & Africa, Other
    """
    if year:
        df = df[df["year"] == year]
    summary = df.groupby("region").agg(
        revenue=("revenue", "sum"),
        profit=("profit", "sum"),
        orders=("order_id", "nunique"),
    ).reset_index()
    # Target = revenue * 1.05 (5% stretch target)
    summary["target"] = (summary["revenue"] * 1.05).round(0)
    summary["attainment"] = (summary["revenue"] / summary["target"] * 100).round(1)
    return summary.sort_values("revenue", ascending=False).reset_index(drop=True)


def country_summary(df, year=None, top_n=20):
    """
    Top N countries by revenue.
    More useful than state_summary for international data.
    """
    if year:
        df = df[df["year"] == year]
    summary = df.groupby("country").agg(
        revenue=("revenue", "sum"),
        profit=("profit", "sum"),
        orders=("order_id", "nunique"),
    ).reset_index().nlargest(top_n, "revenue")
    return summary


# Keep the old name as an alias for backward compatibility
state_summary = country_summary


def segment_summary(df, year=None):
    """
    Break down performance by customer segment.

    Segments (engineered from spending patterns):
      Premium (top 25%), Standard (middle 50%),
      Budget (bottom 25%), Walk-In (unknown customers)
    """
    if year:
        df = df[df["year"] == year]
    summary = df.groupby("segment").agg(
        revenue=("revenue", "sum"),
        profit=("profit", "sum"),
        orders=("order_id", "nunique"),
    ).reset_index()
    summary["aov"] = (summary["revenue"] / summary["orders"]).round(2)
    return summary.sort_values("revenue", ascending=False).reset_index(drop=True)


def product_table(df, year=None):
    """
    Build a product-level leaderboard ranked by revenue.
    Each row: product name, category, revenue, profit, orders, margin %, rank.
    """
    if year:
        df = df[df["year"] == year]
    products = df.groupby(["product_name", "category"]).agg(
        revenue=("revenue", "sum"),
        profit=("profit", "sum"),
        orders=("order_id", "nunique"),
        avg_discount=("discount", "mean"),
        total_qty=("quantity", "sum"),
    ).reset_index()
    products["margin_pct"] = np.where(
        products["revenue"] != 0,
        (products["profit"] / products["revenue"] * 100).round(1),
        0,
    )
    products["avg_discount"] = (products["avg_discount"] * 100).round(0)
    products = products.sort_values("revenue", ascending=False).reset_index(drop=True)
    products["rank"] = range(1, len(products) + 1)
    return products


def discount_analysis(df, year=None):
    """
    Analyze how different discount levels affect profit margins.
    Groups orders into bands (0%, 5%, 10%, 15%, 20%) and shows
    average margin for each band.
    """
    if year:
        df = df[df["year"] == year]
    df = df.copy()
    bins = [-.01, 0.001, 0.06, 0.11, 0.16, 0.21, 1.0]
    labels = ["0%", "5%", "10%", "15%", "20%", "20%+"]
    df["disc_band"] = pd.cut(df["discount"], bins=bins, labels=labels)
    summary = df.groupby("disc_band", observed=True).agg(
        avg_margin=("profit", lambda x: (x.sum() / df.loc[x.index, "revenue"].sum() * 100) if df.loc[x.index, "revenue"].sum() != 0 else 0),
        orders=("order_id", "nunique"),
        revenue=("revenue", "sum"),
    ).reset_index()
    return summary


def shipping_analysis(df, year=None):
    """
    Analyze shipping costs by region.
    Since we don't have shipping mode in the real data, we group by region instead.
    """
    if year:
        df = df[df["year"] == year]
    summary = df.groupby("region").agg(
        orders=("order_id", "nunique"),
        revenue=("revenue", "sum"),
        avg_ship_cost=("shipping_cost", "mean"),
        total_ship_cost=("shipping_cost", "sum"),
    ).reset_index()
    return summary.sort_values("revenue", ascending=False).reset_index(drop=True)


def heatmap_data(df, year=None):
    """
    Create a Category x Month revenue matrix for heatmap visualization.
    Rows = product categories, Columns = months (1-12).
    """
    if year:
        df = df[df["year"] == year]
    pivot = df.pivot_table(
        values="revenue", index="category", columns="month", aggfunc="sum", fill_value=0
    )
    return pivot


def monthly_time_series(df):
    """
    Build a full monthly time series across all years for forecasting.
    Each row: year, month, date, revenue, profit, orders.
    """
    ts = df.groupby(["year", "month"]).agg(
        revenue=("revenue", "sum"),
        profit=("profit", "sum"),
        orders=("order_id", "nunique"),
    ).reset_index()
    ts["date"] = pd.to_datetime(ts[["year", "month"]].assign(day=1))
    ts = ts.sort_values("date").reset_index(drop=True)
    return ts


def hourly_analysis(df, year=None):
    """
    NEW: Analyze order patterns by hour of day.
    Shows when customers are most active (unique to real timestamp data).
    """
    if year:
        df = df[df["year"] == year]
    summary = df.groupby("hour").agg(
        orders=("order_id", "nunique"),
        revenue=("revenue", "sum"),
        avg_order_value=("revenue", "mean"),
    ).reset_index()
    return summary


def day_of_week_analysis(df, year=None):
    """
    NEW: Analyze order patterns by day of week.
    Shows busiest days (e.g. Thursday tends to be peak for B2B retail).
    """
    if year:
        df = df[df["year"] == year]
    day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    summary = df.groupby("day_of_week").agg(
        orders=("order_id", "nunique"),
        revenue=("revenue", "sum"),
    ).reset_index()
    summary["day_of_week"] = pd.Categorical(summary["day_of_week"], categories=day_order, ordered=True)
    return summary.sort_values("day_of_week").reset_index(drop=True)


def compute_kpis(df, year=None):
    """
    Calculate executive KPIs for the Overview dashboard page.

    If no year specified, uses the most recent full year in the data.
    Compares current year vs. previous year for YoY growth.
    """
    available_years = sorted(df["year"].unique())
    if year is None:
        year = available_years[-1]

    curr = df[df["year"] == year]
    prev_year = year - 1
    prev = df[df["year"] == prev_year] if prev_year in available_years else pd.DataFrame()

    rev_curr = curr["revenue"].sum()
    prf_curr = curr["profit"].sum()
    ord_curr = curr["order_id"].nunique()
    aov_curr = rev_curr / ord_curr if ord_curr else 0
    cust_curr = curr[curr["customer_id"] != "UNKNOWN"]["customer_id"].nunique()

    rev_prev = prev["revenue"].sum() if not prev.empty else 0
    prf_prev = prev["profit"].sum() if not prev.empty else 0
    ord_prev = prev["order_id"].nunique() if not prev.empty else 0
    aov_prev = rev_prev / ord_prev if ord_prev else 0

    rev_target = rev_curr * 1.04
    margin_pct = (prf_curr / rev_curr * 100) if rev_curr else 0

    return {
        "total_revenue": round(rev_curr, 2),
        "rev_yoy": round(((rev_curr - rev_prev) / rev_prev * 100) if rev_prev else 0, 1),
        "rev_target": round(rev_target, 2),
        "rev_attainment": round((rev_curr / rev_target * 100) if rev_target else 0, 1),
        "net_profit": round(prf_curr, 2),
        "profit_yoy": round(((prf_curr - prf_prev) / prf_prev * 100) if prf_prev else 0, 1),
        "margin_pct": round(margin_pct, 1),
        "total_orders": ord_curr,
        "orders_yoy": round(((ord_curr - ord_prev) / ord_prev * 100) if ord_prev else 0, 1),
        "aov": round(aov_curr, 2),
        "aov_yoy": round(((aov_curr - aov_prev) / aov_prev * 100) if aov_prev else 0, 1),
        "unique_customers": cust_curr,
        "prev_revenue": round(rev_prev, 2),
        "prev_profit": round(prf_prev, 2),
        "prev_orders": ord_prev,
        "total_rows": len(df),
        "fiscal_year": year,
    }


def pipeline_metrics(df, year=None):
    """
    Simulate a sales funnel from the order data.
    Works backwards from closed orders to estimate upper funnel stages.
    """
    if year:
        df = df[df["year"] == year]
    total_orders = df["order_id"].nunique()
    total_customers = df[df["customer_id"] != "UNKNOWN"]["customer_id"].nunique()

    # Estimate funnel stages from actual data
    awareness = int(total_customers * 5.5)
    leads = int(awareness * 0.45)
    qualified = int(leads * 0.38)
    proposal = int(qualified * 0.44)
    negotiation = int(proposal * 0.48)
    closed = total_orders

    stages = [
        {"stage": "Awareness", "count": awareness, "conv": "-"},
        {"stage": "Lead", "count": leads, "conv": f"{leads/awareness*100:.1f}%" if awareness else "-"},
        {"stage": "Qualified", "count": qualified, "conv": f"{qualified/leads*100:.1f}%" if leads else "-"},
        {"stage": "Proposal", "count": proposal, "conv": f"{proposal/qualified*100:.1f}%" if qualified else "-"},
        {"stage": "Negotiation", "count": negotiation, "conv": f"{negotiation/proposal*100:.1f}%" if proposal else "-"},
        {"stage": "Closed Won", "count": closed, "conv": f"{closed/negotiation*100:.1f}%" if negotiation else "-"},
    ]
    return stages
