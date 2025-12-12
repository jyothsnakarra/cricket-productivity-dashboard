#!/usr/bin/env python3
"""
Test script to verify the Streamlit app loads without errors
"""

import sys
import os
import pandas as pd

# Add src to path
sys.path.insert(0, 'src')

def test_data_loading():
    """Test if the dashboard data can be loaded"""
    try:
        df = pd.read_csv("src/data/dashboard_ready.csv")
        df['timestamp_utc'] = pd.to_datetime(df['timestamp_utc'])
        print(f"✅ Data loaded successfully: {len(df)} records")
        return True
    except FileNotFoundError:
        print("❌ Dashboard data not found. Run the pipeline first.")
        return False
    except Exception as e:
        print(f"❌ Error loading data: {e}")
        return False

def test_app_imports():
    """Test if all required modules can be imported"""
    try:
        import streamlit as st
        import plotly.express as px
        import plotly.graph_objects as go
        from plotly.subplots import make_subplots
        import numpy as np
        from datetime import datetime
        print("✅ All required modules imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing Streamlit App Components")
    print("=" * 40)
    
    tests = [
        ("Module Imports", test_app_imports),
        ("Data Loading", test_data_loading)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🔍 Testing {test_name}...")
        result = test_func()
        results.append(result)
    
    print("\n" + "=" * 40)
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"🎉 All tests passed ({passed}/{total})")
        print("\n✅ App is ready to run!")
        print("🚀 Launch with: streamlit run src/app.py")
        return True
    else:
        print(f"❌ Some tests failed ({passed}/{total})")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)