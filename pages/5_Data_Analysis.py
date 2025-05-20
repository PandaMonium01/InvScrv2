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
    
    # Initialize recommended_portfolio in session state if it doesn't exist
    if 'recommended_portfolio' not in st.session_state:
        st.session_state.recommended_portfolio = {}
        
    # Function to add selected funds to the recommended portfolio
    def add_to_portfolio(fund_name, fund_apir, fund_category, comments):
        if fund_apir not in st.session_state.recommended_portfolio:
            st.session_state.recommended_portfolio[fund_apir] = {
                'Name': fund_name,
                'APIR Code': fund_apir,
                'Morningstar Category': fund_category,
                'Comments': comments
            }
            st.success(f"Added {fund_name} to your recommended portfolio")
        else:
            st.info(f"{fund_name} is already in your recommended portfolio")
    
    # Ensure the dataframe displays the specified columns first
    if display_data is not None and not display_data.empty:
        # Add fund selection interface using expander
        with st.expander("Select Funds for Recommended Portfolio", expanded=False):
            st.markdown("""
            Select funds from the current data view to add to your recommended portfolio. 
            You can add comments for each selection to explain your rationale.
            """)
            
            # Form for adding a fund to the portfolio
            fund_selector = st.selectbox(
                "Select a fund to add to your portfolio",
                options=display_data['Name'].tolist(),
                key="fund_selector_analysis"
            )
            
            # Get the selected fund details
            selected_fund = display_data[display_data['Name'] == fund_selector].iloc[0]
            
            selected_apir = selected_fund['APIR Code'] if 'APIR Code' in selected_fund else "Unknown"
            selected_category = selected_fund['Morningstar Category'] if 'Morningstar Category' in selected_fund else "Unknown"
            
            # Comments for the selected fund
            fund_comments = st.text_area(
                "Comments (reason for selection, allocation percentage, etc.)",
                key="fund_comments_analysis",
                help="Add your rationale for selecting this fund or any other notes."
            )
            
            if st.button("Add to Recommended Portfolio", key="add_button_analysis", use_container_width=True):
                add_to_portfolio(fund_selector, selected_apir, selected_category, fund_comments)
                
            if st.session_state.recommended_portfolio:
                num_selected = len(st.session_state.recommended_portfolio)
                st.success(f"You have {num_selected} funds in your recommended portfolio.")
                st.info("Go to the **Recommended Portfolio** page to view and manage your selections.")
        
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