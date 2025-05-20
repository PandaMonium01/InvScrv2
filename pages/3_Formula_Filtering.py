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

# Formula input
formula = st.text_area(
    "Enter your formula:", 
    value=st.session_state.formula,
    height=100,
    help="Enter a Python expression that evaluates to True or False for each investment."
)

if formula and formula != st.session_state.formula:
    st.session_state.formula = formula

if st.button("Apply Formula", use_container_width=True):
    with st.spinner("Applying formula..."):
        try:
            st.session_state.filtered_selection = apply_formula(
                st.session_state.combined_data, 
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
        # Display the filtered selection
        st.dataframe(st.session_state.filtered_selection, use_container_width=True)
        
        # Compare the filtered selection to the overall averages
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