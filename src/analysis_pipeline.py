"""Cyclistic / Divvy 2019 analysis pipeline.

Designed for the Google Data Analytics capstone business question:
How do annual members and casual riders use the service differently?

Usage:
    python src/analysis_pipeline.py --raw-dir data/raw --output-dir outputs/summary_tables

The script does not redistribute raw trip data. It expects the four 2019 Divvy
quarterly ZIP files to be downloaded separately and placed in --raw-dir.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import zipfile
import json
import numpy as np
import pandas as pd

USER_MAP = {"Subscriber": "member", "Customer": "casual"}
WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]


def locate_quarters(raw_dir: Path) -> list[Path]:
    files = []
    for q in range(1, 5):
        matches = sorted(raw_dir.glob(f"*2019_Q{q}*.zip"))
        if not matches:
            raise FileNotFoundError(f"Missing 2019 Q{q} ZIP in {raw_dir}")
        files.append(matches[0])
    return files


def csv_member(zip_path: Path) -> str:
    with zipfile.ZipFile(zip_path) as zf:
        members = [n for n in zf.namelist() if n.lower().endswith(".csv") and not n.startswith("__MACOSX")]
    if not members:
        raise ValueError(f"No CSV found in {zip_path}")
    return members[0]


def load_quarter(zip_path: Path) -> pd.DataFrame:
    """Load and normalize one 2019 quarter into a consistent schema."""
    member = csv_member(zip_path)
    with zipfile.ZipFile(zip_path) as zf:
        with zf.open(member) as fh:
            header = pd.read_csv(fh, nrows=0).columns.tolist()

        q2_style = "01 - Rental Details Rental ID" in header
        mapping = {
            ("01 - Rental Details Rental ID" if q2_style else "trip_id"): "ride_id",
            ("01 - Rental Details Local Start Time" if q2_style else "start_time"): "started_at",
            ("01 - Rental Details Local End Time" if q2_style else "end_time"): "ended_at",
            ("01 - Rental Details Duration In Seconds Uncapped" if q2_style else "tripduration"): "source_duration_sec",
            ("03 - Rental Start Station ID" if q2_style else "from_station_id"): "start_station_id",
            ("03 - Rental Start Station Name" if q2_style else "from_station_name"): "start_station_name",
            ("02 - Rental End Station ID" if q2_style else "to_station_id"): "end_station_id",
            ("02 - Rental End Station Name" if q2_style else "to_station_name"): "end_station_name",
            ("User Type" if q2_style else "usertype"): "source_user_type",
        }
        with zf.open(member) as fh:
            df = pd.read_csv(fh, usecols=list(mapping), low_memory=False).rename(columns=mapping)

    df["started_at"] = pd.to_datetime(df["started_at"], errors="coerce")
    df["ended_at"] = pd.to_datetime(df["ended_at"], errors="coerce")
    df["source_duration_sec"] = pd.to_numeric(
        df["source_duration_sec"].astype(str).str.replace(",", "", regex=False), errors="coerce"
    )
    df["member_casual"] = df["source_user_type"].map(USER_MAP)

    calc_duration = (df["ended_at"] - df["started_at"]).dt.total_seconds()
    # DST fallback on 2019-11-03 creates a small set of negative local-clock differences.
    fallback = (calc_duration <= 0) & (df["source_duration_sec"] > 0)
    df["duration_sec"] = calc_duration.where(~fallback, df["source_duration_sec"])
    df["duration_fallback"] = fallback

    valid = (
        df["started_at"].notna()
        & df["ended_at"].notna()
        & df["member_casual"].notna()
        & (df["duration_sec"] > 0)
    )
    df = df.loc[valid].copy()
    df["ride_duration_min"] = df["duration_sec"] / 60
    df["month"] = df["started_at"].dt.month.astype("int8")
    df["weekday_num"] = df["started_at"].dt.dayofweek.astype("int8")
    df["weekday"] = df["weekday_num"].map(dict(enumerate(WEEKDAYS)))
    df["hour"] = df["started_at"].dt.hour.astype("int8")
    df["day_type"] = np.where(df["weekday_num"] >= 5, "Weekend", "Weekday")
    df["season"] = np.select(
        [df["month"].isin([12, 1, 2]), df["month"].isin([3, 4, 5]), df["month"].isin([6, 7, 8]), df["month"].isin([9, 10, 11])],
        ["Winter", "Spring", "Summer", "Fall"],
        default="Unknown",
    )
    df["same_station"] = df["start_station_id"].astype(str).eq(df["end_station_id"].astype(str))
    df["commute_window"] = (df["weekday_num"] < 5) & df["hour"].isin([7, 8, 9, 16, 17, 18])
    return df


def run(raw_dir: Path, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    quarters = locate_quarters(raw_dir)

    compact_frames = []
    station_parts = []
    route_parts = []
    hashes = []
    audit = {"raw_rows": 0, "duration_fallback_to_source_rows": 0}

    for path in quarters:
        # Count raw rows separately so validation exclusions remain auditable.
        member = csv_member(path)
        with zipfile.ZipFile(path) as zf, zf.open(member) as fh:
            raw_count = sum(1 for _ in fh) - 1
        audit["raw_rows"] += raw_count

        df = load_quarter(path)
        audit["duration_fallback_to_source_rows"] += int(df["duration_fallback"].sum())
        hashes.append(pd.util.hash_pandas_object(df["ride_id"].astype(str), index=False).to_numpy(dtype="uint64"))

        compact_frames.append(
            df[["member_casual", "ride_duration_min", "month", "weekday_num", "weekday", "hour", "day_type", "season", "same_station", "commute_window"]].copy()
        )
        station_parts.append(
            df.groupby(["member_casual", "start_station_name"], as_index=False).size().rename(columns={"size": "rides"})
        )
        route_parts.append(
            df.groupby(["member_casual", "start_station_name", "end_station_name"], as_index=False).size().rename(columns={"size": "rides"})
        )

    data = pd.concat(compact_frames, ignore_index=True)
    hash_values = np.concatenate(hashes)
    hash_values.sort()
    audit["duplicate_ride_id_hashes"] = int(np.sum(hash_values[1:] == hash_values[:-1]))
    audit["analysis_rows"] = len(data)
    audit["rides_over_24_hours"] = int((data["ride_duration_min"] > 1440).sum())

    membership = data.groupby("member_casual").size().rename("rides").reset_index()
    membership["share"] = membership["rides"] / membership["rides"].sum()
    membership.to_csv(output_dir / "membership_mix.csv", index=False)

    duration = data.groupby("member_casual")["ride_duration_min"].agg(
        rides="size", mean_duration_min="mean", median_duration_min="median"
    ).reset_index()
    duration.to_csv(output_dir / "duration_summary.csv", index=False)

    monthly = data.groupby(["member_casual", "month"])["ride_duration_min"].agg(
        rides="size", avg_duration_min="mean", median_duration_min="median"
    ).reset_index()
    monthly["month_name"] = monthly["month"].map({i + 1: m for i, m in enumerate(MONTHS)})
    monthly.to_csv(output_dir / "monthly_usage.csv", index=False)

    weekday = data.groupby(["member_casual", "weekday_num", "weekday"])["ride_duration_min"].agg(
        rides="size", avg_duration_min="mean", median_duration_min="median"
    ).reset_index()
    weekday.to_csv(output_dir / "weekday_usage.csv", index=False)

    hourly = data.groupby(["member_casual", "hour"])["ride_duration_min"].agg(
        rides="size", avg_duration_min="mean", median_duration_min="median"
    ).reset_index()
    hourly.to_csv(output_dir / "hourly_usage.csv", index=False)

    day_hour = data.groupby(["member_casual", "weekday_num", "weekday", "hour"]).size().rename("rides").reset_index()
    day_hour.to_csv(output_dir / "day_hour_heatmap.csv", index=False)

    same_station = data.groupby("member_casual")["same_station"].agg(same_station_rides="sum", rides="size").reset_index()
    same_station["same_station_share"] = same_station["same_station_rides"] / same_station["rides"]
    same_station.to_csv(output_dir / "same_station_usage.csv", index=False)

    starts = pd.concat(station_parts, ignore_index=True).groupby(["member_casual", "start_station_name"], as_index=False)["rides"].sum()
    station = starts.pivot(index="start_station_name", columns="member_casual", values="rides").fillna(0).reset_index()
    station = station.rename(columns={"member": "member_rides", "casual": "casual_rides"})
    station["total_rides"] = station["member_rides"] + station["casual_rides"]
    station["casual_share"] = station["casual_rides"] / station["total_rides"]
    station.sort_values("total_rides", ascending=False).to_csv(output_dir / "start_station_summary.csv", index=False)

    routes = pd.concat(route_parts, ignore_index=True).groupby(
        ["member_casual", "start_station_name", "end_station_name"], as_index=False
    )["rides"].sum()
    routes.sort_values(["member_casual", "rides"], ascending=[True, False]).groupby("member_casual").head(50).to_csv(
        output_dir / "top_routes.csv", index=False
    )

    with open(output_dir / "pipeline_audit.json", "w", encoding="utf-8") as fh:
        json.dump(audit, fh, indent=2)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw-dir", type=Path, default=Path("data/raw"))
    parser.add_argument("--output-dir", type=Path, default=Path("outputs/summary_tables"))
    args = parser.parse_args()
    run(args.raw_dir, args.output_dir)
