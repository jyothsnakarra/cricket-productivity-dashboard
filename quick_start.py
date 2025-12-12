#!/usr/bin/env python3
"""
Quick Start Script
Sets up the project for immediate testing with sample data
"""

import subprocess
import sys
import os
from datetime import datetime

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True

def install_requirements():
    """Install required packages"""
    print("📦 Installing required packages...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                      check=True, capture_output=True)
        print("✅ Packages installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install packages: {e}")
        return False

def create_sample_data():
    """Generate sample data"""
    print("🏏 Creating sample data...")
    try:
        subprocess.run([sys.executable, "src/create_sample_data.py"], 
                      check=True, capture_output=True)
        print("✅ Sample data created successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to create sample data: {e}")
        return False

def test_dashboard():
    """Test if dashboard can load"""
    print("🧪 Testing dashboard components...")
    try:
        subprocess.run([sys.executable, "test_app.py"], 
                      check=True, capture_output=True)
        print("✅ Dashboard test passed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"⚠️  Dashboard test failed: {e}")
        return False

def main():
    """Quick start setup"""
    print("🏏 The Wicket-Down Downtime - Quick Start Setup")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    steps = [
        ("Checking Python Version", check_python_version),
        ("Installing Requirements", install_requirements),
        ("Creating Sample Data", create_sample_data),
        ("Testing Dashboard", test_dashboard)
    ]
    
    for step_name, step_func in steps:
        print(f"\n🚀 {step_name}...")
        if not step_func():
            print(f"\n❌ Quick start failed at: {step_name}")
            print("\n🔧 Manual setup required:")
            print("1. pip install -r requirements.txt")
            print("2. python src/create_sample_data.py")
            print("3. streamlit run src/app.py")
            sys.exit(1)
    
    print("\n" + "=" * 60)
    print("🎉 Quick start setup complete!")
    print("\n🚀 Ready to launch dashboard:")
    print("streamlit run src/app.py")
    print("\n🌐 Dashboard will be available at: http://localhost:8501")
    print("\n💡 What you'll see:")
    print("   - Sample T20 World Cup Final data")
    print("   - Simulated GitHub commit patterns")
    print("   - Interactive correlation analysis")
    print("   - Wicket impact on developer productivity")
    
    print(f"\nCompleted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Ask if user wants to launch dashboard
    try:
        launch = input("\n🚀 Launch dashboard now? (y/N): ").lower().strip()
        if launch in ['y', 'yes']:
            print("\n🌟 Launching dashboard...")
            subprocess.run(["streamlit", "run", "src/app.py"])
    except KeyboardInterrupt:
        print("\n👋 Setup complete. Launch manually with: streamlit run src/app.py")

if __name__ == "__main__":
    main()