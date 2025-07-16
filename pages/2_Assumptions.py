import streamlit as st
import pandas as pd

# Set page config
st.set_page_config(
    page_title="Assumptions - Investment Selection Tool",
    page_icon="📋",
    layout="wide",
)

# Initialize strategic asset allocation in session state
if 'strategic_asset_allocation' not in st.session_state:
    st.session_state.strategic_asset_allocation = {
        'Asset Class': ['Cash', 'Fixed Interest', 'International Fixed Interest', 'Australian Shares', 'International Shares', 'Property', 'Alternatives'],
        'Type': ['Income', 'Income', 'Income', 'Growth', 'Growth', 'Income and Growth', 'Income and Growth'],
        'Defensive (100/0)': [70, 30, 0, 0, 0, 0, 0],
        'Conservative (80/20)': [20, 40, 20, 8, 6, 3, 3],
        'Moderate (60/40)': [15, 30, 15, 18, 12, 5, 5],
        'Balanced (40/60)': [5, 25, 10, 28, 20, 6, 6],
        'Growth (20/80)': [2, 12, 6, 38, 26, 8, 8],
        'High Growth (0/100)': [2, 0, 0, 48, 34, 8, 8]
    }

st.title("📋 Assumptions")

st.markdown("""
This page outlines the key assumptions and methodology used in the investment selection tool.
""")

# Strategic Asset Allocation
st.header("📊 Strategic Asset Allocation")

st.markdown("""
The following table shows the strategic asset allocation guidelines for different risk profiles. 
Each investment risk profile is supported by asset allocation guidelines designed to match your investment experience and risk tolerance with your expectations for investment returns.

You can modify these default values if needed for your specific analysis.
""")

# Create editable table for strategic asset allocation
with st.expander("Strategic Asset Allocation Table", expanded=True):
    # Create DataFrame from session state
    allocation_df = pd.DataFrame(st.session_state.strategic_asset_allocation)
    
    # Display editable table
    st.subheader("Asset Allocation by Risk Profile")
    
    # Create columns for the table
    col1, col2, col3, col4, col5, col6, col7, col8 = st.columns(8)
    
    with col1:
        st.write("**Asset Class**")
        st.write("**Type**")
    with col2:
        st.write("**Defensive**")
        st.write("**(100/0)**")
    with col3:
        st.write("**Conservative**")
        st.write("**(80/20)**")
    with col4:
        st.write("**Moderate**")
        st.write("**(60/40)**")
    with col5:
        st.write("**Balanced**")
        st.write("**(40/60)**")
    with col6:
        st.write("**Growth**")
        st.write("**(20/80)**")
    with col7:
        st.write("**High Growth**")
        st.write("**(0/100)**")
    with col8:
        st.write("**Actions**")
        st.write("")
    
    # Create input fields for each row
    for i, asset_class in enumerate(allocation_df['Asset Class']):
        with col1:
            st.write(f"**{asset_class}**")
            st.write(f"*{allocation_df.loc[i, 'Type']}*")
        
        with col2:
            new_defensive = st.number_input(
                f"def_{i}", 
                value=allocation_df.loc[i, 'Defensive (100/0)'],
                min_value=0,
                max_value=100,
                step=1,
                label_visibility="collapsed"
            )
            st.session_state.strategic_asset_allocation['Defensive (100/0)'][i] = new_defensive
        
        with col3:
            new_conservative = st.number_input(
                f"con_{i}", 
                value=allocation_df.loc[i, 'Conservative (80/20)'],
                min_value=0,
                max_value=100,
                step=1,
                label_visibility="collapsed"
            )
            st.session_state.strategic_asset_allocation['Conservative (80/20)'][i] = new_conservative
        
        with col4:
            new_moderate = st.number_input(
                f"mod_{i}", 
                value=allocation_df.loc[i, 'Moderate (60/40)'],
                min_value=0,
                max_value=100,
                step=1,
                label_visibility="collapsed"
            )
            st.session_state.strategic_asset_allocation['Moderate (60/40)'][i] = new_moderate
        
        with col5:
            new_balanced = st.number_input(
                f"bal_{i}", 
                value=allocation_df.loc[i, 'Balanced (40/60)'],
                min_value=0,
                max_value=100,
                step=1,
                label_visibility="collapsed"
            )
            st.session_state.strategic_asset_allocation['Balanced (40/60)'][i] = new_balanced
        
        with col6:
            new_growth = st.number_input(
                f"gro_{i}", 
                value=allocation_df.loc[i, 'Growth (20/80)'],
                min_value=0,
                max_value=100,
                step=1,
                label_visibility="collapsed"
            )
            st.session_state.strategic_asset_allocation['Growth (20/80)'][i] = new_growth
        
        with col7:
            new_high_growth = st.number_input(
                f"hg_{i}", 
                value=allocation_df.loc[i, 'High Growth (0/100)'],
                min_value=0,
                max_value=100,
                step=1,
                label_visibility="collapsed"
            )
            st.session_state.strategic_asset_allocation['High Growth (0/100)'][i] = new_high_growth
        
        with col8:
            if st.button(f"Reset {asset_class}", key=f"reset_{i}"):
                # Reset to default values
                defaults = {
                    'Cash': {'Defensive (100/0)': 70, 'Conservative (80/20)': 20, 'Moderate (60/40)': 15, 'Balanced (40/60)': 5, 'Growth (20/80)': 2, 'High Growth (0/100)': 2},
                    'Fixed Interest': {'Defensive (100/0)': 30, 'Conservative (80/20)': 40, 'Moderate (60/40)': 30, 'Balanced (40/60)': 25, 'Growth (20/80)': 12, 'High Growth (0/100)': 0},
                    'International Fixed Interest': {'Defensive (100/0)': 0, 'Conservative (80/20)': 20, 'Moderate (60/40)': 15, 'Balanced (40/60)': 10, 'Growth (20/80)': 6, 'High Growth (0/100)': 0},
                    'Australian Shares': {'Defensive (100/0)': 0, 'Conservative (80/20)': 8, 'Moderate (60/40)': 18, 'Balanced (40/60)': 28, 'Growth (20/80)': 38, 'High Growth (0/100)': 48},
                    'International Shares': {'Defensive (100/0)': 0, 'Conservative (80/20)': 6, 'Moderate (60/40)': 12, 'Balanced (40/60)': 20, 'Growth (20/80)': 26, 'High Growth (0/100)': 34},
                    'Property': {'Defensive (100/0)': 0, 'Conservative (80/20)': 3, 'Moderate (60/40)': 5, 'Balanced (40/60)': 6, 'Growth (20/80)': 8, 'High Growth (0/100)': 8},
                    'Alternatives': {'Defensive (100/0)': 0, 'Conservative (80/20)': 3, 'Moderate (60/40)': 5, 'Balanced (40/60)': 6, 'Growth (20/80)': 8, 'High Growth (0/100)': 8}
                }
                
                if asset_class in defaults:
                    for profile, value in defaults[asset_class].items():
                        st.session_state.strategic_asset_allocation[profile][i] = value
                st.rerun()
    
    # Calculate and display totals
    st.subheader("Profile Totals")
    totals_df = pd.DataFrame(st.session_state.strategic_asset_allocation)
    
    profile_totals = {}
    for profile in ['Defensive (100/0)', 'Conservative (80/20)', 'Moderate (60/40)', 'Balanced (40/60)', 'Growth (20/80)', 'High Growth (0/100)']:
        total = sum(totals_df[profile])
        profile_totals[profile] = total
        
        # Color code based on total
        if total == 100:
            st.success(f"{profile}: {total}%")
        elif total > 100:
            st.error(f"{profile}: {total}% (Over-allocated)")
        else:
            st.warning(f"{profile}: {total}% (Under-allocated)")
    
    # Reset all button
    if st.button("Reset All to Defaults"):
        st.session_state.strategic_asset_allocation = {
            'Asset Class': ['Cash', 'Fixed Interest', 'International Fixed Interest', 'Australian Shares', 'International Shares', 'Property', 'Alternatives'],
            'Type': ['Income', 'Income', 'Income', 'Growth', 'Growth', 'Income and Growth', 'Income and Growth'],
            'Defensive (100/0)': [70, 30, 0, 0, 0, 0, 0],
            'Conservative (80/20)': [20, 40, 20, 8, 6, 3, 3],
            'Moderate (60/40)': [15, 30, 15, 18, 12, 5, 5],
            'Balanced (40/60)': [5, 25, 10, 28, 20, 6, 6],
            'Growth (20/80)': [2, 12, 6, 38, 26, 8, 8],
            'High Growth (0/100)': [2, 0, 0, 48, 34, 8, 8]
        }
        st.rerun()

# Investment Analysis Assumptions
st.header("📊 Investment Analysis Assumptions")

with st.expander("Data Sources and Quality", expanded=True):
    st.markdown("""
    - **Data Source**: Investment data imported from CSV files containing fund performance metrics
    - **Data Currency**: Analysis assumes data is current and accurate as of the import date
    - **Missing Data**: Funds with missing critical metrics (3-year return, standard deviation, beta, Sharpe ratio) are excluded from certain calculations
    - **Data Validation**: System validates presence of required columns but does not verify data accuracy
    """)

with st.expander("Performance Metrics", expanded=True):
    st.markdown("""
    - **3-Year Annualized Return**: Used as primary performance measure, assumes past performance indicates future trends
    - **Standard Deviation**: 3-year standard deviation used as primary risk measure
    - **Beta**: Measures correlation with market movements, assumes market beta of 1.0 as baseline
    - **Sharpe Ratio**: Risk-adjusted return measure, higher values indicate better risk-adjusted performance
    - **Management Expense Ratio (MER)**: Annual fee assumption, impacts net returns
    """)

# Composite Scoring Methodology
st.header("🧮 Composite Scoring Methodology")

with st.expander("Scoring Formula", expanded=True):
    st.markdown("""
    The composite score uses the following formula:
    
    **Composite Score = (-(Fund StdDev - Category Avg StdDev)/10) + (Fund Sharpe - Category Avg Sharpe) + (Category Avg Beta - Fund Beta)**
    
    **Components:**
    - **Standard Deviation Component**: `(-(Fund StdDev - Category Avg StdDev)/10)`
      - Rewards funds with lower volatility than category average
      - Divided by 10 to normalize impact relative to other components
    
    - **Sharpe Ratio Component**: `(Fund Sharpe - Category Avg Sharpe)`
      - Rewards funds with better risk-adjusted returns than category average
      - Direct difference, higher Sharpe ratios score better
    
    - **Beta Component**: `(Category Avg Beta - Fund Beta)`
      - Rewards funds with lower market correlation than category average
      - Lower beta indicates less market risk
    """)

with st.expander("Scoring Assumptions", expanded=True):
    st.markdown("""
    - **Category Averages**: Calculated using Morningstar Category classifications
    - **Equal Weighting**: All three components have equal influence on the final score
    - **Relative Scoring**: Funds are scored relative to their category peers, not absolute benchmarks
    - **Higher is Better**: Higher composite scores indicate more favorable risk-adjusted characteristics
    """)

# Portfolio Construction Assumptions
st.header("📈 Portfolio Construction Assumptions")

with st.expander("Portfolio Metrics", expanded=True):
    st.markdown("""
    - **Weighted Averages**: All portfolio metrics calculated as allocation-weighted averages
    - **Allocation Basis**: Percentage allocations determine weighting for all calculations
    - **Missing Allocations**: Funds without allocation percentages are excluded from portfolio calculations
    - **Rebalancing**: Assumes static allocations, no automatic rebalancing considered
    """)

with st.expander("Risk Assumptions", expanded=True):
    st.markdown("""
    - **Correlation**: Portfolio calculations assume no correlation adjustments between holdings
    - **Diversification**: Benefits assumed through allocation across different asset classes/categories
    - **Market Conditions**: Historical metrics assumed to persist under similar market conditions
    - **Liquidity**: All selected investments assumed to be equally liquid
    """)

# Platform and Filtering Assumptions
st.header("🔍 Platform and Filtering Assumptions")

with st.expander("HUB24 Platform Filter", expanded=True):
    st.markdown("""
    - **APIR Code Matching**: Exact matching of APIR codes between platform lists and fund data
    - **Platform Availability**: Assumes HUB24 platform list is current and complete
    - **PDF Extraction**: Platform availability determined by PDF parsing of official HUB24 documentation
    - **Code Format**: APIR codes must match exactly (case-sensitive)
    """)

with st.expander("Custom Formula Filtering", expanded=True):
    st.markdown("""
    - **Expression Evaluation**: Custom formulas evaluated using pandas operations
    - **Variable Mapping**: Column names mapped to user-friendly variable names
    - **Safety**: Formula execution limited to mathematical operations and pandas functions
    - **Data Types**: Assumes numeric data for all formula calculations
    """)

# Limitations and Disclaimers
st.header("⚠️ Limitations and Disclaimers")

with st.expander("Important Limitations", expanded=True):
    st.markdown("""
    - **Past Performance**: Historical performance does not guarantee future results
    - **Market Risk**: All investments carry market risk that cannot be eliminated
    - **Data Accuracy**: Tool relies on accuracy of imported data, cannot verify source data quality
    - **Professional Advice**: Tool provides analysis only, not investment advice
    - **Regulatory Changes**: Does not account for potential regulatory or tax changes
    - **Market Conditions**: Analysis based on historical data under past market conditions
    """)

with st.expander("Technical Limitations", expanded=True):
    st.markdown("""
    - **Session Storage**: Data stored in browser session, lost when session ends
    - **Processing Limits**: Large datasets may impact performance
    - **Browser Compatibility**: Optimized for modern web browsers
    - **Network Dependency**: Requires stable internet connection for operation
    """)

# Methodology Notes
st.header("📝 Methodology Notes")

with st.expander("Top Quartile Identification", expanded=True):
    st.markdown("""
    - **Green Dot Indicator**: 🟢 marks funds in top quartile for 3-year returns within their category
    - **Quartile Calculation**: Based on 75th percentile of 3-year returns by Morningstar Category
    - **Category Basis**: Quartiles calculated separately for each asset class/category
    - **Performance Ranking**: Used for identification purposes, not included in composite scoring
    """)

with st.expander("Data Processing Notes", expanded=True):
    st.markdown("""
    - **CSV Import**: Supports multiple file upload and automatic data combination
    - **Column Mapping**: Expects specific column names for proper data processing
    - **Data Cleaning**: Automatic handling of common data formatting issues
    - **Validation**: Built-in validation for required columns and data types
    """)

# Footer
st.markdown("---")
st.markdown("*This tool is for analysis purposes only and does not constitute investment advice. Always consult with a qualified financial advisor before making investment decisions.*")