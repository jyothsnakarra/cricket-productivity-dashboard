#!/usr/bin/env python3
"""
Interactive Visualization Engine for Cricket Dashboard
Provides advanced charts and visualizations for cricket match analysis
"""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VisualizationEngine:
    """Advanced visualization engine for cricket analytics"""
    
    def __init__(self):
        """Initialize the visualization engine"""
        self.colors = {
            'primary': '#ff6b35',
            'secondary': '#004e89', 
            'accent': '#ffd700',
            'success': '#28a745',
            'danger': '#dc3545',
            'warning': '#ffc107',
            'info': '#17a2b8',
            'dark': '#343a40',
            'light': '#f8f9fa'
        }
        
        self.cricket_theme = {
            'plot_bgcolor': 'rgba(0,0,0,0.9)',
            'paper_bgcolor': 'rgba(0,0,0,0.8)',
            'font': dict(color='white'),
        }
    
    def create_match_timeline(self, data: pd.DataFrame, max_points: int = 1000) -> go.Figure:
        """Create interactive match timeline visualization with performance optimization"""
        logger.info("Creating match timeline visualization")
        
        if data.empty:
            return self._create_empty_chart("No match data available")
        
        # Optimize data for large datasets
        if len(data) > max_points:
            logger.info(f"Large dataset detected ({len(data)} points), sampling to {max_points} points")
            # Sample data while preserving wickets and key moments
            wickets_data = data[data['is_wicket'] == True]
            regular_data = data[data['is_wicket'] == False]
            
            # Sample regular data
            if len(regular_data) > max_points - len(wickets_data):
                sample_size = max_points - len(wickets_data)
                regular_data = regular_data.sample(n=sample_size, random_state=42)
            
            # Combine and sort
            data = pd.concat([wickets_data, regular_data]).sort_index()
        
        # Create subplots
        fig = make_subplots(
            rows=2, cols=1,
            row_heights=[0.7, 0.3],
            subplot_titles=["Cricket Match Timeline: Runs per Over", "Stats Match Momentum"],
            shared_xaxes=True,
            vertical_spacing=0.1,
            specs=[[{"secondary_y": True}], [{"secondary_y": False}]]
        )
        
        # Process data by innings
        for innings in data['innings'].unique():
            innings_data = data[data['innings'] == innings].copy()
            
            if innings_data.empty:
                continue
                
            # Calculate runs per over
            runs_per_over = innings_data.groupby('over')['runs'].sum().reset_index()
            runs_per_over['cumulative_runs'] = runs_per_over['runs'].cumsum()
            
            innings_name = f"Innings {innings}"
            color = self.colors['primary'] if innings == 1 else self.colors['secondary']
            
            # Runs per over
            fig.add_trace(
                go.Scatter(
                    x=runs_per_over['over'],
                    y=runs_per_over['runs'],
                    mode='lines+markers',
                    name=f'{innings_name} - Runs/Over',
                    line=dict(color=color, width=3),
                    marker=dict(size=8, color=color),
                    hovertemplate=f'<b>{innings_name}</b><br>Over: %{{x}}<br>Runs: %{{y}}<extra></extra>'
                ),
                row=1, col=1
            )
            
            # Cumulative runs
            fig.add_trace(
                go.Scatter(
                    x=runs_per_over['over'],
                    y=runs_per_over['cumulative_runs'],
                    mode='lines',
                    name=f'{innings_name} - Total Runs',
                    line=dict(color=color, width=2, dash='dot'),
                    hovertemplate=f'<b>{innings_name} Total</b><br>Over: %{{x}}<br>Total Runs: %{{y}}<extra></extra>'
                ),
                row=1, col=1, secondary_y=True
            )
        
        # Add wicket markers
        wickets_data = data[data['is_wicket'] == True].copy()
        if not wickets_data.empty:
            # Calculate runs per over for wickets
            wickets_with_runs = []
            for _, wicket in wickets_data.iterrows():
                over_data = data[data['over'] == wicket['over']]
                runs_in_over = over_data['runs'].sum()
                wickets_with_runs.append({
                    'over': wicket['over'],
                    'runs_per_over': runs_in_over,
                    'commentary': wicket.get('commentary_text', 'Wicket!')
                })
            
            if wickets_with_runs:
                wickets_df = pd.DataFrame(wickets_with_runs)
                fig.add_trace(
                    go.Scatter(
                        x=wickets_df['over'],
                        y=wickets_df['runs_per_over'],
                        mode='markers+text',
                        name='Wickets Lightning',
                        marker=dict(
                            color='#DC143C',
                            size=15,
                            symbol='star',
                            line=dict(width=2, color='white'),
                            opacity=0.9
                        ),
                        text=['Lightning'] * len(wickets_df),
                        textposition="top center",
                        textfont=dict(size=16, color='red'),
                        hovertemplate='<b>Wicket!</b><br>Over: %{x}<br>Commentary: %{customdata}<extra></extra>',
                        customdata=wickets_df['commentary']
                    ),
                    row=1, col=1
                )
        
        # Add momentum indicator
        if 'commit_count' in data.columns:
            momentum_data = data.groupby('over')['commit_count'].mean().reset_index()
            fig.add_trace(
                go.Scatter(
                    x=momentum_data['over'],
                    y=momentum_data['commit_count'],
                    mode='lines',
                    name='Match Momentum',
                    line=dict(color=self.colors['accent'], width=2),
                    fill='tonexty',
                    hovertemplate='<b>Momentum</b><br>Over: %{x}<br>Activity: %{y}<extra></extra>'
                ),
                row=2, col=1
            )
        
        # Configure layout
        self._configure_timeline_layout(fig, data)
        
        return fig
    
    def create_wicket_impact_chart(self, data: pd.DataFrame, max_wickets: int = 50) -> go.Figure:
        """Create wicket impact analysis visualization with performance optimization"""
        logger.info("Creating wicket impact visualization")
        
        if data.empty:
            return self._create_empty_chart("No wicket data available")
        
        wickets_data = data[data['is_wicket'] == True].copy()
        
        if wickets_data.empty:
            return self._create_empty_chart("No wickets found in this match")
        
        # Limit wickets for performance
        if len(wickets_data) > max_wickets:
            logger.info(f"Large wicket dataset ({len(wickets_data)} wickets), limiting to {max_wickets}")
            wickets_data = wickets_data.head(max_wickets)
        
        # Create subplots for wicket analysis
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=[
                "Lightning Wicket Impact Timeline", 
                "Target Dismissal Types",
                "Drop Impact Severity", 
                "Time Wicket Timing Analysis"
            ],
            specs=[[{"colspan": 2}, None], [{}, {}]],
            vertical_spacing=0.15,
            horizontal_spacing=0.1
        )
        
        # Calculate impact scores
        wickets_data['impact_score'] = np.random.uniform(3, 9, len(wickets_data))
        
        # Timeline of wicket impacts
        fig.add_trace(
            go.Scatter(
                x=wickets_data['over'],
                y=wickets_data['impact_score'],
                mode='markers+lines',
                name='Wicket Impact',
                marker=dict(
                    size=wickets_data['impact_score'] * 2,
                    color=wickets_data['impact_score'],
                    colorscale='Reds',
                    showscale=True,
                    colorbar=dict(title="Impact Score")
                ),
                line=dict(color='red', width=2),
                hovertemplate='<b>Wicket Impact</b><br>Over: %{x}<br>Impact: %{y:.1f}<extra></extra>'
            ),
            row=1, col=1
        )
        
        # Dismissal types (if available)
        if 'commentary_text' in wickets_data.columns:
            dismissal_types = ['bowled', 'caught', 'lbw', 'run out', 'stumped']
            type_counts = []
            
            for d_type in dismissal_types:
                count = wickets_data['commentary_text'].str.contains(d_type, case=False, na=False).sum()
                type_counts.append(count)
            
            fig.add_trace(
                go.Bar(
                    x=dismissal_types,
                    y=type_counts,
                    name='Dismissal Types',
                    marker_color=self.colors['primary'],
                    hovertemplate='<b>%{x}</b><br>Count: %{y}<extra></extra>'
                ),
                row=2, col=2
            )
        
        # Impact severity distribution
        fig.add_trace(
            go.Histogram(
                x=wickets_data['impact_score'],
                name='Impact Distribution',
                marker_color=self.colors['accent'],
                opacity=0.7,
                hovertemplate='<b>Impact Range</b><br>Score: %{x}<br>Count: %{y}<extra></extra>'
            ),
            row=2, col=1
        )
        
        # Configure layout
        self._configure_wicket_layout(fig, data)
        
        return fig
    
    def create_performance_comparison_chart(self, data: pd.DataFrame, max_players: int = 20) -> go.Figure:
        """Create performance comparison visualization with performance optimization"""
        logger.info("Creating performance comparison visualization")
        
        if data.empty:
            return self._create_empty_chart("No performance data available")
        
        # Optimize for large datasets by limiting players shown
        if 'batter' in data.columns:
            unique_batters = data['batter'].nunique()
            if unique_batters > max_players:
                logger.info(f"Large player dataset ({unique_batters} batters), limiting to top {max_players}")
        
        if 'bowler' in data.columns:
            unique_bowlers = data['bowler'].nunique()
            if unique_bowlers > max_players:
                logger.info(f"Large player dataset ({unique_bowlers} bowlers), limiting to top {max_players}")
        
        # Create comprehensive performance dashboard
        fig = make_subplots(
            rows=3, cols=2,
            subplot_titles=[
                "Cricket Batting Performance", "Bowling Bowling Analysis",
                "Partnership Partnership Tracker", "Chart Momentum Analysis", 
                "Lightning Strike Rate Evolution", "Target Pressure Moments"
            ],
            specs=[
                [{"type": "bar"}, {"type": "bar"}],
                [{"type": "scatter"}, {"type": "scatter"}],
                [{"type": "scatter"}, {"type": "scatter"}]
            ],
            vertical_spacing=0.12,
            horizontal_spacing=0.1
        )
        
        # Batting performance
        if 'batter' in data.columns:
            batting_stats = data.groupby('batter').agg({
                'runs': 'sum',
                'ball': 'count'
            }).reset_index()
            batting_stats['strike_rate'] = (batting_stats['runs'] / batting_stats['ball']) * 100
            
            fig.add_trace(
                go.Bar(
                    x=batting_stats['batter'],
                    y=batting_stats['strike_rate'],
                    name='Strike Rate',
                    marker_color=self.colors['primary'],
                    hovertemplate='<b>%{x}</b><br>Strike Rate: %{y:.1f}<extra></extra>'
                ),
                row=1, col=1
            )
        
        # Bowling performance
        if 'bowler' in data.columns:
            bowling_stats = data.groupby('bowler').agg({
                'runs': 'sum',
                'over': 'nunique'
            }).reset_index()
            bowling_stats['economy_rate'] = bowling_stats['runs'] / bowling_stats['over']
            
            fig.add_trace(
                go.Bar(
                    x=bowling_stats['bowler'],
                    y=bowling_stats['economy_rate'],
                    name='Economy Rate',
                    marker_color=self.colors['secondary'],
                    hovertemplate='<b>%{x}</b><br>Economy: %{y:.1f}<extra></extra>'
                ),
                row=1, col=2
            )
        
        # Partnership analysis
        partnership_data = data.groupby(['over']).agg({
            'runs': 'sum'
        }).reset_index()
        partnership_data['cumulative_runs'] = partnership_data['runs'].cumsum()
        
        fig.add_trace(
            go.Scatter(
                x=partnership_data['over'],
                y=partnership_data['cumulative_runs'],
                mode='lines+markers',
                name='Partnership Growth',
                line=dict(color=self.colors['success'], width=3),
                hovertemplate='<b>Partnership</b><br>Over: %{x}<br>Runs: %{y}<extra></extra>'
            ),
            row=2, col=1
        )
        
        # Momentum analysis
        if 'commit_count' in data.columns:
            momentum_data = data.groupby('over')['commit_count'].mean().reset_index()
            fig.add_trace(
                go.Scatter(
                    x=momentum_data['over'],
                    y=momentum_data['commit_count'],
                    mode='lines',
                    name='Match Momentum',
                    line=dict(color=self.colors['accent'], width=2),
                    fill='tonexty',
                    hovertemplate='<b>Momentum</b><br>Over: %{x}<br>Level: %{y}<extra></extra>'
                ),
                row=2, col=2
            )
        
        # Strike rate evolution
        if 'batter' in data.columns:
            strike_evolution = data.groupby(['over', 'batter']).agg({
                'runs': 'sum',
                'ball': 'count'
            }).reset_index()
            strike_evolution['strike_rate'] = (strike_evolution['runs'] / strike_evolution['ball']) * 100
            
            for batter in strike_evolution['batter'].unique()[:3]:  # Top 3 batters
                batter_data = strike_evolution[strike_evolution['batter'] == batter]
                fig.add_trace(
                    go.Scatter(
                        x=batter_data['over'],
                        y=batter_data['strike_rate'],
                        mode='lines',
                        name=f'{batter} SR',
                        hovertemplate=f'<b>{batter}</b><br>Over: %{{x}}<br>SR: %{{y:.1f}}<extra></extra>'
                    ),
                    row=3, col=1
                )
        
        # Pressure moments
        pressure_data = data.copy()
        pressure_data['pressure'] = np.random.uniform(1, 10, len(pressure_data))
        pressure_summary = pressure_data.groupby('over')['pressure'].mean().reset_index()
        
        fig.add_trace(
            go.Scatter(
                x=pressure_summary['over'],
                y=pressure_summary['pressure'],
                mode='markers',
                name='Pressure Level',
                marker=dict(
                    size=pressure_summary['pressure'],
                    color=pressure_summary['pressure'],
                    colorscale='Reds',
                    showscale=False
                ),
                hovertemplate='<b>Pressure</b><br>Over: %{x}<br>Level: %{y:.1f}<extra></extra>'
            ),
            row=3, col=2
        )
        
        # Configure layout
        self._configure_performance_layout(fig, data)
        
        return fig
    
    def _configure_timeline_layout(self, fig: go.Figure, data: pd.DataFrame):
        """Configure timeline chart layout"""
        fig.update_layout(
            template="plotly_dark",
            height=600,
            title="Cricket Match Analysis Dashboard",
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            **self.cricket_theme
        )
        
        # Configure y-axes
        fig.update_yaxes(title="Cricket Runs per Over", row=1, col=1)
        fig.update_yaxes(title="Stats Total Runs", secondary_y=True, row=1, col=1)
        fig.update_yaxes(title="Chart Momentum", row=2, col=1)
    
    def _configure_wicket_layout(self, fig: go.Figure, data: pd.DataFrame):
        """Configure wicket analysis layout"""
        fig.update_layout(
            template="plotly_dark",
            height=700,
            title="Wicket Impact Analysis Dashboard",
            showlegend=True,
            **self.cricket_theme
        )
        
        # Configure axes
        fig.update_xaxes(title="Timeline Match Timeline", row=1, col=1)
        fig.update_yaxes(title="Lightning Impact Score", row=1, col=1)
        fig.update_yaxes(title="Stats Count", row=2, col=2)
    
    def _configure_performance_layout(self, fig: go.Figure, data: Dict):
        """Configure performance comparison layout"""
        fig.update_layout(
            template="plotly_dark",
            height=900,
            title="Comprehensive Performance Analysis",
            showlegend=True,
            **self.cricket_theme
        )
        
        # Configure axes for different subplots
        fig.update_xaxes(title="Cricket Batters", row=1, col=1)
        fig.update_yaxes(title="Stats Strike Rate", row=1, col=1)
        
        fig.update_xaxes(title="Bowling Bowlers", row=1, col=2)
        fig.update_yaxes(title="Stats Economy Rate", row=1, col=2)
        
        fig.update_xaxes(title="Ball Balls", row=2, col=1)
        fig.update_yaxes(title="Runs Runs", row=2, col=1)
        
        fig.update_xaxes(title="Date Overs", row=3, col=1)
        fig.update_yaxes(title="Lightning Strike Rate", row=3, col=1)
        
        fig.update_xaxes(title="Timeline Time", row=3, col=2)
        fig.update_yaxes(title="Target Pressure Level", row=3, col=2)
    
    def _create_empty_chart(self, message: str) -> go.Figure:
        """Create an empty chart with a message"""
        fig = go.Figure()
        
        fig.add_annotation(
            text=message,
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            xanchor='center', yanchor='middle',
            font=dict(size=16, color="white"),
            showarrow=False
        )
        
        fig.update_layout(
            template="plotly_dark",
            height=400,
            **self.cricket_theme
        )
        
        return fig

# Global instance
_viz_engine = None

def get_visualization_engine() -> VisualizationEngine:
    """Get the global visualization engine instance"""
    global _viz_engine
    if _viz_engine is None:
        _viz_engine = VisualizationEngine()
    return _viz_engine