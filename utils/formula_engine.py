import pandas as pd
import numpy as np

def apply_formula(df, formula_str):
    """
    Apply a custom formula to filter investments.
    
    Parameters:
    df (DataFrame): DataFrame containing investment data
    formula_str (str): Formula string as a Python expression
    
    Returns:
    DataFrame: Filtered DataFrame based on the formula
    """
    if df is None or df.empty:
        return pd.DataFrame()
    
    try:
        # Create a safe local environment for formula evaluation
        local_vars = {}
        
        # Create variable mappings to make formula writing easier
        rename_map = {
            'return': '3 Years Annualised (%)',
            'expense_ratio': 'Investment Management Fee(%)',
            'risk': '3 Year Standard Deviation',
            'beta': '3 Year Beta',
            'sharpe': '3 Year Sharpe Ratio'
        }
        
        # Extract all column values that might be used in the formula
        for col in df.columns:
            if pd.api.types.is_numeric_dtype(df[col]):
                # Use the original column name
                local_vars[col] = df[col]
                
                # Also add any shorthand version for convenience
                for short_name, full_name in rename_map.items():
                    if col == full_name:
                        local_vars[short_name] = df[col]
        
        # Apply the formula to create a mask
        mask = eval(formula_str, {"__builtins__": {}}, local_vars)
        
        # Apply the mask to filter the dataframe
        filtered_df = df[mask].copy()
        
        return filtered_df
    
    except NameError as e:
        # Handle case where a column name isn't recognized
        missing_var = str(e).split("'")[1]
        available_vars = ", ".join(list(local_vars.keys()) if 'local_vars' in locals() else ["No variables available"])
        raise ValueError(f"Column '{missing_var}' not found or not numeric. Available variables are: {available_vars}")
    
    except SyntaxError:
        raise ValueError("Invalid formula syntax")
    
    except Exception as e:
        raise ValueError(f"Error applying formula: {str(e)}")

def calculate_performance_metrics(df):
    """
    Calculate additional performance metrics for investments.
    
    Parameters:
    df (DataFrame): DataFrame containing investment data
    
    Returns:
    DataFrame: DataFrame with additional performance metrics
    """
    if df is None or df.empty:
        return df
    
    try:
        result = df.copy()
        
        # Calculate return-to-risk ratio (return divided by risk)
        if '3 Years Annualised (%)' in result.columns and '3 Year Standard Deviation' in result.columns:
            result['Return/Risk Ratio'] = result['3 Years Annualised (%)'] / result['3 Year Standard Deviation']
        
        # Calculate return-to-expense ratio (return divided by expense ratio)
        if '3 Years Annualised (%)' in result.columns and 'Investment Management Fee(%)' in result.columns:
            result['Return/Fee Ratio'] = result['3 Years Annualised (%)'] / result['Investment Management Fee(%)']
        
        return result
    
    except Exception as e:
        print(f"Error calculating performance metrics: {str(e)}")
        return df

def rank_investments(df, metric, ascending=False):
    """
    Rank investments based on a specific metric.
    
    Parameters:
    df (DataFrame): DataFrame containing investment data
    metric (str): Column name to rank by
    ascending (bool): Whether to rank in ascending order
    
    Returns:
    DataFrame: DataFrame with ranking
    """
    if df is None or df.empty or metric not in df.columns:
        return df
    
    try:
        result = df.copy()
        result['rank'] = result[metric].rank(ascending=ascending)
        return result.sort_values('rank')
    
    except Exception as e:
        print(f"Error ranking investments: {str(e)}")
        return df
