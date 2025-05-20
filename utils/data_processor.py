import pandas as pd
import numpy as np
import io

# Required columns in CSV files
REQUIRED_COLUMNS = ['Name', 'APIR Code', 'Morningstar Category', '3 Years Annualised (%)', 
                    'Investment Management Fee(%)', 'Equity StyleBox™', 'Morningstar Rating',
                    '3 Year Beta', '3 Year Standard Deviation', '3 Year Sharpe Ratio']

# Define numeric columns for validation and processing
NUMERIC_COLUMNS = ['3 Years Annualised (%)', 'Investment Management Fee(%)', 
                   '3 Year Beta', '3 Year Standard Deviation', '3 Year Sharpe Ratio']

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
        for col in NUMERIC_COLUMNS:
            try:
                # Filter out empty values before validation for all numeric columns
                values = df[col].astype(str)
                # Replace special Unicode minus symbol (−) with standard ASCII minus (-)
                # This is critical for negative numbers in CSV files that use the Unicode minus
                values = values.str.replace('−', '-')
                non_empty_values = values[values.str.strip() != '']
                if len(non_empty_values) > 0:
                    pd.to_numeric(non_empty_values)
            except:
                return False, f"Column '{col}' must contain numeric values (when not blank)"
        
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
        for col in NUMERIC_COLUMNS:
            # Process all numeric columns to allow blank fields
            # Convert to string first to handle any existing data type
            df[col] = df[col].astype(str)
            
            # Replace special characters and non-numeric values
            # Use a more comprehensive approach to handle various forms of missing/non-numeric data
            df[col] = df[col].replace({
                'Unknown': np.nan,
                'N/A': np.nan,
                'n/a': np.nan,
                'na': np.nan,
                '-': np.nan,
                '': np.nan,
                'null': np.nan,
                'NULL': np.nan,
                'NaN': np.nan,
                'nan': np.nan,
                ' ': np.nan  # Handle spaces-only values
            })
            
            # Handle special Unicode minus symbol (−) by replacing it with standard ASCII minus (-)
            # This is critical for negative numbers in CSV files that use the Unicode minus
            if isinstance(df[col], pd.Series):
                df[col] = df[col].str.replace('−', '-')
            
            # Handle any remaining non-numeric values more explicitly
            # First identify values that are essentially empty or non-numeric
            empty_mask = df[col].str.strip() == ''
            df.loc[empty_mask, col] = np.nan
            
            # Convert to numeric, coercing any remaining non-numeric values to NaN
            # This ensures that properly formatted negative numbers (with either minus symbol) are parsed correctly
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Check for missing values in important columns
        has_missing = df[REQUIRED_COLUMNS].isna().sum().sum() > 0
                
        if has_missing:
            missing_count = df[REQUIRED_COLUMNS].isna().sum().sum()
            print(f"Warning: {missing_count} missing values found in important columns")
        
        # Handle missing values - for numeric columns, fill with median
        numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns
        for col in numeric_cols:
            if df[col].isna().sum() > 0:
                df[col] = df[col].fillna(df[col].median())
        
        # For categorical/string columns, fill with "Unknown"
        object_cols = df.select_dtypes(include=['object']).columns
        for col in object_cols:
            if df[col].isna().sum() > 0:
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
    Calculate average metrics for each asset class (Morningstar Category).
    
    Parameters:
    df (DataFrame): DataFrame containing investment data
    
    Returns:
    DataFrame: DataFrame with average metrics by asset class
    """
    if df is None or df.empty:
        return None
    
    try:
        # Group by Morningstar Category (asset class) and calculate mean values
        asset_class_averages = df.groupby('Morningstar Category').mean()
        return asset_class_averages
    
    except Exception as e:
        print(f"Error calculating asset class averages: {str(e)}")
        return None
