import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import os
import io
from utils.data_processor import load_and_process_csv, validate_csv
from utils.formula_engine import apply_formula, calculate_performance_metrics
from utils.visualization import create_asset_class_chart, create_selection_comparison_chart, create_risk_return_scatter

st.set_page_config(
    page_title="Investment Selection Tool",
    page_icon="📊",
    layout="wide",
)

def main():
    st.title("Investment Selection Tool")
    
    st.markdown("""
    This application helps you analyze investment data from multiple CSV sources, 
    calculate asset class averages, and apply custom formulas to create a concentrated investment selection.
    """)
    
    # Initialize session state variables if they don't exist
    if 'dataframes' not in st.session_state:
        st.session_state.dataframes = []
    if 'asset_class_averages' not in st.session_state:
        st.session_state.asset_class_averages = None
    if 'filtered_selection' not in st.session_state:
        st.session_state.filtered_selection = None
    if 'formula' not in st.session_state:
        st.session_state.formula = ""
    
    with st.sidebar:
        st.header("Data Import")
        
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
                        
                        # Calculate averages by Morningstar Category
                        st.session_state.asset_class_averages = combined_data.groupby('Morningstar Category').mean()
                        st.session_state.combined_data = combined_data
                    except Exception as e:
                        st.error(f"Error calculating asset class averages: {str(e)}")
        
        st.header("Formula Configuration")
        st.markdown("""
        Define a custom formula to filter investments.
        
        **Available variables**:
        - Full column names:
          - `3 Years Annualised (%)`: 3-year annualized return
          - `Investment Management Fee(%)`: Management fee
          - `3 Year Standard Deviation`: Standard deviation (risk measure)
          - `3 Year Beta`: Beta value
          - `3 Year Sharpe Ratio`: Sharpe ratio
        
        - Short aliases for convenience:
          - `return`: Maps to 3 Years Annualised (%)
          - `expense_ratio`: Maps to Investment Management Fee(%)
          - `risk`: Maps to 3 Year Standard Deviation
          - `beta`: Maps to 3 Year Beta
          - `sharpe`: Maps to 3 Year Sharpe Ratio
        
        **Examples**:
        - `return > 5`: Investments with annualized return > 5%
        - `return / risk > 1`: Return-to-risk ratio > 1
        - `expense_ratio < 1 and return > 7`: Low fee, high return
        - `sharpe > 0.5`: Sharpe ratio greater than 0.5
        """)
        
        formula = st.text_area(
            "Enter your formula:", 
            value=st.session_state.formula,
            help="Enter a Python expression that evaluates to True or False for each investment."
        )
        
        if formula and formula != st.session_state.formula:
            st.session_state.formula = formula
        
        if st.session_state.asset_class_averages is not None and st.session_state.formula:
            if st.button("Apply Formula", use_container_width=True):
                with st.spinner("Applying formula..."):
                    try:
                        st.session_state.filtered_selection = apply_formula(
                            st.session_state.combined_data, 
                            st.session_state.formula
                        )
                        if st.session_state.filtered_selection.empty:
                            st.warning("No investments match your formula criteria.")
                    except Exception as e:
                        st.error(f"Error applying formula: {str(e)}")
    
    # Display data and visualizations in the main area
    if st.session_state.dataframes:
        st.header("Imported Data")
        
        # Create tabs for raw data and aggregated data
        tabs = st.tabs(["Combined Data", "Category Averages", "Risk-Return Plot"])
        
        with tabs[0]:
            st.dataframe(st.session_state.combined_data, use_container_width=True)
            
            # Export combined data
            csv_combined = st.session_state.combined_data.to_csv(index=False)
            st.download_button(
                label="Download Combined Data",
                data=csv_combined,
                file_name="combined_investment_data.csv",
                mime="text/csv",
            )
        
        with tabs[1]:
            if st.session_state.asset_class_averages is not None:
                st.dataframe(st.session_state.asset_class_averages, use_container_width=True)
                
                # Create visualization for Morningstar Category averages
                fig = create_asset_class_chart(st.session_state.asset_class_averages)
                st.plotly_chart(fig, use_container_width=True)
                
                # Export category averages
                csv_averages = st.session_state.asset_class_averages.to_csv()
                st.download_button(
                    label="Download Category Averages",
                    data=csv_averages,
                    file_name="category_averages.csv",
                    mime="text/csv",
                )
            else:
                st.info("No category averages data available")
                
        with tabs[2]:
            # Create risk-return scatter plot
            if st.session_state.combined_data is not None and not st.session_state.combined_data.empty:
                risk_return_fig = create_risk_return_scatter(st.session_state.combined_data)
                st.plotly_chart(risk_return_fig, use_container_width=True)
            else:
                st.info("No data available for risk-return analysis")
    
    # Display filtered selection if available
    if st.session_state.filtered_selection is not None:
        st.header("Concentrated Investment Selection")
        
        st.dataframe(st.session_state.filtered_selection, use_container_width=True)
        
        # Compare the filtered selection to the overall averages
        if not st.session_state.filtered_selection.empty:
            st.subheader("Selection Performance")
            
            # Create comparison visualization
            fig = create_selection_comparison_chart(
                st.session_state.asset_class_averages,
                st.session_state.filtered_selection
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Export filtered selection
            csv_filtered = st.session_state.filtered_selection.to_csv(index=False)
            st.download_button(
                label="Download Filtered Selection",
                data=csv_filtered,
                file_name="filtered_investment_selection.csv",
                mime="text/csv",
            )
    
    # Display sample data format information if no data is loaded
    if not st.session_state.dataframes:
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
