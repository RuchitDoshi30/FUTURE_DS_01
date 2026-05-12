# Power BI Setup Guide -- NexaRetail Sales Command Center v3

Step-by-step guide to build the dashboard from the 15 CSV files.

---

## Prerequisites

1. **Power BI Desktop** installed (free from Microsoft Store)
2. **Data already exported** -- run `python scripts/01_refresh_data.py` if you haven't
3. CSVs are in: `D:\future_interns\FUTURE_DS_1\sales-dashboard\exports\`

---

## Step 1: Import All Data Tables

1. Open **Power BI Desktop**
2. Click **Get Data** -> **Text/CSV**
3. Navigate to `exports/` and select **sales_transactions.csv**
4. In the preview, click **Transform Data** (this opens Power Query Editor)
5. Verify column types:
   - `order_date` -> Date/Time
   - `revenue`, `profit`, `unit_price`, `shipping_cost` -> Decimal Number
   - `quantity` -> Whole Number
   - Everything else -> Text
6. Click **Close & Apply**
7. Repeat for ALL remaining CSV files:

| File | Key Columns |
|---|---|
| `sales_transactions.csv` | 1,036,962 rows -- the main fact table |
| `monthly_revenue.csv` | month, year, revenue, profit, orders |
| `category_summary.csv` | category, revenue, profit, margin_pct, rev_share |
| `region_summary.csv` | region, revenue, profit, target, attainment |
| `country_summary.csv` | country, revenue, profit, orders |
| `segment_summary.csv` | segment, revenue, profit, orders, aov |
| `product_table.csv` | product_name, category, revenue, profit, rank |
| `discount_analysis.csv` | disc_band, avg_margin, orders, revenue |
| `shipping_analysis.csv` | region, orders, revenue, avg_ship_cost |
| `heatmap_data.csv` | category x 12 month columns |
| `hourly_analysis.csv` | hour, orders, revenue |
| `day_of_week_analysis.csv` | day_of_week, orders, revenue |
| `kpi_summary.csv` | 17 KPI metric columns (1 row) |
| `pipeline_metrics.csv` | stage, count, conv |

---

## Step 2: Apply the NexaRetail Theme

1. Go to **View** -> **Themes** -> **Browse for themes**
2. Select `NexaRetail_Theme.json` from the project root
3. Click **Open**

This sets: Blue/Green/Indigo/Red/Amber palette, IBM Plex Sans font, light gray background.

---

## Step 3: Build Report Pages

### Page 1: Overview

**KPI Cards (top row):**
1. Add 4 **Card** visuals across the top
2. Connect each to `kpi_summary` table:
   - Card 1: `total_revenue` (title: "Total Revenue")
   - Card 2: `net_profit` (title: "Net Profit")
   - Card 3: `total_orders` (title: "Total Orders")
   - Card 4: `aov` (title: "Avg Order Value")
3. Add subtitle text boxes showing YoY: `rev_yoy`, `profit_yoy`, `orders_yoy`, `aov_yoy`

**Revenue Trend (middle left):**
1. Add a **Line Chart**
2. X-axis: `monthly_revenue[month]`
3. Y-axis: `monthly_revenue[revenue]`
4. Legend: `monthly_revenue[year]`
5. This shows 3 trend lines (2009, 2010, 2011) for YoY comparison

**Category Donut (middle right):**
1. Add a **Donut Chart**
2. Values: `category_summary[revenue]`
3. Legend: `category_summary[category]`
4. Shows 7 categories with revenue share

**Top Products Table (bottom):**
1. Add a **Table** visual
2. Columns: rank, product_name, category, revenue, profit, margin_pct
3. Sort by rank ascending
4. Add data bars to the revenue column
5. Add conditional formatting to margin_pct (green > 30%, red < 20%)

---

### Page 2: Revenue Deep Dive

**Multi-Year Revenue Trend:**
- Line chart: monthly_revenue with year as series

**Category Revenue Bars:**
- Clustered bar: category_summary[category] vs [revenue]
- Sort descending by revenue

**Hourly Sales Pattern (NEW - only possible with real data):**
- Column chart: hourly_analysis[hour] vs [revenue]
- Shows peak shopping hours (real timestamps!)

**Day-of-Week Analysis (NEW):**
- Bar chart: day_of_week_analysis[day_of_week] vs [orders]
- Shows busiest days (Thursday tends to be peak for B2B retail)

**Discount Impact:**
- Combo chart: discount_analysis[disc_band]
- Bars = revenue, Line = avg_margin
- Shows how discounts destroy margins

---

### Page 3: Pipeline / Funnel

**Sales Funnel:**
- Funnel visual: pipeline_metrics[stage] and [count]
- Shows: Awareness -> Lead -> Qualified -> Proposal -> Negotiation -> Closed Won

**Conversion Table:**
- Table: stage, count, conv
- Shows conversion % between each stage

**Segment Performance:**
- Clustered bar: segment_summary[segment] vs [revenue] and [profit]
- 4 segments: Premium, Standard, Budget, Walk-In

---

### Page 4: Products

**Product Leaderboard:**
- Table/Matrix visual from `product_table`
- Columns: rank, product_name, category, revenue, profit, total_qty, margin_pct, avg_discount
- Enable sorting on all columns
- Add data bars for revenue
- Add conditional formatting for margin_pct
- Add search box (filter by product_name)
- Shows top 500 out of 3,899 products

---

### Page 5: Regions & Geography

**Region Revenue Bars:**
- Clustered bar: region_summary[region] vs [revenue] + [target]
- 8 regions: UK, Western Europe, Northern Europe, etc.

**Target Attainment Gauges:**
- Gauge visuals for top 3 regions
- Value: revenue, Target: target

**Country Leaderboard:**
- Bar chart: country_summary[country] vs [revenue]
- Top 20 countries

**Heatmap:**
- Matrix visual from heatmap_data
- Rows: category, Columns: months 1-12
- Conditional formatting (color scale) on values
- Shows seasonal patterns per category

---

### Page 6: Customers

**Segment Comparison:**
- Grouped bar: segment_summary (revenue + profit side by side)

**AOV by Segment:**
- Bar chart: segment_summary[segment] vs [aov]
- Shows Premium customers have highest AOV

**Customer Distribution:**
- Donut or pie: segment_summary[orders] by segment

---

### Page 7: Forecast (requires Prophet)

**Forecast Chart:**
- Line chart from forecast_results
- X: date, Y: forecast (solid line), actual (dashed)
- Add area fill between lower_80 and upper_80

**Forecast KPIs:**
- Card: projected total, growth rate, trend direction

---

### Page 8: Insights

**Hourly Heatmap:**
- Matrix: hour x day_of_week with revenue as values
- Color scale shows peak trading times

**Key Findings (text boxes):**
- "UK accounts for 92% of revenue"
- "Seasonal/Christmas is highest-margin category (42%)"
- "Peak hours: 10am-2pm"
- "Thursday is the busiest day"
- "Premium segment (25% of customers) drives 60%+ of revenue"

---

## Step 4: Optional DAX Measures

```dax
// Year-over-Year Revenue Growth
Rev YoY % = 
VAR CurrentYear = CALCULATE(SUM(sales_transactions[revenue]), sales_transactions[year] = 2011)
VAR PreviousYear = CALCULATE(SUM(sales_transactions[revenue]), sales_transactions[year] = 2010)
RETURN DIVIDE(CurrentYear - PreviousYear, PreviousYear, 0)

// Profit Margin %
Margin % = DIVIDE(SUM(sales_transactions[profit]), SUM(sales_transactions[revenue]), 0)

// Average Order Value
AOV = DIVIDE(SUM(sales_transactions[revenue]), DISTINCTCOUNT(sales_transactions[order_id]), 0)

// Customer Count (excluding unknown)
Active Customers = 
CALCULATE(
    DISTINCTCOUNT(sales_transactions[customer_id]),
    sales_transactions[customer_id] <> "UNKNOWN"
)

// Revenue per Customer
Rev Per Customer = DIVIDE([Rev Total], [Active Customers], 0)
```

---

## Step 5: Add Slicers

Add these **slicer** visuals to filter across all pages:

1. **Year Slicer**: `sales_transactions[year]` -- dropdown (2009, 2010, 2011)
2. **Category Slicer**: `sales_transactions[category]` -- checkbox list
3. **Region Slicer**: `sales_transactions[region]` -- dropdown
4. **Segment Slicer**: `sales_transactions[segment]` -- checkbox

Sync slicers across pages: View -> Sync Slicers

---

## Refreshing Data

1. Run `python scripts/01_refresh_data.py`
2. In Power BI, click **Refresh** on the Home tab
3. All visuals update automatically
  