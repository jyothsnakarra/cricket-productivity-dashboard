#!/usr/bin/env python3
"""
Dashboard Launch Script
Quick launcher for the Streamlit dashboard
"""

import subprocess
import sys
import os

def check_data_files():
    """Check if required data files exist"""
    required_files = [
        "src/data/dashboard_ready.csv"
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print("❌ Missing required data files:")
        for file in missing_files:
            print(f"   - {file}")
        print("\n🚀 Run the data pipeline first:")
        print("python run_pipeline.py")
        return False
    
    return True

def main():
    """Launch the dashboard"""
    print("🏏 The Wicket-Down Downtime - Dashboard Launcher")
    print("=" * 50)
    
    # Check if data files exist
    if not check_data_files():
        sys.exit(1)
    
    print("✅ Data files found!")
    print("🚀 Launching Streamlit dashboard...")
    print("\n📊 Dashboard will be available at: http://localhost:8501")
    print("Press Ctrl+C to stop the dashboard")
    print("-" * 50)
    
    try:
        # Launch Streamlit with proper arguments
        subprocess.run(["streamlit", "run", "src/app.py", "--server.port=8501", "--server.address=localhost"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to launch dashboard: {e}")
        print("Try running manually: streamlit run src/app.py")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n👋 Dashboard stopped by user")
    except FileNotFoundError:
        print("❌ Streamlit not found! Please install it:")
        print("pip install streamlit")
        print("Then try: streamlit run src/app.py")
        sys.exit(1)

if __name__ == "__main__":
    main()