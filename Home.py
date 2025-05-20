import streamlit as st
import pandas as pd
import numpy as np
import os
import io
import re
import PyPDF2

# Set page configuration
st.set_page_config(
    page_title="Investment Selection Tool",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state variables if they don't exist
if 'dataframes' not in st.session_state:
    st.session_state.dataframes = []
if 'combined_data' not in st.session_state:
    st.session_state.combined_data = None
if 'asset_class_averages' not in st.session_state:
    st.session_state.asset_class_averages = None
if 'filtered_selection' not in st.session_state:
    st.session_state.filtered_selection = None
if 'formula' not in st.session_state:
    st.session_state.formula = ""
if 'hub24_filtered' not in st.session_state:
    st.session_state.hub24_filtered = None
if 'hub24_apir_codes' not in st.session_state:
    st.session_state.hub24_apir_codes = []

# Home Page
def main():
    st.title("Investment Selection Tool")
    
    st.markdown("""
    ## Welcome to the Investment Selection Tool
    
    This application helps you analyze investment data from multiple CSV sources, 
    calculate asset class averages, and apply custom formulas to create a concentrated investment selection.
    
    ### Features:
    - Import and combine data from multiple CSV files
    - Calculate averages by Morningstar Category
    - Apply custom formulas to filter investments
    - Filter investments available on the HUB24 platform
    - Visualize investment data with interactive charts
    
    ### How to use this application:
    1. **Data Import** - Upload your CSV files with investment data
    2. **Data Analysis** - View the combined data and category averages
    3. **Formula Configuration** - Set up a custom formula to filter investments
    4. **HUB24 Platform Filter** - Filter investments available on HUB24
    5. **Results** - View and download your filtered investment selection
    
    Navigate using the sidebar to access different sections of the application.
    """)
    


if __name__ == "__main__":
    main()