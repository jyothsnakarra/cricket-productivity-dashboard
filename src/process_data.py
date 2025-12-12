#!/usr/bin/env python3
"""
Data Processing Script
Merges and normalizes cricket and GitHub data for dashboard
"""

import pandas as pd
import numpy as np
from datetime import datetime

def process_and_merge_data():
    """
    Load, process, and merge cricket and GitHub data
    """
    
    # Load cricket data
    try:
        cricket_df = pd.read_csv("src/data/cricket_timeline.csv")
        print(f"Loaded cricket data: {len(cricket_df)} records")
    except FileNotFoundError:
        print("ERROR: Cricket data not found. Run ingest_cricket.py first")
        return None
    
    # Load GitHub data
    try:
        github_df = pd.read_csv("src/data/github_volume.csv")
        print(f"Loaded GitHub data: {len(github_df)} records")
    except FileNotFoundError:
        print("ERROR: GitHub data not found. Run ingest_github.py first")
        return None
    
    # Convert timestamps to datetime
    cricket_df['timestamp_utc'] = pd.to_datetime(cricket_df['timestamp_utc'])
    github_df['timestamp'] = pd.to_datetime(github_df['timestamp'])
    
    # Sort by timestamp
    cricket_df = cricket_df.sort_values('timestamp_utc')
    github_df = github_df.sort_values('timestamp')
    
    print("Processing time alignment...")
    
    # Use merge_asof to align GitHub commit counts to cricket timestamps
    # This finds the nearest GitHub data point for each cricket event
    merged_df = pd.merge_asof(
        cricket_df.sort_values('timestamp_utc'),
        github_df.sort_values('timestamp'),
        left_on='timestamp_utc',
        right_on='timestamp',
        direction='nearest'
    )
    
    # Calculate derived metrics
    print("Calculating derived metrics...")
    
    # Commit velocity: moving average of commit counts (window=3)
    merged_df['commit_velocity'] = merged_df['commit_count'].rolling(
        window=3, 
        min_periods=1, 
        center=True
    ).mean()
    
    # Calculate cumulative runs for the match
    merged_df['cumulative_runs'] = merged_df.groupby('innings')['runs'].cumsum()
    
    # Calculate runs per over for visualization
    merged_df['runs_per_over'] = merged_df.groupby(['innings', 'over'])['runs'].transform('sum')
    
    # Add time-based features
    merged_df['match_minute'] = (
        merged_df['timestamp_utc'] - merged_df['timestamp_utc'].iloc[0]
    ).dt.total_seconds() / 60
    
    # Create wicket impact analysis
    # Look at commit count changes around wickets
    wicket_moments = merged_df[merged_df['is_wicket'] == True].copy()
    
    if len(wicket_moments) > 0:
        print(f"Found {len(wicket_moments)} wickets for impact analysis")
        
        # Calculate commit drop percentage for wickets
        for idx, wicket_row in wicket_moments.iterrows():
            # Find commits before and after wicket (within 10 minutes)
            before_mask = (
                (merged_df['timestamp_utc'] >= wicket_row['timestamp_utc'] - pd.Timedelta(minutes=10)) &
                (merged_df['timestamp_utc'] < wicket_row['timestamp_utc'])
            )
            after_mask = (
                (merged_df['timestamp_utc'] > wicket_row['timestamp_utc']) &
                (merged_df['timestamp_utc'] <= wicket_row['timestamp_utc'] + pd.Timedelta(minutes=10))
            )
            
            commits_before = merged_df[before_mask]['commit_count'].mean() if before_mask.any() else 0
            commits_after = merged_df[after_mask]['commit_count'].mean() if after_mask.any() else 0
            
            if commits_before > 0:
                drop_percentage = ((commits_before - commits_after) / commits_before) * 100
                merged_df.loc[idx, 'commit_drop_percentage'] = drop_percentage
            else:
                merged_df.loc[idx, 'commit_drop_percentage'] = 0
    
    # Fill NaN values
    merged_df['commit_drop_percentage'] = merged_df['commit_drop_percentage'].fillna(0)
    
    # Add match phase labels
    total_balls = len(merged_df)
    merged_df['match_phase'] = pd.cut(
        merged_df.index,
        bins=3,
        labels=['Early Overs', 'Middle Overs', 'Death Overs']
    )
    
    # Clean up columns
    columns_to_keep = [
        'timestamp_utc', 'run_rate', 'is_wicket', 'commentary_text',
        'over', 'ball', 'runs', 'innings', 'commit_count', 'commit_velocity',
        'cumulative_runs', 'runs_per_over', 'match_minute', 'commit_drop_percentage',
        'match_phase'
    ]
    
    final_df = merged_df[columns_to_keep].copy()
    
    # Save processed data
    output_file = "src/data/dashboard_ready.csv"
    final_df.to_csv(output_file, index=False)
    
    print(f"\nProcessed data saved to: {output_file}")
    print(f"Final dataset: {len(final_df)} records")
    print(f"Time range: {final_df['timestamp_utc'].min()} to {final_df['timestamp_utc'].max()}")
    print(f"Total wickets: {final_df['is_wicket'].sum()}")
    print(f"Average commit count: {final_df['commit_count'].mean():.1f}")
    
    return final_df

def generate_summary_stats(df):
    """Generate summary statistics for the dashboard"""
    
    if df is None:
        return None
    
    stats = {
        'total_balls': len(df),
        'total_wickets': df['is_wicket'].sum(),
        'total_runs': df['runs'].sum(),
        'total_commits': df['commit_count'].sum(),
        'avg_commit_rate': df['commit_count'].mean(),
        'max_commit_drop': df['commit_drop_percentage'].max(),
        'match_duration_minutes': df['match_minute'].max()
    }
    
    # Wicket impact analysis
    wickets_df = df[df['is_wicket'] == True]
    if len(wickets_df) > 0:
        stats['avg_commit_drop_on_wicket'] = wickets_df['commit_drop_percentage'].mean()
        stats['biggest_wicket_impact'] = wickets_df['commit_drop_percentage'].max()
    else:
        stats['avg_commit_drop_on_wicket'] = 0
        stats['biggest_wicket_impact'] = 0
    
    print("\n=== MATCH SUMMARY ===")
    print(f"Total Balls: {stats['total_balls']}")
    print(f"Total Wickets: {stats['total_wickets']}")
    print(f"Total Runs: {stats['total_runs']}")
    print(f"Total Commits: {stats['total_commits']}")
    print(f"Average Commit Rate: {stats['avg_commit_rate']:.1f} commits/5min")
    print(f"Match Duration: {stats['match_duration_minutes']:.1f} minutes")
    print(f"Average Commit Drop on Wicket: {stats['avg_commit_drop_on_wicket']:.1f}%")
    print(f"Biggest Wicket Impact: {stats['biggest_wicket_impact']:.1f}%")
    
    return stats

if __name__ == "__main__":
    # Process and merge data
    processed_df = process_and_merge_data()
    
    if processed_df is not None:
        # Generate summary statistics
        summary = generate_summary_stats(processed_df)
        
        print("\nSample processed data:")
        print(processed_df.head())
        
        print("\nData processing complete! Ready for dashboard.")
    else:
        print("Data processing failed. Check input files.")