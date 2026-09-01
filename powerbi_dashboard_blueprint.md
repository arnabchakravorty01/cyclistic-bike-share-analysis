# Power BI dashboard blueprint

## Page 1 - Executive overview
**KPI cards**: Total rides, member share, casual median duration, casual weekend share, casual same-station share.

**Visuals**:
- Line chart: monthly rides by rider type
- Clustered column chart: median ride duration by rider type
- Clustered column chart: weekend share by rider type
- Horizontal bar chart: casual share at high-volume start stations

**Executive takeaway**: casual riders behave more like seasonal/weekend/leisure users; members show more recurring weekday usage.

## Page 2 - Time behavior
- Line chart: normalized ride share by hour and rider type
- Heatmap: weekday x hour, member rides
- Heatmap: weekday x hour, casual rides
- Slicer: month / season

## Page 3 - Location & route opportunities
- Table: station, member rides, casual rides, total rides, casual share
- Top routes table filtered by rider type
- KPI: same-station trip share
- Optional map only if a current station-coordinate reference is joined separately

## Suggested measures
```DAX
Total Rides = SUM('membership_mix'[rides])

Casual Share =
DIVIDE(
    CALCULATE([Total Rides], 'membership_mix'[member_casual] = "casual"),
    [Total Rides]
)

Weekend Share =
DIVIDE(
    CALCULATE(SUM('day_type_usage'[rides]), 'day_type_usage'[day_type] = "Weekend"),
    SUM('day_type_usage'[rides])
)
```

Use `outputs/summary_tables/` as the Power BI input layer. The tables are deliberately small and presentation-ready.
