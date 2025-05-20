import streamlit as st
import pandas as pd
import numpy as np
import os
import io
from utils.data_processor import load_and_process_csv, validate_csv

# Set page configuration
st.set_page_config(
    page_title="Data Import - Investment Selection Tool",
    page_icon="📊",
    layout="wide",
)

st.title("Data Import")

st.markdown("""
This page allows you to upload your investment data files in CSV format. 
The system will validate, process, and combine the data for analysis.
""")

# Display the expected data format
with st.expander("Expected Data Format", expanded=True):
    st.markdown("""
    Please upload a CSV file with the following columns:
    
    - `Name`: Name of the investment
    - `APIR Code`: APIR code for the investment
    - `Morningstar Category`: Category of the investment (e.g., Equity Large Cap, Australian Bond, etc.)
    - `3 Years Annualised (%)`: 3-year annualized return in percentage
    - `Investment Management Fee(%)`: Annual management fee in percentage
    - `Equity StyleBox™`: Morningstar's style classification
    - `Morningstar Rating`: Star rating
    - `3 Year Beta`: Beta value over 3 years
    - `3 Year Standard Deviation`: Standard deviation over 3 years
    - `3 Year Sharpe Ratio`: Sharpe ratio over 3 years
    
    You can include additional numerical columns that can be used in your custom formulas.
    
    **Example**:
    ```
    Name,APIR Code,Morningstar Category,3 Years Annualised (%),Investment Management Fee(%),Equity StyleBox™,Morningstar Rating,3 Year Beta,3 Year Standard Deviation,3 Year Sharpe Ratio
    Australian Shares Fund,ABC123,Equity Large Cap,8.5,0.75,Large Value,5,1.05,15.2,0.53
    Global Bond Fund,DEF456,Global Fixed Income,4.2,0.45,N/A,4,0.32,6.1,0.67
    ```
    """)
    
    # Create an example CSV file for download
    example_data = {
        'Name': ['Australian Shares Fund', 'Global Bond Fund', 'Small Cap Index Fund', 'Emerging Markets ETF', 'High-Yield Bond Fund'],
        'APIR Code': ['ABC123', 'DEF456', 'GHI789', 'JKL012', 'MNO345'],
        'Morningstar Category': ['Equity Large Cap', 'Global Fixed Income', 'Equity Small Cap', 'Equity Emerging Markets', 'Fixed Income High Yield'],
        '3 Years Annualised (%)': [8.5, 4.2, 9.1, 11.3, 6.5],
        'Investment Management Fee(%)': [0.75, 0.45, 0.55, 0.95, 0.65],
        'Equity StyleBox™': ['Large Value', 'N/A', 'Small Growth', 'Mid Blend', 'N/A'],
        'Morningstar Rating': [5, 4, 3, 4, 3],
        '3 Year Beta': [1.05, 0.32, 1.22, 1.45, 0.78],
        '3 Year Standard Deviation': [15.2, 6.1, 22.4, 25.3, 12.5],
        '3 Year Sharpe Ratio': [0.53, 0.67, 0.41, 0.44, 0.50]
    }
    example_df = pd.DataFrame(example_data)
    csv = example_df.to_csv(index=False)
    
    st.download_button(
        label="Download Example CSV",
        data=csv,
        file_name="example_investment_data.csv",
        mime="text/csv",
    )

# File uploader for multiple files
uploaded_files = st.file_uploader(
    "Upload CSV Files", 
    type="csv", 
    accept_multiple_files=True,
    help="Upload one or more CSV files containing investment data."
)

if uploaded_files:
    if st.button("Process Files", use_container_width=True):
        # Clear existing data
        st.session_state.dataframes = []
        
        with st.spinner("Processing files..."):
            for uploaded_file in uploaded_files:
                try:
                    # Validate CSV format
                    is_valid, error_msg = validate_csv(uploaded_file)
                    
                    if is_valid:
                        # Reset file pointer after validation
                        uploaded_file.seek(0)
                        
                        # Load and process the CSV
                        df = load_and_process_csv(uploaded_file)
                        if df is not None:
                            st.session_state.dataframes.append(df)
                            st.success(f"Successfully processed: {uploaded_file.name}")
                    else:
                        st.error(f"Error in {uploaded_file.name}: {error_msg}")
                except Exception as e:
                    st.error(f"Error processing {uploaded_file.name}: {str(e)}")
        
        # Calculate asset class averages if files were successfully loaded
        if st.session_state.dataframes:
            try:
                # Combine all dataframes
                combined_data = pd.concat(st.session_state.dataframes, ignore_index=True)
                st.session_state.combined_data = combined_data
                
                # Calculate averages only for specific fields by Morningstar Category
                avg_fields = [
                    '3 Years Annualised (%)',
                    'Investment Management Fee(%)',
                    '3 Year Beta',
                    '3 Year Standard Deviation',
                    '3 Year Sharpe Ratio'
                ]
                
                # Create a subset with only the needed columns for averaging
                # First check which of the required fields actually exist in the data
                existing_fields = [f for f in avg_fields if f in combined_data.columns]
                subset_for_avg = combined_data[['Morningstar Category'] + existing_fields].copy()
                
                # Calculate averages by Morningstar Category for specific fields only
                st.session_state.asset_class_averages = subset_for_avg.groupby('Morningstar Category').mean(numeric_only=True)
                
                st.success(f"Successfully processed {len(st.session_state.dataframes)} files with {len(combined_data)} investments.")
                st.info("Navigate to the 'Data Analysis' page to view the imported data.")
                
            except Exception as e:
                st.error(f"Error calculating asset class averages: {str(e)}")

# Show data summary if available
if st.session_state.combined_data is not None and not st.session_state.combined_data.empty:
    st.header("Data Summary")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Number of Investments", len(st.session_state.combined_data))
        
    with col2:
        st.metric("Number of Categories", st.session_state.combined_data['Morningstar Category'].nunique())
    
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
    existing_columns = list(st.session_state.combined_data.columns)
    
    # Keep only columns that exist in the actual dataframe
    ordered_columns = [col for col in ordered_columns if col in existing_columns]
    
    # Add any remaining columns that weren't specified in the order
    remaining_columns = [col for col in existing_columns if col not in ordered_columns]
    final_column_order = ordered_columns + remaining_columns
    
    # Reorder the dataframe columns
    reordered_df = st.session_state.combined_data[final_column_order].copy()
    
    # Display the first 5 rows
    st.dataframe(reordered_df.head(5), use_container_width=True)