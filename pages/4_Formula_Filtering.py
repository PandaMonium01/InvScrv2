import streamlit as st
import pandas as pd
import numpy as np
from utils.formula_engine import apply_formula, calculate_performance_metrics
from utils.visualization import create_selection_comparison_chart

# Set page configuration
st.set_page_config(
    page_title="Formula Filtering - Investment Selection Tool",
    page_icon="📊",
    layout="wide",
)

st.title("Formula Filtering")

# Check if data is available
if st.session_state.combined_data is None or st.session_state.combined_data.empty:
    st.warning("No data available for filtering. Please import data first on the 'Data Import' page.")
    st.stop()

st.markdown("""
Define a custom formula to filter investments based on your criteria.

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

# Initialize session state variables for selections
if 'selected_categories' not in st.session_state:
    st.session_state.selected_categories = []
if 'recommended_portfolio' not in st.session_state:
    st.session_state.recommended_portfolio = {}

# Quick filtering tools
st.subheader("Quick Filters")

col1, col2 = st.columns(2)

with col1:
    # APL filter button for Morningstar Rating >= 3
    if st.button("APL Filter (Morningstar Rating ≥ 3)", use_container_width=True):
        # Use data that might already have been filtered by HUB24
        source_data = st.session_state.combined_data if st.session_state.hub24_filtered is None else st.session_state.hub24_filtered
        
        # Check if column exists
        if 'Morningstar Rating' not in source_data.columns:
            st.error("Morningstar Rating column not found in the data")
        else:
            with st.spinner("Applying APL filter..."):
                try:
                    # Convert Morningstar Rating to numeric (handle potential non-numeric values)
                    numeric_ratings = pd.to_numeric(source_data['Morningstar Rating'], errors='coerce')
                    
                    # Filter based on the numeric ratings
                    filtered_data = source_data[numeric_ratings >= 3]
                    
                    # Update the filtered selection
                    st.session_state.filtered_selection = filtered_data
                    
                    if filtered_data.empty:
                        st.warning("No investments match the APL filter criteria (Morningstar Rating ≥ 3).")
                    else:
                        st.success(f"Found {len(filtered_data)} investments with Morningstar Rating ≥ 3.")
                except Exception as e:
                    st.error(f"Error applying APL filter: {str(e)}")
                    st.error("Debug info: Data types - " + str(source_data['Morningstar Rating'].dtypes))

with col2:
    # Morningstar Category selector using dropdown with checkboxes
    if 'Morningstar Category' in st.session_state['combined_data'].columns:
        st.write("**Morningstar Categories**")
        
        available_categories = sorted(st.session_state['combined_data']['Morningstar Category'].dropna().unique().tolist())
        
        # Initialize selected_categories if not already in session_state
        if 'selected_categories' not in st.session_state:
            st.session_state['selected_categories'] = []
        
        # Add Select All / Deselect All buttons
        select_col1, select_col2 = st.columns(2)
        
        with select_col1:
            if st.button("Select All", use_container_width=True, key="select_all_btn"):
                st.session_state['selected_categories'] = available_categories.copy()
                # Force page refresh
                st.rerun()
                
        with select_col2:
            if st.button("Deselect All", use_container_width=True, key="deselect_all_btn"):
                st.session_state['selected_categories'] = []
                # Force page refresh
                st.rerun()
        
        # Use multi-select dropdown with checkboxes
        selected_categories = st.multiselect(
            "Select Morningstar categories",
            options=available_categories,
            default=st.session_state['selected_categories'],
            help="Select Morningstar categories to include in your filter"
        )
        
        # Update session state with selected categories
        st.session_state['selected_categories'] = selected_categories
        
        # Show count of selected categories
        if selected_categories:
            st.info(f"Selected: {len(selected_categories)} of {len(available_categories)} categories")
        else:
            st.warning("No categories selected")
        
        if st.button("Apply Category Filter", use_container_width=True):
            if not st.session_state.selected_categories:
                st.warning("Please select at least one Morningstar Category.")
            else:
                # Use data that might already have been filtered by HUB24
                source_data = st.session_state.combined_data if st.session_state.hub24_filtered is None else st.session_state.hub24_filtered
                
                with st.spinner("Applying category filter..."):
                    try:
                        # Use pandas direct filtering instead of formula engine
                        # This is more reliable for list-based filters
                        filtered_df = source_data[source_data['Morningstar Category'].isin(st.session_state.selected_categories)]
                        
                        # Update the filtered selection
                        st.session_state.filtered_selection = filtered_df
                        
                        if filtered_df.empty:
                            st.warning("No investments match the selected categories.")
                        else:
                            st.success(f"Found {len(filtered_df)} investments in the selected categories.")
                    except Exception as e:
                        st.error(f"Error applying category filter: {str(e)}")
                        st.error(f"Debug info: Selected categories - {st.session_state.selected_categories}")

# Divider
st.markdown("---")

# Custom Formula input
st.subheader("Custom Formula Filter")

formula = st.text_area(
    "Enter your custom formula:", 
    value=st.session_state.formula,
    height=100,
    help="Enter a Python expression that evaluates to True or False for each investment."
)

if formula and formula != st.session_state.formula:
    st.session_state.formula = formula

if st.button("Apply Custom Formula", use_container_width=True):
    # Use data that might already have been filtered by HUB24
    source_data = st.session_state.combined_data if st.session_state.hub24_filtered is None else st.session_state.hub24_filtered
    
    with st.spinner("Applying formula..."):
        try:
            st.session_state.filtered_selection = apply_formula(
                source_data, 
                st.session_state.formula
            )
            if st.session_state.filtered_selection.empty:
                st.warning("No investments match your formula criteria.")
            else:
                st.success(f"Found {len(st.session_state.filtered_selection)} investments matching your criteria.")
        except Exception as e:
            st.error(f"Error applying formula: {str(e)}")

# Display filtered selection if available
if st.session_state.filtered_selection is not None:
    st.header("Filtered Investment Selection")
    
    if st.session_state.filtered_selection.empty:
        st.warning("No investments match your formula criteria. Try adjusting your formula.")
    else:
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
        
        # Selection interface using expander to save space
        with st.expander("Add Funds to Recommended Portfolio", expanded=True):
            st.markdown("""
            Select funds from the filtered list below to add to your recommended portfolio. 
            You can add comments for each selection to explain your rationale.
            """)
            
            # Form for adding a fund to the portfolio
            fund_selector = st.selectbox(
                "Select a fund to add to your recommended portfolio",
                options=st.session_state.filtered_selection['Name'].tolist(),
                key="fund_selector"
            )
            
            # Get the selected fund details
            selected_fund = st.session_state.filtered_selection[
                st.session_state.filtered_selection['Name'] == fund_selector
            ].iloc[0]
            
            selected_apir = selected_fund['APIR Code'] if 'APIR Code' in selected_fund else "Unknown"
            selected_category = selected_fund['Morningstar Category'] if 'Morningstar Category' in selected_fund else "Unknown"
            
            # Comments for the selected fund
            fund_comments = st.text_area(
                "Comments (reason for selection, allocation percentage, etc.)",
                key="fund_comments",
                help="Add your rationale for selecting this fund or any other notes."
            )
            
            if st.button("Add to Recommended Portfolio", use_container_width=True):
                add_to_portfolio(fund_selector, selected_apir, selected_category, fund_comments)
        
        # Display the filtered selection in a dataframe
        st.subheader("Filtered Investment List")
        st.dataframe(st.session_state.filtered_selection, use_container_width=True)
        
        # Compare the filtered selection to the overall averages
        st.subheader("Selection Performance")
        
        # Create comparison visualization
        try:
            fig = create_selection_comparison_chart(
                st.session_state.asset_class_averages,
                st.session_state.filtered_selection
            )
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Error creating selection comparison chart: {str(e)}")
            st.info("Chart couldn't be displayed, but your filtered data is still available below.")
        
        # Export filtered selection
        csv_filtered = st.session_state.filtered_selection.to_csv(index=False)
        st.download_button(
            label="Download Filtered Selection",
            data=csv_filtered,
            file_name="filtered_investment_selection.csv",
            mime="text/csv",
        )