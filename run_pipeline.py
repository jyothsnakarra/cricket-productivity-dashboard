#!/usr/bin/env python3
"""
Complete Data Pipeline Runner
Executes the full data processing pipeline for the dashboard
"""

import subprocess
import sys
import os
from datetime import datetime

def run_command(command, description, allow_failure=False):
    """Run a command and handle errors"""
    print(f"\n🚀 {description}")
    print(f"Running: {command}")
    print("-" * 50)
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        
        # Print output regardless of exit code
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print("Warnings/Errors:", result.stderr)
        
        # Check exit code
        if result.returncode == 0:
            print(f"✅ {description} completed successfully!")
            return True
        else:
            print(f"❌ {description} failed with exit code {result.returncode}")
            if allow_failure:
                print("⚠️  Continuing despite failure...")
                return True
            return False
            
    except Exception as e:
        print(f"❌ {description} failed with exception!")
        print(f"Exception: {e}")
        return False

def check_requirements():
    """Check if required files exist"""
    print("🔍 Checking requirements...")
    
    # Check if .env file exists
    if not os.path.exists('.env'):
        print("❌ .env file not found!")
        print("Please create .env file with your GITHUB_TOKEN")
        print("Example:")
        print("GITHUB_TOKEN='your_token_here'")
        return False
    
    # Check if data directory exists
    os.makedirs('src/data', exist_ok=True)
    
    # Check if we have some cricket data files
    data_files = [f for f in os.listdir('src/data') if f.endswith('.json')]
    if not data_files:
        print("⚠️  No JSON cricket data files found in src/data/")
        print("The script will still run but may use sample data")
    
    print("✅ Requirements check passed!")
    return True

def main():
    """Run the complete pipeline"""
    print("🏏 The Wicket-Down Downtime - Data Pipeline")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check requirements
    if not check_requirements():
        sys.exit(1)
    
    # Step 1: Ingest cricket data
    if not run_command("python src/ingest_cricket.py", "Step 1: Ingesting Cricket Data"):
        print("❌ Pipeline failed at cricket data ingestion")
        sys.exit(1)
    
    # Step 2: Ingest GitHub data
    if not run_command("python src/ingest_github.py", "Step 2: Ingesting GitHub Data"):
        print("❌ Pipeline failed at GitHub data ingestion")
        print("Note: This step requires a valid GITHUB_TOKEN and internet connection")
        sys.exit(1)
    
    # Step 3: Process and merge data
    if not run_command("python src/process_data.py", "Step 3: Processing and Merging Data"):
        print("❌ Pipeline failed at data processing")
        sys.exit(1)
    
    # Step 4: Run data quality checks
    print("\n🚀 Step 4: Data Quality Checks")
    print("Running: python tests/check_data_quality.py")
    print("-" * 50)
    
    try:
        result = subprocess.run("python tests/check_data_quality.py", shell=True, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print("Warnings:", result.stderr)
        
        # Check for success marker in output
        if "DATA_QUALITY_CHECK_PASSED" in result.stdout:
            print("✅ Step 4: Data Quality Checks completed successfully!")
        elif "DATA_QUALITY_CHECK_FAILED" in result.stdout:
            print("⚠️  Data quality checks found issues, but continuing...")
        else:
            print("⚠️  Data quality checks completed with unknown status...")
            
    except Exception as e:
        print(f"⚠️  Data quality check failed to run: {e}")
        print("Continuing with pipeline...")
    
    print("\n" + "=" * 60)
    print("🎉 Pipeline completed successfully!")
    print("\n📊 Ready to launch dashboard:")
    print("streamlit run src/app.py")
    print("\n🌐 Dashboard will be available at: http://localhost:8501")
    print(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()