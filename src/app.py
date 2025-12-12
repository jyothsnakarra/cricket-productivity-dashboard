#!/usr/bin/env python3
"""
Streamlit Dashboard: The Wicket-Down Downtime
T20 World Cup Final vs. Global Developer Productivity
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="The Wicket-Down Downtime",
    page_icon="🏏",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for dark theme and styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #FF6B35;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
        font-style: italic;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #FF6B35;
    }
    .wicket-alert {
        background-color: #ffebee;
        padding: 0.5rem;
        border-radius: 0.25rem;
        border-left: 3px solid #f44336;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    """Load the processed dashboard data"""
    try:
        df = pd.read_csv("src/data/dashboard_ready.csv")
        df['timestamp_utc'] = pd.to_datetime(df['timestamp_utc'])
        return df
    except FileNotFoundError:
        st.error("Dashboard data not found. Please run the data processing pipeline first.")
        st.code("""
        # Run these commands in order:
        python src/ingest_cricket.py
        python src/ingest_github.py  
        python src/process_data.py
        """)
        return None

def create_cricket_chart(df):
    """Create the cricket match visualization"""
    
    # Create subplot with secondary y-axis
    fig = make_subplots(
        rows=1, cols=1,
        subplot_titles=["🏏 The Match: Runs per Over"],
        specs=[[{"secondary_y": True}]]
    )
    
    # Add runs per over line
    fig.add_trace(
        go.Scatter(
            x=df['timestamp_utc'],
            y=df['runs_per_over'],
            mode='lines+markers',
            name='Runs per Over',
            line=dict(color='#1f77b4', width=3),
            marker=dict(size=6),
            hovertemplate='<b>%{y} runs</b><br>Time: %{x}<br><extra></extra>'
        )
    )
    
    # Add wicket markers
    wickets_df = df[df['is_wicket'] == True]
    if len(wickets_df) > 0:
        fig.add_trace(
            go.Scatter(
                x=wickets_df['timestamp_utc'],
                y=wickets_df['runs_per_over'],
                mode='markers',
                name='Wickets',
                marker=dict(
                    color='red',
                    size=15,
                    symbol='x',
                    line=dict(width=3, color='darkred')
                ),
                hovertemplate='<b>WICKET!</b><br>%{text}<br>Time: %{x}<br><extra></extra>',
                text=wickets_df['commentary_text']
            )
        )
        
        # Add vertical lines for wickets using shapes
        for _, wicket in wickets_df.iterrows():
            fig.add_shape(
                type="line",
                x0=wicket['timestamp_utc'], x1=wicket['timestamp_utc'],
                y0=0, y1=1,
                yref="paper",
                line=dict(color="red", width=2, dash="dash"),
                opacity=0.7
            )
            # Add annotation for wicket
            fig.add_annotation(
                x=wicket['timestamp_utc'],
                y=1.02,
                yref="paper",
                text="WICKET",
                showarrow=False,
                font=dict(color="red", size=10),
                bgcolor="rgba(255,255,255,0.8)"
            )
    
    # Update layout
    fig.update_layout(
        template="plotly_dark",
        height=400,
        showlegend=True,
        hovermode='x unified',
        xaxis_title="Match Time",
        yaxis_title="Runs per Over"
    )
    
    return fig

def create_github_chart(df):
    """Create the GitHub commits visualization"""
    
    fig = go.Figure()
    
    # Add commit count area chart
    fig.add_trace(
        go.Scatter(
            x=df['timestamp_utc'],
            y=df['commit_count'],
            fill='tonexty',
            mode='lines',
            name='GitHub Commits',
            line=dict(color='#2E8B57', width=2),
            fillcolor='rgba(46, 139, 87, 0.3)',
            hovertemplate='<b>%{y} commits</b><br>Time: %{x}<br><extra></extra>'
        )
    )
    
    # Add commit velocity (smoothed line)
    fig.add_trace(
        go.Scatter(
            x=df['timestamp_utc'],
            y=df['commit_velocity'],
            mode='lines',
            name='Commit Velocity (3-ball avg)',
            line=dict(color='#90EE90', width=3, dash='dot'),
            hovertemplate='<b>%{y:.1f} avg commits</b><br>Time: %{x}<br><extra></extra>'
        )
    )
    
    # Highlight wicket moments using shapes
    wickets_df = df[df['is_wicket'] == True]
    if len(wickets_df) > 0:
        for _, wicket in wickets_df.iterrows():
            fig.add_shape(
                type="line",
                x0=wicket['timestamp_utc'], x1=wicket['timestamp_utc'],
                y0=0, y1=1,
                yref="paper",
                line=dict(color="red", width=1, dash="dash"),
                opacity=0.5
            )
    
    # Update layout
    fig.update_layout(
        template="plotly_dark",
        height=400,
        showlegend=True,
        hovermode='x unified',
        xaxis_title="Match Time",
        yaxis_title="GitHub Commits (per 5 min)",
        title="💻 The Code: Global GitHub Activity"
    )
    
    return fig

def create_correlation_chart(df):
    """Create correlation analysis chart"""
    
    # Calculate correlation between wickets and commit drops
    wickets_df = df[df['is_wicket'] == True].copy()
    
    if len(wickets_df) == 0:
        st.warning("No wickets found in the data for correlation analysis.")
        return None
    
    fig = go.Figure()
    
    # Scatter plot of wickets vs commit impact
    fig.add_trace(
        go.Scatter(
            x=wickets_df['match_minute'],
            y=wickets_df['commit_drop_percentage'],
            mode='markers+text',
            marker=dict(
                size=15,
                color=wickets_df['commit_drop_percentage'],
                colorscale='Reds',
                showscale=True,
                colorbar=dict(title="Commit Drop %")
            ),
            text=[f"Wicket {i+1}" for i in range(len(wickets_df))],
            textposition="top center",
            hovertemplate='<b>%{text}</b><br>Match Minute: %{x:.1f}<br>Commit Drop: %{y:.1f}%<br><extra></extra>'
        )
    )
    
    fig.update_layout(
        template="plotly_dark",
        height=400,
        title="📊 Wicket Impact Analysis: Commit Drops",
        xaxis_title="Match Time (minutes)",
        yaxis_title="Commit Drop Percentage (%)"
    )
    
    return fig

def main():
    """Main dashboard function"""
    
    # Header
    st.markdown('<h1 class="main-header">🏏 The Wicket-Down Downtime</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">"Production deployments stop when Kohli is batting" - Every Indian Engineering Manager</p>', unsafe_allow_html=True)
    
    # Load data
    df = load_data()
    if df is None:
        return
    
    # Sidebar with match info
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
    
    # Main dashboard
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("🏏 The Match")
        cricket_fig = create_cricket_chart(df)
        st.plotly_chart(cricket_fig, width='stretch')
    
    with col2:
        st.subheader("💻 The Code")
        github_fig = create_github_chart(df)
        st.plotly_chart(github_fig, width='stretch')
    
    # Correlation analysis
    st.subheader("📈 The Correlation")
    correlation_fig = create_correlation_chart(df)
    if correlation_fig:
        st.plotly_chart(correlation_fig, width='stretch')
    
    # Interactive data exploration
    st.subheader("🔍 Interactive Data Explorer")
    
    # Time range selector
    col1, col2 = st.columns(2)
    
    # Get unique time options
    time_options_start = df['timestamp_utc'].dt.strftime('%H:%M:%S').unique()[:10]
    time_options_end = df['timestamp_utc'].dt.strftime('%H:%M:%S').unique()[-10:]
    
    with col1:
        start_time = st.selectbox(
            "Start Time",
            options=time_options_start,
            index=0
        )
    with col2:
        end_time = st.selectbox(
            "End Time", 
            options=time_options_end,
            index=len(time_options_end)-1  # Last item, not -1
        )
    
    # Filter data based on selection
    filtered_df = df[
        (df['timestamp_utc'].dt.strftime('%H:%M:%S') >= start_time) &
        (df['timestamp_utc'].dt.strftime('%H:%M:%S') <= end_time)
    ]
    
    # Show key moments
    st.subheader("🎯 Key Moments")
    
    wicket_moments = filtered_df[filtered_df['is_wicket'] == True]
    if len(wicket_moments) > 0:
        for _, wicket in wicket_moments.iterrows():
            with st.expander(f"⚡ Wicket at {wicket['timestamp_utc'].strftime('%H:%M:%S')}"):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Commit Drop", f"{wicket['commit_drop_percentage']:.1f}%")
                with col2:
                    st.metric("Commits at Time", int(wicket['commit_count']))
                with col3:
                    st.metric("Over.Ball", f"{wicket['over']}.{wicket['ball']}")
                
                st.write(f"**Commentary:** {wicket['commentary_text']}")
    else:
        st.info("No wickets in selected time range")
    
    # Raw data view
    if st.checkbox("Show Raw Data"):
        st.subheader("📋 Raw Data")
        st.dataframe(
            filtered_df[['timestamp_utc', 'over', 'ball', 'runs', 'is_wicket', 
                        'commit_count', 'commit_velocity', 'commentary_text']],
            width='stretch'
        )
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; padding: 1rem;'>
        Built with ❤️ and Kiro's Agentic IDE for the AI for Bharat Challenge<br>
        <small>Data sources: Cricsheet (Cricket) + GitHub Search API (Commits)</small>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()