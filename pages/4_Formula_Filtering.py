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

# Initialize session state variables if they don't exist
if 'combined_data' not in st.session_state:
    st.session_state['combined_data'] = None

# Check if data is available
if st.session_state['combined_data'] is None or (isinstance(st.session_state['combined_data'], pd.DataFrame) and st.session_state['combined_data'].empty):
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

# Create tabs for different filtering approaches
filter_tabs = st.tabs(["Quick Filters", "Advanced Filters", "Preset Strategies"])

with filter_tabs[0]:
    st.subheader("Quick Filters")
    col1, col2 = st.columns(2)
    
with filter_tabs[1]:
    st.subheader("Advanced Filters")
    st.markdown("""
    Use these advanced filtering options to create sophisticated investment selections
    based on multiple criteria and statistical measures.
    """)
    
    # Create a multi-step filtering interface
    st.markdown("### 1. Performance Filters")
    perf_col1, perf_col2 = st.columns(2)
    
    with perf_col1:
        min_return = st.slider("Minimum Return (%)", 
                               min_value=0.0, 
                               max_value=20.0, 
                               value=0.0, 
                               step=0.5,
                               help="Filter investments with returns greater than this value")
    
    with perf_col2:
        max_expense = st.slider("Maximum Expense Ratio (%)", 
                                min_value=0.0, 
                                max_value=3.0, 
                                value=3.0, 
                                step=0.1,
                                help="Filter investments with expense ratios lower than this value")
    
    st.markdown("### 2. Risk Metrics")
    risk_col1, risk_col2 = st.columns(2)
    
    with risk_col1:
        max_risk = st.slider("Maximum Standard Deviation", 
                             min_value=0.0, 
                             max_value=30.0, 
                             value=30.0, 
                             step=1.0,
                             help="Filter investments with standard deviation lower than this value")
    
    with risk_col2:
        min_sharpe = st.slider("Minimum Sharpe Ratio", 
                               min_value=0.0, 
                               max_value=2.0, 
                               value=0.0, 
                               step=0.1,
                               help="Filter investments with Sharpe ratio greater than this value")
    
    st.markdown("### 3. Statistical Filters")
    stat_col1, stat_col2 = st.columns(2)
    
    with stat_col1:
        return_percentile = st.slider("Minimum Return Percentile", 
                                     min_value=0, 
                                     max_value=100, 
                                     value=0, 
                                     step=5,
                                     help="Filter to include only the top N% of investments by return")
    
    with stat_col2:
        expense_percentile = st.slider("Maximum Expense Percentile", 
                                      min_value=0, 
                                      max_value=100, 
                                      value=100, 
                                      step=5,
                                      help="Filter to include only the bottom N% of investments by expense")
    
    # Apply advanced filters button
    if st.button("Apply Advanced Filters", use_container_width=True):
        source_data = st.session_state['hub24_filtered'] if st.session_state['hub24_filtered'] is not None else st.session_state['combined_data']
        
        with st.spinner("Applying advanced filters..."):
            try:
                # Calculate additional metrics for better filtering
                enhanced_data = calculate_performance_metrics(source_data)
                
                # Start with all rows selected
                mask = pd.Series([True] * len(enhanced_data))
                
                # Apply each filter based on user input
                if min_return > 0:
                    mask = mask & (enhanced_data['3 Years Annualised (%)'] >= min_return)
                
                if max_expense < 3.0:
                    mask = mask & (enhanced_data['Investment Management Fee(%)'] <= max_expense)
                
                if max_risk < 30.0:
                    mask = mask & (enhanced_data['3 Year Standard Deviation'] <= max_risk)
                
                if min_sharpe > 0:
                    mask = mask & (enhanced_data['3 Year Sharpe Ratio'] >= min_sharpe)
                
                # Apply percentile filters if selected
                if return_percentile > 0:
                    return_threshold = np.percentile(enhanced_data['3 Years Annualised (%)'].dropna(), 100 - return_percentile)
                    mask = mask & (enhanced_data['3 Years Annualised (%)'] >= return_threshold)
                
                if expense_percentile < 100:
                    expense_threshold = np.percentile(enhanced_data['Investment Management Fee(%)'].dropna(), expense_percentile)
                    mask = mask & (enhanced_data['Investment Management Fee(%)'] <= expense_threshold)
                
                # Apply the combined mask
                filtered_data = enhanced_data[mask].copy()
                
                # Store the filtered results
                st.session_state['filtered_selection'] = filtered_data
                st.session_state['last_formula'] = "Advanced Filtering"
                
                # Show results
                if filtered_data.empty:
                    st.warning("No investments match all the selected criteria. Try relaxing some filters.")
                else:
                    st.success(f"Found {len(filtered_data)} investments matching all criteria.")
                    # Show a preview of the filtered data
                    st.dataframe(filtered_data[['Name', 'APIR Code', 'Morningstar Category', 
                                              '3 Years Annualised (%)', 'Investment Management Fee(%)']].head(5))
            
            except Exception as e:
                st.error(f"Error applying advanced filters: {str(e)}")
    
with filter_tabs[2]:
    st.subheader("Preset Strategies")
    st.info("Choose from pre-configured investment strategies to quickly filter your data")
    
    # Offer preset strategy options
    strategy = st.selectbox(
        "Select a strategy",
        [
            "Balanced Portfolio",
            "High Growth",
            "Low Cost",
            "Income Focus",
            "Conservative",
            "Quality Value",
            "Category Leaders"
        ],
        help="Pre-configured strategies with optimized filtering parameters"
    )
    
    # Display strategy description
    if strategy == "Balanced Portfolio":
        st.markdown("""
        **Balanced Portfolio Strategy:**
        This strategy balances return and risk, selecting investments with:
        - Above-average returns
        - Below-average expenses
        - Moderate risk profile
        - Positive risk-adjusted performance
        """)
    elif strategy == "High Growth":
        st.markdown("""
        **High Growth Strategy:**
        Focused on maximizing growth potential:
        - Top 25% of returns
        - Above-average Sharpe ratio
        - Accepts higher volatility for growth
        """)
    elif strategy == "Low Cost":
        st.markdown("""
        **Low Cost Strategy:**
        Prioritizes fee efficiency:
        - Bottom 25% in expense ratio
        - Acceptable performance
        - Good for long-term passive investment
        """)
    elif strategy == "Income Focus":
        st.markdown("""
        **Income Focus Strategy:**
        Emphasizes stable income generation:
        - Fixed Income categories
        - Lower volatility
        - Better risk-adjusted returns
        """)
    elif strategy == "Conservative":
        st.markdown("""
        **Conservative Strategy:**
        Minimizes downside risk:
        - Lower beta
        - Lower standard deviation
        - Moderate expenses
        - Capital preservation focus
        """)
    elif strategy == "Quality Value":
        st.markdown("""
        **Quality Value Strategy:**
        Identifies undervalued quality investments:
        - Strong Sharpe ratio
        - Moderate fees
        - Strong relative performance
        """)
    elif strategy == "Category Leaders":
        st.markdown("""
        **Category Leaders Strategy:**
        Selects top performers within each investment category:
        - Top 20% in each Morningstar Category
        - Above-average Sharpe ratio
        - Competitive fees
        """)
    
    # Apply preset strategy button
    if st.button("Apply Strategy", use_container_width=True):
        source_data = st.session_state['hub24_filtered'] if st.session_state['hub24_filtered'] is not None else st.session_state['combined_data']
        
        with st.spinner(f"Applying {strategy} strategy..."):
            try:
                # Calculate additional metrics for strategy implementation
                enhanced_data = calculate_performance_metrics(source_data)
                
                # Initialize filtered_data as empty
                filtered_data = pd.DataFrame()
                
                # Define and apply strategy logic
                if strategy == "Balanced Portfolio":
                    # Use formula engine for Balanced Portfolio
                    formula = "(`3 Years Annualised (%)` > 5) & (`Investment Management Fee(%)` < 1.0) & (`3 Year Standard Deviation` < 15)"
                    filtered_data = apply_formula(enhanced_data, formula)
                
                elif strategy == "High Growth":
                    # Top 25% of returns
                    if '3 Years Annualised (%)' in enhanced_data.columns:
                        return_threshold = np.percentile(enhanced_data['3 Years Annualised (%)'].dropna(), 75)
                        mask = enhanced_data['3 Years Annualised (%)'] >= return_threshold
                        filtered_data = enhanced_data[mask].copy()
                
                elif strategy == "Low Cost":
                    # Bottom 25% in expense ratio
                    if 'Investment Management Fee(%)' in enhanced_data.columns:
                        expense_threshold = np.percentile(enhanced_data['Investment Management Fee(%)'].dropna(), 25)
                        mask = enhanced_data['Investment Management Fee(%)'] <= expense_threshold
                        filtered_data = enhanced_data[mask].copy()
                
                elif strategy == "Income Focus":
                    # Focus on Fixed Income categories with good risk-adjusted returns
                    if 'Morningstar Category' in enhanced_data.columns and '3 Year Sharpe Ratio' in enhanced_data.columns:
                        mask = enhanced_data['Morningstar Category'].str.contains('Fixed Income|Bond|Income', case=False, na=False)
                        mask = mask & (enhanced_data['3 Year Sharpe Ratio'] > enhanced_data['3 Year Sharpe Ratio'].median())
                        filtered_data = enhanced_data[mask].copy()
                
                elif strategy == "Conservative":
                    # Lower risk, lower beta
                    if '3 Year Standard Deviation' in enhanced_data.columns and '3 Year Beta' in enhanced_data.columns:
                        risk_threshold = np.percentile(enhanced_data['3 Year Standard Deviation'].dropna(), 30)
                        mask = (enhanced_data['3 Year Standard Deviation'] <= risk_threshold)
                        mask = mask & (enhanced_data['3 Year Beta'] < 0.8)
                        filtered_data = enhanced_data[mask].copy()
                
                elif strategy == "Quality Value":
                    # Strong Sharpe ratio, moderate fees
                    if '3 Year Sharpe Ratio' in enhanced_data.columns and 'Investment Management Fee(%)' in enhanced_data.columns:
                        sharpe_threshold = np.percentile(enhanced_data['3 Year Sharpe Ratio'].dropna(), 70)
                        expense_threshold = np.percentile(enhanced_data['Investment Management Fee(%)'].dropna(), 60)
                        mask = (enhanced_data['3 Year Sharpe Ratio'] >= sharpe_threshold)
                        mask = mask & (enhanced_data['Investment Management Fee(%)'] <= expense_threshold)
                        filtered_data = enhanced_data[mask].copy()
                
                elif strategy == "Category Leaders":
                    # For Category Leaders, use a special approach to get top performers in each category
                    if 'Morningstar Category' in enhanced_data.columns and '3 Years Annualised (%)' in enhanced_data.columns:
                        result = []
                        for category, group in enhanced_data.groupby('Morningstar Category'):
                            if len(group) > 0:
                                # Select top 20% in each category by returns
                                threshold = np.percentile(group['3 Years Annualised (%)'].dropna(), 80)
                                top_in_category = group[
                                    (group['3 Years Annualised (%)'] >= threshold) & 
                                    (group['3 Year Sharpe Ratio'] > group['3 Year Sharpe Ratio'].median())
                                ]
                                result.append(top_in_category)
                        
                        if result:
                            filtered_data = pd.concat(result)
                        else:
                            filtered_data = pd.DataFrame()
                
                # Store the filtered results
                st.session_state['filtered_selection'] = filtered_data
                st.session_state['last_formula'] = f"Strategy: {strategy}"
                
                # Show results
                if filtered_data.empty:
                    st.warning(f"No investments match the {strategy} criteria.")
                else:
                    st.success(f"Found {len(filtered_data)} investments matching the {strategy} strategy.")
                    # Show a preview of the filtered data
                    st.dataframe(filtered_data[['Name', 'APIR Code', 'Morningstar Category', 
                                              '3 Years Annualised (%)', 'Investment Management Fee(%)']].head(5))
            
            except Exception as e:
                st.error(f"Error applying strategy: {str(e)}")
                st.error(f"Debug info: {strategy}")

with col1:
    # APL filter button for Morningstar Rating >= 3
    if st.button("APL Filter (Morningstar Rating ≥ 3)", use_container_width=True):
        # Use data that might already have been filtered by HUB24
        source_data = st.session_state['combined_data'] if st.session_state['hub24_filtered'] is None else st.session_state['hub24_filtered']
        
        # Check if column exists
        if 'Morningstar Rating' not in source_data.columns:
            st.error("Morningstar Rating column not found in the data")
        else:
            with st.spinner("Applying APL filter..."):
                try:
                    # Convert Morningstar Rating to numeric (handle potential non-numeric values)
                    ratings = source_data['Morningstar Rating'].copy()
                    ratings = pd.to_numeric(ratings, errors='coerce')
                    
                    # Create a mask for funds with rating of 3 or higher
                    # Convert to numpy array for safer comparison
                    mask = ratings.fillna(0).values >= 3
                    filtered_data = source_data[mask]
                    
                    # Update the filtered selection
                    st.session_state['filtered_selection'] = filtered_data
                    
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