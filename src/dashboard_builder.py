"""Validate and return the canonical self-contained HTML dashboard."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DASHBOARD = ROOT / "dashboard" / "index.html"

ASSETS = [
    "09_executive_dashboard.png",
    "04_monthly_usage.png",
    "10_insight_storyboard.png",
    "05_hourly_profile.png",
    "07_casual_hotspots.png",
    "02_median_duration.png",
    "03_weekend_share.png",
    "06_same_station_share.png",
    "08_heatmap_member.png",
    "08_heatmap_casual.png",
]

def build_dashboard():
    """Confirm that the portfolio's single dashboard is self-contained."""
    html = DASHBOARD.read_text(encoding="utf-8")
    embedded_assets = html.count("data:image/png;base64,")
    if embedded_assets < len(ASSETS):
        raise ValueError("Dashboard is missing one or more embedded figure assets")
    return [DASHBOARD]

if __name__ == "__main__":
    for path in build_dashboard():
        print(path)
