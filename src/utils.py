"""
Utilities for data processing and helpers.
"""
import pandas as pd
import os
from datetime import datetime


def ensure_output_dir(output_dir: str = "output") -> str:
    """
    Ensure output directory exists.
    
    Args:
        output_dir: Path to output directory
        
    Returns:
        Absolute path to output directory
    """
    if not os.path.isabs(output_dir):
        output_dir = os.path.join(os.getcwd(), output_dir)
    
    os.makedirs(output_dir, exist_ok=True)
    return output_dir


def get_timestamp() -> str:
    """
    Get current timestamp for file naming.
    
    Returns:
        Timestamp string in format YYYYMMDD_HHMMSS
    """
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def format_currency(value: float) -> str:
    """
    Format value as currency.
    
    Args:
        value: Numeric value
        
    Returns:
        Formatted currency string
    """
    return f"${value:,.2f}"


def format_percentage(value: float) -> str:
    """
    Format value as percentage.
    
    Args:
        value: Numeric value
        
    Returns:
        Formatted percentage string
    """
    return f"{value:.2f}%"


def format_number(value: float) -> str:
    """
    Format value as number with commas.
    
    Args:
        value: Numeric value
        
    Returns:
        Formatted number string
    """
    return f"{value:,.0f}"


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """
    Safely divide two numbers, returning default if denominator is 0.
    
    Args:
        numerator: Numerator value
        denominator: Denominator value
        default: Default value if division by zero
        
    Returns:
        Result of division or default
    """
    return numerator / denominator if denominator != 0 else default
