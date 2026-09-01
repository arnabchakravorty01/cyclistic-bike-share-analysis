# Normalized data dictionary

| Field | Type | Role | Description |
|---|---|---|---|
| `ride_id` | string | source | Unique trip identifier |
| `started_at` | datetime | source | Local ride start timestamp |
| `ended_at` | datetime | source | Local ride end timestamp |
| `source_duration_sec` | numeric | source | Legacy Divvy trip duration in seconds |
| `ride_duration_min` | numeric | derived | Primary duration measure in minutes; timestamp difference with source-duration fallback for DST anomalies |
| `start_station_id` | string | source | Start station ID |
| `start_station_name` | string | source | Start station name |
| `end_station_id` | string | source | End station ID |
| `end_station_name` | string | source | End station name |
| `member_casual` | category | normalized | `member` for legacy `Subscriber`; `casual` for legacy `Customer` |
| `month` | integer | derived | Ride-start month, 1-12 |
| `weekday_num` | integer | derived | Monday=0 through Sunday=6 |
| `weekday` | category | derived | Ride-start weekday name |
| `hour` | integer | derived | Ride-start hour, 0-23 |
| `day_type` | category | derived | Weekday or Weekend |
| `season` | category | derived | Winter, Spring, Summer, Fall |
| `same_station` | boolean | derived | Start and end station IDs are equal |
| `commute_window` | boolean | derived | Weekday start in 07:00-09:59 or 16:00-18:59; used as a behavioral proxy, not proof of commute purpose |

## Fields intentionally excluded

`gender`, `birthyear`, and `bikeid` are not required for the assigned marketing question and are excluded from the core analytical model.
