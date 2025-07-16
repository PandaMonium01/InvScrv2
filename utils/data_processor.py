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
                
                # Handle literal "nan" strings by replacing them with actual np.nan values
                values = values.replace({'nan': '', 'NaN': '', 'Nan': '', 'NAN': ''})
                
                # Print problematic values for debugging (temp)
                problematic_values = []
                for idx, val in enumerate(values):
                    # Skip blank/empty values and recognized missing value terms
                    if (not val or val.strip() == '' or 
                        val.lower() in ['na', 'n/a', 'unknown', 'null', 'nan', '-']):
                        continue
                    
                    # Handle literal nan values case-insensitively
                    if val.lower().strip() == 'nan':
                        continue
                        
                    # Try to convert to float
                    try:
                        # Replace special Unicode minus with standard ASCII minus
                        cleaned_val = val.replace('−', '-')
                        float(cleaned_val)
                    except ValueError:
                        problematic_values.append(f"Row {idx+1}: '{val}'")
                
                # If there are problematic values, raise an error with details
                if problematic_values:
                    if len(problematic_values) > 3:
                        problem_str = ", ".join(problematic_values[:3]) + f", and {len(problematic_values)-3} more"
                    else:
                        problem_str = ", ".join(problematic_values)
                    return False, f"Column '{col}' contains non-numeric values: {problem_str}"
                
                # Continue with normal validation
                # Replace special Unicode minus symbol (−) with standard ASCII minus (-)
                # This is critical for negative numbers in CSV files that use the Unicode minus
                values = values.str.replace('−', '-')
                # Replace literal "nan" strings with empty strings
                values = values.str.replace('(?i)nan', '', regex=True)
                
                # Skip empty values for validation
                non_empty_values = values[(values.str.strip() != '') & (~values.isna())]
                if len(non_empty_values) > 0:
                    pd.to_numeric(non_empty_values)
            except Exception as e:
                return False, f"Column '{col}' must contain numeric values (when not blank). Error: {str(e)}"
        
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
            
            # Clean up literal string 'nan' values which are causing problems
            df[col] = df[col].apply(lambda x: np.nan if isinstance(x, str) and x.lower().strip() == 'nan' else x)
            
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
                ' ': np.nan,  # Handle spaces-only values
                # Remove all variations of literal "nan" strings
                'nan': np.nan,
                'NaN': np.nan, 
                'Nan': np.nan,
                'NAN': np.nan
            })
            
            # Handle special Unicode minus symbol (−) by replacing it with standard ASCII minus (-)
            # This is critical for negative numbers in CSV files that use the Unicode minus
            if isinstance(df[col], pd.Series):
                df[col] = df[col].str.replace('−', '-')
            
            # Handle any remaining non-numeric values more explicitly
            # First identify values that are essentially empty or non-numeric
            empty_mask = df[col].str.strip() == ''
            df.loc[empty_mask, col] = np.nan
            
            # Special handling for Investment Management Fee(%) column which often has problematic formats
            if col == 'Investment Management Fee(%)':
                # Clean up any potential problematic characters, especially for fee data 
                # (which might have symbols like % or formatting issues)
                df[col] = df[col].str.replace('%', '', regex=False)  # Remove percent symbols
                df[col] = df[col].str.replace('$', '', regex=False)  # Remove dollar signs
                df[col] = df[col].str.replace(',', '.', regex=False)  # Replace European commas with decimal points
                
                # Sometimes fees are presented as "X.XX / Y.YY" - take the first number
                df[col] = df[col].apply(lambda x: x.split('/')[0].strip() if isinstance(x, str) and '/' in x else x)
                
                # As requested by client, treat zeros as missing values in this column
                df[col] = df[col].apply(lambda x: np.nan if (isinstance(x, str) and x.strip() in ['0', '0.0', '0.00']) else x)
                
                # Handle literal nan strings one more time (in case they survived earlier processing)
                df[col] = df[col].apply(lambda x: np.nan if (isinstance(x, str) and x.lower().strip() == 'nan') else x)
                
                # Attempt to fix ranges like "0.5-0.8" by taking the average
                def process_range(val):
                    if isinstance(val, str) and '-' in val:
                        parts = val.split('-')
                        if len(parts) == 2:
                            try:
                                low = float(parts[0].strip())
                                high = float(parts[1].strip())
                                return (low + high) / 2
                            except ValueError:
                                return val
                    return val
                    
                df[col] = df[col].apply(process_range)
            
            # Convert to numeric, coercing any remaining non-numeric values to NaN
            # This ensures that properly formatted negative numbers (with either minus symbol) are parsed correctly
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Check for missing values in important columns
        has_missing = df[REQUIRED_COLUMNS].isna().sum().sum() > 0
                
        if has_missing:
            missing_count = df[REQUIRED_COLUMNS].isna().sum().sum()
            print(f"Warning: {missing_count} missing values found in important columns")
        
        # Handle missing values - for numeric columns, fill with median EXCEPT for key 3-year metrics
        # These should remain as NaN to exclude from averages
        key_3year_metrics = ['3 Year Beta', '3 Year Standard Deviation', '3 Year Sharpe Ratio']
        
        numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns
        for col in numeric_cols:
            if df[col].isna().sum() > 0:
                # Don't fill missing values for key 3-year metrics - keep as NaN
                if col not in key_3year_metrics:
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
        # This will automatically exclude NaN values from the calculation
        asset_class_averages = df.groupby('Morningstar Category').mean(numeric_only=True)
        
        # Debug: Show the counts and averages for Equity World Large Blend
        if 'Equity World Large Blend' in asset_class_averages.index:
            category_data = df[df['Morningstar Category'] == 'Equity World Large Blend']
            
            # Count funds with valid 3-year data
            beta_count = category_data['3 Year Beta'].notna().sum()
            stdev_count = category_data['3 Year Standard Deviation'].notna().sum()
            sharpe_count = category_data['3 Year Sharpe Ratio'].notna().sum()
            
            print(f"DEBUG - Equity World Large Blend:")
            print(f"  Total funds: {len(category_data)}")
            print(f"  Beta count (valid): {beta_count}")
            print(f"  StdDev count (valid): {stdev_count}")
            print(f"  Sharpe count (valid): {sharpe_count}")
            
            if beta_count > 0:
                print(f"  Beta average: {asset_class_averages.loc['Equity World Large Blend', '3 Year Beta']:.8f}")
            if stdev_count > 0:
                print(f"  StdDev average: {asset_class_averages.loc['Equity World Large Blend', '3 Year Standard Deviation']:.8f}")
            if sharpe_count > 0:
                print(f"  Sharpe average: {asset_class_averages.loc['Equity World Large Blend', '3 Year Sharpe Ratio']:.8f}")
        
        return asset_class_averages
    
    except Exception as e:
        print(f"Error calculating asset class averages: {str(e)}")
        return None
