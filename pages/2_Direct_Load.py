import streamlit as st
import pandas as pd
import os
from utils.data_processor import load_and_process_csv, validate_csv

# Set page configuration
st.set_page_config(
    page_title="Direct Load - Investment Selection Tool",
    page_icon="📊",
    layout="wide",
)

# Initialize session state variables
if 'dataframes' not in st.session_state:
    st.session_state['dataframes'] = []
if 'combined_data' not in st.session_state:
    st.session_state['combined_data'] = None
if 'asset_class_averages' not in st.session_state:
    st.session_state['asset_class_averages'] = None

st.title("Direct Load")
st.markdown("""
This page loads investment data directly from the pre-uploaded CSV file in the assets folder.
This is an alternative to using the standard file uploader which might be experiencing technical issues.
""")

# Direct data loading from the uploaded file
def load_data_from_assets():
    try:
        file_path = "attached_assets/download-2.csv"
        
        # Check if file exists
        if not os.path.exists(file_path):
            st.error(f"File not found: {file_path}")
            return False
        
        # Reset existing data
        st.session_state['dataframes'] = []
        
        with st.spinner("Processing file..."):
            # Open and read the file
            with open(file_path, 'rb') as file:
                # Validate CSV format
                is_valid, error_msg = validate_csv(file)
                
                if is_valid:
                    # Reset file pointer after validation
                    file.seek(0)
                    
                    # Load and process the CSV
                    df = load_and_process_csv(file)
                    if df is not None:
                        st.session_state['dataframes'].append(df)
                        st.success(f"Successfully processed: {os.path.basename(file_path)}")
                else:
                    st.error(f"Error in file: {error_msg}")
                    return False
            
            # Calculate asset class averages if file was successfully loaded
            if st.session_state['dataframes']:
                # Combine all dataframes
                combined_data = pd.concat(st.session_state['dataframes'], ignore_index=True)
                
                # Store combined data in session state
                st.session_state['combined_data'] = combined_data.copy()
                
                # Reset derived data
                st.session_state['hub24_filtered'] = None
                st.session_state['filtered_selection'] = None
                
                # Store the timestamp
                st.session_state['data_last_updated'] = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
                
                # Calculate averages for specific fields by Morningstar Category
                avg_fields = [
                    '3 Years Annualised (%)',
                    'Investment Management Fee(%)',
                    '3 Year Beta',
                    '3 Year Standard Deviation',
                    '3 Year Sharpe Ratio'
                ]
                
                # Create a subset with only the needed columns for averaging
                existing_fields = [f for f in avg_fields if f in combined_data.columns]
                subset_for_avg = combined_data[['Morningstar Category'] + existing_fields].copy()
                
                # Calculate averages by Morningstar Category
                st.session_state['asset_class_averages'] = subset_for_avg.groupby('Morningstar Category').mean(numeric_only=True)
                
                st.success(f"Successfully processed file with {len(combined_data)} investments.")
                st.info("Navigate to the 'Formula Filtering' page to apply filters to your data.")
                
                return True
                
        return False
    except Exception as e:
        st.error(f"Error processing file: {str(e)}")
        return False

# Button to trigger data loading
if st.button("Load Data From Assets", use_container_width=True):
    success = load_data_from_assets()
    if success:
        # Update interface to show success
        st.balloons()

# Show data summary if available
if st.session_state['combined_data'] is not None and not st.session_state['combined_data'].empty:
    st.header("Data Summary")
    
    col1, col2 = st.columns(2)
    
    with col1:
        num_investments = int(len(st.session_state['combined_data']))
        st.metric("Number of Investments", num_investments)
        
    with col2:
        num_categories = int(st.session_state['combined_data']['Morningstar Category'].nunique())
        st.metric("Number of Categories", num_categories)
    
    # Show sample of the data
    st.subheader("Sample Data (5 rows)")
    
    # Define the column order with specified columns first
    ordered_columns = [
        'Name',
        'APIR Code',
        'Morningstar Category',
        '3 Years Annualised (%)',
        'Investment Management Fee(%)',
        'Equity StyleBox™',
        'Morningstar Rating',
        '3 Year Beta',
        '3 Year Standard Deviation',
        '3 Year Sharpe Ratio'
    ]
    
    # Get the actual columns from the dataframe 
    existing_columns = list(st.session_state['combined_data'].columns)
    
    # Keep only columns that exist in the actual dataframe
    ordered_columns = [col for col in ordered_columns if col in existing_columns]
    
    # Add any remaining columns that weren't specified in the order
    remaining_columns = [col for col in existing_columns if col not in ordered_columns]
    final_column_order = ordered_columns + remaining_columns
    
    # Reorder the dataframe columns
    reordered_df = st.session_state['combined_data'][final_column_order].copy()
    
    # Display the first 5 rows
    st.dataframe(reordered_df.head(5), use_container_width=True)