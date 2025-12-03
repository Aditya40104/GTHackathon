"""
Data ingestion module for loading and previewing raw data.
"""
import pandas as pd
import streamlit as st
from typing import Optional, Tuple


def load_csv(uploaded_file) -> Optional[pd.DataFrame]:
    """
    Load CSV file from Streamlit file uploader.
    
    Args:
        uploaded_file: Streamlit UploadedFile object
        
    Returns:
        DataFrame or None if error occurs
    """
    try:
        df = pd.read_csv(uploaded_file)
        return df
    except Exception as e:
        st.error(f"Error loading CSV: {str(e)}")
        return None


def preview_data(df: pd.DataFrame, title: str = "Data Preview", rows: int = 10) -> None:
    """
    Display data preview in Streamlit.
    
    Args:
        df: DataFrame to preview
        title: Title for the preview section
        rows: Number of rows to display
    """
    st.subheader(title)
    st.write(f"**Shape:** {df.shape[0]} rows × {df.shape[1]} columns")
    st.dataframe(df.head(rows))
    
    # Show basic info
    with st.expander("Column Info"):
        col_info = pd.DataFrame({
            'Column': df.columns,
            'Type': df.dtypes.values,
            'Non-Null Count': df.count().values,
            'Null Count': df.isnull().sum().values
        })
        st.dataframe(col_info)


def validate_required_columns(df: pd.DataFrame, required_cols: list) -> Tuple[bool, list]:
    """
    Validate that required columns exist in the DataFrame.
    
    Args:
        df: DataFrame to validate
        required_cols: List of required column names
        
    Returns:
        Tuple of (is_valid, missing_columns)
    """
    missing_cols = [col for col in required_cols if col not in df.columns]
    is_valid = len(missing_cols) == 0
    return is_valid, missing_cols
