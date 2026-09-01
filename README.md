# SQL layer

`analysis_queries.sql` contains business-facing aggregation queries that mirror the main Python analysis. The SQL assumes a normalized `cyclistic_rides` table using the fields in `docs/data_dictionary.md`.

The project uses Python for the reproducible raw-file cleaning because the 2019 Q2 schema differs from the other quarters and because the daylight-saving duration anomaly is easiest to document in one controlled transformation layer. SQL then demonstrates how the cleaned analytical model can be queried for reporting.
