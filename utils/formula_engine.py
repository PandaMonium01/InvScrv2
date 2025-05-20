import pandas as pd
import numpy as np
import scipy.stats as stats

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
        local_vars = {}
        for col in df.columns:
            if pd.api.types.is_numeric_dtype(df[col]):
                # Handle blank/NaN values in the data
                clean_series = df[col].copy()
                
                # For all numeric columns, replace NaNs with a very low number 
                # This ensures rows with empty values don't pass through the formula unexpectedly
                clean_series = clean_series.fillna(-9999)
                
                # Use the original column name
                local_vars[col] = clean_series
                
                # Also add any shorthand version for convenience
                for short_name, full_name in rename_map.items():
                    if col == full_name:
                        local_vars[short_name] = clean_series
                        
                # Add Z-score normalized version of each numeric column
                # This helps with statistical filtering based on standard deviations from the mean
                try:
                    if clean_series.nunique() > 1:  # Only normalize if there's variation
                        z_col = f"{col}_zscore"
                        local_vars[z_col] = stats.zscore(clean_series, nan_policy='omit')
                        
                        # Also add normalized version for shorthand variables
                        for short_name, full_name in rename_map.items():
                            if col == full_name:
                                local_vars[f"{short_name}_zscore"] = local_vars[z_col]
                except:
                    # Skip normalization if it fails (e.g., for columns with all identical values)
                    pass
                    
                # Add percentile ranks for each numeric column
                # This enables filtering based on top/bottom percentiles
                try:
                    pct_col = f"{col}_percentile"
                    local_vars[pct_col] = clean_series.rank(pct=True) * 100
                    
                    # Also add percentile version for shorthand variables
                    for short_name, full_name in rename_map.items():
                        if col == full_name:
                            local_vars[f"{short_name}_percentile"] = local_vars[pct_col]
                except:
                    # Skip percentile calculation if it fails
                    pass
        
        # Add helper functions for statistical filtering
        def top_n_pct(series, n):
            """Return a boolean mask for the top n% of values"""
            if isinstance(n, (int, float)) and 0 <= n <= 100:
                threshold = np.percentile(series.dropna(), 100 - n)
                return series >= threshold
            return pd.Series([False] * len(series))
            
        def bottom_n_pct(series, n):
            """Return a boolean mask for the bottom n% of values"""
            if isinstance(n, (int, float)) and 0 <= n <= 100:
                threshold = np.percentile(series.dropna(), n)
                return series <= threshold
            return pd.Series([False] * len(series))
            
        # Make these functions available in the formula evaluation
        local_vars['top_n_pct'] = top_n_pct
        local_vars['bottom_n_pct'] = bottom_n_pct
        
        # Apply the formula to create a mask
        mask = eval(formula_str, {"__builtins__": {}}, local_vars)
        
        # Apply the mask to filter the dataframe
        filtered_df = df[mask].copy()
        
        return filtered_df
    
    except NameError as e:
        # Handle case where a column name isn't recognized
        missing_var = str(e).split("'")[1]
        try:
            available_vars = ", ".join(list(local_vars.keys()))
        except:
            available_vars = "No variables available"
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
        
        # 1. Standard ratios
        # Calculate return-to-risk ratio (return divided by risk)
        if '3 Years Annualised (%)' in result.columns and '3 Year Standard Deviation' in result.columns:
            result['Return/Risk Ratio'] = result['3 Years Annualised (%)'] / result['3 Year Standard Deviation'].replace(0, np.nan)
        
        # Calculate return-to-expense ratio (return divided by expense ratio)
        if '3 Years Annualised (%)' in result.columns and 'Investment Management Fee(%)' in result.columns:
            result['Return/Fee Ratio'] = result['3 Years Annualised (%)'] / result['Investment Management Fee(%)'].replace(0, np.nan)
        
        # 2. Risk-adjusted metrics
        # Calculate risk-adjusted performance (similar to Treynor ratio but using standard deviation)
        if '3 Years Annualised (%)' in result.columns and '3 Year Beta' in result.columns:
            # Assumption: Risk-free rate of 1.5% (adjust as needed)
            risk_free_rate = 1.5
            excess_return = result['3 Years Annualised (%)'] - risk_free_rate
            result['Treynor Ratio'] = excess_return / result['3 Year Beta'].replace(0, np.nan)
        
        # 3. Composite score
        # Create a composite quality score (higher is better)
        composite_columns = []
        
        # Return (higher is better)
        if '3 Years Annualised (%)' in result.columns:
            result['Return_Score'] = result['3 Years Annualised (%)'].rank(pct=True) * 100
            composite_columns.append('Return_Score')
        
        # Fee (lower is better)
        if 'Investment Management Fee(%)' in result.columns:
            result['Fee_Score'] = (1 - result['Investment Management Fee(%)'].rank(pct=True)) * 100
            composite_columns.append('Fee_Score')
        
        # Risk (lower is better)
        if '3 Year Standard Deviation' in result.columns:
            result['Risk_Score'] = (1 - result['3 Year Standard Deviation'].rank(pct=True)) * 100
            composite_columns.append('Risk_Score')
        
        # Sharpe (higher is better)
        if '3 Year Sharpe Ratio' in result.columns:
            result['Sharpe_Score'] = result['3 Year Sharpe Ratio'].rank(pct=True) * 100
            composite_columns.append('Sharpe_Score')
        
        # Calculate composite score if we have the required metrics
        if len(composite_columns) > 0:
            # Calculate composite score with different weights
            weights = {
                'Return_Score': 0.25,
                'Fee_Score': 0.25,
                'Risk_Score': 0.25,
                'Sharpe_Score': 0.25
            }
            
            # Initialize composite score
            result['Composite Score'] = 0
            
            # Add weighted scores for each available metric
            for col in composite_columns:
                if col in weights:
                    result['Composite Score'] += result[col] * weights[col]
            
            # Adjust the score based on the number of metrics used
            total_weight = sum(weights[col] for col in composite_columns if col in weights)
            if total_weight > 0:
                result['Composite Score'] = result['Composite Score'] / total_weight
            
            # Clean up intermediate score columns
            result = result.drop(composite_columns, axis=1)
        
        # 4. Peer comparison
        # Calculate percentile rank within each Morningstar Category for key metrics
        if 'Morningstar Category' in result.columns:
            for metric in ['3 Years Annualised (%)', 'Investment Management Fee(%)', 
                          '3 Year Standard Deviation', '3 Year Sharpe Ratio']:
                if metric in result.columns:
                    # For expenses, lower is better, so invert the percentile
                    if metric == 'Investment Management Fee(%)' or metric == '3 Year Standard Deviation':
                        result[f'{metric} Category Percentile'] = result.groupby('Morningstar Category')[metric].transform(
                            lambda x: (1 - (x.rank(pct=True))) * 100
                        )
                    else:
                        result[f'{metric} Category Percentile'] = result.groupby('Morningstar Category')[metric].transform(
                            lambda x: x.rank(pct=True) * 100
                        )
        
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
