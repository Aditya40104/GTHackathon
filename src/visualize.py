"""
Visualization module for generating charts and graphs.
"""
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import pandas as pd
import numpy as np
from typing import Tuple, Optional
import os


def setup_plot_style():
    """Set up consistent plot styling."""
    plt.style.use('seaborn-v0_8-darkgrid')
    plt.rcParams['figure.figsize'] = (10, 6)
    plt.rcParams['font.size'] = 10
    plt.rcParams['axes.labelsize'] = 12
    plt.rcParams['axes.titlesize'] = 14
    plt.rcParams['xtick.labelsize'] = 10
    plt.rcParams['ytick.labelsize'] = 10


def generate_ctr_trend_chart(df: pd.DataFrame, output_path: str) -> str:
    """
    Generate CTR trend chart over time.
    
    Args:
        df: DataFrame with CTR data
        output_path: Path to save the chart
        
    Returns:
        Path to saved chart
    """
    setup_plot_style()
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Try to find date column
    date_col = None
    for col in df.columns:
        if 'date' in col.lower() or 'day' in col.lower():
            date_col = col
            break
    
    if date_col and 'CTR' in df.columns:
        # Sort by date
        df_sorted = df.sort_values(date_col)
        ax.plot(df_sorted[date_col], df_sorted['CTR'], marker='o', linewidth=2, markersize=6, color='#2E86AB')
        ax.set_xlabel('Date', fontweight='bold')
        ax.set_ylabel('CTR (%)', fontweight='bold')
        ax.set_title('Click-Through Rate (CTR) Trend Over Time', fontweight='bold', fontsize=16)
        plt.xticks(rotation=45, ha='right')
    elif 'CTR' in df.columns:
        # Plot CTR by index
        ax.plot(df.index, df['CTR'], marker='o', linewidth=2, markersize=6, color='#2E86AB')
        ax.set_xlabel('Index', fontweight='bold')
        ax.set_ylabel('CTR (%)', fontweight='bold')
        ax.set_title('Click-Through Rate (CTR) Trend', fontweight='bold', fontsize=16)
    else:
        # No CTR data available
        ax.text(0.5, 0.5, 'CTR data not available', ha='center', va='center', fontsize=14)
        ax.set_title('Click-Through Rate (CTR) Trend', fontweight='bold', fontsize=16)
    
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    return output_path


def generate_spend_impressions_chart(df: pd.DataFrame, output_path: str) -> str:
    """
    Generate spend vs impressions bar chart.
    
    Args:
        df: DataFrame with spend and impressions data
        output_path: Path to save the chart
        
    Returns:
        Path to saved chart
    """
    setup_plot_style()
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Try to find a grouping column (campaign, ad_group, etc.)
    group_col = None
    for col in df.columns:
        if col.lower() in ['campaign', 'campaign_name', 'ad_group', 'ad_name', 'source', 'channel']:
            group_col = col
            break
    
    if group_col and 'spend' in df.columns and 'impressions' in df.columns:
        # Aggregate by group
        df_agg = df.groupby(group_col).agg({
            'spend': 'sum',
            'impressions': 'sum'
        }).reset_index()
        
        # Take top 10 by spend
        df_top = df_agg.nlargest(10, 'spend')
        
        x = np.arange(len(df_top))
        width = 0.35
        
        # Normalize impressions to fit on same scale
        impressions_normalized = df_top['impressions'] / df_top['impressions'].max() * df_top['spend'].max()
        
        ax.bar(x - width/2, df_top['spend'], width, label='Spend ($)', color='#A23B72')
        ax.bar(x + width/2, impressions_normalized, width, label='Impressions (normalized)', color='#F18F01')
        
        ax.set_xlabel(group_col.replace('_', ' ').title(), fontweight='bold')
        ax.set_ylabel('Value', fontweight='bold')
        ax.set_title('Spend vs Impressions by ' + group_col.replace('_', ' ').title(), fontweight='bold', fontsize=16)
        ax.set_xticks(x)
        ax.set_xticklabels(df_top[group_col], rotation=45, ha='right')
        ax.legend()
        
    elif 'spend' in df.columns and 'impressions' in df.columns:
        # Aggregate totals
        total_spend = df['spend'].sum()
        total_impressions = df['impressions'].sum()
        
        categories = ['Spend ($)', 'Impressions\n(in thousands)']
        values = [total_spend, total_impressions / 1000]
        colors = ['#A23B72', '#F18F01']
        
        ax.bar(categories, values, color=colors, width=0.6)
        ax.set_title('Total Spend vs Impressions', fontweight='bold', fontsize=16)
        ax.set_ylabel('Value', fontweight='bold')
        
    else:
        ax.text(0.5, 0.5, 'Spend/Impressions data not available', ha='center', va='center', fontsize=14)
        ax.set_title('Spend vs Impressions', fontweight='bold', fontsize=16)
    
    ax.grid(True, alpha=0.3, axis='y')
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    return output_path


def generate_conversion_revenue_chart(df: pd.DataFrame, output_path: str) -> str:
    """
    Generate conversion or revenue trend chart.
    
    Args:
        df: DataFrame with conversion/revenue data
        output_path: Path to save the chart
        
    Returns:
        Path to saved chart
    """
    setup_plot_style()
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Try to find date column
    date_col = None
    for col in df.columns:
        if 'date' in col.lower() or 'day' in col.lower():
            date_col = col
            break
    
    has_conversions = 'conversions' in df.columns
    has_revenue = 'revenue' in df.columns
    
    if date_col and (has_conversions or has_revenue):
        df_sorted = df.sort_values(date_col)
        
        if has_conversions and has_revenue:
            # Dual axis plot
            ax2 = ax.twinx()
            
            line1 = ax.plot(df_sorted[date_col], df_sorted['conversions'], 
                          marker='o', linewidth=2, markersize=6, color='#06A77D', label='Conversions')
            line2 = ax2.plot(df_sorted[date_col], df_sorted['revenue'], 
                           marker='s', linewidth=2, markersize=6, color='#D62246', label='Revenue')
            
            ax.set_xlabel('Date', fontweight='bold')
            ax.set_ylabel('Conversions', fontweight='bold', color='#06A77D')
            ax2.set_ylabel('Revenue ($)', fontweight='bold', color='#D62246')
            ax.set_title('Conversions & Revenue Trend Over Time', fontweight='bold', fontsize=16)
            
            ax.tick_params(axis='y', labelcolor='#06A77D')
            ax2.tick_params(axis='y', labelcolor='#D62246')
            
            # Combine legends
            lines = line1 + line2
            labels = [l.get_label() for l in lines]
            ax.legend(lines, labels, loc='upper left')
            
        elif has_conversions:
            ax.plot(df_sorted[date_col], df_sorted['conversions'], 
                   marker='o', linewidth=2, markersize=6, color='#06A77D')
            ax.set_xlabel('Date', fontweight='bold')
            ax.set_ylabel('Conversions', fontweight='bold')
            ax.set_title('Conversions Trend Over Time', fontweight='bold', fontsize=16)
            
        else:  # has_revenue
            ax.plot(df_sorted[date_col], df_sorted['revenue'], 
                   marker='s', linewidth=2, markersize=6, color='#D62246')
            ax.set_xlabel('Date', fontweight='bold')
            ax.set_ylabel('Revenue ($)', fontweight='bold')
            ax.set_title('Revenue Trend Over Time', fontweight='bold', fontsize=16)
        
        plt.xticks(rotation=45, ha='right')
        
    elif has_conversions or has_revenue:
        # Plot by index
        if has_conversions:
            ax.plot(df.index, df['conversions'], marker='o', linewidth=2, markersize=6, color='#06A77D')
            ax.set_ylabel('Conversions', fontweight='bold')
            ax.set_title('Conversions Trend', fontweight='bold', fontsize=16)
        else:
            ax.plot(df.index, df['revenue'], marker='s', linewidth=2, markersize=6, color='#D62246')
            ax.set_ylabel('Revenue ($)', fontweight='bold')
            ax.set_title('Revenue Trend', fontweight='bold', fontsize=16)
        
        ax.set_xlabel('Index', fontweight='bold')
    else:
        ax.text(0.5, 0.5, 'Conversion/Revenue data not available', ha='center', va='center', fontsize=14)
        ax.set_title('Conversion & Revenue Trend', fontweight='bold', fontsize=16)
    
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    return output_path


def generate_all_charts(df: pd.DataFrame, output_dir: str) -> dict:
    """
    Generate all charts and return paths.
    
    Args:
        df: DataFrame with KPI data
        output_dir: Directory to save charts
        
    Returns:
        Dictionary with chart names and paths
    """
    os.makedirs(output_dir, exist_ok=True)
    
    charts = {}
    
    # Generate CTR trend chart
    ctr_path = os.path.join(output_dir, 'ctr_trend.png')
    charts['ctr_trend'] = generate_ctr_trend_chart(df, ctr_path)
    
    # Generate spend vs impressions chart
    spend_path = os.path.join(output_dir, 'spend_impressions.png')
    charts['spend_impressions'] = generate_spend_impressions_chart(df, spend_path)
    
    # Generate conversion/revenue chart
    conv_path = os.path.join(output_dir, 'conversion_revenue.png')
    charts['conversion_revenue'] = generate_conversion_revenue_chart(df, conv_path)
    
    return charts
