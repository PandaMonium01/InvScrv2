import pandas as pd
import numpy as np
import io

# Required columns in CSV files
REQUIRED_COLUMNS = ['investment_name', 'asset_class', 'return', 'risk', 'expense_ratio']

def validate_csv(file):
    """
    Validate if the CSV file has the required columns and format.
    
    Parameters:
    file (IO): File-like object containing CSV data
    
    Returns:
    tuple: (is_valid, error_message)
    """
    try:
        # Read the first few rows to check headers
        df = pd.read_csv(file, nrows=5)
        
        # Check for required columns
        missing_columns = [col for col in REQUIRED_COLUMNS if col not in df.columns]
        
        if missing_columns:
            return False, f"Missing required columns: {', '.join(missing_columns)}"
        
        # Check data types (at least for basic validation)
        for col in ['return', 'risk', 'expense_ratio']:
            if not pd.api.types.is_numeric_dtype(df[col]):
                return False, f"Column '{col}' must contain numeric values"
        
        return True, ""
    except pd.errors.EmptyDataError:
        return False, "The CSV file is empty"
    except pd.errors.ParserError:
        return False, "The file is not a valid CSV format"
    except Exception as e:
        return False, f"Validation error: {str(e)}"

def load_and_process_csv(file):
    """
    Load and process a CSV file containing investment data.
    
    Parameters:
    file (IO): File-like object containing CSV data
    
    Returns:
    DataFrame: Processed pandas DataFrame or None if processing failed
    """
    try:
        # Read the CSV file
        df = pd.read_csv(file)
        
        # Ensure all required columns are present
        for col in REQUIRED_COLUMNS:
            if col not in df.columns:
                raise ValueError(f"Required column '{col}' not found in CSV")
        
        # Convert numeric columns to appropriate types
        numeric_columns = ['return', 'risk', 'expense_ratio']
        for col in numeric_columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Check for missing values in important columns
        important_cols = REQUIRED_COLUMNS
        if df[important_cols].isnull().any().any():
            missing_count = df[important_cols].isnull().sum().sum()
            print(f"Warning: {missing_count} missing values found in important columns")
        
        # Handle missing values - for numeric columns, fill with median
        for col in df.select_dtypes(include=['float64', 'int64']).columns:
            if df[col].isnull().any():
                df[col] = df[col].fillna(df[col].median())
        
        # For categorical/string columns, fill with "Unknown"
        for col in df.select_dtypes(include=['object']).columns:
            if df[col].isnull().any():
                df[col] = df[col].fillna("Unknown")
        
        return df
    
    except Exception as e:
        print(f"Error processing CSV: {str(e)}")
        return None

def combine_dataframes(dataframes):
    """
    Combine multiple dataframes into a single dataframe.
    
    Parameters:
    dataframes (list): List of pandas DataFrames
    
    Returns:
    DataFrame: Combined DataFrame
    """
    if not dataframes:
        return None
    
    try:
        # Concatenate all dataframes
        combined_df = pd.concat(dataframes, ignore_index=True)
        return combined_df
    
    except Exception as e:
        print(f"Error combining dataframes: {str(e)}")
        return None

def calculate_asset_class_averages(df):
    """
    Calculate average metrics for each asset class.
    
    Parameters:
    df (DataFrame): DataFrame containing investment data
    
    Returns:
    DataFrame: DataFrame with average metrics by asset class
    """
    if df is None or df.empty:
        return None
    
    try:
        # Group by asset class and calculate mean values
        asset_class_averages = df.groupby('asset_class').mean()
        return asset_class_averages
    
    except Exception as e:
        print(f"Error calculating asset class averages: {str(e)}")
        return None
