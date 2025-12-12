#!/usr/bin/env python3
"""
Test script for enhanced cricket dashboard functionality
"""

import sys
import os
import time
from datetime import datetime

# Add current directory to path
sys.path.append('.')

def test_imports():
    """Test that all modules can be imported"""
    print("🧪 Testing module imports...")
    
    try:
        from src.enhanced_match_processor import get_enhanced_processor
        print("✅ Enhanced match processor imported successfully")
    except ImportError as e:
        print(f"❌ Enhanced match processor import failed: {e}")
        return False
    
    try:
        from src.visualization_engine import get_visualization_engine
        print("✅ Visualization engine imported successfully")
    except ImportError as e:
        print(f"❌ Visualization engine import failed: {e}")
        return False
    
    try:
        import src.app
        print("✅ Main app module imported successfully")
    except ImportError as e:
        print(f"❌ Main app import failed: {e}")
        return False
    
    return True

def test_enhanced_processor():
    """Test enhanced match processor functionality"""
    print("\n🧪 Testing enhanced match processor...")
    
    try:
        from src.enhanced_match_processor import get_enhanced_processor
        processor = get_enhanced_processor()
        
        # Test basic functionality
        matches = processor.discover_all_matches(lazy=True, max_matches=5)
        print(f"✅ Discovered {len(matches)} matches")
        
        # Test performance stats
        stats = processor.get_performance_stats()
        print(f"✅ Performance stats: {stats.get('memory_limit_mb', 'unknown')} MB limit")
        
        return True
        
    except Exception as e:
        print(f"❌ Enhanced processor test failed: {e}")
        return False

def test_visualization_engine():
    """Test visualization engine functionality"""
    print("\n🧪 Testing visualization engine...")
    
    try:
        from src.visualization_engine import get_visualization_engine
        viz_engine = get_visualization_engine()
        
        if viz_engine is None:
            print("❌ Visualization engine returned None")
            return False
        
        print("✅ Visualization engine created successfully")
        
        # Test with sample data
        import pandas as pd
        import numpy as np
        
        sample_data = pd.DataFrame({
            'over': range(1, 21),
            'runs': np.random.randint(0, 20, 20),
            'is_wicket': np.random.choice([True, False], 20, p=[0.1, 0.9]),
            'innings': [1] * 10 + [2] * 10
        })
        
        # Test timeline creation
        timeline_fig = viz_engine.create_match_timeline(sample_data)
        if timeline_fig:
            print("✅ Timeline visualization created successfully")
        else:
            print("❌ Timeline visualization failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Visualization engine test failed: {e}")
        return False

def test_error_handling():
    """Test error handling functionality"""
    print("\n🧪 Testing error handling...")
    
    try:
        from src.app import handle_json_error, handle_memory_error, handle_network_error
        
        # These functions should not raise exceptions
        handle_json_error("test.json", Exception("Test error"))
        handle_memory_error("test operation")
        handle_network_error("test operation", Exception("Network error"))
        
        print("✅ Error handling functions work correctly")
        return True
        
    except Exception as e:
        print(f"❌ Error handling test failed: {e}")
        return False

def test_system_health():
    """Test system health check"""
    print("\n🧪 Testing system health check...")
    
    try:
        from src.app import system_health_check
        
        health = system_health_check()
        print(f"✅ System health check completed:")
        print(f"   - Data folder: {health.get('data_folder', 'unknown')}")
        print(f"   - Enhanced processor: {health.get('enhanced_processor', 'unknown')}")
        print(f"   - Visualization engine: {health.get('visualization_engine', 'unknown')}")
        print(f"   - Memory status: {health.get('memory_status', 'unknown')}")
        
        return True
        
    except Exception as e:
        print(f"❌ System health check failed: {e}")
        return False

def main():
    """Run all tests with enhanced visibility and progress tracking"""
    print("\n" + "🏏" * 25)
    print("🏏 CRICKET DASHBOARD - ENHANCEMENT TESTS")
    print("🏏" * 25)
    print(f"📅 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🎯 Testing enhanced cricket dashboard functionality...")
    print("=" * 70)
    
    tests = [
        ("Module Imports", test_imports),
        ("Enhanced Processor", test_enhanced_processor),
        ("Visualization Engine", test_visualization_engine),
        ("Error Handling", test_error_handling),
        ("System Health Check", test_system_health)
    ]
    
    passed = 0
    total = len(tests)
    
    for i, (test_name, test_func) in enumerate(tests, 1):
        print(f"\n🧪 TEST {i}/{total}: {test_name}")
        print("=" * 50)
        
        try:
            start_time = time.time()
            result = test_func()
            end_time = time.time()
            
            if result:
                print(f"✅ PASSED: {test_name} ({end_time - start_time:.2f}s)")
                passed += 1
            else:
                print(f"❌ FAILED: {test_name} ({end_time - start_time:.2f}s)")
                
        except Exception as e:
            print(f"💥 CRASHED: {test_name} - {str(e)}")
            import traceback
            print("🔍 Stack trace:")
            traceback.print_exc()
    
    print("\n" + "=" * 70)
    print(f"📊 FINAL RESULTS: {passed}/{total} tests passed")
    print(f"⏱️ Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if passed == total:
        print("🎉 ALL ENHANCEMENT TESTS PASSED!")
        print("✅ The enhanced cricket dashboard is ready!")
        print("🚀 All features are working correctly!")
        return True
    else:
        print("⚠️ SOME ENHANCEMENT TESTS FAILED!")
        print("❌ Check the detailed output above for specific issues")
        print("🔧 Fix the failing tests before proceeding")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)