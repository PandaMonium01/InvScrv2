import streamlit as st
import pandas as pd
import os

# Set page configuration
st.set_page_config(
    page_title="Direct Load - Investment Selection Tool",
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

st.title("Direct Data Load")

st.write("""
Due to upload permission issues, this page loads investment data directly from a file. 
Click the button below to load example data into the application.
""")

# Example file path
example_file = "example_investment_data.csv"

# Check if the file exists
if os.path.exists(example_file):
    st.success(f"Example file found: {example_file}")
    
    # Button to load the data
    if st.button("Load Example Data", use_container_width=True):
        try:
            # Read the data from the file
            df = pd.read_csv(example_file)
            
            # Store the data in session state
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
                
                st.success(f"Successfully loaded example data with {len(df)} investments!")
                st.info("You can now navigate to other pages to analyze and filter the data.")
                
                # Show data preview
                st.subheader("Data Preview")
                st.dataframe(df)
                
            except Exception as e:
                st.error(f"Error calculating averages: {str(e)}")
        except Exception as e:
            st.error(f"Error reading file: {str(e)}")
else:
    st.error(f"Example file not found at {example_file}")
    st.info("Make sure the example CSV file exists in the root directory of the application.")

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