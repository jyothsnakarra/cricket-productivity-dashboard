#!/usr/bin/env python3
"""
GitHub Data Ingestion Script
Fetches commit volume data during cricket match timeframe
"""

import os
import requests
import pandas as pd
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_github_commits(start_time, end_time, token):
    """
    Fetch GitHub commit count for a specific time range
    """
    # Format times for GitHub API (ISO 8601)
    start_str = start_time.strftime("%Y-%m-%dT%H:%M:%SZ")
    end_str = end_time.strftime("%Y-%m-%dT%H:%M:%SZ")
    
    # GitHub Search API endpoint
    url = "https://api.github.com/search/commits"
    
    # Search query for commits in time range
    query = f"committer-date:{start_str}..{end_str}"
    
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.cloak-preview+json"
    }
    
    params = {
        "q": query,
        "per_page": 1  # We only need the count
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            return data.get('total_count', 0)
        elif response.status_code == 403:
            print(f"Rate limit hit. Waiting...")
            time.sleep(60)  # Wait 1 minute for rate limit reset
            return get_github_commits(start_time, end_time, token)
        else:
            print(f"API Error {response.status_code}: {response.text}")
            return 0
    except Exception as e:
        print(f"Request failed: {e}")
        return 0

def fetch_github_data():
    """
    Main function to fetch GitHub commit data during match timeframe
    """
    token = os.getenv('GITHUB_TOKEN')
    if not token:
        print("ERROR: GITHUB_TOKEN not found in environment variables")
        print("Please add your GitHub token to the .env file")
        return None
    
    # Load cricket timeline to get match timeframe
    try:
        cricket_df = pd.read_csv("src/data/cricket_timeline.csv")
        match_start = pd.to_datetime(cricket_df['timestamp_utc'].iloc[0])
        match_end = pd.to_datetime(cricket_df['timestamp_utc'].iloc[-1])
    except FileNotFoundError:
        print("Cricket data not found. Please run ingest_cricket.py first")
        return None
    
    print(f"Fetching GitHub data from {match_start} to {match_end}")
    
    # Generate 5-minute intervals
    github_data = []
    current_time = match_start
    interval_minutes = 5
    
    while current_time < match_end:
        end_time = current_time + timedelta(minutes=interval_minutes)
        
        print(f"Fetching commits for {current_time.strftime('%H:%M')} - {end_time.strftime('%H:%M')}")
        
        # Get commit count for this interval
        commit_count = get_github_commits(current_time, end_time, token)
        
        github_data.append({
            'timestamp': current_time.isoformat(),
            'commit_count': commit_count
        })
        
        print(f"  Found {commit_count} commits")
        
        # Move to next interval
        current_time = end_time
        
        # Rate limiting: GitHub allows 30 requests per minute for authenticated users
        time.sleep(2)  # 2 seconds between requests
    
    # Create DataFrame
    df = pd.DataFrame(github_data)
    
    # Save to CSV
    output_file = "src/data/github_volume.csv"
    df.to_csv(output_file, index=False)
    print(f"\nGitHub data saved to: {output_file}")
    print(f"Total intervals: {len(df)}")
    print(f"Total commits found: {df['commit_count'].sum()}")
    
    return df

if __name__ == "__main__":
    # Create data directory if it doesn't exist
    os.makedirs("src/data", exist_ok=True)
    
    # Fetch GitHub data
    github_df = fetch_github_data()
    
    if github_df is not None:
        print("\nSample GitHub data:")
        print(github_df.head())
    else:
        print("Failed to fetch GitHub data")
