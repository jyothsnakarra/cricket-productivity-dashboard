#!/usr/bin/env python3
"""
Data Quality Check Script
Used by Kiro hooks to validate data integrity
"""

import pandas as pd
import sys
import os
import traceback

def check_cricket_data():
    """Check cricket data quality"""
    try:
        df = pd.read_csv("src/data/cricket_timeline.csv")
        
        # Basic checks
        if len(df) == 0:
            print("Cricket data is empty")
            return False
            
        if df['timestamp_utc'].isnull().any():
            print("Cricket data has null timestamps")
            return False
            
        if not df['is_wicket'].dtype == bool:
            print("Cricket wicket column is not boolean")
            return False
            
        print(f"Cricket data looks good: {len(df)} records")
        return True
        
    except FileNotFoundError:
        print("Cricket data file not found")
        return False
    except Exception as e:
        print(f"Cricket data error: {e}")
        return False

def check_github_data():
    """Check GitHub data quality"""
    try:
        df = pd.read_csv("src/data/github_volume.csv")
        
        # Basic checks
        if len(df) == 0:
            print("GitHub data is empty")
            return False
            
        if df['commit_count'].isnull().any():
            print("GitHub data has null commit counts")
            return False
            
        if df['commit_count'].min() < 0:
            print("GitHub data has negative commit counts")
            return False
            
        print(f"GitHub data looks good: {len(df)} records")
        return True
        
    except FileNotFoundError:
        print("GitHub data file not found")
        return False
    except Exception as e:
        print(f"GitHub data error: {e}")
        return False

def check_processed_data():
    """Check processed data quality"""
    try:
        df = pd.read_csv("src/data/dashboard_ready.csv")
        
        # Basic checks
        if len(df) == 0:
            print("Processed data is empty")
            return False
            
        required_columns = ['timestamp_utc', 'run_rate', 'is_wicket', 'commit_count']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            print(f"Processed data missing columns: {missing_columns}")
            return False
            
        print(f"Processed data looks good: {len(df)} records")
        return True
        
    except FileNotFoundError:
        print("Processed data file not found")
        return False
    except Exception as e:
        print(f"Processed data error: {e}")
        return False

def main():
    """Main data quality check"""
    try:
        print("Running data quality checks...")
        
        checks = []
        
        # Run each check individually and collect results
        print("\n1. Checking cricket data...")
        cricket_ok = check_cricket_data()
        checks.append(cricket_ok)
        
        print("\n2. Checking GitHub data...")
        github_ok = check_github_data()
        checks.append(github_ok)
        
        print("\n3. Checking processed data...")
        processed_ok = check_processed_data()
        checks.append(processed_ok)
        
        # Summary
        passed_checks = sum(checks)
        total_checks = len(checks)
        
        print(f"\nSummary: {passed_checks}/{total_checks} checks passed")
        
        if all(checks):
            print("All data quality checks passed!")
            print("DATA_QUALITY_CHECK_PASSED")  # Clear success marker
            return True
        else:
            print("Some data quality checks failed!")
            print("DATA_QUALITY_CHECK_FAILED")  # Clear failure marker
            return False
            
    except Exception as e:
        print(f"Data quality check crashed: {e}")
        print("DATA_QUALITY_CHECK_ERROR")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    # Use os._exit to ensure clean exit
    if success:
        os._exit(0)
    else:
        os._exit(1)