"""
helpers.py — Shared Utilities & Constants
==========================================

WHAT THIS FILE DOES:
    Provides formatting functions, color constants, and chart layout helpers
    used across the project. This is the "toolbox" that other files import from.

WHAT WAS REMOVED:
    The old version had ~600 lines of CSS/HTML for the Streamlit web UI.
    Since we migrated to Power BI Desktop, all that CSS is gone.
    Power BI handles styling natively through its theme system.

WHAT REMAINS:
    - Color constants (used by the Power BI theme file)
    - Category color mapping
    - Month labels
    - Currency formatting (fmt) and percentage formatting (fmt_pct)
    - Hex-to-RGBA converter (for any Python visuals in Power BI)
"""


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  COLOR PALETTE — NexaRetail Design System
#  These colors are also defined in NexaRetail_Theme.json for Power BI
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

COLORS = {
    "bg": "#f5f5f7",        # Light gray background
    "surface": "#ffffff",   # White card/panel background
    "surface2": "#fafafa",  # Slightly off-white for table headers
    "border": "#e5e5e7",    # Light border color
    "border2": "#d1d1d6",   # Slightly darker border
    "text": "#1d1d1f",      # Primary text (near-black)
    "text2": "#3a3a3c",     # Secondary text
    "muted": "#86868b",     # Muted/gray text
    "muted2": "#aeaeb2",    # Even lighter muted text
    "blue": "#0071e3",      # Primary accent (links, active states)
    "blue_bg": "#e8f0fe",   # Light blue background
    "green": "#1d9a6c",     # Positive values (up arrows, profit)
    "green_bg": "#e8f8f3",  # Light green background
    "red": "#d93025",       # Negative values (down arrows, losses)
    "red_bg": "#fce8e6",    # Light red background
    "amber": "#c77700",     # Warning/caution color
    "amber_bg": "#fef3d8",  # Light amber background
    "indigo": "#5856d6",    # AI/forecast accent color
}

# Colors assigned to each product category -- used in charts
CAT_COLORS = {
    "Seasonal & Christmas": "#d93025",   # Red
    "Kitchen & Dining": "#1d9a6c",       # Green
    "Home Decor": "#0071e3",             # Blue
    "Storage & Organization": "#5856d6", # Indigo
    "Stationery & Gifts": "#c77700",     # Amber
    "Garden & Outdoor": "#34a853",       # Forest Green
    "General Merchandise": "#86868b",    # Gray
}

# Short month labels for chart axes
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  FORMATTING FUNCTIONS
#  Convert raw numbers into human-readable strings
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def hex_to_rgba(hex_color, alpha=0.6):
    """
    Convert a hex color string like '#0071e3' to 'rgba(0,113,227,0.6)'.

    Used when creating Python visuals in Power BI that need
    semi-transparent colors (Plotly/Matplotlib).
    """
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"


def fmt(val):
    """
    Format a number as a compact currency string.

    Examples:
        1234567  → "$1.23M"
        45300    → "$45.3K"
        230      → "$230"
        -5000    → "-$5.0K"
        None     → "$0"
    """
    if val is None or (isinstance(val, float) and val != val):
        return "$0"
    av = abs(val)
    s = "-" if val < 0 else ""
    if av >= 1e6:
        return f"{s}${av/1e6:.2f}M"
    elif av >= 1e3:
        return f"{s}${av/1e3:.1f}K"
    return f"{s}${av:,.0f}"


def fmt_pct(val):
    """
    Format a number as a percentage with a +/- sign.

    Examples:
        15.3  → "+15.3%"
        -4.2  → "-4.2%"
        0     → "0.0%"
        None  → "0.0%"
    """
    if val is None:
        return "0.0%"
    return f"{val:+.1f}%" if val != 0 else "0.0%"