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
    
    # Display sample data format information
    st.header("Expected Data Format")
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
    
    Download an example file below:
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

if __name__ == "__main__":
    main()