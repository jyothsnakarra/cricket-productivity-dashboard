#!/usr/bin/env python3
"""
Sample Data Generator
Creates sample cricket and GitHub data for testing the dashboard
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import json

def create_sample_cricket_data():
    """Create sample cricket match data"""
    
    # T20 World Cup Final 2024 - Sample match
    match_start = datetime(2024, 6, 29, 19, 30, 0)  # 7:30 PM IST
    
    cricket_data = []
    current_time = match_start
    
    # Simulate a T20 match (40 overs total, 2 innings)
    for innings in [1, 2]:
        for over in range(1, 21):  # 20 overs per innings
            for ball in range(1, 7):  # 6 balls per over
                current_time += timedelta(seconds=30)  # 30 seconds per ball
                
                # Random runs (weighted towards lower scores)
                runs = np.random.choice([0, 1, 2, 3, 4, 6], p=[0.3, 0.25, 0.2, 0.1, 0.1, 0.05])
                
                # Wicket probability (higher in death overs)
                wicket_prob = 0.02 if over <= 15 else 0.04
                is_wicket = np.random.random() < wicket_prob
                
                # Calculate run rate for the over
                balls_so_far = (ball - 1) + (over - 1) * 6
                if balls_so_far > 0:
                    total_runs = sum([r['runs'] for r in cricket_data if r['innings'] == innings])
                    run_rate = (total_runs / balls_so_far) * 6
                else:
                    run_rate = 0
                
                # Generate commentary
                if is_wicket:
                    commentary = f"WICKET! Batsman out in over {over}.{ball}"
                elif runs == 6:
                    commentary = f"SIX! Massive hit in over {over}.{ball}"
                elif runs == 4:
                    commentary = f"FOUR! Beautiful shot in over {over}.{ball}"
                else:
                    commentary = f"{runs} run(s) scored in over {over}.{ball}"
                
                cricket_data.append({
                    'timestamp_utc': current_time.isoformat(),
                    'run_rate': round(run_rate, 2),
                    'is_wicket': is_wicket,
                    'commentary_text': commentary,
                    'over': over,
                    'ball': ball,
                    'runs': runs,
                    'innings': innings
                })
    
    # Create DataFrame and save
    df = pd.DataFrame(cricket_data)
    output_file = "src/data/cricket_timeline.csv"
    df.to_csv(output_file, index=False)
    
    print(f"✅ Sample cricket data created: {output_file}")
    print(f"   Records: {len(df)}")
    print(f"   Wickets: {df['is_wicket'].sum()}")
    print(f"   Match duration: {df['timestamp_utc'].iloc[0]} to {df['timestamp_utc'].iloc[-1]}")
    
    return df

def create_sample_github_data(cricket_df):
    """Create sample GitHub commit data aligned with cricket timeline"""
    
    match_start = pd.to_datetime(cricket_df['timestamp_utc'].iloc[0])
    match_end = pd.to_datetime(cricket_df['timestamp_utc'].iloc[-1])
    
    github_data = []
    current_time = match_start
    
    # Generate 5-minute intervals
    while current_time < match_end:
        # Base commit rate (simulating global GitHub activity)
        base_commits = np.random.poisson(150)  # Average 150 commits per 5 minutes
        
        # Add some correlation with cricket events
        # Check if there are wickets in this time window
        window_end = current_time + timedelta(minutes=5)
        wickets_in_window = cricket_df[
            (pd.to_datetime(cricket_df['timestamp_utc']) >= current_time) &
            (pd.to_datetime(cricket_df['timestamp_utc']) < window_end) &
            (cricket_df['is_wicket'] == True)
        ]
        
        # Reduce commits if there are wickets (simulating developers watching)
        if len(wickets_in_window) > 0:
            reduction_factor = 0.7 - (len(wickets_in_window) * 0.1)  # More wickets = fewer commits
            commit_count = int(base_commits * reduction_factor)
        else:
            commit_count = base_commits
        
        # Add some random variation
        commit_count = max(0, commit_count + np.random.randint(-20, 21))
        
        github_data.append({
            'timestamp': current_time.isoformat(),
            'commit_count': commit_count
        })
        
        current_time += timedelta(minutes=5)
    
    # Create DataFrame and save
    df = pd.DataFrame(github_data)
    output_file = "src/data/github_volume.csv"
    df.to_csv(output_file, index=False)
    
    print(f"✅ Sample GitHub data created: {output_file}")
    print(f"   Records: {len(df)}")
    print(f"   Total commits: {df['commit_count'].sum()}")
    print(f"   Average commits/5min: {df['commit_count'].mean():.1f}")
    
    return df

def create_sample_json_data():
    """Create a sample JSON file that looks like Cricsheet data"""
    
    sample_cricsheet = {
        "meta": {
            "data_version": "1.0.0",
            "created": "2024-06-29",
            "revision": 1
        },
        "info": {
            "balls_per_over": 6,
            "city": "Bridgetown",
            "dates": ["2024-06-29"],
            "event": {
                "name": "ICC Men's T20 World Cup 2024",
                "match_number": "Final"
            },
            "gender": "male",
            "match_type": "T20",
            "outcome": {
                "winner": "India",
                "by": {
                    "runs": 7
                }
            },
            "overs": 20,
            "player_of_match": ["V Kohli"],
            "players": {
                "India": ["V Kohli", "R Sharma", "S Gill", "H Pandya", "R Pant"],
                "South Africa": ["Q de Kock", "R van der Dussen", "A Markram", "D Miller", "H Klaasen"]
            },
            "registry": {
                "people": {
                    "V Kohli": "Virat Kohli",
                    "R Sharma": "Rohit Sharma"
                }
            },
            "teams": ["India", "South Africa"],
            "toss": {
                "winner": "South Africa",
                "decision": "field"
            },
            "venue": "Kensington Oval, Bridgetown, Barbados"
        },
        "innings": [
            {
                "team": "India",
                "overs": [
                    {
                        "over": 0,
                        "deliveries": [
                            {
                                "batsman": "V Kohli",
                                "bowler": "K Rabada",
                                "runs": {"batsman": 1, "extras": 0, "total": 1}
                            },
                            {
                                "batsman": "R Sharma",
                                "bowler": "K Rabada",
                                "runs": {"batsman": 4, "extras": 0, "total": 4}
                            }
                        ]
                    }
                ]
            }
        ]
    }
    
    # Save sample JSON
    output_file = "src/data/sample_t20_final_2024.json"
    with open(output_file, 'w') as f:
        json.dump(sample_cricsheet, f, indent=2)
    
    print(f"✅ Sample JSON data created: {output_file}")
    
    return sample_cricsheet

def main():
    """Create all sample data files"""
    print("🏏 Creating Sample Data for Dashboard Testing")
    print("=" * 50)
    
    # Create data directory
    os.makedirs("src/data", exist_ok=True)
    
    # Create sample data files
    print("\n1️⃣ Creating sample cricket timeline...")
    cricket_df = create_sample_cricket_data()
    
    print("\n2️⃣ Creating sample GitHub data...")
    github_df = create_sample_github_data(cricket_df)
    
    print("\n3️⃣ Creating sample JSON data...")
    create_sample_json_data()
    
    print("\n4️⃣ Processing sample data...")
    # Import and run the processing script
    try:
        import sys
        sys.path.append('src')
        from process_data import process_and_merge_data
        processed_df = process_and_merge_data()
        
        if processed_df is not None:
            print("✅ Sample data processing completed!")
        else:
            print("❌ Sample data processing failed")
            
    except Exception as e:
        print(f"⚠️  Could not run processing: {e}")
        print("Run 'python src/process_data.py' manually")
    
    print("\n" + "=" * 50)
    print("🎉 Sample data creation complete!")
    print("\n📊 Ready to test dashboard:")
    print("streamlit run src/app.py")
    print("\n💡 This sample data simulates:")
    print("   - T20 World Cup Final 2024 (India vs South Africa)")
    print("   - Realistic cricket timeline with wickets")
    print("   - Correlated GitHub commit patterns")
    print("   - Wicket impact on developer productivity")

if __name__ == "__main__":
    main()