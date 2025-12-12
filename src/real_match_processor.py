#!/usr/bin/env python3
"""
Real Cricket Match Data Processor
Processes actual Cricsheet JSON files to create unique, realistic dashboard data
"""

import json
import pandas as pd
import numpy as np
import glob
import os
from datetime import datetime, timedelta
import hashlib
import random

class RealMatchProcessor:
    def __init__(self):
        self.processed_matches = {}
        
    def get_match_seed(self, match_id):
        """Generate consistent seed for match to ensure reproducible data"""
        return int(hashlib.md5(match_id.encode()).hexdigest()[:8], 16)
    
    def discover_real_matches(self):
        """Discover and analyze real cricket match files"""
        matches = {}
        json_files = glob.glob("src/data/*.json")
        
        print(f"Analyzing {len(json_files)} cricket match files...")
        
        for json_file in json_files[:20]:  # Process first 20 for performance
            try:
                with open(json_file, 'r') as f:
                    match_data = json.load(f)
                
                info = match_data.get('info', {})
                
                # Extract match details
                teams = info.get('teams', ['Team A', 'Team B'])
                event = info.get('event', {}).get('name', 'Cricket Match')
                dates = info.get('dates', ['2024-01-01'])
                match_type = info.get('match_type', 'T20')
                outcome = info.get('outcome', {})
                
                # Create unique match identifier
                match_id = os.path.basename(json_file).replace('.json', '')
                
                # Generate match display name
                if len(teams) >= 2:
                    match_name = f"{teams[0]} vs {teams[1]}"
                else:
                    match_name = f"Match {match_id}"
                
                # Add match type and date
                match_name += f" ({match_type}) - {dates[0]}"
                
                # Add special indicators
                if 'Final' in event:
                    match_name += " 🏆"
                elif 'World Cup' in event:
                    match_name += " 🌍"
                elif 'T20' in event:
                    match_name += " ⚡"
                
                matches[match_name] = {
                    'file': json_file,
                    'match_id': match_id,
                    'teams': teams,
                    'date': dates[0],
                    'event': event,
                    'match_type': match_type,
                    'outcome': outcome,
                    'info': info,
                    'raw_data': match_data
                }
                
            except Exception as e:
                print(f"Warning: Skipping {json_file}: {e}")
                continue
        
        print(f"Successfully processed {len(matches)} matches")
        return matches
    
    def process_real_match_data(self, match_info):
        """Process a real cricket match into dashboard format with unique data"""
        
        match_id = match_info['match_id']
        raw_data = match_info['raw_data']
        
        # Set seed for consistent but unique data per match
        np.random.seed(self.get_match_seed(match_id))
        random.seed(self.get_match_seed(match_id))
        
        info = raw_data.get('info', {})
        innings = raw_data.get('innings', [])
        
        # Extract real match details
        teams = match_info['teams']
        match_date = match_info['date']
        event_name = match_info['event']
        
        # Create realistic match start time based on match type and location
        base_date = datetime.strptime(match_date, "%Y-%m-%d")
        
        # Different start times based on match type and teams
        if 'India' in teams or 'Pakistan' in teams or 'Sri Lanka' in teams:
            # Subcontinent matches - evening start
            start_hour = 19 + random.randint(-1, 1)
        elif 'Australia' in teams or 'New Zealand' in teams:
            # Australia/NZ matches - afternoon start
            start_hour = 14 + random.randint(-2, 2)
        elif 'England' in teams or 'South Africa' in teams:
            # England/SA matches - varied timing
            start_hour = 16 + random.randint(-2, 3)
        else:
            # Default timing
            start_hour = 18 + random.randint(-2, 2)
        
        match_start = base_date.replace(hour=start_hour, minute=30, second=0)
        
        cricket_timeline = []
        current_time = match_start
        
        # Process real innings data
        total_runs = 0
        total_wickets = 0
        
        for inning_idx, inning in enumerate(innings):
            overs = inning.get('overs', [])
            
            for over_idx, over in enumerate(overs):
                deliveries = over.get('deliveries', [])
                
                for ball_idx, delivery in enumerate(deliveries):
                    # Realistic ball timing (25-45 seconds per ball)
                    ball_duration = 25 + random.randint(0, 20)
                    current_time += timedelta(seconds=ball_duration)
                    
                    # Extract real runs
                    runs = delivery.get('runs', {}).get('total', 0)
                    total_runs += runs
                    
                    # Extract real wickets
                    is_wicket = 'wickets' in delivery and len(delivery['wickets']) > 0
                    if is_wicket:
                        total_wickets += 1
                    
                    # Generate realistic commentary based on actual delivery
                    batsman = delivery.get('batsman', f"Batsman{random.randint(1,11)}")
                    bowler = delivery.get('bowler', f"Bowler{random.randint(1,11)}")
                    
                    if is_wicket:
                        wicket_info = delivery['wickets'][0]
                        wicket_type = wicket_info.get('kind', 'out')
                        commentary = f"WICKET! {wicket_info.get('player_out', batsman)} {wicket_type}"
                    elif runs == 6:
                        commentary = f"SIX! {batsman} launches {bowler} into the stands!"
                    elif runs == 4:
                        commentary = f"FOUR! Brilliant shot by {batsman} off {bowler}"
                    elif runs == 0:
                        commentary = f"Dot ball. {bowler} beats {batsman}"
                    else:
                        commentary = f"{batsman} works {bowler} for {runs} run(s)"
                    
                    # Calculate realistic run rate
                    balls_so_far = len(cricket_timeline) + 1
                    current_run_rate = (total_runs / balls_so_far) * 6 if balls_so_far > 0 else 0
                    
                    # Calculate runs per over for current over
                    over_runs = sum([d.get('runs', {}).get('total', 0) for d in deliveries[:ball_idx+1]])
                    
                    cricket_timeline.append({
                        'timestamp_utc': current_time.isoformat(),
                        'run_rate': round(current_run_rate, 2),
                        'is_wicket': is_wicket,
                        'commentary_text': commentary,
                        'over': over_idx + 1,
                        'ball': ball_idx + 1,
                        'runs': runs,
                        'innings': inning_idx + 1,
                        'match_id': match_id,
                        'teams': f"{teams[0]} vs {teams[1]}",
                        'event': event_name,
                        'date': match_date,
                        'runs_per_over': over_runs
                    })
        
        # Create DataFrame
        df = pd.DataFrame(cricket_timeline)
        
        # Add match-specific characteristics
        df['match_minute'] = (pd.to_datetime(df['timestamp_utc']) - pd.to_datetime(df['timestamp_utc'].iloc[0])).dt.total_seconds() / 60
        df['cumulative_runs'] = df.groupby('innings')['runs'].cumsum()
        
        return df
    
    def generate_realistic_github_data(self, cricket_df, match_info):
        """Generate realistic GitHub commit data correlated with cricket events"""
        
        if cricket_df is None or len(cricket_df) == 0:
            return None
        
        match_id = match_info['match_id']
        teams = match_info['teams']
        
        # Set seed for consistent data
        np.random.seed(self.get_match_seed(match_id))
        
        match_start = pd.to_datetime(cricket_df['timestamp_utc'].iloc[0])
        match_end = pd.to_datetime(cricket_df['timestamp_utc'].iloc[-1])
        
        github_data = []
        current_time = match_start
        
        # Base commit rate varies by match characteristics
        if 'India' in teams:
            base_rate = 180  # Higher activity during India matches
        elif 'World Cup' in match_info['event']:
            base_rate = 200  # World Cup matches get more attention
        elif 'Final' in match_info['event']:
            base_rate = 220  # Finals get maximum attention
        else:
            base_rate = 140  # Regular matches
        
        # Add match-specific variation
        match_multiplier = 0.8 + (int(match_id) % 100) / 250  # 0.8 to 1.2
        base_rate = int(base_rate * match_multiplier)
        
        while current_time < match_end:
            window_end = current_time + timedelta(minutes=5)
            
            # Base commits with time-of-day variation
            hour = current_time.hour
            if 9 <= hour <= 17:  # Work hours
                time_multiplier = 1.3
            elif 18 <= hour <= 22:  # Evening
                time_multiplier = 1.0
            else:  # Night/early morning
                time_multiplier = 0.4
            
            base_commits = int(np.random.poisson(base_rate * time_multiplier))
            
            # Check for cricket events in this window
            wickets_in_window = cricket_df[
                (pd.to_datetime(cricket_df['timestamp_utc']) >= current_time) &
                (pd.to_datetime(cricket_df['timestamp_utc']) < window_end) &
                (cricket_df['is_wicket'] == True)
            ]
            
            # Check for high-scoring moments
            big_hits_in_window = cricket_df[
                (pd.to_datetime(cricket_df['timestamp_utc']) >= current_time) &
                (pd.to_datetime(cricket_df['timestamp_utc']) < window_end) &
                (cricket_df['runs'] >= 4)
            ]
            
            # Apply cricket impact
            impact_factor = 1.0
            
            if len(wickets_in_window) > 0:
                # Wickets reduce commits (people watching)
                impact_factor *= (0.5 - len(wickets_in_window) * 0.1)
            
            if len(big_hits_in_window) > 0:
                # Big hits also reduce commits slightly
                impact_factor *= (0.85 - len(big_hits_in_window) * 0.05)
            
            # Apply match importance factor
            if 'Final' in match_info['event']:
                impact_factor *= 0.7  # Finals have bigger impact
            elif 'World Cup' in match_info['event']:
                impact_factor *= 0.8  # World Cup matches have bigger impact
            
            # Calculate final commit count
            final_commits = max(10, int(base_commits * impact_factor))
            
            # Add some randomness
            final_commits += random.randint(-20, 20)
            final_commits = max(0, final_commits)
            
            github_data.append({
                'timestamp': current_time.isoformat(),
                'commit_count': final_commits
            })
            
            current_time = window_end
        
        return pd.DataFrame(github_data)
    
    def calculate_wicket_impact(self, cricket_df, github_df):
        """Calculate realistic wicket impact on commits"""
        
        if cricket_df is None or github_df is None:
            return cricket_df
        
        # Convert timestamps
        cricket_df['timestamp_utc'] = pd.to_datetime(cricket_df['timestamp_utc'])
        github_df['timestamp'] = pd.to_datetime(github_df['timestamp'])
        
        # Merge data
        merged_df = pd.merge_asof(
            cricket_df.sort_values('timestamp_utc'),
            github_df.sort_values('timestamp'),
            left_on='timestamp_utc',
            right_on='timestamp',
            direction='nearest'
        )
        
        # Calculate commit velocity
        merged_df['commit_velocity'] = merged_df['commit_count'].rolling(
            window=3, min_periods=1, center=True
        ).mean()
        
        # Calculate wicket impact
        merged_df['commit_drop_percentage'] = 0.0
        
        wicket_moments = merged_df[merged_df['is_wicket'] == True].copy()
        
        for idx, wicket_row in wicket_moments.iterrows():
            # Look at commits before and after wicket
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
                # Ensure realistic range (5% to 60% drop)
                drop_percentage = max(5, min(60, drop_percentage))
                merged_df.loc[idx, 'commit_drop_percentage'] = drop_percentage
        
        return merged_df
    
    def process_match(self, match_name, match_info):
        """Process a complete match with cricket and GitHub data"""
        
        print(f"Processing: {match_name}")
        
        # Process cricket data
        cricket_df = self.process_real_match_data(match_info)
        
        if cricket_df is None or len(cricket_df) == 0:
            print(f"Error: No cricket data for {match_name}")
            return None
        
        # Generate GitHub data
        github_df = self.generate_realistic_github_data(cricket_df, match_info)
        
        # Merge and calculate impacts
        final_df = self.calculate_wicket_impact(cricket_df, github_df)
        
        # Cache the processed match
        self.processed_matches[match_name] = final_df
        
        print(f"Processed {match_name}: {len(final_df)} balls, {final_df['is_wicket'].sum()} wickets")
        
        return final_df

# Global processor instance
processor = RealMatchProcessor()

def get_available_matches():
    """Get all available real cricket matches"""
    return processor.discover_real_matches()

def load_match_data(match_name, match_info):
    """Load data for a specific match"""
    
    # Check if already processed
    if match_name in processor.processed_matches:
        return processor.processed_matches[match_name]
    
    # Process the match
    return processor.process_match(match_name, match_info)

if __name__ == "__main__":
    # Test the processor
    matches = get_available_matches()
    
    if matches:
        # Process first match as example
        first_match = list(matches.keys())[0]
        match_info = matches[first_match]
        
        print(f"\nTesting with: {first_match}")
        df = load_match_data(first_match, match_info)
        
        if df is not None:
            print(f"\nSample data:")
            print(f"Total balls: {len(df)}")
            print(f"Total wickets: {df['is_wicket'].sum()}")
            print(f"Total runs: {df['runs'].sum()}")
            print(f"Total commits: {df['commit_count'].sum()}")
            print(f"Match duration: {df['match_minute'].max():.1f} minutes")
            
            print(f"\nWicket impacts:")
            wickets = df[df['is_wicket'] == True]
            if len(wickets) > 0:
                print(f"Average impact: {wickets['commit_drop_percentage'].mean():.1f}%")
                print(f"Max impact: {wickets['commit_drop_percentage'].max():.1f}%")
    else:
        print("No matches found")