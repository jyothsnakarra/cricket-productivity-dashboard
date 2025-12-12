# Data Ingestion Specification

## Objective
We need to fetch two distinct datasets and align them by timestamp.

## 1. Cricket Data Service
- **Source:** Cricsheet (Free JSON data).
- **Task:** Create a script `src/ingest_cricket.py` that loads the provided JSON file for the 'T20 World Cup Final 2024'.
- **Output:** A Pandas DataFrame with columns: `timestamp_utc`, `run_rate`, `is_wicket` (boolean), `commentary_text`.
- **Note:** Ensure timestamps are converted to ISO 8601.

## 2. GitHub Data Service
- **Source:** GitHub Search API.
- **Task:** Create a script `src/ingest_github.py`.
- **Logic:**
  - Loop through the match duration in 5-minute intervals.
  - For each interval, query the GitHub Search API for `created:START_TIME..END_TIME` to get the total count of commits.
  - **Constraint:** Handle GitHub API rate limits (sleep 2 seconds between requests).
- **Output:** A CSV file `data/commit_volume.csv` with `timestamp`, `commit_count`.

## 3. Data Merging
- Merge both datasets on the nearest timestamp (round to 5 min).