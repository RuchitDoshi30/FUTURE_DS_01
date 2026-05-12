# NexaRetail — Sales Analytics & Business Intelligence Dashboard

A comprehensive, production-grade sales analytics solution built on **1,036,962 real e-commerce transactions** from the UCI Online Retail II dataset. This project demonstrates end-to-end data analytics capabilities — from raw data cleaning to executive-ready visualizations and strategic business recommendations.

## Project Overview

| Attribute | Detail |
|---|---|
| **Dataset** | [UCI Online Retail II](https://archive.ics.uci.edu/dataset/502/online+retail+ii) — real UK-based e-commerce transactions |
| **Records** | 1,067,371 raw → 1,036,962 cleaned (97.2% retention) |
| **Period** | December 2009 – December 2011 |
| **Markets** | 40 countries across 8 geographic regions |
| **Products** | 3,899 active SKUs across 7 engineered categories |
| **Tools** | Python (pandas, numpy) + Microsoft Power BI Desktop |

## Key Deliverables

### 1. Data Cleaning & Feature Engineering Pipeline
A **10-stage data quality pipeline** that handles real-world messiness:
- Cancelled invoices, returns, zero-price entries, non-product codes
- Missing Customer IDs (22.8%) — imputed as "Walk-In" segment
- Statistical outlier removal
- **Engineered features:** 7 product categories (NLP keyword extraction), 8 geographic regions (country mapping), 4 customer segments (revenue-based tiering), computed revenue/profit/temporal fields

### 2. Interactive Power BI Dashboard (8 Pages)
| Page | Content |
|---|---|
| Overview | Executive KPIs, revenue trend, category breakdown |
| Revenue Deep Dive | Hourly patterns, day-of-week, discount impact analysis |
| Pipeline & Segments | Sales funnel, conversion rates, segment performance |
| Products | 500-product searchable leaderboard with margin data |
| Regions | Geographic distribution, country rankings, category × month heatmap |
| Customers | Segment revenue comparison, AOV analysis, order distribution |
| Forecast | Time-series revenue projection (Prophet) |
| Insights | Hour × Day heatmap, key business findings, interactive slicers |

### 3. Business Analysis Report
A board-level [ANALYSIS_REPORT.md](ANALYSIS_REPORT.md) with:
- Executive summary with risk severity matrix
- Financial performance overview with YoY growth analysis
- Category, geographic, customer, and product deep dives
- Formal risk register (6 identified risks with mitigations)
- 12 strategic recommendations with expected ROI
- 3-scenario FY2012 revenue projection

## Key Business Insights

| Finding | Detail |
|---|---|
| Total Revenue | GBP 9.17M with 35.5% contribution margin |
| YoY Growth | +41.8% revenue growth (FY2010 → FY2011) |
| Geographic Risk | UK accounts for 92.6% of revenue (critical concentration) |
| Hidden Revenue | GBP 1.3M from anonymous "Walk-In" buyers with no retention strategy |
| Best Category | Kitchen & Dining (GBP 2.38M, 38% margin) |
| Highest Margin | Stationery & Gifts (45% margin, underinvested) |
| B2B Pattern | Peak hours 10am–2pm, Thursday busiest, near-zero weekend trading |
| Top Product | Regency Cakestand 3 Tier (GBP 146K revenue) |

## Project Structure

```
sales-dashboard/
├── data/
│   ├── fetch_data.py          # 10-stage data cleaning + feature engineering pipeline
│   ├── raw/                   # Raw Excel data
│   └── __init__.py
├── processing/
│   ├── transform.py           # KPI computation, aggregations, BI transformations
│   └── __init__.py
├── models/
│   ├── forecast.py            # Prophet time-series forecasting module
│   └── __init__.py
├── utils/
│   ├── helpers.py             # Color palettes, formatting utilities, category maps
│   └── __init__.py
├── scripts/
│   ├── 01_refresh_data.py     # Master pipeline: runs ETL + exports 14 CSV files
│   ├── 02_pbi_load_sales.py   # Power BI Python data source (sales)
│   ├── 03_pbi_load_kpis.py    # Power BI Python data source (KPIs)
│   ├── 04_pbi_load_forecast.py# Power BI Python data source (forecast)
│   └── 05_pbi_load_pipeline.py# Power BI Python data source (pipeline)
├── exports/                   # Pre-computed CSV files for Power BI consumption
│   ├── sales_transactions.csv # Full cleaned dataset 
│   ├── monthly_revenue.csv
│   ├── category_summary.csv
│   ├── region_summary.csv
│   ├── country_summary.csv
│   ├── segment_summary.csv
│   ├── product_table.csv
│   ├── kpi_summary.csv
│   ├── pipeline_metrics.csv
│   ├── hourly_analysis.csv
│   ├── day_of_week_analysis.csv
│   ├── discount_analysis.csv
│   ├── heatmap_data.csv
│   └── shipping_analysis.csv
├── ANALYSIS_REPORT.md         # Comprehensive business analysis & recommendations
├── POWER_BI_SETUP.md          # Step-by-step dashboard build guide
├── NexaRetail_Theme.json      # Power BI custom theme file
├── requirements.txt           # Python dependencies
├── .gitignore
└── README.md
```

## Getting Started

### Prerequisites
- Python 3.9 or higher
- Microsoft Power BI Desktop (for dashboard visualization)
- The UCI Online Retail II dataset (`.xlsx` file placed in `data/raw/`)

### Installation & Data Pipeline

```bash
# 1. Clone the repository
git clone https://github.com/YOUR_USERNAME/sales-dashboard.git
cd sales-dashboard

# 2. Create virtual environment
python -m venv venv
venv\Scripts\activate     # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Download dataset
# Place 'online_retail_II.xlsx' in data/raw/ folder
# Source: https://archive.ics.uci.edu/dataset/502/online+retail+ii

# 5. Run the data pipeline
python scripts/01_refresh_data.py
```

This generates 14 clean CSV files in the `exports/` folder, ready for Power BI.

### Power BI Dashboard Setup
See [POWER_BI_SETUP.md](POWER_BI_SETUP.md) for detailed, step-by-step instructions to build the 8-page dashboard from the exported CSV files.

## Technical Highlights

### Data Cleaning Pipeline (10 Stages)
| Stage | Action | Records Affected |
|---|---|---|
| 1 | Remove cancelled invoices (prefix 'C') | 19,494 |
| 2 | Remove returns (negative quantities) | 3,457 |
| 3 | Remove zero/negative prices | 2,750 |
| 4 | Handle missing descriptions | 0 |
| 5 | Remove non-product codes (POSTAGE, fees) | 4,586 |
| 6 | Impute missing Customer IDs as "Walk-In" | 234,407 |
| 7 | Remove statistical outliers | 122 |
| 8 | Standardise descriptions | All |
| 9 | Compute revenue, profit, temporal fields | All |
| 10 | Engineer categories, regions, segments | All |

### DAX Measures (12 Interactive Measures)
```dax
Total Revenue = SUM(sales_transactions[revenue])
Margin % = DIVIDE([Total Profit], [Total Revenue], 0)
Rev YoY % = VAR CurrYear = CALCULATE([Total Revenue], sales_transactions[year] = 2011)
             VAR PrevYear = CALCULATE([Total Revenue], sales_transactions[year] = 2010)
             RETURN DIVIDE(CurrYear - PrevYear, PrevYear, 0)
```

## Skills Demonstrated

- **Data Cleaning & Preparation** — Handling 1M+ rows with 10 real-world data quality issues
- **Feature Engineering** — NLP-based categorization, geographic mapping, customer segmentation
- **Business KPI Analysis** — Revenue, margin, AOV, YoY growth, conversion rates
- **Trend & Performance Analysis** — Temporal patterns, seasonal decomposition, category performance
- **Data Visualization** — 8-page interactive Power BI dashboard with DAX measures
- **Insight Generation & Reporting** — Board-level analysis report with strategic recommendations
- **Business Storytelling** — Translating data patterns into actionable business decisions

## Tools Used

| Tool | Purpose |
|---|---|
| **Python** | Data cleaning, feature engineering, ETL pipeline |
| **pandas / numpy** | Data manipulation and computation |
| **openpyxl** | Excel file parsing |
| **Power BI Desktop** | Interactive dashboard and DAX measures |
| **Prophet** (optional) | Time-series revenue forecasting |

## Author

Built as part of the **Future Interns Data Science Internship** — demonstrating real-world data analytics capabilities using actual e-commerce transaction data.

## License

This project uses the [UCI Online Retail II dataset](https://archive.ics.uci.edu/dataset/502/online+retail+ii) which is publicly available for educational and research purposes.
