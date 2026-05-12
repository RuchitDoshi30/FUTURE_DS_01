"""
forecast.py — Prophet Forecasting Engine
==========================================

WHAT THIS FILE DOES:
    Uses Facebook Prophet to predict future monthly revenue.
    Takes historical monthly revenue data and projects N months ahead,
    along with 80% confidence bands (upper and lower bounds).

HOW IT WORKS:
    1. Takes a DataFrame with 'date' and 'revenue' columns
    2. Feeds it to Prophet (a time-series forecasting library)
    3. Prophet learns the trend + yearly seasonality pattern
    4. Generates future predictions with uncertainty ranges
    5. Returns a clean DataFrame with actual + forecasted values

USED BY:
    - scripts/01_refresh_data.py → exports forecast results as CSV
    - Power BI reads the CSV and renders the forecast chart
"""

import pandas as pd
import logging
from prophet import Prophet

# Suppress noisy Prophet/CmdStan log messages
logging.getLogger("prophet").setLevel(logging.WARNING)
logging.getLogger("cmdstanpy").setLevel(logging.WARNING)


def train_and_forecast(monthly_ts, periods=6):
    """
    Train a Prophet model on monthly revenue and forecast N months ahead.

    INPUTS:
        monthly_ts — DataFrame with 'date' and 'revenue' columns (monthly)
        periods    — how many months to forecast forward (default: 6)

    OUTPUTS:
        Returns a tuple of three values: (forecast_df, summary_dict, error_string)

        forecast_df — DataFrame with columns:
            date, forecast, lower_80, upper_80, trend, type, actual
            'type' is either "actual" or "forecast"

        summary_dict — Key forecast metrics:
            projected_h1_total  — total revenue for the forecast period
            growth_rate         — % change from last actual to last forecasted
            avg_confidence_band — average width of the 80% confidence interval
            trend_direction     — "Bullish" or "Bearish"

        error_string — None if successful, or a description of what went wrong
    """
    try:
        # Need at least 12 months of history for meaningful forecasting
        if monthly_ts is None or monthly_ts.empty or len(monthly_ts) < 12:
            return None, None, "Need at least 12 months of data"

        # Prepare data in Prophet's required format (columns named 'ds' and 'y')
        prophet_df = monthly_ts[["date", "revenue"]].copy()
        prophet_df = prophet_df.rename(columns={"date": "ds", "revenue": "y"})
        prophet_df = prophet_df.dropna(subset=["y"])

        # Configure and train the Prophet model
        # - No daily/weekly seasonality (we only have monthly data)
        # - Yearly seasonality ON (retail has strong annual patterns)
        # - changepoint_prior_scale = 0.05 (conservative trend changes)
        # - interval_width = 0.80 (80% confidence bands)
        model = Prophet(
            daily_seasonality=False,
            weekly_seasonality=False,
            yearly_seasonality=True,
            changepoint_prior_scale=0.05,
            seasonality_prior_scale=10.0,
            interval_width=0.80,
        )
        model.fit(prophet_df)

        # Generate future dates and make predictions
        future = model.make_future_dataframe(periods=periods, freq="MS")
        forecast = model.predict(future)

        # Clean up the output — keep only the columns we need
        result = forecast[["ds", "yhat", "yhat_lower", "yhat_upper", "trend"]].copy()
        result = result.rename(columns={
            "ds": "date", "yhat": "forecast",
            "yhat_lower": "lower_80", "yhat_upper": "upper_80",
        })

        # Mark each row as "actual" (historical) or "forecast" (projected)
        last_actual = prophet_df["ds"].max()
        result["type"] = result["date"].apply(
            lambda d: "actual" if d <= last_actual else "forecast"
        )

        # Merge the actual revenue values back in for comparison
        actual_map = prophet_df.set_index("ds")["y"].to_dict()
        result["actual"] = result["date"].map(actual_map)

        # Build a summary of key forecast metrics
        future_only = result[result["type"] == "forecast"]
        if not future_only.empty:
            projected_total = future_only["forecast"].sum()
            last_actual_rev = prophet_df["y"].iloc[-1]
            first_forecast = future_only["forecast"].iloc[0]
            last_forecast = future_only["forecast"].iloc[-1]
            avg_band = (future_only["upper_80"] - future_only["lower_80"]).mean()

            summary = {
                "projected_h1_total": projected_total,
                "first_month_forecast": first_forecast,
                "last_month_forecast": last_forecast,
                "growth_rate": ((last_forecast - last_actual_rev) / last_actual_rev * 100) if last_actual_rev else 0,
                "avg_confidence_band": avg_band,
                "trend_direction": "Bullish" if last_forecast > first_forecast else "Bearish",
                "periods": len(future_only),
            }
        else:
            summary = None

        return result, summary, None

    except Exception as e:
        return None, None, f"Forecast failed: {str(e)}"


def category_forecast(df, periods=6):
    """
    Run separate forecasts for each product category.

    This lets Power BI show per-category projections
    (e.g. Technology forecast vs. Furniture forecast).

    Skips any category with less than 12 months of data.

    RETURNS:
        Dictionary mapping category name → {forecast: df, summary: dict}
    """
    results = {}
    for cat in df["category"].unique():
        cat_data = df[df["category"] == cat]
        ts = cat_data.groupby(pd.Grouper(key="order_date", freq="MS")).agg(
            revenue=("revenue", "sum")
        ).reset_index().rename(columns={"order_date": "date"})

        if len(ts) < 12:
            continue

        fc, summary, err = train_and_forecast(ts, periods)
        if fc is not None:
            results[cat] = {"forecast": fc, "summary": summary}
    return results
