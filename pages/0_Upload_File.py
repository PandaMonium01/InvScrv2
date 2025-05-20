import streamlit as st
import pandas as pd
import os

# Set page configuration
st.set_page_config(
    page_title="File Upload - Investment Selection Tool",
    page_icon="📊",
    layout="wide",
)

# Initialize session state variables if they don't exist
if 'combined_data' not in st.session_state:
    st.session_state['combined_data'] = None
if 'asset_class_averages' not in st.session_state:
    st.session_state['asset_class_averages'] = None
if 'dataframes' not in st.session_state:
    st.session_state['dataframes'] = []

st.title("Investment Data Upload")

st.write("""
This simplified page helps with uploading your investment data CSV files. 
Once uploaded, your data will be processed and ready for analysis.
""")

# File uploader for multiple files - simplified version
uploaded_file = st.file_uploader(
    "Upload CSV File", 
    type="csv",
    help="Upload a CSV file containing investment data."
)

if uploaded_file is not None:
    try:
        # Read the data from the uploaded file
        df = pd.read_csv(uploaded_file)
        
        # Show basic information about the data
        st.write(f"Successfully uploaded: {uploaded_file.name}")
        st.write(f"Number of rows: {len(df)}")
        st.write(f"Number of columns: {len(df.columns)}")
        
        # Process the data
        if st.button("Process Data", use_container_width=True):
            # Store the uploaded data in session state
            st.session_state['combined_data'] = df.copy()
            st.session_state['dataframes'] = [df]
            
            # Calculate averages for specific fields
            try:
                # Define the fields we want to calculate averages for
                avg_fields = [
                    '3 Years Annualised (%)',
                    'Investment Management Fee(%)',
                    '3 Year Beta',
                    '3 Year Standard Deviation',
                    '3 Year Sharpe Ratio'
                ]
                
                # Create subset for averages
                existing_fields = [f for f in avg_fields if f in df.columns]
                if 'Morningstar Category' in df.columns and existing_fields:
                    subset_for_avg = df[['Morningstar Category'] + existing_fields].copy()
                    # Calculate averages
                    st.session_state['asset_class_averages'] = subset_for_avg.groupby('Morningstar Category').mean(numeric_only=True)
                
                # Store timestamp
                st.session_state['data_last_updated'] = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
                
                st.success("Data processed successfully!")
                st.info("You can now navigate to the other pages to analyze and filter your data.")
            except Exception as e:
                st.error(f"Error processing data: {str(e)}")
    except Exception as e:
        st.error(f"Error reading file: {str(e)}")

# Show data preview if available
if st.session_state['combined_data'] is not None:
    st.header("Data Preview")
    st.dataframe(st.session_state['combined_data'].head())

# Navigation buttons
st.write("---")
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("Go to Formula Filtering", use_container_width=True):
        st.switch_page("pages/4_Formula_Filtering.py")
with col2:
    if st.button("Go to Data Analysis", use_container_width=True):
        st.switch_page("pages/5_Data_Analysis.py")
with col3:
    if st.button("Go to Home", use_container_width=True):
        st.switch_page("Home.py")