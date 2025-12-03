"""
Data processing and cleaning module.
"""
import pandas as pd
import numpy as np
from typing import Dict, Any


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean and preprocess the dataset.
    
    Args:
        df: Raw DataFrame
        
    Returns:
        Cleaned DataFrame
    """
    df_clean = df.copy()
    
    # Convert date columns if they exist
    date_columns = ['date', 'Date', 'DATE', 'day', 'Day']
    for col in df_clean.columns:
        if col in date_columns or 'date' in col.lower():
            try:
                df_clean[col] = pd.to_datetime(df_clean[col], errors='coerce')
            except:
                pass
    
    # Clean numeric columns - remove commas, currency symbols, etc.
    numeric_candidates = ['impressions', 'clicks', 'spend', 'conversions', 'revenue', 
                         'cost', 'sales', 'cpc', 'cpm', 'ctr']
    
    for col in df_clean.columns:
        if any(keyword in col.lower() for keyword in numeric_candidates):
            if df_clean[col].dtype == 'object':
                # Remove currency symbols and commas
                df_clean[col] = df_clean[col].astype(str).str.replace('$', '', regex=False)
                df_clean[col] = df_clean[col].str.replace(',', '', regex=False)
                df_clean[col] = df_clean[col].str.replace('%', '', regex=False)
                df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')
    
    # Fill NaN values with 0 for numeric columns
    numeric_cols = df_clean.select_dtypes(include=[np.number]).columns
    df_clean[numeric_cols] = df_clean[numeric_cols].fillna(0)
    
    # Fill NaN values with empty string for text columns
    text_cols = df_clean.select_dtypes(include=['object']).columns
    df_clean[text_cols] = df_clean[text_cols].fillna('')
    
    return df_clean


def calculate_kpis(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate AdTech KPIs from the cleaned data.
    
    Args:
        df: Cleaned DataFrame
        
    Returns:
        DataFrame with calculated KPIs
    """
    df_kpi = df.copy()
    
    # Standardize column names (case-insensitive)
    col_mapping = {}
    for col in df_kpi.columns:
        col_lower = col.lower()
        if 'impression' in col_lower:
            col_mapping[col] = 'impressions'
        elif 'click' in col_lower and 'ctr' not in col_lower:
            col_mapping[col] = 'clicks'
        elif 'spend' in col_lower or 'cost' in col_lower:
            col_mapping[col] = 'spend'
        elif 'conversion' in col_lower:
            col_mapping[col] = 'conversions'
        elif 'revenue' in col_lower or 'sales' in col_lower:
            col_mapping[col] = 'revenue'
    
    df_kpi = df_kpi.rename(columns=col_mapping)
    
    # Calculate KPIs
    # CTR = (clicks / impressions) * 100
    if 'clicks' in df_kpi.columns and 'impressions' in df_kpi.columns:
        df_kpi['CTR'] = np.where(
            df_kpi['impressions'] > 0,
            (df_kpi['clicks'] / df_kpi['impressions']) * 100,
            0
        )
    
    # CPC = spend / clicks
    if 'spend' in df_kpi.columns and 'clicks' in df_kpi.columns:
        df_kpi['CPC'] = np.where(
            df_kpi['clicks'] > 0,
            df_kpi['spend'] / df_kpi['clicks'],
            0
        )
    
    # CPM = (spend / impressions) * 1000
    if 'spend' in df_kpi.columns and 'impressions' in df_kpi.columns:
        df_kpi['CPM'] = np.where(
            df_kpi['impressions'] > 0,
            (df_kpi['spend'] / df_kpi['impressions']) * 1000,
            0
        )
    
    # Conversion Rate = (conversions / clicks) * 100
    if 'conversions' in df_kpi.columns and 'clicks' in df_kpi.columns:
        df_kpi['Conversion_Rate'] = np.where(
            df_kpi['clicks'] > 0,
            (df_kpi['conversions'] / df_kpi['clicks']) * 100,
            0
        )
    
    # ROAS = revenue / spend
    if 'revenue' in df_kpi.columns and 'spend' in df_kpi.columns:
        df_kpi['ROAS'] = np.where(
            df_kpi['spend'] > 0,
            df_kpi['revenue'] / df_kpi['spend'],
            0
        )
    
    return df_kpi


def get_summary_metrics(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Generate summary metrics for the dataset.
    
    Args:
        df: DataFrame with calculated KPIs
        
    Returns:
        Dictionary of summary metrics
    """
    summary = {}
    
    # Aggregate totals
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    
    for col in ['impressions', 'clicks', 'spend', 'conversions', 'revenue']:
        if col in df.columns:
            summary[f'total_{col}'] = df[col].sum()
            summary[f'avg_{col}'] = df[col].mean()
    
    # Overall KPIs
    if 'impressions' in summary and 'clicks' in summary:
        if summary['total_impressions'] > 0:
            summary['overall_CTR'] = (summary['total_clicks'] / summary['total_impressions']) * 100
        else:
            summary['overall_CTR'] = 0
    
    if 'spend' in summary and 'clicks' in summary:
        if summary['total_clicks'] > 0:
            summary['overall_CPC'] = summary['total_spend'] / summary['total_clicks']
        else:
            summary['overall_CPC'] = 0
    
    if 'spend' in summary and 'impressions' in summary:
        if summary['total_impressions'] > 0:
            summary['overall_CPM'] = (summary['total_spend'] / summary['total_impressions']) * 1000
        else:
            summary['overall_CPM'] = 0
    
    if 'conversions' in summary and 'clicks' in summary:
        if summary['total_clicks'] > 0:
            summary['overall_Conversion_Rate'] = (summary['total_conversions'] / summary['total_clicks']) * 100
        else:
            summary['overall_Conversion_Rate'] = 0
    
    if 'revenue' in summary and 'spend' in summary:
        if summary['total_spend'] > 0:
            summary['overall_ROAS'] = summary['total_revenue'] / summary['total_spend']
        else:
            summary['overall_ROAS'] = 0
    
    return summary
