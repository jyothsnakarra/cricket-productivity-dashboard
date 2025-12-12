# Dashboard Spec (Streamlit)

Create a `src/app.py` using Streamlit.

## Layout
1. **Title:** "The Wicket-Down Downtime: T20 World Cup Final vs. Global Productivity"
2. **Top Chart (The Match):**
   - Line chart of "Runs per Over".
   - **Crucial:** Add red vertical lines (annotations) whenever `is_wicket` is True.
3. **Bottom Chart (The Code):**
   - Area chart of "GitHub Commits (Global)".
   - Color: Green.
4. **The Interaction:**
   - Both charts must share the same X-Axis (Time).
   - When the user hovers over a Wicket, show a tooltip: "Kohli Out -> Commits Dropped by 40%".

## Styling
- Use a dark theme.
- Use Plotly Express for interactive charts.