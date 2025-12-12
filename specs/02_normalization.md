# Spec 02: Data Normalization

## Task: Create `src/process_data.py`
1. **Inputs:** Load `src/data/cricket_timeline.csv` and `src/data/github_volume.csv`.
2. **Time Alignment:**
   - Convert both `timestamp` columns to datetime objects (UTC).
   - The Cricket data is event-based (ball-by-ball). The GitHub data is interval-based (5 mins).
   - Use `pandas.merge_asof` to align the GitHub commit counts to the nearest Cricket timestamp.
   - **Crucial:** We want to see the commit count *at the moment* a wicket falls.
3. **Derived Metrics:**
   - Calculate `commit_velocity`: A moving average of commit counts (window=3) to smooth out the line.
4. **Output:** Save the final merged dataset to `src/data/dashboard_ready.csv`.