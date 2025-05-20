import streamlit as st
import pandas as pd
import numpy as np
from utils.visualization import create_asset_class_chart, create_risk_return_scatter

# Set page configuration
st.set_page_config(
    page_title="Data Analysis - Investment Selection Tool",
    page_icon="📊",
    layout="wide",
)

st.title("Data Analysis")

# Check if data is available
if st.session_state.combined_data is None or st.session_state.combined_data.empty:
    st.warning("No data available for analysis. Please import data first on the 'Data Import' page.")
    st.stop()

# Determine which data to display based on filter status
display_data = None
if st.session_state.filtered_selection is not None and not st.session_state.filtered_selection.empty:
    display_data = st.session_state.filtered_selection
    data_status = "Formula Filtered Data"
elif st.session_state.hub24_filtered is not None and not st.session_state.hub24_filtered.empty:
    display_data = st.session_state.hub24_filtered
    data_status = "HUB24 Filtered Data"
else:
    display_data = st.session_state.combined_data
    data_status = "Combined Data (No Filters Applied)"

# Create tabs for different views
tabs = st.tabs(["Current Data View", "Category Averages", "Risk-Return Plot"])

with tabs[0]:
    st.header(data_status)
    
    # Add filter status information
    if st.session_state.hub24_filtered is not None and not st.session_state.hub24_filtered.empty:
        st.info(f"HUB24 Filter: {len(st.session_state.hub24_filtered)} investments available on HUB24 platform")
    
    if st.session_state.filtered_selection is not None and not st.session_state.filtered_selection.empty:
        st.info(f"Formula Filter: {len(st.session_state.filtered_selection)} investments matched your formula criteria")
    
    # Ensure the dataframe displays the specified columns first
    if display_data is not None and not display_data.empty:
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
        existing_columns = list(display_data.columns)
        
        # Keep only columns that exist in the actual dataframe
        ordered_columns = [col for col in ordered_columns if col in existing_columns]
        
        # Add any remaining columns that weren't specified in the order
        remaining_columns = [col for col in existing_columns if col not in ordered_columns]
        final_column_order = ordered_columns + remaining_columns
        
        # Reorder the dataframe columns
        reordered_df = display_data[final_column_order].copy()
        
        # Display the reordered dataframe
        st.dataframe(reordered_df, use_container_width=True)
        
        # Export data
        csv_data = reordered_df.to_csv(index=False)
        st.download_button(
            label=f"Download {data_status}",
            data=csv_data,
            file_name="investment_data.csv",
            mime="text/csv",
        )
    else:
        st.info("No data available to display")

with tabs[1]:
    st.header("Category Averages")
    
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
    st.header("Risk-Return Analysis")
    
    # Create risk-return scatter plot using the same data source as the main view
    if display_data is not None and not display_data.empty:
        st.subheader(f"Risk-Return Analysis: {data_status}")
        risk_return_fig = create_risk_return_scatter(display_data)
        st.plotly_chart(risk_return_fig, use_container_width=True)
    else:
        st.info("No data available for risk-return analysis")