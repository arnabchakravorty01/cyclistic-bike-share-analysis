"""Build the self-contained Cyclistic HTML dashboard with all PNG assets embedded."""
from pathlib import Path
import base64

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "dashboard" / "template.html"
FIGURES = ROOT / "outputs" / "figures"
OUTPUTS = [ROOT / "dashboard" / "index.html", ROOT / "Cyclistic_Interactive_Dashboard.html"]

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
    html = TEMPLATE.read_text(encoding="utf-8")
    for name in ASSETS:
        encoded = base64.b64encode((FIGURES / name).read_bytes()).decode("ascii")
        html = html.replace("{{" + name + "}}", "data:image/png;base64," + encoded)
    for output in OUTPUTS:
        output.write_text(html, encoding="utf-8")
    return OUTPUTS

if __name__ == "__main__":
    for path in build_dashboard():
        print(path)
