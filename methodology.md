# Methodology - Ask, Prepare, Process, Analyze, Share, Act

## Ask

**Business question:** How do annual members and casual riders use Cyclistic differently, and which behavioral differences can inform membership-conversion marketing?

**Primary stakeholder:** Director of Marketing and the marketing analytics team.

**Decision supported:** Where, when, and how to test campaigns intended to convert casual riders into annual members.

## Prepare

The supplied files include many Divvy periods. 2019 was selected because it is the **most recent complete uninterrupted 12-month window among the uploaded files**, providing a full seasonal cycle without missing-month bias.

Core dataset: **3,818,004 trips** across Q1-Q4 2019.

The four quarters use two header conventions. Q2's verbose field names are harmonized with the shorter Q1/Q3/Q4 names. `Subscriber` is mapped to `member`; `Customer` is mapped to `casual`.

Gender and birth-year fields are excluded because they do not help answer the assigned business question and are unnecessary for a privacy-minimized analysis.

## Process

The pipeline performs the following checks:

1. Validate required columns and normalize Q2 schema.
2. Parse ride start/end timestamps.
3. Check ride-ID duplication - **0 duplicates detected**.
4. Validate rider type - **0 missing or unmapped values**.
5. Validate station names - **0 missing start/end station names**.
6. Calculate duration from timestamps and compare with source `tripduration`.
7. Detect **13 daylight-saving fallback rows** where local clock time makes `ended_at < started_at`; recover those rows using positive source `tripduration` rather than discarding them.
8. Flag **1,849 rides >24 hours** as extreme duration observations. They are retained for volume/time/station counts but excluded from mean-based duration interpretation.
9. Engineer month, weekday, hour, season, day type, commute-window indicator, and same-station indicator.

Median duration is used as the primary duration statistic because the duration distribution is strongly right-skewed. The `duration_sensitivity.csv` table shows how mean duration changes under 2-hour and 24-hour caps.

## Analyze

The analysis compares segments across:

- annual ride share
- median/mean ride duration
- day-of-week mix
- weekday vs weekend mix
- hourly ride-start distribution
- commute-window concentration
- month and seasonality
- same-station round trips
- high-volume stations and casual share
- top origin-destination routes

## Share

The visual design emphasizes business questions rather than chart volume. The executive dashboard focuses on four KPIs and three decision-driving views: monthly demand, median duration/weekend behavior, and high-casual stations. Supporting figures show hourly patterns, same-station behavior, and day-hour heatmaps.

## Act

Recommendations are framed as testable marketing hypotheses:

1. Geo-target high-casual stations.
2. Concentrate seasonal/weekend spend around casual usage peaks while separately testing commute-context messaging.
3. Use differentiated creative and privacy-safe conversion measurement/A-B testing to learn which behavior segments actually convert.
