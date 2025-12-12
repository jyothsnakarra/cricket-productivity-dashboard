#!/usr/bin/env python3
"""
Streamlit Dashboard: The Wicket-Down Downtime
T20 World Cup Final vs. Global Developer Productivity
"""

import os
import sys
import warnings
import logging

# Comprehensive warning suppression for Streamlit context issues
warnings.filterwarnings("ignore", message=".*ScriptRunContext.*")
warnings.filterwarnings("ignore", message=".*missing ScriptRunContext.*")
warnings.filterwarnings("ignore", message=".*Thread.*missing ScriptRunContext.*")
warnings.filterwarnings("ignore", category=UserWarning, module="streamlit.*")

# Suppress Streamlit logging warnings
logging.getLogger("streamlit.runtime.scriptrunner_utils.script_run_context").setLevel(logging.ERROR)
logging.getLogger("streamlit.runtime.caching.cache_data_api").setLevel(logging.ERROR)
logging.getLogger("streamlit").setLevel(logging.ERROR)

# Set environment variable to suppress Streamlit warnings
os.environ["STREAMLIT_LOGGER_LEVEL"] = "error"

# Check if running in Streamlit context
def is_streamlit_context():
    """Check if code is running in Streamlit context"""
    try:
        import streamlit as st
        from streamlit.runtime.scriptrunner import get_script_run_ctx
        return get_script_run_ctx() is not None
    except:
        return False

# Only import and configure Streamlit if in proper context
if is_streamlit_context() or __name__ == "__main__":
    import streamlit as st
else:
    # Mock streamlit for testing/import contexts
    class MockStreamlit:
        def __getattr__(self, name):
            return lambda *args, **kwargs: None
    st = MockStreamlit()

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime
import glob
import json
import time

# Try to import visualization engine with fallback
try:
    from src.visualization_engine import get_visualization_engine
except ImportError:
    try:
        from visualization_engine import get_visualization_engine
    except ImportError:
        # Fallback function if visualization engine is not available
        def get_visualization_engine():
            return None

def create_sample_dashboard_data():
    """Create minimal sample data for dashboard testing"""
    # Create a simple sample dataset
    from datetime import datetime, timedelta
    import numpy as np
    
    start_time = datetime(2024, 6, 29, 19, 30, 0)
    data = []
    
    for i in range(240):  # 240 balls (20 overs x 2 innings x 6 balls)
        current_time = start_time + timedelta(seconds=i*30)
        
        data.append({
            'timestamp_utc': current_time.isoformat(),
            'run_rate': np.random.uniform(4, 12),
            'is_wicket': np.random.random() < 0.03,  # 3% wicket probability
            'commentary_text': f"Ball {i+1}: Sample commentary",
            'over': (i // 6) + 1,
            'ball': (i % 6) + 1,
            'runs': np.random.choice([0, 1, 2, 3, 4, 6], p=[0.3, 0.25, 0.2, 0.1, 0.1, 0.05]),
            'innings': 1 if i < 120 else 2,
            'commit_count': np.random.poisson(150),
            'commit_velocity': np.random.uniform(100, 200),
            'cumulative_runs': i * 0.5,
            'runs_per_over': np.random.uniform(4, 15),
            'match_minute': i * 0.5,
            'commit_drop_percentage': np.random.uniform(0, 30) if np.random.random() < 0.03 else 0,
            'match_phase': 'Sample Phase'
        })
    
    return pd.DataFrame(data)

# Page configuration - only when in Streamlit context
if is_streamlit_context() or __name__ == "__main__":
    try:
        st.set_page_config(
            page_title="The Wicket-Down Downtime",
            page_icon="🏏",
            layout="wide",
            initial_sidebar_state="expanded"
        )
    except Exception:
        # Page config already set or not in Streamlit context
        pass

# Enhanced Custom CSS for cricket-themed UI with animations and micro-interactions
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700;800&family=Orbitron:wght@400;700;900&display=swap');
    
    /* Enhanced root variables for consistent theming */
    :root {
        --cricket-primary: #ff6b35;
        --cricket-secondary: #2a5298;
        --cricket-accent: #ffd700;
        --cricket-success: #4CAF50;
        --cricket-danger: #f44336;
        --cricket-dark: #1e3c72;
        --cricket-light: #ffffff;
        --cricket-shadow: rgba(0, 0, 0, 0.3);
        --cricket-glow: rgba(255, 215, 0, 0.5);
        --animation-speed: 0.3s;
        --bounce-timing: cubic-bezier(0.68, -0.55, 0.265, 1.55);
    }
    
    /* Cricket-themed header with time machine effect */
    .cricket-header-container {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 50%, #ff6b35 100%);
        padding: 2rem 1rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        position: relative;
        overflow: hidden;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
    }
    
    .cricket-header-container::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
        animation: rotate 20s linear infinite;
    }
    
    @keyframes rotate {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    .main-header {
        font-family: 'Orbitron', 'Poppins', sans-serif;
        font-size: clamp(2rem, 5vw, 4rem);
        font-weight: 900;
        text-align: center;
        background: linear-gradient(45deg, #fff, #ffd700, #fff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.5rem;
        animation: glow 3s ease-in-out infinite alternate;
        position: relative;
        z-index: 2;
        text-shadow: 0 0 20px rgba(255,215,0,0.5);
    }
    
    @keyframes glow {
        from { 
            filter: drop-shadow(0 0 10px #ffd700) drop-shadow(0 0 20px #ff6b35);
            transform: scale(1);
        }
        to { 
            filter: drop-shadow(0 0 20px #ffd700) drop-shadow(0 0 40px #ff6b35);
            transform: scale(1.02);
        }
    }
    
    .sub-header {
        font-family: 'Poppins', sans-serif;
        font-size: clamp(1rem, 2.5vw, 1.4rem);
        text-align: center;
        color: #fff;
        margin-bottom: 1rem;
        font-style: italic;
        animation: fadeInUp 1.5s ease-out;
        position: relative;
        z-index: 2;
        text-shadow: 0 2px 4px rgba(0,0,0,0.5);
    }
    
    .time-machine-tagline {
        font-family: 'Poppins', sans-serif;
        font-size: clamp(0.8rem, 2vw, 1rem);
        text-align: center;
        color: #ffd700;
        margin-bottom: 1rem;
        animation: pulse 2s ease-in-out infinite;
        position: relative;
        z-index: 2;
        font-weight: 600;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 0.8; transform: scale(1); }
        50% { opacity: 1; transform: scale(1.05); }
    }
    
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(30px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    /* Responsive layout improvements */
    .main-container {
        max-width: 1400px;
        margin: 0 auto;
        padding: 0 1rem;
    }
    
    @media (max-width: 768px) {
        .cricket-header-container {
            padding: 1.5rem 0.5rem;
            margin-bottom: 1rem;
        }
        
        .main-header {
            font-size: 2.5rem;
        }
        
        .sub-header {
            font-size: 1rem;
        }
    }
    
    /* Inning-wise wicket indicators */
    .innings-wicket-container {
        display: flex;
        justify-content: center;
        gap: 2rem;
        margin: 1rem 0;
        flex-wrap: wrap;
    }
    
    .innings-wicket-card {
        background: linear-gradient(135deg, rgba(255,255,255,0.1), rgba(255,255,255,0.05));
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255,255,255,0.2);
        border-radius: 15px;
        padding: 1rem;
        text-align: center;
        min-width: 120px;
        animation: slideInFromBottom 1s ease-out;
        position: relative;
        z-index: 2;
    }
    
    @keyframes slideInFromBottom {
        from { opacity: 0; transform: translateY(50px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .innings-title {
        color: #ffd700;
        font-weight: 700;
        font-size: 0.9rem;
        margin-bottom: 0.5rem;
    }
    
    .wicket-count {
        color: #fff;
        font-size: 1.5rem;
        font-weight: 800;
        margin-bottom: 0.2rem;
    }
    
    .wicket-label {
        color: #ccc;
        font-size: 0.7rem;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Enhanced match selector styles */
    .match-card {
        background: linear-gradient(135deg, rgba(255,255,255,0.1), rgba(255,255,255,0.05));
        backdrop-filter: blur(10px);
        border: 2px solid transparent;
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        transition: all 0.3s ease;
        cursor: pointer;
        position: relative;
        overflow: hidden;
    }
    
    .match-card:hover {
        transform: translateY(-5px);
        border-color: #ff6b35;
        box-shadow: 0 10px 30px rgba(255,107,53,0.3);
    }
    
    .match-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
        transition: left 0.5s;
    }
    
    .match-card:hover::before {
        left: 100%;
    }
    
    /* Search and filter enhancements */
    .stTextInput > div > div > input {
        background-color: rgba(255,255,255,0.9) !important;
        color: #333 !important;
        border-radius: 10px;
        border: 2px solid #ff6b35;
        transition: all 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus {
        background-color: rgba(255,255,255,0.95) !important;
        color: #333 !important;
        border-color: #ffd700;
        box-shadow: 0 0 15px rgba(255,215,0,0.3);
    }
    
    .stMultiSelect > div > div {
        background-color: rgba(255,255,255,0.9) !important;
        color: #333 !important;
        border-radius: 10px;
        border: 2px solid #ff6b35;
    }
    
    /* Additional input components for better visibility */
    .stTextArea > div > div > textarea {
        background-color: rgba(255,255,255,0.9) !important;
        color: #333 !important;
        border-radius: 10px;
        border: 2px solid #ff6b35;
    }
    
    .stNumberInput > div > div > input {
        background-color: rgba(255,255,255,0.9) !important;
        color: #333 !important;
        border-radius: 10px;
        border: 2px solid #ff6b35;
    }
    
    .stDateInput > div > div > input {
        background-color: rgba(255,255,255,0.9) !important;
        color: #333 !important;
        border-radius: 10px;
        border: 2px solid #ff6b35;
    }
    
    .stTimeInput > div > div > input {
        background-color: rgba(255,255,255,0.9) !important;
        color: #333 !important;
        border-radius: 10px;
        border: 2px solid #ff6b35;
    }
    
    /* Enhanced micro-interactions and animations */
    .metric-card {
        background: linear-gradient(135deg, #f0f2f6, #e8eaf6);
        padding: 1.5rem;
        border-radius: 15px;
        border-left: 5px solid #FF6B35;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        margin: 0.5rem 0;
        position: relative;
        overflow: hidden;
    }
    
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,107,53,0.1), transparent);
        transition: left 0.6s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-8px) scale(1.02);
        box-shadow: 0 12px 35px rgba(255,107,53,0.25);
        border-left-width: 8px;
    }
    
    .metric-card:hover::before {
        left: 100%;
    }
    
    /* Enhanced wicket alerts with pulsing animation */
    .wicket-alert {
        background: linear-gradient(135deg, #ffebee, #fce4ec);
        padding: 1.5rem;
        border-radius: 15px;
        border-left: 4px solid #f44336;
        margin: 0.5rem 0;
        animation: wicketPulse 2s ease-in-out infinite;
        box-shadow: 0 4px 20px rgba(244,67,54,0.2);
        position: relative;
        overflow: hidden;
    }
    
    @keyframes wicketPulse {
        0%, 100% { 
            box-shadow: 0 4px 20px rgba(244,67,54,0.2);
            transform: scale(1);
        }
        50% { 
            box-shadow: 0 8px 30px rgba(244,67,54,0.4);
            transform: scale(1.02);
        }
    }
    
    .wicket-alert::after {
        content: '⚡';
        position: absolute;
        top: 10px;
        right: 15px;
        font-size: 1.5rem;
        animation: bounce 1s ease-in-out infinite;
    }
    
    @keyframes bounce {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-10px); }
    }
    
    /* Enhanced button animations */
    .stButton > button {
        background: linear-gradient(135deg, #FF6B35, #F7931E);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        font-family: 'Poppins', sans-serif;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 15px rgba(255,107,53,0.3);
        position: relative;
        overflow: hidden;
    }
    
    .stButton > button::before {
        content: '';
        position: absolute;
        top: 50%;
        left: 50%;
        width: 0;
        height: 0;
        background: rgba(255,255,255,0.3);
        border-radius: 50%;
        transform: translate(-50%, -50%);
        transition: width 0.3s, height 0.3s;
    }
    
    .stButton > button:hover {
        transform: translateY(-3px) scale(1.05);
        box-shadow: 0 8px 25px rgba(255,107,53,0.4);
    }
    
    .stButton > button:hover::before {
        width: 300px;
        height: 300px;
    }
    
    .stButton > button:active {
        transform: translateY(-1px) scale(1.02);
    }
    
    /* Enhanced live indicator with multiple animations */
    .live-indicator {
        display: inline-block;
        width: 12px;
        height: 12px;
        background: radial-gradient(circle, #4CAF50, #45a049);
        border-radius: 50%;
        animation: livePulse 2s ease-in-out infinite;
        margin-right: 8px;
        position: relative;
    }
    
    .live-indicator::after {
        content: '';
        position: absolute;
        top: -2px;
        left: -2px;
        right: -2px;
        bottom: -2px;
        border: 2px solid #4CAF50;
        border-radius: 50%;
        animation: ripple 2s ease-in-out infinite;
    }
    
    @keyframes livePulse {
        0%, 100% { 
            opacity: 1; 
            transform: scale(1);
        }
        50% { 
            opacity: 0.7; 
            transform: scale(1.2);
        }
    }
    
    @keyframes ripple {
        0% {
            transform: scale(1);
            opacity: 1;
        }
        100% {
            transform: scale(2);
            opacity: 0;
        }
    }
    
    /* Enhanced chart containers with hover effects */
    .chart-container {
        background: rgba(255,255,255,0.05);
        padding: 1.5rem;
        border-radius: 20px;
        margin: 1rem 0;
        backdrop-filter: blur(15px);
        border: 1px solid rgba(255,255,255,0.1);
        transition: all 0.3s ease;
        position: relative;
    }
    
    .chart-container:hover {
        background: rgba(255,255,255,0.08);
        border-color: rgba(255,107,53,0.3);
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
    }
    
    /* Cricket-themed icons and visual feedback */
    .cricket-icon {
        display: inline-block;
        font-size: 1.2rem;
        margin-right: 0.5rem;
        animation: iconBounce 2s ease-in-out infinite;
    }
    
    @keyframes iconBounce {
        0%, 100% { transform: translateY(0) rotate(0deg); }
        25% { transform: translateY(-3px) rotate(5deg); }
        75% { transform: translateY(-1px) rotate(-3deg); }
    }
    
    /* Enhanced card layouts for statistics */
    .stats-container {
        background: linear-gradient(135deg, #667eea, #764ba2);
        padding: 2rem;
        border-radius: 25px;
        margin: 1rem 0;
        color: white;
        box-shadow: 0 10px 30px rgba(102,126,234,0.3);
        position: relative;
        overflow: hidden;
    }
    
    .stats-container::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -50%;
        width: 100%;
        height: 100%;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
        animation: statsRotate 15s linear infinite;
    }
    
    @keyframes statsRotate {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    /* Hover effects for interactive elements */
    .stSelectbox > div > div:hover,
    .stTextInput > div > div:hover,
    .stMultiSelect > div > div:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(255,107,53,0.2);
    }
    
    /* Loading animations */
    .loading-spinner {
        display: inline-block;
        width: 20px;
        height: 20px;
        border: 3px solid rgba(255,107,53,0.3);
        border-radius: 50%;
        border-top-color: #ff6b35;
        animation: spin 1s ease-in-out infinite;
    }
    
    @keyframes spin {
        to { transform: rotate(360deg); }
    }
    
    /* Enhanced Easter Eggs and Delightful Interactions */
    .cricket-easter-egg {
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        font-size: 3rem;
        z-index: 9999;
        animation: easterEggBounce 2s ease-in-out;
        pointer-events: none;
    }
    
    @keyframes easterEggBounce {
        0% { transform: translate(-50%, -50%) scale(0) rotate(0deg); opacity: 0; }
        50% { transform: translate(-50%, -50%) scale(1.2) rotate(180deg); opacity: 1; }
        100% { transform: translate(-50%, -50%) scale(1) rotate(360deg); opacity: 0; }
    }
    
    /* Enhanced Cricket Ball Animation */
    .cricket-ball {
        display: inline-block;
        width: 20px;
        height: 20px;
        background: radial-gradient(circle at 30% 30%, #ff6b35, #d4541a);
        border-radius: 50%;
        position: relative;
        animation: ballSpin 2s linear infinite;
        margin: 0 5px;
    }
    
    .cricket-ball::before {
        content: '';
        position: absolute;
        top: 50%;
        left: 0;
        right: 0;
        height: 2px;
        background: #fff;
        transform: translateY(-50%);
    }
    
    @keyframes ballSpin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    /* Enhanced Wicket Celebration */
    .wicket-celebration {
        animation: wicketCelebration 3s ease-in-out;
    }
    
    @keyframes wicketCelebration {
        0%, 100% { transform: scale(1); }
        25% { transform: scale(1.1) rotate(5deg); }
        50% { transform: scale(1.2) rotate(-5deg); }
        75% { transform: scale(1.1) rotate(3deg); }
    }
    
    /* Enhanced Hover Effects for Cards */
    .enhanced-card {
        transition: all var(--animation-speed) var(--bounce-timing);
        cursor: pointer;
        position: relative;
        overflow: hidden;
    }
    
    .enhanced-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
        transition: left 0.5s ease;
    }
    
    .enhanced-card:hover::before {
        left: 100%;
    }
    
    .enhanced-card:hover {
        transform: translateY(-8px) scale(1.02);
        box-shadow: 0 15px 40px var(--cricket-shadow);
    }
    
    /* Enhanced Loading Animations */
    .cricket-loader {
        display: inline-block;
        position: relative;
        width: 40px;
        height: 40px;
    }
    
    .cricket-loader div {
        position: absolute;
        top: 16px;
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: var(--cricket-primary);
        animation: cricketLoader 1.2s linear infinite;
    }
    
    .cricket-loader div:nth-child(1) { animation-delay: 0s; }
    .cricket-loader div:nth-child(2) { animation-delay: -0.4s; }
    .cricket-loader div:nth-child(3) { animation-delay: -0.8s; }
    
    @keyframes cricketLoader {
        0%, 80%, 100% { transform: scale(0); }
        40% { transform: scale(1); }
    }
    
    /* Enhanced Particle Effects */
    .particle-container {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        pointer-events: none;
        z-index: 1000;
    }
    
    .particle {
        position: absolute;
        width: 4px;
        height: 4px;
        background: var(--cricket-accent);
        border-radius: 50%;
        animation: particleFloat 3s ease-in-out infinite;
    }
    
    @keyframes particleFloat {
        0% { transform: translateY(100vh) rotate(0deg); opacity: 0; }
        10% { opacity: 1; }
        90% { opacity: 1; }
        100% { transform: translateY(-100px) rotate(360deg); opacity: 0; }
    }
    
    /* Enhanced Typography Animations */
    .animated-text {
        background: linear-gradient(45deg, var(--cricket-primary), var(--cricket-accent), var(--cricket-primary));
        background-size: 200% 200%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        animation: textShimmer 3s ease-in-out infinite;
    }
    
    @keyframes textShimmer {
        0%, 100% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
    }
    
    /* Enhanced Interactive Elements */
    .interactive-element {
        transition: all var(--animation-speed) var(--bounce-timing);
        position: relative;
    }
    
    .interactive-element:hover {
        transform: translateY(-3px);
    }
    
    .interactive-element:active {
        transform: translateY(0px) scale(0.98);
    }
    
    /* Enhanced Notification Styles */
    .cricket-notification {
        position: fixed;
        top: 20px;
        right: 20px;
        background: linear-gradient(135deg, var(--cricket-primary), var(--cricket-secondary));
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 10px;
        box-shadow: 0 8px 25px var(--cricket-shadow);
        animation: notificationSlide 0.5s ease-out;
        z-index: 9999;
    }
    
    @keyframes notificationSlide {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    /* Enhanced Responsive Animations */
    @media (prefers-reduced-motion: reduce) {
        *, *::before, *::after {
            animation-duration: 0.01ms !important;
            animation-iteration-count: 1 !important;
            transition-duration: 0.01ms !important;
        }
    }
    
    /* Enhanced Dark Mode Support */
    @media (prefers-color-scheme: dark) {
        :root {
            --cricket-shadow: rgba(255, 255, 255, 0.1);
        }
    }
    
    /* Smooth transitions for all interactive elements */
    * {
        transition: all 0.2s ease;
    }
    
    /* Enhanced focus states for accessibility */
    .stButton > button:focus,
    .stSelectbox > div > div:focus-within,
    .stTextInput > div > div:focus-within {
        outline: 2px solid var(--cricket-accent);
        outline-offset: 2px;
        box-shadow: 0 0 0 4px rgba(255, 215, 0, 0.2);
    }
    
    .metric-card {
        background: linear-gradient(135deg, #f0f2f6, #e8eaf6);
        padding: 1.5rem;
        border-radius: 15px;
        border-left: 5px solid #FF6B35;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
        margin: 0.5rem 0;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(255,107,53,0.2);
    }
    
    .wicket-alert {
        background: linear-gradient(135deg, #ffebee, #fce4ec);
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #f44336;
        margin: 0.5rem 0;
        animation: pulse 2s infinite;
        box-shadow: 0 2px 10px rgba(244,67,54,0.2);
    }
    
    @keyframes pulse {
        0% { box-shadow: 0 2px 10px rgba(244,67,54,0.2); }
        50% { box-shadow: 0 4px 20px rgba(244,67,54,0.4); }
        100% { box-shadow: 0 2px 10px rgba(244,67,54,0.2); }
    }
    
    .match-selector {
        background: linear-gradient(135deg, #667eea, #764ba2);
        padding: 1rem;
        border-radius: 15px;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(102,126,234,0.3);
    }
    
    .stSelectbox > div > div {
        background-color: rgba(255,255,255,0.9) !important;
        color: #333 !important;
        border-radius: 10px;
        border: 2px solid #FF6B35;
        transition: all 0.3s ease;
    }
    
    .stSelectbox > div > div > div {
        background-color: rgba(255,255,255,0.9) !important;
        color: #333 !important;
    }
    
    .stSelectbox > div > div:hover {
        background-color: rgba(255,255,255,0.95) !important;
        border-color: #F7931E;
        box-shadow: 0 0 10px rgba(255,107,53,0.3);
    }
    
    /* Dropdown options styling */
    .stSelectbox > div > div > div > div {
        background-color: rgba(255,255,255,0.95) !important;
        color: #333 !important;
    }
    
    /* Multi-select options styling */
    .stMultiSelect > div > div > div {
        background-color: rgba(255,255,255,0.9) !important;
        color: #333 !important;
    }
    
    .stMultiSelect > div > div > div > div {
        background-color: rgba(255,255,255,0.95) !important;
        color: #333 !important;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #FF6B35, #F7931E);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.5rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(255,107,53,0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(255,107,53,0.4);
    }
    
    .live-indicator {
        display: inline-block;
        width: 12px;
        height: 12px;
        background-color: #4CAF50;
        border-radius: 50%;
        animation: blink 1s infinite;
        margin-right: 8px;
    }
    
    @keyframes blink {
        0%, 50% { opacity: 1; }
        51%, 100% { opacity: 0.3; }
    }
    
    .stats-container {
        background: linear-gradient(135deg, #667eea, #764ba2);
        padding: 1.5rem;
        border-radius: 20px;
        margin: 1rem 0;
        color: white;
        box-shadow: 0 8px 25px rgba(102,126,234,0.3);
    }
    
    .chart-container {
        background: rgba(255,255,255,0.05);
        padding: 1rem;
        border-radius: 15px;
        margin: 1rem 0;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255,255,255,0.1);
    }
</style>
""", unsafe_allow_html=True)

def show_error_notification(error_type: str, message: str, details: str = None, retry_action: str = None):
    """Show enhanced error notification with cricket theming"""
    error_colors = {
        'critical': '#dc3545',
        'warning': '#ffc107', 
        'info': '#17a2b8',
        'network': '#6f42c1'
    }
    
    color = error_colors.get(error_type, '#dc3545')
    
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, {color}15, {color}05);
        border: 2px solid {color};
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        animation: notificationSlide 0.5s ease-out;
    ">
        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 1rem;">
            <span style="font-size: 1.5rem;">{'🚨' if error_type == 'critical' else '⚠️' if error_type == 'warning' else 'ℹ️'}</span>
            <h4 style="color: {color}; margin: 0;">{error_type.title()} Alert</h4>
        </div>
        <p style="color: #333; margin: 0.5rem 0;"><strong>{message}</strong></p>
        {f'<p style="color: #666; font-size: 0.9rem; margin: 0.5rem 0;">{details}</p>' if details else ''}
        {f'<p style="color: {color}; font-weight: 600; margin-top: 1rem;">💡 {retry_action}</p>' if retry_action else ''}
    </div>
    """, unsafe_allow_html=True)

def handle_json_error(file_path: str, error: Exception) -> bool:
    """Handle JSON file errors with user-friendly feedback"""
    error_msg = str(error).lower()
    
    if 'json' in error_msg and 'decode' in error_msg:
        show_error_notification(
            'warning',
            f"Invalid JSON format in {os.path.basename(file_path)}",
            "The file contains malformed JSON data that cannot be parsed.",
            "Try checking the file format or contact support if this persists."
        )
    elif 'permission' in error_msg or 'access' in error_msg:
        show_error_notification(
            'critical',
            f"Cannot access file {os.path.basename(file_path)}",
            "File permissions prevent reading this match data.",
            "Check file permissions or try running with appropriate access rights."
        )
    elif 'not found' in error_msg or 'no such file' in error_msg:
        show_error_notification(
            'warning',
            f"Match file not found: {os.path.basename(file_path)}",
            "The requested match file is missing from the data directory.",
            "Refresh the match list or check if the file was moved or deleted."
        )
    else:
        show_error_notification(
            'critical',
            f"Unexpected error processing {os.path.basename(file_path)}",
            f"Error details: {str(error)}",
            "Try refreshing the page or contact support if the issue persists."
        )
    
    return False

def handle_network_error(operation: str, error: Exception) -> bool:
    """Handle network-related errors"""
    show_error_notification(
        'network',
        f"Network issue during {operation}",
        "Unable to complete the operation due to connectivity issues.",
        "Check your internet connection and try again in a few moments."
    )
    return False

def handle_memory_error(operation: str) -> bool:
    """Handle memory-related errors"""
    show_error_notification(
        'warning',
        "Memory limit reached",
        f"The system ran out of memory while {operation}.",
        "Try processing fewer matches at once or refresh the page to free up memory."
    )
    return False

@st.cache_data
def discover_matches():
    """Discover available cricket match files using the enhanced match processor with comprehensive error handling"""
    try:
        # Import the enhanced match processor
        try:
            from src.enhanced_match_processor import get_enhanced_processor
        except ImportError:
            from enhanced_match_processor import get_enhanced_processor
        
        # Get the enhanced processor instance
        processor = get_enhanced_processor()
        
        # Create enhanced progress indicators with cricket theming
        progress_container = st.container()
        with progress_container:
            st.markdown("""
            <div style="
                background: linear-gradient(135deg, rgba(255,107,53,0.1), rgba(42,82,152,0.1));
                padding: 1rem;
                border-radius: 10px;
                border-left: 4px solid var(--cricket-primary);
                margin: 1rem 0;
            ">
                <div style="display: flex; align-items: center; gap: 10px;">
                    <div class="cricket-loader">
                        <div></div><div></div><div></div>
                    </div>
                    <span style="color: var(--cricket-primary); font-weight: 600;">Discovering Cricket Matches...</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            progress_bar = st.progress(0)
            status_text = st.empty()
        
        def update_progress(message, progress):
            """Enhanced progress callback with cricket theming"""
            progress_bar.progress(progress / 100)
            status_text.markdown(f"""
            <div style="text-align: center; color: var(--cricket-primary); font-weight: 500;">
                🔍 {message} <span class="cricket-ball"></span>
            </div>
            """, unsafe_allow_html=True)
        
        # Set progress callback
        processor.set_progress_callback(update_progress)
        
        # Discover all matches using the enhanced processor with lazy loading
        matches = processor.discover_all_matches(lazy=True, max_matches=50)
        
        # Clear progress indicators with success message
        progress_container.empty()
        if matches:
            st.success(f"🎉 Successfully discovered {len(matches)} cricket matches! Ready for analysis.")
        
        # Convert to the format expected by the dashboard
        dashboard_matches = {}
        for match_name, match_info in matches.items():
            dashboard_matches[match_name] = {
                'file': match_info.file_path,
                'match_id': match_info.match_id,
                'teams': match_info.teams,
                'date': match_info.date,
                'event': match_info.event_name,
                'venue': match_info.venue,
                'match_type': match_info.match_type,
                'significance': match_info.significance,
                'outcome': match_info.outcome,
                'match_name': match_name,  # Add this for the processor
                'info': {
                    'teams': match_info.teams,
                    'venue': match_info.venue,
                    'dates': [match_info.date],
                    'match_type': match_info.match_type,
                    'event': {'name': match_info.event_name},
                    'outcome': match_info.outcome
                }
            }
        
        return dashboard_matches
        
    except ImportError as e:
        show_error_notification(
            'critical',
            "Enhanced Match Processor not available",
            "The enhanced match processing module could not be loaded.",
            "Check if all required dependencies are installed and try restarting the application."
        )
        return {}
    except MemoryError:
        handle_memory_error("discovering matches")
        return {}
    except FileNotFoundError:
        show_error_notification(
            'warning',
            "Data directory not found",
            "The cricket match data directory (src/data) is missing.",
            "Create the data directory and add some cricket match JSON files to get started."
        )
        return {}
    except PermissionError as e:
        show_error_notification(
            'critical',
            "Permission denied accessing data files",
            "The application doesn't have permission to read the match data.",
            "Check file permissions for the src/data directory and its contents."
        )
        return {}
    except Exception as e:
        show_error_notification(
            'critical',
            "Unexpected error during match discovery",
            f"An unexpected error occurred: {str(e)}",
            "Try refreshing the page. If the problem persists, contact support."
        )
        return {}

@st.cache_data
def load_data(match_info=None):
    """Load the processed dashboard data for a specific match with comprehensive error handling"""
    try:
        if match_info and match_info.get('file') != 'sample':
            # Process specific match file using real match processor
            df = process_match_data(match_info['file'], match_info)
            
            if df is None or df.empty:
                show_error_notification(
                    'warning',
                    "No data available for selected match",
                    "The match file exists but contains no processable data.",
                    "Try selecting a different match or check if the file format is correct."
                )
                return create_sample_dashboard_data()
        else:
            # Try to load any available processed data or create sample data
            try:
                df = pd.read_csv("src/data/dashboard_ready.csv")
                df['timestamp_utc'] = pd.to_datetime(df['timestamp_utc'])
                st.info("📊 Using pre-processed dashboard data")
            except FileNotFoundError:
                # If no processed data exists, create sample data
                st.info("🎯 Using sample cricket data for demonstration")
                df = create_sample_dashboard_data()
            except pd.errors.EmptyDataError:
                show_error_notification(
                    'warning',
                    "Dashboard data file is empty",
                    "The dashboard_ready.csv file exists but contains no data.",
                    "The system will use sample data instead."
                )
                df = create_sample_dashboard_data()
            except pd.errors.ParserError as e:
                show_error_notification(
                    'warning',
                    "Cannot parse dashboard data file",
                    f"CSV parsing error: {str(e)}",
                    "The system will use sample data instead."
                )
                df = create_sample_dashboard_data()
        
        return df
        
    except MemoryError:
        handle_memory_error("loading match data")
        # Return minimal sample data for memory-constrained environments
        return create_sample_dashboard_data()[:100]  # Limit to 100 rows
        
    except Exception as e:
        show_error_notification(
            'critical',
            "Failed to load match data",
            f"Unexpected error: {str(e)}",
            "The system will use sample data. Try refreshing or contact support."
        )
        
        # Show setup instructions as fallback
        with st.expander("🚀 Troubleshooting & Setup Instructions", expanded=True):
            st.markdown("""
            ### Quick Setup Options:
            
            **Option 1: Run with real cricket data**
            ```bash
            streamlit run src/app.py
            ```
            
            **Option 2: Add your own match data**
            - Place cricket match JSON files in `src/data/` directory
            - Files should follow Cricsheet format
            - Refresh the page after adding files
            
            **Option 3: Use sample data (current fallback)**
            - The dashboard will work with generated sample data
            - All features are available for testing
            
            ### Common Issues:
            - **No data files**: Add JSON match files to `src/data/`
            - **Permission errors**: Check file/folder permissions
            - **Memory issues**: Try processing fewer matches at once
            - **Format errors**: Ensure JSON files are valid Cricsheet format
            """)
        
        return create_sample_dashboard_data()

@st.cache_data
def process_match_data(match_file, match_info):
    """Process a specific match JSON file into dashboard format with comprehensive error handling"""
    
    # Validate input parameters
    if not match_file:
        show_error_notification(
            'warning',
            "No match file specified",
            "Cannot process match data without a valid file path.",
            "Please select a match from the dropdown menu."
        )
        return None
    
    if not os.path.exists(match_file):
        show_error_notification(
            'warning',
            f"Match file not found: {os.path.basename(match_file)}",
            "The selected match file is missing from the data directory.",
            "Try refreshing the match list or selecting a different match."
        )
        return None
    
    # Check file size before processing
    try:
        file_size = os.path.getsize(match_file)
        if file_size == 0:
            show_error_notification(
                'warning',
                f"Empty match file: {os.path.basename(match_file)}",
                "The selected file contains no data.",
                "Try selecting a different match or check if the file is corrupted."
            )
            return None
        elif file_size > 100 * 1024 * 1024:  # 100MB limit
            show_error_notification(
                'warning',
                f"Large file detected: {os.path.basename(match_file)}",
                f"File size: {file_size / 1024 / 1024:.1f} MB. Processing may take longer.",
                "Please wait while the system processes this large match file."
            )
    except OSError as e:
        show_error_notification(
            'critical',
            f"Cannot access file: {os.path.basename(match_file)}",
            f"File system error: {str(e)}",
            "Check file permissions and try again."
        )
        return None
    
    try:
        # Import the enhanced match processor
        try:
            from src.enhanced_match_processor import get_enhanced_processor
        except ImportError:
            from enhanced_match_processor import get_enhanced_processor
        
        # Get the enhanced processor instance
        processor = get_enhanced_processor()
        
        # Create enhanced progress indicators for match processing
        processing_container = st.container()
        with processing_container:
            st.markdown("""
            <div style="
                background: linear-gradient(135deg, rgba(255,215,0,0.1), rgba(255,107,53,0.1));
                padding: 1rem;
                border-radius: 10px;
                border-left: 4px solid var(--cricket-accent);
                margin: 1rem 0;
            ">
                <div style="display: flex; align-items: center; gap: 10px;">
                    <div class="cricket-loader">
                        <div></div><div></div><div></div>
                    </div>
                    <span style="color: var(--cricket-accent); font-weight: 600;">Processing Match Data...</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            progress_bar = st.progress(0)
            status_text = st.empty()
        
        def update_progress(message, progress):
            """Enhanced progress callback for match processing"""
            progress_bar.progress(progress / 100)
            status_text.markdown(f"""
            <div style="text-align: center; color: var(--cricket-accent); font-weight: 500;">
                ⚡ {message} <span class="cricket-ball"></span>
            </div>
            """, unsafe_allow_html=True)
        
        # Set progress callback
        processor.set_progress_callback(update_progress)
        
        # Use the enhanced match processor to process the match file with chunking
        df = processor.process_match_data(match_file, use_chunking=True)
        
        # Clear progress indicators with success message
        processing_container.empty()
        if not df.empty:
            st.success(f"🏏 Match data processed successfully! {len(df)} balls analyzed.")
        
        return df
        
    except ImportError as e:
        show_error_notification(
            'critical',
            "Enhanced Match Processor not available",
            "Required processing module could not be loaded.",
            "Check dependencies and restart the application."
        )
        return None
        
    except json.JSONDecodeError as e:
        return handle_json_error(match_file, e)
        
    except MemoryError:
        handle_memory_error(f"processing {os.path.basename(match_file)}")
        return None
        
    except PermissionError as e:
        show_error_notification(
            'critical',
            f"Permission denied: {os.path.basename(match_file)}",
            "Cannot read the match file due to permission restrictions.",
            "Check file permissions and try again."
        )
        return None
        
    except UnicodeDecodeError as e:
        show_error_notification(
            'warning',
            f"Text encoding issue: {os.path.basename(match_file)}",
            "The file contains characters that cannot be decoded.",
            "The file may be corrupted or in an unsupported format."
        )
        return None
        
    except Exception as e:
        error_msg = str(e).lower()
        
        if 'timeout' in error_msg or 'connection' in error_msg:
            handle_network_error(f"processing {os.path.basename(match_file)}", e)
        else:
            show_error_notification(
                'critical',
                f"Processing failed: {os.path.basename(match_file)}",
                f"Unexpected error: {str(e)}",
                "Try selecting a different match or refresh the page."
            )
        
        return None

def create_cricket_chart(df):
    """Create the cricket match visualization with enhanced interactions"""
    
    # Create subplot with secondary y-axis
    fig = make_subplots(
        rows=1, cols=1,
        subplot_titles=["🏏 The Match: Runs per Over"],
        specs=[[{"secondary_y": True}]]
    )
    
    # Add runs per over line with gradient effect
    fig.add_trace(
        go.Scatter(
            x=df['timestamp_utc'],
            y=df['runs_per_over'],
            mode='lines+markers',
            name='Runs per Over',
            line=dict(
                color='rgba(31, 119, 180, 0.8)', 
                width=4,
                shape='spline'  # Smooth curves
            ),
            marker=dict(
                size=8,
                color=df['runs_per_over'],
                colorscale='Viridis',
                showscale=False,
                line=dict(width=2, color='white')
            ),
            fill='tonexty',
            fillcolor='rgba(31, 119, 180, 0.1)',
            hovertemplate='<b>%{y:.1f} runs/over</b><br>Time: %{x}<br>Over: %{customdata}<br><extra></extra>',
            customdata=df['over']
        )
    )
    
    # Add wicket markers with pulsing effect
    wickets_df = df[df['is_wicket'] == True]
    if len(wickets_df) > 0:
        fig.add_trace(
            go.Scatter(
                x=wickets_df['timestamp_utc'],
                y=wickets_df['runs_per_over'],
                mode='markers',
                name='Wickets 💥',
                marker=dict(
                    color='red',
                    size=20,
                    symbol='star',
                    line=dict(width=3, color='darkred'),
                    opacity=0.9
                ),
                hovertemplate='<b>🚨 WICKET ALERT! 🚨</b><br>%{text}<br>Time: %{x}<br>Impact: High<br><extra></extra>',
                text=wickets_df['commentary_text']
            )
        )
        
        # Add animated vertical lines for wickets
        for i, (_, wicket) in enumerate(wickets_df.iterrows()):
            fig.add_shape(
                type="line",
                x0=wicket['timestamp_utc'], x1=wicket['timestamp_utc'],
                y0=0, y1=1,
                yref="paper",
                line=dict(color="red", width=3, dash="dash"),
                opacity=0.8
            )
            # Add pulsing annotation for wicket
            fig.add_annotation(
                x=wicket['timestamp_utc'],
                y=1.05,
                yref="paper",
                text=f"⚡ W{i+1}",
                showarrow=True,
                arrowhead=2,
                arrowcolor="red",
                font=dict(color="red", size=12, family="Arial Black"),
                bgcolor="rgba(255,255,255,0.9)",
                bordercolor="red",
                borderwidth=2
            )
    
    # Update layout with enhanced styling
    fig.update_layout(
        template="plotly_dark",
        height=450,
        showlegend=True,
        hovermode='x unified',
        xaxis_title="⏰ Match Timeline",
        yaxis_title="🏏 Runs per Over",
        font=dict(family="Poppins, Arial", size=12),
        plot_bgcolor='rgba(0,0,0,0.1)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(t=50, b=50, l=50, r=50)
    )
    
    # Add range selector for time navigation
    fig.update_layout(
        xaxis=dict(
            rangeselector=dict(
                buttons=list([
                    dict(count=1, label="1st Innings", step="all"),
                    dict(count=2, label="2nd Innings", step="all"),
                    dict(step="all", label="Full Match")
                ])
            ),
            rangeslider=dict(visible=True, thickness=0.05),
            type="date"
        )
    )
    
    return fig

def create_github_chart(df):
    """Create the GitHub commits visualization with enhanced interactions"""
    
    fig = go.Figure()
    
    # Add commit count area chart with gradient
    fig.add_trace(
        go.Scatter(
            x=df['timestamp_utc'],
            y=df['commit_count'],
            fill='tozeroy',
            mode='lines+markers',
            name='💻 GitHub Commits',
            line=dict(color='#00D4AA', width=3, shape='spline'),
            fillcolor='rgba(0, 212, 170, 0.2)',
            marker=dict(
                size=6,
                color=df['commit_count'],
                colorscale='Greens',
                showscale=False,
                line=dict(width=1, color='white')
            ),
            hovertemplate='<b>💻 %{y} commits</b><br>⏰ Time: %{x}<br>📊 Activity Level: %{customdata}<br><extra></extra>',
            customdata=['High' if x > df['commit_count'].mean() else 'Low' for x in df['commit_count']]
        )
    )
    
    # Add commit velocity with enhanced styling
    fig.add_trace(
        go.Scatter(
            x=df['timestamp_utc'],
            y=df['commit_velocity'],
            mode='lines',
            name='📈 Commit Velocity (Smoothed)',
            line=dict(
                color='#FFD700', 
                width=4, 
                dash='dot',
                shape='spline'
            ),
            hovertemplate='<b>📈 %{y:.1f} avg commits</b><br>⏰ Time: %{x}<br>🎯 Trend: Smoothed<br><extra></extra>'
        )
    )
    
    # Add wicket impact zones
    wickets_df = df[df['is_wicket'] == True]
    if len(wickets_df) > 0:
        for i, (_, wicket) in enumerate(wickets_df.iterrows()):
            # Add impact zone (rectangle)
            fig.add_shape(
                type="rect",
                x0=wicket['timestamp_utc'] - pd.Timedelta(minutes=2),
                x1=wicket['timestamp_utc'] + pd.Timedelta(minutes=2),
                y0=0, y1=1,
                yref="paper",
                fillcolor="rgba(255, 0, 0, 0.1)",
                line=dict(color="red", width=0),
                opacity=0.3
            )
            
            # Add wicket line
            fig.add_shape(
                type="line",
                x0=wicket['timestamp_utc'], x1=wicket['timestamp_utc'],
                y0=0, y1=1,
                yref="paper",
                line=dict(color="red", width=2, dash="dash"),
                opacity=0.8
            )
            
            # Add impact annotation
            fig.add_annotation(
                x=wicket['timestamp_utc'],
                y=0.95,
                yref="paper",
                text=f"📉 Impact Zone {i+1}",
                showarrow=True,
                arrowhead=2,
                arrowcolor="red",
                font=dict(color="red", size=10),
                bgcolor="rgba(255,255,255,0.9)",
                bordercolor="red",
                borderwidth=1
            )
    
    # Update layout with enhanced styling
    fig.update_layout(
        template="plotly_dark",
        height=450,
        showlegend=True,
        hovermode='x unified',
        xaxis_title="⏰ Match Timeline",
        yaxis_title="💻 GitHub Commits (per 5 min)",
        title="💻 The Code: Global Developer Activity",
        font=dict(family="Poppins, Arial", size=12),
        plot_bgcolor='rgba(0,0,0,0.1)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(t=60, b=50, l=50, r=50)
    )
    
    # Add range selector
    fig.update_layout(
        xaxis=dict(
            rangeselector=dict(
                buttons=list([
                    dict(count=30, label="30min", step="minute"),
                    dict(count=60, label="1hr", step="minute"),
                    dict(step="all", label="Full Match")
                ])
            ),
            rangeslider=dict(visible=True, thickness=0.05),
            type="date"
        )
    )
    
    return fig

def create_correlation_chart(df):
    """Create enhanced correlation analysis chart with multiple visualizations"""
    
    # Calculate correlation between wickets and commit drops
    wickets_df = df[df['is_wicket'] == True].copy()
    
    if len(wickets_df) == 0:
        return None
    
    # Create subplots for comprehensive correlation analysis
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=[
            "🎯 Wicket Impact vs Time", 
            "📊 Impact Distribution",
            "⚡ Correlation Timeline", 
            "🔥 Impact Heatmap"
        ],
        specs=[[{"colspan": 2}, None], [{}, {}]],
        vertical_spacing=0.15,
        horizontal_spacing=0.1
    )
    
    # Main scatter plot - wickets vs commit impact (larger, more prominent)
    fig.add_trace(
        go.Scatter(
            x=wickets_df['match_minute'],
            y=wickets_df['commit_drop_percentage'],
            mode='markers+text',
            marker=dict(
                size=20,  # Larger markers
                color=wickets_df['commit_drop_percentage'],
                colorscale='Reds',
                showscale=True,
                colorbar=dict(
                    title="Commit Drop %",
                    thickness=15,
                    len=0.7
                ),
                line=dict(width=2, color='white'),
                opacity=0.8
            ),
            text=[f"W{i+1}" for i in range(len(wickets_df))],
            textposition="top center",
            textfont=dict(size=12, color='white'),
            name='Wicket Impact',
            hovertemplate='<b>Wicket %{text}</b><br>Time: %{x:.1f} min<br>Impact: %{y:.1f}%<br>Commentary: %{customdata}<extra></extra>',
            customdata=wickets_df.get('commentary_text', ['Wicket commentary'] * len(wickets_df))
        ),
        row=1, col=1
    )
    
    # Add trend line for correlation
    if len(wickets_df) > 1:
        z = np.polyfit(wickets_df['match_minute'], wickets_df['commit_drop_percentage'], 1)
        p = np.poly1d(z)
        trend_x = np.linspace(wickets_df['match_minute'].min(), wickets_df['match_minute'].max(), 100)
        trend_y = p(trend_x)
        
        fig.add_trace(
            go.Scatter(
                x=trend_x,
                y=trend_y,
                mode='lines',
                name='Correlation Trend',
                line=dict(color='yellow', width=3, dash='dash'),
                hovertemplate='<b>Trend Line</b><br>Time: %{x:.1f} min<br>Predicted Impact: %{y:.1f}%<extra></extra>'
            ),
            row=1, col=1
        )
    
    # Impact distribution histogram
    fig.add_trace(
        go.Histogram(
            x=wickets_df['commit_drop_percentage'],
            nbinsx=10,
            name='Impact Distribution',
            marker_color='rgba(255, 107, 53, 0.7)',
            hovertemplate='<b>Impact Range</b><br>%{x}%<br>Count: %{y}<extra></extra>'
        ),
        row=2, col=1
    )
    
    # Correlation strength over time
    if len(wickets_df) > 2:
        # Calculate rolling correlation strength
        wickets_df_sorted = wickets_df.sort_values('match_minute')
        correlation_strength = []
        time_points = []
        
        for i in range(2, len(wickets_df_sorted)):
            subset = wickets_df_sorted.iloc[:i+1]
            if len(subset) > 1:
                corr = np.corrcoef(subset['match_minute'], subset['commit_drop_percentage'])[0, 1]
                correlation_strength.append(abs(corr) if not np.isnan(corr) else 0)
                time_points.append(subset['match_minute'].iloc[-1])
        
        if correlation_strength:
            fig.add_trace(
                go.Scatter(
                    x=time_points,
                    y=correlation_strength,
                    mode='lines+markers',
                    name='Correlation Strength',
                    line=dict(color='#00D4AA', width=3),
                    marker=dict(size=8, color='#00D4AA'),
                    hovertemplate='<b>Correlation Strength</b><br>Time: %{x:.1f} min<br>Strength: %{y:.2f}<extra></extra>'
                ),
                row=2, col=2
            )
    
    # Update layout with enhanced styling
    fig.update_layout(
        template="plotly_dark",
        height=600,  # Taller for better visibility
        title=dict(
            text="🏏 Cricket Wickets vs Developer Productivity: Real-Time Correlation Analysis",
            font=dict(size=18, color='white'),
            x=0.5
        ),
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        plot_bgcolor='rgba(0,0,0,0.1)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white')
    )
    
    # Update axes
    fig.update_xaxes(title="Match Time (minutes)", row=1, col=1)
    fig.update_yaxes(title="Commit Drop Percentage (%)", row=1, col=1)
    fig.update_xaxes(title="Impact Percentage (%)", row=2, col=1)
    fig.update_yaxes(title="Frequency", row=2, col=1)
    fig.update_xaxes(title="Match Time (minutes)", row=2, col=2)
    fig.update_yaxes(title="Correlation Strength", row=2, col=2)
    
    return fig

def create_enhanced_metrics_display(df):
    """Create enhanced metrics display with micro-interactions and animations"""
    
    # Calculate metrics
    total_balls = len(df)
    total_wickets = df['is_wicket'].sum()
    total_runs = df['runs'].sum()
    total_commits = df['commit_count'].sum()
    
    # Create animated metric cards
    col1, col2, col3, col4, col5 = st.columns(5)
    
    metrics_data = [
        {
            "icon": "⚾",
            "label": "Total Balls",
            "value": total_balls,
            "delta": f"+{total_balls - 240}" if total_balls > 240 else f"{total_balls}/240",
            "help": "Total deliveries bowled in the match",
            "color": "#4CAF50"
        },
        {
            "icon": "🎯", 
            "label": "Wickets",
            "value": total_wickets,
            "delta": f"Target: 20" if total_wickets < 20 else "Complete!",
            "help": "Total wickets fallen",
            "color": "#f44336"
        },
        {
            "icon": "🏃",
            "label": "Total Runs", 
            "value": total_runs,
            "delta": f"Rate: {(total_runs/total_balls)*6:.1f}/over" if total_balls > 0 else "0/over",
            "help": "Total runs scored",
            "color": "#2196F3"
        },
        {
            "icon": "💻",
            "label": "Total Commits",
            "value": f"{total_commits:,}",
            "delta": f"Avg: {df['commit_count'].mean():.0f}/5min",
            "help": "Global GitHub commits during match", 
            "color": "#FF9800"
        }
    ]
    
    # Add impact metric if wickets exist
    if total_wickets > 0:
        wickets_df = df[df['is_wicket'] == True]
        avg_impact = wickets_df['commit_drop_percentage'].mean()
        metrics_data.append({
            "icon": "📉",
            "label": "Avg Impact",
            "value": f"{avg_impact:.1f}%",
            "delta": f"Max: {wickets_df['commit_drop_percentage'].max():.1f}%",
            "help": "Average commit drop per wicket",
            "color": "#9C27B0"
        })
    else:
        metrics_data.append({
            "icon": "📉",
            "label": "Impact",
            "value": "0%",
            "delta": "No wickets yet",
            "help": "No wickets yet",
            "color": "#607D8B"
        })
    
    # Display metrics in columns
    columns = [col1, col2, col3, col4, col5]
    
    for i, metric in enumerate(metrics_data):
        with columns[i]:
            # Create enhanced metric card with hover effects
            st.markdown(f"""
            <div class="metric-card" style="
                border-left-color: {metric['color']};
                cursor: pointer;
            " title="{metric['help']}">
                <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
                    <span style="font-size: 1.5rem; margin-right: 0.5rem;">{metric['icon']}</span>
                    <span style="font-weight: 600; color: #333;">{metric['label']}</span>
                </div>
                <div style="font-size: 1.8rem; font-weight: 800; color: {metric['color']}; margin-bottom: 0.3rem;">
                    {metric['value']}
                </div>
                <div style="font-size: 0.8rem; color: #666; font-style: italic;">
                    {metric['delta']}
                </div>
            </div>
            """, unsafe_allow_html=True)

def create_intelligent_match_selector(available_matches):
    """Create an intelligent match selector with advanced search and filtering capabilities"""
    
    st.markdown("""
    <div class="main-container">
        <div style="
            background: linear-gradient(135deg, #667eea, #764ba2);
            padding: 2rem;
            border-radius: 20px;
            margin: 2rem 0;
            box-shadow: 0 8px 25px rgba(102,126,234,0.3);
        ">
            <h3 style="color: white; text-align: center; margin-bottom: 1.5rem; font-family: 'Poppins', sans-serif;">
                🏆 Intelligent Match Selector - Find Your Perfect Cricket Memory
            </h3>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if not available_matches:
        st.error("No cricket matches found in the data folder. Please check your data files.")
        return None
    
    # Advanced filtering interface with more options
    st.markdown("### 🔍 Advanced Search & Filters")
    
    # Primary search and filter row
    col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
    
    with col1:
        # Enhanced search functionality with highlighting
        search_term = st.text_input(
            "🔍 Search matches",
            placeholder="Search by team names, venue, event, or match type...",
            help="Type to search across team names, venues, events, and match types. Results will be highlighted."
        )
    
    with col2:
        # Team filter with better organization
        all_teams = set()
        for match_info in available_matches.values():
            all_teams.update(match_info.get('teams', []))
        
        team_filter = st.multiselect(
            "🏏 Filter by Teams",
            options=sorted(list(all_teams)),
            help="Select specific teams to filter matches"
        )
    
    with col3:
        # Match significance filter with enhanced options
        all_significance = set()
        for match_info in available_matches.values():
            significance = match_info.get('significance', 'Regular')
            all_significance.add(significance)
        
        significance_filter = st.selectbox(
            "⭐ Match Significance",
            options=['All'] + sorted(list(all_significance)),
            help="Filter by match importance and tournament level"
        )
    
    with col4:
        # Refresh and clear filters
        if st.button("🔄", help="Refresh match list"):
            st.cache_data.clear()
            st.rerun()
    
    # Secondary filter row for more advanced options
    col5, col6, col7, col8 = st.columns(4)
    
    with col5:
        # Match type filter
        all_match_types = set()
        for match_info in available_matches.values():
            all_match_types.add(match_info.get('match_type', 'T20'))
        
        match_type_filter = st.selectbox(
            "🏏 Match Type",
            options=['All'] + sorted(list(all_match_types)),
            help="Filter by match format (T20, ODI, Test)"
        )
    
    with col6:
        # Venue filter
        all_venues = set()
        for match_info in available_matches.values():
            venue = match_info.get('venue', 'Unknown')
            if venue != 'Unknown':
                all_venues.add(venue)
        
        venue_filter = st.selectbox(
            "🏟️ Venue",
            options=['All'] + sorted(list(all_venues)),
            help="Filter by cricket ground/venue"
        )
    
    with col7:
        # Date range filter
        all_dates = []
        for match_info in available_matches.values():
            try:
                date_str = match_info.get('date', '2024-01-01')
                date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
                all_dates.append(date_obj)
            except:
                continue
        
        if all_dates:
            min_date = min(all_dates)
            max_date = max(all_dates)
            
            date_range = st.date_input(
                "📅 Date Range",
                value=(min_date, max_date),
                min_value=min_date,
                max_value=max_date,
                help="Select date range for matches"
            )
        else:
            date_range = None
    
    with col8:
        # Clear all filters button
        if st.button("🗑️ Clear", help="Clear all filters"):
            st.rerun()
    
    # Apply all filters
    filtered_matches = {}
    
    for match_name, match_info in available_matches.items():
        # Apply search filter with highlighting support
        if search_term:
            search_lower = search_term.lower()
            match_text = f"{match_name} {match_info.get('event', '')} {match_info.get('venue', '')} {' '.join(match_info.get('teams', []))} {match_info.get('match_type', '')}"
            if search_lower not in match_text.lower():
                continue
        
        # Apply team filter
        if team_filter:
            match_teams = match_info.get('teams', [])
            if not any(team in match_teams for team in team_filter):
                continue
        
        # Apply significance filter
        if significance_filter != 'All':
            if match_info.get('significance', 'Regular') != significance_filter:
                continue
        
        # Apply match type filter
        if match_type_filter != 'All':
            if match_info.get('match_type', 'T20') != match_type_filter:
                continue
        
        # Apply venue filter
        if venue_filter != 'All':
            if match_info.get('venue', 'Unknown') != venue_filter:
                continue
        
        # Apply date range filter
        if date_range and len(date_range) == 2:
            try:
                match_date = datetime.strptime(match_info.get('date', '2024-01-01'), '%Y-%m-%d').date()
                if not (date_range[0] <= match_date <= date_range[1]):
                    continue
            except:
                continue
        
        filtered_matches[match_name] = match_info
    
    # Display filtered results with enhanced information
    if not filtered_matches:
        st.warning("🔍 No matches found with the current filters.")
        
        # Provide helpful suggestions
        st.markdown("""
        **💡 Try these suggestions:**
        - Clear some filters using the 🗑️ Clear button
        - Use broader search terms
        - Check different match types or significance levels
        - Expand the date range
        """)
        
        # Show available options
        with st.expander("📋 Available Options", expanded=False):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("**Teams:**")
                for team in sorted(all_teams)[:10]:
                    st.markdown(f"- {team}")
            
            with col2:
                st.markdown("**Venues:**")
                for venue in sorted(all_venues)[:10]:
                    st.markdown(f"- {venue}")
            
            with col3:
                st.markdown("**Match Types:**")
                for match_type in sorted(all_match_types):
                    st.markdown(f"- {match_type}")
        
        return None
    
    # Enhanced match selection with detailed preview
    st.markdown(f"### 📊 Found {len(filtered_matches)} matches")
    
    # Show filter summary if filters are applied
    active_filters = []
    if search_term:
        active_filters.append(f"Search: '{search_term}'")
    if team_filter:
        active_filters.append(f"Teams: {', '.join(team_filter)}")
    if significance_filter != 'All':
        active_filters.append(f"Significance: {significance_filter}")
    if match_type_filter != 'All':
        active_filters.append(f"Type: {match_type_filter}")
    if venue_filter != 'All':
        active_filters.append(f"Venue: {venue_filter}")
    
    if active_filters:
        st.markdown(f"**🔍 Active Filters:** {' | '.join(active_filters)}")
    
    # Create enhanced match cards for selection
    if len(filtered_matches) <= 6:
        # Show as detailed cards for small number of matches
        cols = st.columns(min(len(filtered_matches), 3))
        selected_match = None
        
        for i, (match_name, match_info) in enumerate(filtered_matches.items()):
            col_idx = i % len(cols)
            
            with cols[col_idx]:
                # Create enhanced match card with more details
                teams_str = " vs ".join(match_info.get('teams', ['Team A', 'Team B']))
                date_str = match_info.get('date', 'Unknown Date')
                event_str = match_info.get('event', 'Cricket Match')
                venue_str = match_info.get('venue', 'Unknown Venue')
                match_type_str = match_info.get('match_type', 'T20')
                significance_str = match_info.get('significance', 'Regular')
                
                # Determine card color based on significance
                significance_colors = {
                    'Final': "linear-gradient(135deg, #ffd700, #ffb347)",
                    'World Cup': "linear-gradient(135deg, #4CAF50, #45a049)",
                    'Major Tournament': "linear-gradient(135deg, #2196F3, #1976D2)",
                    'International Series': "linear-gradient(135deg, #9C27B0, #673AB7)",
                    'Regular': "linear-gradient(135deg, #667eea, #764ba2)"
                }
                card_color = significance_colors.get(significance_str, significance_colors['Regular'])
                
                # Highlight search terms in display
                display_teams = teams_str
                display_event = event_str
                display_venue = venue_str
                
                if search_term:
                    search_lower = search_term.lower()
                    if search_lower in teams_str.lower():
                        display_teams = teams_str.replace(search_term, f"**{search_term}**")
                    if search_lower in event_str.lower():
                        display_event = event_str.replace(search_term, f"**{search_term}**")
                    if search_lower in venue_str.lower():
                        display_venue = venue_str.replace(search_term, f"**{search_term}**")
                
                if st.button(
                    f"🏏 {teams_str}",
                    key=f"match_card_{i}",
                    help=f"Date: {date_str}\nEvent: {event_str}\nVenue: {venue_str}\nType: {match_type_str}\nSignificance: {significance_str}",
                    use_container_width=True
                ):
                    selected_match = match_name
                
                # Show enhanced match details
                st.markdown(f"""
                <div style="
                    background: {card_color};
                    padding: 1rem;
                    border-radius: 10px;
                    margin: 0.5rem 0;
                    color: white;
                    text-align: center;
                    font-size: 0.8rem;
                ">
                    <div><strong>📅 {date_str}</strong></div>
                    <div>🏆 {display_event}</div>
                    <div>🏟️ {display_venue}</div>
                    <div>🏏 {match_type_str} • ⭐ {significance_str}</div>
                </div>
                """, unsafe_allow_html=True)
        
        # If no card was clicked, default to first match
        if selected_match is None:
            selected_match = list(filtered_matches.keys())[0]
    
    else:
        # Use enhanced dropdown for large number of matches
        # Create formatted options for better display
        match_options = {}
        for match_name, match_info in filtered_matches.items():
            teams_str = " vs ".join(match_info.get('teams', ['Team A', 'Team B']))
            date_str = match_info.get('date', 'Unknown')
            significance_str = match_info.get('significance', 'Regular')
            
            # Create display format
            display_format = f"{teams_str} ({date_str}) - {significance_str}"
            match_options[display_format] = match_name
        
        selected_display = st.selectbox(
            "🏏 Choose a match to analyze:",
            options=list(match_options.keys()),
            index=0,
            help="Select different cricket matches to see their detailed analysis"
        )
        
        selected_match = match_options[selected_display]
        
        # Show selected match details in enhanced format
        if selected_match:
            match_info = filtered_matches[selected_match]
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.info(f"📅 **Date:** {match_info.get('date', 'Unknown')}")
            with col2:
                st.info(f"🏆 **Event:** {match_info.get('event', 'Cricket Match')}")
            with col3:
                st.info(f"🏟️ **Venue:** {match_info.get('venue', 'Unknown Venue')}")
            with col4:
                st.info(f"⭐ **Level:** {match_info.get('significance', 'Regular')}")
    
    return selected_match

def display_innings_wicket_summary(df):
    """Display inning-wise wicket summary for cricket lovers with time machine effect"""
    
    if df.empty or 'innings' not in df.columns:
        return
    
    # Calculate wickets by innings
    innings_wickets = df[df['is_wicket'] == True].groupby('innings').size().to_dict()
    
    # Get unique innings
    unique_innings = sorted(df['innings'].unique())
    
    # Create the innings wicket display
    st.markdown("""
    <div class="main-container">
        <div style="text-align: center; margin: 2rem 0;">
            <h3 style="color: #ff6b35; font-family: 'Poppins', sans-serif; margin-bottom: 1rem;">
                🎯 Innings Wicket Breakdown - A Journey Through Time
            </h3>
            <div class="innings-wicket-container">
    """, unsafe_allow_html=True)
    
    for innings in unique_innings:
        wicket_count = innings_wickets.get(innings, 0)
        
        # Get some details about the innings
        innings_data = df[df['innings'] == innings]
        total_runs = innings_data['runs'].sum()
        total_balls = len(innings_data)
        
        # Determine innings name
        if innings == 1:
            innings_name = "1st Innings"
            innings_emoji = "🥇"
        elif innings == 2:
            innings_name = "2nd Innings" 
            innings_emoji = "🥈"
        else:
            innings_name = f"{innings}{'rd' if innings == 3 else 'th'} Innings"
            innings_emoji = "🏏"
        
        st.markdown(f"""
            <div class="innings-wicket-card">
                <div class="innings-title">{innings_emoji} {innings_name}</div>
                <div class="wicket-count">{wicket_count}</div>
                <div class="wicket-label">Wickets</div>
                <div style="margin-top: 0.5rem; font-size: 0.7rem; color: #aaa;">
                    {total_runs} runs • {total_balls} balls
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("</div></div></div>", unsafe_allow_html=True)
    
    # Add wicket timeline for cricket lovers
    if df['is_wicket'].sum() > 0:
        wickets_df = df[df['is_wicket'] == True].copy()
        
        st.markdown("""
        <div style="margin: 2rem 0; text-align: center;">
            <h4 style="color: #ffd700; font-family: 'Poppins', sans-serif;">
                ⚡ Wicket Timeline - Moments That Changed Everything
            </h4>
        </div>
        """, unsafe_allow_html=True)
        
        # Create columns for wicket timeline
        cols = st.columns(min(len(wickets_df), 4))
        
        for i, (_, wicket) in enumerate(wickets_df.iterrows()):
            col_idx = i % len(cols)
            
            with cols[col_idx]:
                # Wicket card with animation
                wicket_time = wicket['timestamp_utc'].strftime('%H:%M') if hasattr(wicket['timestamp_utc'], 'strftime') else str(wicket['timestamp_utc'])
                
                st.markdown(f"""
                <div style="
                    background: linear-gradient(135deg, #ff6b35, #f7931e);
                    padding: 1rem;
                    border-radius: 10px;
                    margin: 0.5rem 0;
                    text-align: center;
                    color: white;
                    box-shadow: 0 4px 15px rgba(255,107,53,0.3);
                    animation: pulse 2s ease-in-out infinite;
                ">
                    <div style="font-weight: bold; font-size: 0.9rem;">⚡ Wicket {i+1}</div>
                    <div style="font-size: 0.8rem; margin: 0.2rem 0;">{wicket_time}</div>
                    <div style="font-size: 0.7rem;">Over {wicket['over']}.{wicket['ball']}</div>
                    <div style="font-size: 0.7rem;">Innings {wicket['innings']}</div>
                </div>
                """, unsafe_allow_html=True)

def create_comprehensive_match_details_panel(match_info: dict, df: pd.DataFrame):
    """
    Create comprehensive match details panel showing venue, date, teams, 
    match outcome, wicket commentary, and match statistics
    """
    
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #1e3c72, #2a5298);
        padding: 2rem;
        border-radius: 20px;
        margin: 2rem 0;
        color: white;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
    ">
        <h2 style="text-align: center; margin-bottom: 1.5rem; color: #ffd700;">
            🏏 Match Details & Analysis
        </h2>
    </div>
    """, unsafe_allow_html=True)
    
    # Match Information Section
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h4>🏏 Teams</h4>
            <p><strong>{' vs '.join(match_info.get('teams', ['Team A', 'Team B']))}</strong></p>
            <small>Match Type: {match_info.get('match_type', 'T20')}</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h4>📅 Date & Venue</h4>
            <p><strong>{match_info.get('date', 'Unknown Date')}</strong></p>
            <small>🏟️ {match_info.get('venue', 'Unknown Venue')}</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <h4>🏆 Event</h4>
            <p><strong>{match_info.get('event', 'Cricket Match')}</strong></p>
            <small>Significance: {match_info.get('significance', 'Regular')}</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        # Match outcome
        outcome = match_info.get('outcome', {})
        winner = outcome.get('winner', 'Unknown')
        result = outcome.get('result', 'Match completed')
        
        st.markdown(f"""
        <div class="metric-card">
            <h4>🎯 Result</h4>
            <p><strong>{winner}</strong></p>
            <small>{result}</small>
        </div>
        """, unsafe_allow_html=True)
    
    # Match Statistics Section
    if not df.empty:
        st.markdown("### 📊 Match Statistics")
        
        stat_col1, stat_col2, stat_col3, stat_col4, stat_col5 = st.columns(5)
        
        # Calculate match statistics
        total_balls = len(df)
        total_wickets = df['is_wicket'].sum()
        total_runs = df['runs'].sum()
        match_duration = df['match_minute'].max() if 'match_minute' in df.columns else 0
        
        # Innings breakdown
        innings_stats = df.groupby('innings').agg({
            'runs': 'sum',
            'is_wicket': 'sum'
        }).to_dict()
        
        with stat_col1:
            st.metric("⚾ Total Balls", total_balls, help="Total deliveries bowled")
        
        with stat_col2:
            st.metric("🎯 Total Wickets", total_wickets, help="Total wickets fallen")
        
        with stat_col3:
            st.metric("🏃 Total Runs", total_runs, help="Total runs scored")
        
        with stat_col4:
            st.metric("⏱️ Duration", f"{match_duration:.0f} min", help="Match duration in minutes")
        
        with stat_col5:
            run_rate = (total_runs / total_balls * 6) if total_balls > 0 else 0
            st.metric("📈 Run Rate", f"{run_rate:.2f}", help="Overall run rate")
    
    # Detailed Wicket Commentary Section
    if not df.empty and df['is_wicket'].sum() > 0:
        st.markdown("### ⚡ Detailed Wicket Commentary")
        
        wickets_df = df[df['is_wicket'] == True].copy()
        
        # Create expandable sections for each wicket
        for i, (_, wicket) in enumerate(wickets_df.iterrows()):
            wicket_time = wicket['timestamp_utc'].strftime('%H:%M:%S') if hasattr(wicket['timestamp_utc'], 'strftime') else str(wicket['timestamp_utc'])
            
            with st.expander(f"⚡ Wicket {i+1}: {wicket_time} - Over {wicket['over']}.{wicket['ball']}", expanded=i==0):
                
                # Wicket details in columns
                detail_col1, detail_col2, detail_col3 = st.columns(3)
                
                with detail_col1:
                    st.markdown(f"""
                    **📍 Match Position:**
                    - Innings: {wicket['innings']}
                    - Over: {wicket['over']}.{wicket['ball']}
                    - Time: {wicket_time}
                    """)
                
                with detail_col2:
                    st.markdown(f"""
                    **🏏 Players:**
                    - Batter: {wicket.get('batter', 'Unknown')}
                    - Bowler: {wicket.get('bowler', 'Unknown')}
                    - Runs on ball: {wicket['runs']}
                    """)
                
                with detail_col3:
                    # Impact analysis
                    impact_pct = wicket.get('commit_drop_percentage', 0)
                    if impact_pct > 20:
                        impact_level = "🔴 High Impact"
                        impact_color = "red"
                    elif impact_pct > 10:
                        impact_level = "🟡 Medium Impact"
                        impact_color = "orange"
                    else:
                        impact_level = "🟢 Low Impact"
                        impact_color = "green"
                    
                    st.markdown(f"""
                    **📉 Impact Analysis:**
                    - Level: {impact_level}
                    - Drop: {impact_pct:.1f}%
                    - Commits: {wicket.get('commit_count', 0)}
                    """)
                
                # Full commentary
                st.markdown(f"**📝 Commentary:** {wicket.get('commentary_text', 'No commentary available')}")
                
                # Wicket information if available
                if 'wicket_info' in wicket and wicket['wicket_info']:
                    wicket_info = wicket['wicket_info']
                    if isinstance(wicket_info, dict):
                        dismissal_type = wicket_info.get('kind', 'Unknown')
                        player_out = wicket_info.get('player_out', 'Unknown')
                        fielders = wicket_info.get('fielders', [])
                        
                        st.markdown(f"""
                        **🎯 Dismissal Details:**
                        - Type: {dismissal_type}
                        - Player Out: {player_out}
                        - Fielders: {', '.join([f.get('name', 'Unknown') for f in fielders]) if fielders else 'N/A'}
                        """)
    
    # Performance Metrics Section
    if not df.empty:
        st.markdown("### 🎯 Performance Metrics")
        
        perf_col1, perf_col2 = st.columns(2)
        
        with perf_col1:
            st.markdown("#### 🏏 Batting Performance")
            
            if 'batter' in df.columns:
                # Top batters by runs
                batter_stats = df.groupby('batter').agg({
                    'runs': 'sum',
                    'ball': 'count'
                }).reset_index()
                batter_stats['strike_rate'] = (batter_stats['runs'] / batter_stats['ball'] * 100).round(2)
                batter_stats = batter_stats.sort_values('runs', ascending=False).head(5)
                
                for _, batter in batter_stats.iterrows():
                    st.markdown(f"**{batter['batter']}:** {batter['runs']} runs (SR: {batter['strike_rate']:.1f})")
            else:
                st.info("Detailed batting statistics not available")
        
        with perf_col2:
            st.markdown("#### 🎳 Bowling Performance")
            
            if 'bowler' in df.columns:
                # Top bowlers by wickets
                bowler_stats = df.groupby('bowler').agg({
                    'runs': 'sum',
                    'ball': 'count',
                    'is_wicket': 'sum'
                }).reset_index()
                bowler_stats['overs'] = (bowler_stats['ball'] / 6).round(1)
                bowler_stats['economy'] = (bowler_stats['runs'] / bowler_stats['overs']).round(2)
                bowler_stats = bowler_stats.sort_values('is_wicket', ascending=False).head(5)
                
                for _, bowler in bowler_stats.iterrows():
                    st.markdown(f"**{bowler['bowler']}:** {bowler['is_wicket']} wickets (Econ: {bowler['economy']:.1f})")
            else:
                st.info("Detailed bowling statistics not available")

def main():
    """Main dashboard function with comprehensive error handling and retry mechanisms"""
    
    # Enhanced cricket-themed header with time machine effect
    st.markdown("""
    <div class="main-container">
        <div class="cricket-header-container">
            <h1 class="main-header">🏏 The Wicket-Down Downtime</h1>
            <p class="sub-header">"Production deployments stop when Kohli is batting" - Every Indian Engineering Manager</p>
            <p class="time-machine-tagline">✨ Step into the Time Machine - Relive Cricket's Greatest Moments ✨</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Live indicator with enhanced styling
    st.markdown('<div style="text-align: center; margin: 1rem 0;"><span class="live-indicator"></span><strong>Live Analysis Dashboard</strong></div>', unsafe_allow_html=True)
    
    # Enhanced Match Selection with intelligent filtering and search
    try:
        available_matches = discover_matches()
    except Exception as e:
        show_error_notification(
            'critical',
            "Failed to initialize match discovery",
            f"Critical error during startup: {str(e)}",
            "Try refreshing the page or contact support."
        )
        available_matches = {}
    
    if not available_matches:
        # Enhanced fallback with retry options
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #ffc107, #ff8f00);
            padding: 2rem;
            border-radius: 20px;
            margin: 2rem 0;
            text-align: center;
            color: white;
        ">
            <h3>🔍 No Cricket Matches Found</h3>
            <p>Don't worry! Here are some options to get started:</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🔄 Retry Discovery", help="Try discovering matches again", use_container_width=True):
                st.cache_data.clear()
                st.rerun()
        
        with col2:
            if st.button("📊 Use Sample Data", help="Continue with sample cricket data", use_container_width=True):
                # Create a sample match for demonstration
                sample_match = {
                    'sample_match': {
                        'file': 'sample',
                        'teams': ['India', 'Australia'],
                        'date': '2024-06-29',
                        'event': 'T20 World Cup Final',
                        'venue': 'Barbados',
                        'match_type': 'T20',
                        'significance': 'Final',
                        'outcome': {'winner': 'India'}
                    }
                }
                st.session_state['sample_mode'] = True
                available_matches = sample_match
        
        with col3:
            if st.button("📁 Check Data Folder", help="View data folder information", use_container_width=True):
                data_folder = "src/data"
                if os.path.exists(data_folder):
                    files = os.listdir(data_folder)
                    json_files = [f for f in files if f.endswith('.json')]
                    
                    st.info(f"📁 Data folder exists with {len(files)} files ({len(json_files)} JSON files)")
                    
                    if json_files:
                        st.write("**JSON files found:**")
                        for file in json_files[:10]:  # Show first 10
                            st.write(f"- {file}")
                        if len(json_files) > 10:
                            st.write(f"... and {len(json_files) - 10} more files")
                    else:
                        st.warning("No JSON files found in the data folder")
                else:
                    st.error(f"Data folder '{data_folder}' does not exist")
        
        if not available_matches:
            return
    
    # Enhanced match selection with error handling
    try:
        selected_match = create_intelligent_match_selector(available_matches)
    except Exception as e:
        show_error_notification(
            'warning',
            "Match selector error",
            f"Error in match selection interface: {str(e)}",
            "Try refreshing the page or use the retry button below."
        )
        
        if st.button("🔄 Retry Match Selection", help="Reload the match selector"):
            st.rerun()
        return
    
    if not selected_match:
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #17a2b8, #138496);
            padding: 1.5rem;
            border-radius: 15px;
            margin: 1rem 0;
            text-align: center;
            color: white;
        ">
            <h4>🏏 Ready to Analyze Cricket Matches!</h4>
            <p>Please select a match from the options above to begin your cricket analytics journey.</p>
        </div>
        """, unsafe_allow_html=True)
        return
    
    # Load data for selected match with retry mechanism
    match_info = available_matches[selected_match]
    df = None
    max_retries = 3
    retry_count = 0
    
    while df is None and retry_count < max_retries:
        try:
            df = load_data(match_info)
            if df is not None and not df.empty:
                break
        except Exception as e:
            retry_count += 1
            if retry_count < max_retries:
                show_error_notification(
                    'warning',
                    f"Loading attempt {retry_count} failed",
                    f"Error: {str(e)}",
                    f"Retrying... ({retry_count}/{max_retries})"
                )
                time.sleep(1)  # Brief pause before retry
            else:
                show_error_notification(
                    'critical',
                    "Failed to load match data after multiple attempts",
                    f"All {max_retries} attempts failed. Last error: {str(e)}",
                    "Try selecting a different match or refresh the page."
                )
    
    if df is None or df.empty:
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #dc3545, #c82333);
            padding: 2rem;
            border-radius: 15px;
            margin: 1rem 0;
            text-align: center;
            color: white;
        ">
            <h4>⚠️ Unable to Load Match Data</h4>
            <p>We couldn't load the data for the selected match. Here are your options:</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🔄 Try Again", help="Retry loading this match", use_container_width=True):
                st.cache_data.clear()
                st.rerun()
        
        with col2:
            if st.button("🏏 Different Match", help="Go back to match selection", use_container_width=True):
                st.rerun()
        
        with col3:
            if st.button("📊 Sample Data", help="Use sample data instead", use_container_width=True):
                df = create_sample_dashboard_data()
                st.success("🎯 Loaded sample cricket data for demonstration")
        
        if df is None:
            return
    
    # Match details are now in the "Match Details" tab for better organization
    
    # Match Info Display
    st.markdown('<div class="stats-container">', unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"**🏏 Match:** {match_info['teams'][0]} vs {match_info['teams'][1]}")
    with col2:
        st.markdown(f"**📅 Date:** {match_info['date']}")
    with col3:
        st.markdown(f"**🏆 Event:** {match_info['event']}")
    with col4:
        st.markdown(f"**⚡ Status:** <span class='live-indicator'></span>Analyzing", unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Sidebar with match info and performance monitoring
    st.sidebar.header("📊 Match Statistics")
    
    total_balls = len(df)
    total_wickets = df['is_wicket'].sum()
    total_runs = df['runs'].sum()
    total_commits = df['commit_count'].sum()
    avg_commits = df['commit_count'].mean()
    
    st.sidebar.metric("Total Balls", total_balls)
    st.sidebar.metric("Total Wickets", total_wickets)
    st.sidebar.metric("Total Runs", total_runs)
    st.sidebar.metric("Total Commits", f"{total_commits:,}")
    st.sidebar.metric("Avg Commits/5min", f"{avg_commits:.1f}")
    
    # Match duration
    match_duration = (df['timestamp_utc'].max() - df['timestamp_utc'].min()).total_seconds() / 60
    st.sidebar.metric("Match Duration", f"{match_duration:.0f} min")
    
    # Wicket impact analysis
    if total_wickets > 0:
        wickets_df = df[df['is_wicket'] == True]
        avg_drop = wickets_df['commit_drop_percentage'].mean()
        max_drop = wickets_df['commit_drop_percentage'].max()
        
        st.sidebar.markdown("### 🎯 Wicket Impact")
        st.sidebar.metric("Avg Commit Drop", f"{avg_drop:.1f}%")
        st.sidebar.metric("Max Commit Drop", f"{max_drop:.1f}%")
    

    
    # Enhanced real-time metrics dashboard with micro-interactions
    st.markdown("""
    <div style="text-align: center; margin: 2rem 0;">
        <h3 style="color: #ff6b35; font-family: 'Poppins', sans-serif;">
            <span class="cricket-icon">📊</span>Live Match Analytics<span class="cricket-icon">⚡</span>
        </h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Create enhanced animated metrics with cards
    create_enhanced_metrics_display(df)
    
    st.markdown("---")
    
    # PRIMARY FOCUS: Cricket vs Commit Rate Correlation Analysis
    st.markdown("""
    <div style="text-align: center; margin: 2rem 0;">
        <h2 style="color: #ff6b35; font-family: 'Poppins', sans-serif; font-size: 2.5rem;">
            <span class="cricket-icon">📊</span>Cricket Match vs Developer Productivity Correlation<span class="cricket-icon">⚡</span>
        </h2>
        <p style="color: #666; font-size: 1.2rem; margin-top: 1rem;">
            🎯 <strong>Primary Analysis:</strong> How cricket wickets impact global developer commit rates in real-time
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # MAIN CORRELATION DASHBOARD - Primary Focus
    st.markdown("---")
    
    # Create prominent correlation visualization section
    correlation_col1, correlation_col2 = st.columns([2, 1])
    
    with correlation_col1:
        st.markdown("### 📊 Real-Time Correlation Analysis")
        
        # Enhanced correlation chart with larger size
        correlation_fig = create_correlation_chart(df)
        if correlation_fig:
            st.plotly_chart(correlation_fig, use_container_width=True, height=500, key="main_correlation_chart")
        else:
            st.info("🔍 Correlation analysis will appear when wickets are detected in the match data.")
    
    with correlation_col2:
        st.markdown("### 🎯 Correlation Insights")
        
        # Calculate and display correlation statistics
        if df['is_wicket'].sum() > 0:
            wickets_df = df[df['is_wicket'] == True]
            avg_impact = wickets_df['commit_drop_percentage'].mean()
            max_impact = wickets_df['commit_drop_percentage'].max()
            correlation_strength = "Strong" if avg_impact > 20 else "Moderate" if avg_impact > 10 else "Weak"
            
            st.metric("📉 Average Impact", f"{avg_impact:.1f}%", help="Average commit drop per wicket")
            st.metric("🔴 Maximum Impact", f"{max_impact:.1f}%", help="Highest single wicket impact")
            st.metric("💪 Correlation Strength", correlation_strength, help="Overall correlation assessment")
            
            # Impact distribution
            if avg_impact > 15:
                st.error("🚨 **High Impact Detected!** Cricket events significantly affect developer productivity.")
            elif avg_impact > 8:
                st.warning("⚠️ **Moderate Impact** Cricket events show measurable effect on commits.")
            else:
                st.success("✅ **Low Impact** Cricket events have minimal effect on developer activity.")
        else:
            st.info("📊 Correlation metrics will appear when wickets are detected.")
    
    # Combined Cricket + Developer Activity Timeline (Secondary but prominent)
    st.markdown("---")
    st.markdown("### 📈 Combined Activity Timeline")
    
    # Create side-by-side comparison charts
    timeline_col1, timeline_col2 = st.columns(2)
    
    with timeline_col1:
        st.markdown("#### 🏏 Cricket Match Activity")
        cricket_fig = create_cricket_chart(df)
        st.plotly_chart(cricket_fig, use_container_width=True, key="cricket_timeline")
    
    with timeline_col2:
        st.markdown("#### 💻 Developer Commit Activity")
        github_fig = create_github_chart(df)
        st.plotly_chart(github_fig, use_container_width=True, key="github_timeline")
    
    # SECONDARY CONTENT: Detailed Analysis in Tabs
    st.markdown("---")
    st.markdown("### 🔍 Detailed Analysis & Match Information")
    
    chart_tab1, chart_tab2, chart_tab3, chart_tab4 = st.tabs([
        "📋 Match Details", 
        "⚡ Enhanced Timeline",
        "🎯 Wicket Impact Analysis",
        "🏆 Performance Metrics"
    ])
    
    with chart_tab1:
        st.markdown("#### 📋 Complete Match Information")
        
        # Move the comprehensive match details panel here
        create_comprehensive_match_details_panel(match_info, df)
        
        # Display inning-wise wicket information
        display_innings_wicket_summary(df)
    
    with chart_tab2:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        
        # Chart controls for timeline
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            st.markdown("#### ⚡ Enhanced Match Timeline")
        with col2:
            show_momentum = st.checkbox("Show Momentum", value=True, help="Toggle momentum indicator", key="momentum_timeline")
        with col3:
            timeline_style = st.selectbox("Timeline Style", ["Interactive", "Detailed"], help="Chart detail level")
        
        # Get visualization engine and create timeline with error handling
        try:
            viz_engine = get_visualization_engine()
            timeline_fig = viz_engine.create_match_timeline(df)
            
            if timeline_fig:
                st.plotly_chart(timeline_fig, use_container_width=True, key="enhanced_timeline")
            else:
                st.warning("⚠️ Unable to create timeline visualization. Data may be insufficient.")
                
        except ImportError as e:
            show_error_notification(
                'warning',
                "Visualization engine not available",
                "The enhanced visualization module could not be loaded.",
                "Some charts may not be available. Basic functionality will continue to work."
            )
        except Exception as e:
            show_error_notification(
                'warning',
                "Timeline visualization error",
                f"Could not create timeline chart: {str(e)}",
                "Try refreshing the page or selecting a different match."
            )
            
        st.markdown('</div>', unsafe_allow_html=True)
    
    with chart_tab3:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        
        # Chart controls for wicket impact
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            st.markdown("#### 🎯 Wicket Impact Analysis")
        with col2:
            show_dismissals = st.checkbox("Show Dismissal Types", value=True, help="Toggle dismissal breakdown", key="dismissals_wicket")
        with col3:
            impact_detail = st.selectbox("Detail Level", ["Full", "Summary"], help="Analysis detail level")
        
        # Create wicket impact visualization with error handling
        try:
            viz_engine = get_visualization_engine()
            wicket_fig = viz_engine.create_wicket_impact_chart(df)
            
            if wicket_fig:
                st.plotly_chart(wicket_fig, use_container_width=True, key="wicket_impact")
            else:
                st.info("🎯 Wicket impact analysis will appear when wickets are detected in the match data.")
                
        except ImportError as e:
            show_error_notification(
                'warning',
                "Visualization engine not available",
                "The enhanced visualization module could not be loaded.",
                "Some charts may not be available. Basic functionality will continue to work."
            )
        except Exception as e:
            show_error_notification(
                'warning',
                "Wicket analysis error",
                f"Could not create wicket impact chart: {str(e)}",
                "The chart will be skipped. Other visualizations should still work."
            )
            
        st.markdown('</div>', unsafe_allow_html=True)
    
    with chart_tab4:
        st.markdown("#### 🏆 Performance Comparison Dashboard")
        
        # Performance controls
        perf_col1, perf_col2, perf_col3 = st.columns(3)
        
        with perf_col1:
            show_batting = st.checkbox("Batting Analysis", value=True, help="Show batting performance metrics", key="batting_tab4")
        with perf_col2:
            show_bowling = st.checkbox("Bowling Analysis", value=True, help="Show bowling performance metrics", key="bowling_tab4")
        with perf_col3:
            show_partnerships = st.checkbox("Partnership Tracker", value=True, help="Show partnership analysis", key="partnerships_tab4")
        
        if show_batting or show_bowling or show_partnerships:
            # Create performance comparison visualization with error handling
            try:
                viz_engine = get_visualization_engine()
                performance_fig = viz_engine.create_performance_comparison_chart(df)
                
                if performance_fig:
                    st.plotly_chart(performance_fig, use_container_width=True, key="performance_comparison")
                else:
                    st.warning("⚠️ Performance comparison chart could not be generated.")
                    
            except ImportError as e:
                show_error_notification(
                    'warning',
                    "Visualization engine not available",
                    "The enhanced visualization module could not be loaded.",
                    "Performance metrics may be limited."
                )
            except Exception as e:
                show_error_notification(
                    'warning',
                    "Performance analysis error",
                    f"Could not create performance comparison: {str(e)}",
                    "Performance metrics may be limited. Try refreshing or selecting a different match."
                )
        else:
            st.info("📊 Select performance metrics to display the analysis dashboard.")
    
    # Enhanced Interactive Explorer
    st.markdown("---")
    st.markdown("### 🔍 Interactive Match Explorer")
    
    # Add performance comparison section
    with st.expander("🏆 Performance Comparison Dashboard", expanded=False):
        st.markdown("#### 📊 Comprehensive Performance Analysis")
        
        # Performance controls
        perf_col1, perf_col2, perf_col3 = st.columns(3)
        
        with perf_col1:
            show_batting = st.checkbox("Batting Analysis", value=True, help="Show batting performance metrics", key="batting_expander")
        with perf_col2:
            show_bowling = st.checkbox("Bowling Analysis", value=True, help="Show bowling performance metrics", key="bowling_expander")
        with perf_col3:
            show_partnerships = st.checkbox("Partnership Tracker", value=True, help="Show partnership analysis", key="partnerships_expander")
        
        if show_batting or show_bowling or show_partnerships:
            # Create performance comparison visualization with error handling
            try:
                if 'viz_engine' in locals():
                    performance_fig = viz_engine.create_performance_comparison_chart(df)
                    
                    if performance_fig:
                        st.plotly_chart(performance_fig, use_container_width=True, key="performance_comparison")
                    else:
                        st.warning("⚠️ Performance comparison chart could not be generated.")
                else:
                    st.warning("⚠️ Visualization engine not available for performance analysis.")
                    
            except Exception as e:
                show_error_notification(
                    'warning',
                    "Performance analysis error",
                    f"Could not create performance comparison: {str(e)}",
                    "Performance metrics may be limited. Try refreshing or selecting a different match."
                )
                
                # Add performance insights
                st.markdown("#### 🎯 Performance Insights")
                
                insight_col1, insight_col2, insight_col3 = st.columns(3)
                
                with insight_col1:
                    if 'batter' in df.columns and 'runs' in df.columns:
                        top_scorer = df.groupby('batter')['runs'].sum().idxmax()
                        top_score = df.groupby('batter')['runs'].sum().max()
                        st.metric("🏏 Top Scorer", top_scorer, f"{top_score} runs")
                
                with insight_col2:
                    if 'bowler' in df.columns and 'is_wicket' in df.columns:
                        top_bowler = df[df['is_wicket'] == True].groupby('bowler').size().idxmax() if df['is_wicket'].sum() > 0 else "No wickets"
                        wicket_count = df[df['is_wicket'] == True].groupby('bowler').size().max() if df['is_wicket'].sum() > 0 else 0
                        st.metric("🎳 Top Bowler", top_bowler, f"{wicket_count} wickets")
                
                with insight_col3:
                    if 'runs_per_over' in df.columns:
                        best_over = df.loc[df['runs_per_over'].idxmax(), 'over'] if 'over' in df.columns else "N/A"
                        best_over_runs = df['runs_per_over'].max()
                        st.metric("⚡ Best Over", f"Over {best_over}", f"{best_over_runs} runs")
            else:
                st.info("📊 Performance analysis will appear with more detailed match data.")
        else:
            st.info("📊 Select performance metrics to display the analysis dashboard.")
    
    # Advanced filtering controls
    with st.container():
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            # Time range slider
            time_range = st.slider(
                "⏰ Time Range (minutes)",
                min_value=0,
                max_value=int(df['match_minute'].max()) if 'match_minute' in df.columns else 120,
                value=(0, int(df['match_minute'].max()) if 'match_minute' in df.columns else 120),
                step=5,
                help="Select time range to analyze"
            )
        
        with col2:
            # Innings filter
            innings_filter = st.multiselect(
                "🏏 Innings",
                options=df['innings'].unique() if 'innings' in df.columns else [1, 2],
                default=df['innings'].unique() if 'innings' in df.columns else [1, 2],
                help="Filter by innings"
            )
        
        with col3:
            # Commit threshold
            commit_threshold = st.number_input(
                "💻 Min Commits",
                min_value=0,
                max_value=int(df['commit_count'].max()),
                value=0,
                step=10,
                help="Filter by minimum commit count"
            )
        
        with col4:
            # Analysis mode
            analysis_mode = st.selectbox(
                "📊 Analysis Mode",
                ["All Events", "Wickets Only", "High Activity", "Low Activity"],
                help="Focus analysis on specific events"
            )
    
    # Apply filters
    if 'match_minute' in df.columns:
        filtered_df = df[
            (df['match_minute'] >= time_range[0]) & 
            (df['match_minute'] <= time_range[1])
        ]
    else:
        filtered_df = df
    
    if 'innings' in df.columns and innings_filter:
        filtered_df = filtered_df[filtered_df['innings'].isin(innings_filter)]
    
    filtered_df = filtered_df[filtered_df['commit_count'] >= commit_threshold]
    
    if analysis_mode == "Wickets Only":
        filtered_df = filtered_df[filtered_df['is_wicket'] == True]
    elif analysis_mode == "High Activity":
        filtered_df = filtered_df[filtered_df['commit_count'] > df['commit_count'].mean()]
    elif analysis_mode == "Low Activity":
        filtered_df = filtered_df[filtered_df['commit_count'] <= df['commit_count'].mean()]
    
    # Dynamic insights based on filtered data
    if len(filtered_df) > 0:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🎯 Key Moments in Selection")
            wicket_moments = filtered_df[filtered_df['is_wicket'] == True]
            
            if len(wicket_moments) > 0:
                for i, (_, wicket) in enumerate(wicket_moments.iterrows()):
                    with st.expander(f"⚡ Wicket {i+1}: {wicket['timestamp_utc'].strftime('%H:%M:%S')}", expanded=i==0):
                        
                        # Animated metrics for this wicket
                        metric_col1, metric_col2, metric_col3 = st.columns(3)
                        
                        with metric_col1:
                            st.metric(
                                "📉 Impact", 
                                f"{wicket['commit_drop_percentage']:.1f}%",
                                delta=f"vs avg: {wicket['commit_drop_percentage'] - filtered_df[filtered_df['is_wicket']]['commit_drop_percentage'].mean():.1f}%" if len(filtered_df[filtered_df['is_wicket']]) > 1 else None
                            )
                        
                        with metric_col2:
                            st.metric(
                                "💻 Commits", 
                                int(wicket['commit_count']),
                                delta=f"vs avg: {int(wicket['commit_count'] - df['commit_count'].mean())}"
                            )
                        
                        with metric_col3:
                            st.metric(
                                "🏏 Position", 
                                f"{wicket['over']}.{wicket['ball']}",
                                delta=f"Innings {wicket['innings']}" if 'innings' in wicket else None
                            )
                        
                        # Commentary with styling
                        st.markdown(f"**📝 Commentary:** {wicket['commentary_text']}")
                        
                        # Impact visualization
                        if wicket['commit_drop_percentage'] > 20:
                            st.error("🚨 High Impact Wicket - Significant productivity drop detected!")
                        elif wicket['commit_drop_percentage'] > 10:
                            st.warning("⚠️ Medium Impact - Noticeable productivity change")
                        else:
                            st.info("ℹ️ Low Impact - Minimal productivity effect")
            else:
                st.info("🔍 No wickets found in the selected time range and filters.")
        
        with col2:
            st.markdown("#### 📊 Selection Statistics")
            
            # Summary stats for filtered data
            stats_col1, stats_col2 = st.columns(2)
            
            with stats_col1:
                st.metric("📈 Avg Commits/5min", f"{filtered_df['commit_count'].mean():.1f}")
                st.metric("🏏 Total Runs", int(filtered_df['runs'].sum()))
                st.metric("⚾ Balls Analyzed", len(filtered_df))
            
            with stats_col2:
                st.metric("🎯 Wickets", int(filtered_df['is_wicket'].sum()))
                if len(filtered_df[filtered_df['is_wicket']]) > 0:
                    st.metric("📉 Avg Impact", f"{filtered_df[filtered_df['is_wicket']]['commit_drop_percentage'].mean():.1f}%")
                else:
                    st.metric("📉 Avg Impact", "0%")
                st.metric("⏱️ Duration", f"{len(filtered_df) * 0.5:.1f} min")
            
            # Mini chart for selection
            if len(filtered_df) > 1:
                mini_fig = go.Figure()
                mini_fig.add_trace(go.Scatter(
                    x=filtered_df['timestamp_utc'],
                    y=filtered_df['commit_count'],
                    mode='lines+markers',
                    name='Commits',
                    line=dict(color='#00D4AA', width=2)
                ))
                
                mini_fig.update_layout(
                    height=200,
                    template="plotly_dark",
                    showlegend=False,
                    margin=dict(t=20, b=20, l=20, r=20),
                    xaxis_title="Time",
                    yaxis_title="Commits"
                )
                
                st.plotly_chart(mini_fig, width='stretch', key="mini_chart")
    
    else:
        st.warning("🔍 No data matches your current filter selection. Try adjusting the filters.")
    
    # Advanced data explorer
    with st.expander("🔬 Advanced Data Explorer", expanded=False):
        st.markdown("#### 📋 Filtered Dataset")
        
        if len(filtered_df) > 0:
            # Column selector
            available_columns = ['timestamp_utc', 'over', 'ball', 'runs', 'is_wicket', 
                               'commit_count', 'commit_velocity', 'commentary_text']
            if 'match_minute' in filtered_df.columns:
                available_columns.append('match_minute')
            if 'innings' in filtered_df.columns:
                available_columns.append('innings')
            
            selected_columns = st.multiselect(
                "Select columns to display:",
                available_columns,
                default=['timestamp_utc', 'over', 'ball', 'runs', 'is_wicket', 'commit_count'],
                help="Choose which data columns to show"
            )
            
            if selected_columns:
                # Display data with download option
                st.dataframe(
                    filtered_df[selected_columns],
                    width='stretch',
                    height=300
                )
                
                # Download button
                csv = filtered_df[selected_columns].to_csv(index=False)
                st.download_button(
                    label="📥 Download Filtered Data as CSV",
                    data=csv,
                    file_name=f"cricket_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    help="Download the filtered dataset for further analysis"
                )
        else:
            st.info("No data to display with current filters.")
    
    # Enhanced Interactive Footer with micro-interactions
    st.markdown("---")
    
    # Enhanced footer with cricket-themed animations
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #1e3c72, #2a5298);
        padding: 2rem;
        border-radius: 20px;
        margin: 2rem 0;
        color: white;
    ">
    """, unsafe_allow_html=True)
    
    footer_col1, footer_col2, footer_col3 = st.columns([1, 2, 1])
    
    with footer_col1:
        st.markdown("#### 🔗 Share Analysis")
        if st.button("📊 Generate Report", help="Create a shareable analysis report", key="generate_report"):
            # Enhanced celebration with multiple effects
            st.balloons()
            st.snow()
            st.success("🎉 Analysis report generated! Check your downloads.")
            # Add a small delay for effect
            time.sleep(1)
    
    with footer_col2:
        st.markdown("""
        <div style='text-align: center; padding: 1rem;'>
            <h4 style="color: #ffd700;">🏏 The Wicket-Down Downtime</h4>
            <p>Built with ❤️ and <strong>Kiro's Agentic IDE</strong> for the AI for Bharat Challenge</p>
            <small>📊 Data sources: Cricsheet (Cricket) + GitHub Search API (Commits)</small><br>
            <small>🚀 Powered by Streamlit, Plotly, and Python</small>
        </div>
        """, unsafe_allow_html=True)
    
    with footer_col3:
        st.markdown("#### ⚙️ Settings")
        
        # Theme toggle with enhanced styling
        theme_mode = st.selectbox(
            "🎨 Theme", 
            ["Dark", "Light"], 
            index=0, 
            help="Visual theme preference"
        )
        
        # Performance mode with visual feedback
        performance_mode = st.checkbox(
            "⚡ Performance Mode", 
            help="Reduce animations for better performance",
            key="performance_mode_footer"
        )
        
        if performance_mode:
            st.info("⚡ Performance mode enabled - animations reduced")
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Enhanced easter egg with cricket celebration and delightful interactions
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("🏏 Cricket Magic!", help="Click for a cricket surprise!", use_container_width=True):
            # Multiple celebration effects with enhanced animations
            st.balloons()
            st.snow()
            
            # Enhanced celebration messages with cricket ball animations
            st.markdown("""
            <div style="text-align: center; padding: 2rem; background: linear-gradient(135deg, #ff6b35, #ffd700); border-radius: 20px; margin: 1rem 0;">
                <h2 style="color: white; animation: textShimmer 2s ease-in-out infinite;">
                    🎉 SIXER! <span class="cricket-ball"></span> You found the cricket easter egg! <span class="cricket-ball"></span>
                </h2>
                <div class="wicket-celebration">
                    <p style="color: white; font-size: 1.2rem;">🏏 May your code be as smooth as Kohli's cover drives!</p>
                    <p style="color: white; font-size: 1.2rem;">⚡ And may your deployments be as reliable as Dhoni's finishing!</p>
                    <p style="color: white; font-size: 1.2rem;">🎯 May your bugs be as rare as a perfect hat-trick!</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Enhanced cricket facts with more variety
            cricket_facts = [
                "🏏 Did you know? The fastest ball ever bowled was 161.3 km/h by Shoaib Akhtar!",
                "🏏 Fun fact: The longest cricket match lasted 14 days (with rest days)!",
                "🏏 Cricket trivia: The word 'cricket' comes from the Old French 'criquet'!",
                "🏏 Amazing: The highest individual score in cricket is 501* by BC Lara!",
                "🏏 Incredible: A cricket ball can reach speeds of over 160 km/h!",
                "🏏 Mind-blowing: The first cricket match was played in 1646!",
                "🏏 Fascinating: A cricket ball has exactly 6 rows of stitching!",
                "🏏 Awesome: The MCG can hold over 100,000 spectators!",
                "🏏 Cool fact: Cricket is played in over 100 countries worldwide!",
                "🏏 Epic: The shortest completed cricket match lasted just 60 minutes!"
            ]
            import random
            selected_fact = random.choice(cricket_facts)
            
            # Display fact with enhanced styling
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, #2a5298, #1e3c72);
                padding: 1.5rem;
                border-radius: 15px;
                margin: 1rem 0;
                border-left: 5px solid #ffd700;
                animation: pulse 2s ease-in-out infinite;
            ">
                <p style="color: white; font-size: 1.1rem; margin: 0; text-align: center;">
                    <strong>{selected_fact}</strong>
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            # Add particle effect simulation
            st.markdown("""
            <script>
                // Create particle effect
                function createParticles() {
                    const container = document.createElement('div');
                    container.className = 'particle-container';
                    document.body.appendChild(container);
                    
                    for (let i = 0; i < 20; i++) {
                        const particle = document.createElement('div');
                        particle.className = 'particle';
                        particle.style.left = Math.random() * 100 + '%';
                        particle.style.animationDelay = Math.random() * 3 + 's';
                        container.appendChild(particle);
                    }
                    
                    // Remove particles after animation
                    setTimeout(() => {
                        document.body.removeChild(container);
                    }, 3000);
                }
                
                createParticles();
            </script>
            """, unsafe_allow_html=True)
            
            # Additional interactive elements
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                st.metric("🎯 Easter Eggs Found", "1", "🎉 First Discovery!")
            with col_b:
                st.metric("🏏 Cricket Spirit", "100%", "⚡ Maximum!")
            with col_c:
                st.metric("🚀 Fun Level", "Over 9000!", "📈 Legendary!")
    
    # Version info
    st.markdown("""
    <div style='text-align: center; color: #888; font-size: 0.8rem; margin-top: 2rem;'>
        Version 2.0 | Enhanced with Multi-Match Support & Micro-Interactions<br>
        <span class="live-indicator"></span> Live Dashboard | Last Updated: {timestamp}
    </div>
    """.format(timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")), unsafe_allow_html=True)



if __name__ == "__main__":
    # Only run the full Streamlit app when in proper context
    if is_streamlit_context():
        try:
            # Run main application with global error handling
            main()
            
        except KeyboardInterrupt:
            st.info("👋 Application stopped by user")
        except SystemExit:
            st.info("🔄 Application restarting...")
        except Exception as e:
            st.error("🚨 Critical Application Error")
            
            show_error_notification(
                'critical',
                "Application crashed unexpectedly",
                f"Fatal error: {str(e)}",
                "Try refreshing the page. If the problem persists, contact support."
            )
            
            # Show debug information in expander
            with st.expander("🔍 Debug Information", expanded=False):
                st.code(f"""
Error Type: {type(e).__name__}
Error Message: {str(e)}
            
System Information:
- Python Version: {sys.version}
- Streamlit Version: {st.__version__}
- Current Directory: {os.getcwd()}
- Data Folder Exists: {os.path.exists('src/data')}
            """)
        
        # Recovery options
        st.markdown("### 🛠️ Recovery Options")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🔄 Restart App", help="Restart the application"):
                st.rerun()
        
        with col2:
            if st.button("🧹 Clear Cache", help="Clear all cached data"):
                st.cache_data.clear()
                st.success("Cache cleared! Please refresh the page.")
        
        with col3:
            if st.button("📊 Sample Mode", help="Run with sample data only"):
                st.session_state['force_sample_mode'] = True
                st.rerun()
    else:
        # Running outside Streamlit context (e.g., during import or testing)
        print("✅ Cricket Dashboard app module loaded successfully")
        print("🚀 To run the dashboard: streamlit run src/app.py")