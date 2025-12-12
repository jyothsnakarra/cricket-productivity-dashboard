#!/usr/bin/env python3
"""
Cricket Data Ingestion Script
Processes Cricsheet JSON data for T20 World Cup Final 2024
"""

import json
import pandas as pd
import os
from datetime import datetime, timedelta
import glob

def load_cricket_data():
    """Load and process cricket data from JSON files"""
    
    # Look for T20 World Cup Final 2024 data files
    data_dir = "src/data"
    json_files = glob.glob(f"{data_dir}/*.json")
    
    if not json_files:
        print("No JSON files found in src/data/")
        return None
    
    # For demo purposes, we'll use the first available JSON file
    # In a real scenario, you'd identify the specific T20 World Cup Final file
    cricket_file = json_files[0]
    print(f"Loading cricket data from: {cricket_file}")
    
    try:
        with open(cricket_file, 'r') as f:
            match_data = json.load(f)
    except Exception as e:
        print(f"Error loading JSON file: {e}")
        return None
    
    # Extract match info
    info = match_data.get('info', {})
    innings = match_data.get('innings', [])
    
    # Get match start time (use a realistic T20 World Cup Final time)
    match_date = info.get('dates', ['2024-06-29'])[0]
    match_start = datetime.strptime(f"{match_date} 19:30:00", "%Y-%m-%d %H:%M:%S")
    
    cricket_timeline = []
    current_time = match_start
    
    # Process each innings
    for inning_idx, inning in enumerate(innings):
        overs = inning.get('overs', [])
        
        for over_idx, over in enumerate(overs):
            deliveries = over.get('deliveries', [])
            
            for ball_idx, delivery in enumerate(deliveries):
                # Calculate timestamp (approximately 30 seconds per ball)
                ball_time = current_time + timedelta(seconds=30)
                current_time = ball_time
                
                # Extract runs
                runs = delivery.get('runs', {}).get('total', 0)
                
                # Check for wicket
                is_wicket = 'wickets' in delivery and len(delivery['wickets']) > 0
                
                # Generate commentary (simplified)
                batsman = delivery.get('batsman', 'Unknown')
                bowler = delivery.get('bowler', 'Unknown')
                
                if is_wicket:
                    wicket_info = delivery['wickets'][0]
                    commentary = f"WICKET! {wicket_info.get('player_out', batsman)} out"
                else:
                    commentary = f"{batsman} scores {runs} run(s) off {bowler}"
                
                # Calculate run rate (runs per over for current over)
                balls_in_over = ball_idx + 1
                over_runs = sum([d.get('runs', {}).get('total', 0) for d in deliveries[:balls_in_over]])
                run_rate = (over_runs / balls_in_over) * 6 if balls_in_over > 0 else 0
                
                cricket_timeline.append({
                    'timestamp_utc': ball_time.isoformat(),
                    'run_rate': round(run_rate, 2),
                    'is_wicket': is_wicket,
                    'commentary_text': commentary,
                    'over': over_idx + 1,
                    'ball': ball_idx + 1,
                    'runs': runs,
                    'innings': inning_idx + 1
                })
    
    # Create DataFrame
    df = pd.DataFrame(cricket_timeline)
    
    # Save to CSV
    output_file = "src/data/cricket_timeline.csv"
    df.to_csv(output_file, index=False)
    print(f"Cricket data saved to: {output_file}")
    print(f"Total balls processed: {len(df)}")
    print(f"Wickets found: {df['is_wicket'].sum()}")
    
    return df

if __name__ == "__main__":
    # Create data directory if it doesn't exist
    os.makedirs("src/data", exist_ok=True)
    
    # Load and process cricket data
    cricket_df = load_cricket_data()
    
    if cricket_df is not None:
        print("\nSample data:")
        print(cricket_df.head())
        print(f"\nMatch duration: {cricket_df['timestamp_utc'].iloc[0]} to {cricket_df['timestamp_utc'].iloc[-1]}")
    else:
        print("Failed to load cricket data")