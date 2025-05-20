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
        st.markdown("### Investment Data Table")
        st.write("Check the boxes in the 'Select' column to add funds to your recommended portfolio.")
        
        # Create a comments field
        if 'portfolio_comments' not in st.session_state:
            st.session_state.portfolio_comments = {}
        
        # Create selection controls
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            # Create a form for comments
            comment_input = st.text_input(
                "Comments for selected fund(s)", 
                help="Enter any comments for the fund(s) you are adding to the portfolio"
            )
        
        with col2:
            # Add button to unselect all options
            if st.button("Unselect All", use_container_width=True):
                # Clear the recommended portfolio
                st.session_state.recommended_portfolio = {}
                st.rerun()  # Rerun the app to refresh the table
                
        with col3:
            # Show number of currently selected items
            num_selected = len(st.session_state.recommended_portfolio)
            st.markdown(f"**Selected: {num_selected}**")
        
        # Create a dataframe with a selection column
        # First, create a copy of the display data
        selection_df = display_data.copy()
        
        # Add a new "Select" column at the beginning
        # Initialize with whether the fund is already in the portfolio
        selection_df.insert(
            0, 
            "Select", 
            selection_df['APIR Code'].apply(lambda x: x in st.session_state.recommended_portfolio)
        )
        
        # Define the column order with "Select" first
        ordered_columns = [
            'Select',
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
        existing_columns = list(selection_df.columns)
        
        # Keep only columns that exist in the actual dataframe
        ordered_columns = [col for col in ordered_columns if col in existing_columns]
        
        # Add any remaining columns that weren't specified in the order
        remaining_columns = [col for col in existing_columns if col not in ordered_columns and col != 'Select']
        final_column_order = ordered_columns + remaining_columns
        
        # Reorder the dataframe columns
        reordered_df = selection_df[final_column_order].copy()
        
        # Display the dataframe with editable checkboxes
        edited_df = st.data_editor(
            reordered_df,
            column_config={
                "Select": st.column_config.CheckboxColumn(
                    "Select",
                    help="Check to add to portfolio",
                    default=False,
                )
            },
            use_container_width=True,
            hide_index=True,
        )
        
        # Process the edited dataframe
        changed_rows = []
        
        # Get newly selected funds
        for idx, row in edited_df.iterrows():
            fund_name = row['Name']
            fund_apir = row['APIR Code']
            fund_category = row['Morningstar Category'] if 'Morningstar Category' in row else "Unknown"
            is_selected = row['Select']
            is_in_portfolio = fund_apir in st.session_state.recommended_portfolio
            
            # Check if selection status changed
            if is_selected and not is_in_portfolio:
                # Add to portfolio
                add_to_portfolio(fund_name, fund_apir, fund_category, comment_input)
                changed_rows.append(fund_name)
            elif not is_selected and is_in_portfolio:
                # Remove from portfolio
                del st.session_state.recommended_portfolio[fund_apir]
                changed_rows.append(fund_name)
        
        # Show portfolio status
        if st.session_state.recommended_portfolio:
            num_selected = len(st.session_state.recommended_portfolio)
            st.success(f"You have {num_selected} funds in your recommended portfolio.")
            
            if changed_rows:
                st.info(f"Updated portfolio status for: {', '.join(changed_rows[:3])}{'...' if len(changed_rows) > 3 else ''}")
                
            st.info("Go to the **Recommended Portfolio** page to view and manage your selections.")
        
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