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
        'Asset Class': ['Cash', 'Australian Fixed Interest', 'International Fixed Interest', 'Australian Equities', 'International Equities', 'Property', 'Alternatives'],
        'Type': ['Income', 'Income', 'Income', 'Growth', 'Growth', 'Income and Growth', 'Income and Growth'],
        'Defensive (100/0)': [70, 30, 0, 0, 0, 0, 0],
        'Conservative (80/20)': [20, 40, 20, 8, 6, 3, 3],
        'Moderate (60/40)': [15, 30, 15, 18, 12, 5, 5],
        'Balanced (40/60)': [5, 25, 10, 28, 20, 6, 6],
        'Growth (20/80)': [2, 12, 6, 38, 26, 8, 8],
        'High Growth (0/100)': [2, 0, 0, 48, 34, 8, 8]
    }

# Initialize Morningstar category mapping in session state
if 'morningstar_asset_class_mapping' not in st.session_state:
    st.session_state.morningstar_asset_class_mapping = {
        'Alternative - Private Equity': 'Alternatives',
        'Australia Equity Income': 'Australian Equities',
        'Australian Cash': 'Cash',
        'Bonds - Australia': 'Australian Fixed Interest',
        'Equity Australia Large Blend': 'Australian Equities',
        'Equity Australia Large Growth': 'Australian Equities',
        'Equity Australia Large Value': 'Australian Equities',
        'Equity Australia Mid/Small Growth': 'Australian Equities',
        'Equity Australia Real Estate': 'Property',
        'Equity Emerging Markets': 'International Equities',
        'Equity Region Emerging Markets': 'International Equities',
        'Equity Sector Global - Real Estate': 'Property',
        'Equity World - Currency Hedged': 'International Equities',
        'Equity World Large Blend': 'International Equities',
        'Equity World Large Growth': 'International Equities',
        'Equity World Large Value': 'International Equities',
        'Equity World Mid/Small': 'International Equities',
        'Global Bond': 'International Fixed Interest'
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
    
    # Create a more structured table using HTML-like formatting
    st.markdown("---")
    
    # Header row
    header_cols = st.columns([2, 1, 1, 1, 1, 1, 1, 1])
    with header_cols[0]:
        st.markdown("**Asset Class / Type**")
    with header_cols[1]:
        st.markdown("**Defensive**<br>**(100/0)**", unsafe_allow_html=True)
    with header_cols[2]:
        st.markdown("**Conservative**<br>**(80/20)**", unsafe_allow_html=True)
    with header_cols[3]:
        st.markdown("**Moderate**<br>**(60/40)**", unsafe_allow_html=True)
    with header_cols[4]:
        st.markdown("**Balanced**<br>**(40/60)**", unsafe_allow_html=True)
    with header_cols[5]:
        st.markdown("**Growth**<br>**(20/80)**", unsafe_allow_html=True)
    with header_cols[6]:
        st.markdown("**High Growth**<br>**(0/100)**", unsafe_allow_html=True)
    with header_cols[7]:
        st.markdown("**Actions**")
    
    st.markdown("---")
    
    # Create input fields for each row
    for i, asset_class in enumerate(allocation_df['Asset Class']):
        cols = st.columns([2, 1, 1, 1, 1, 1, 1, 1])
        
        with cols[0]:
            st.markdown(f"**{asset_class}**")
            st.caption(f"*{allocation_df.loc[i, 'Type']}*")
        
        with cols[1]:
            new_defensive = st.number_input(
                f"Defensive {asset_class}", 
                value=allocation_df.loc[i, 'Defensive (100/0)'],
                min_value=0,
                max_value=100,
                step=1,
                label_visibility="collapsed",
                key=f"def_{i}"
            )
            st.session_state.strategic_asset_allocation['Defensive (100/0)'][i] = new_defensive
        
        with cols[2]:
            new_conservative = st.number_input(
                f"Conservative {asset_class}", 
                value=allocation_df.loc[i, 'Conservative (80/20)'],
                min_value=0,
                max_value=100,
                step=1,
                label_visibility="collapsed",
                key=f"con_{i}"
            )
            st.session_state.strategic_asset_allocation['Conservative (80/20)'][i] = new_conservative
        
        with cols[3]:
            new_moderate = st.number_input(
                f"Moderate {asset_class}", 
                value=allocation_df.loc[i, 'Moderate (60/40)'],
                min_value=0,
                max_value=100,
                step=1,
                label_visibility="collapsed",
                key=f"mod_{i}"
            )
            st.session_state.strategic_asset_allocation['Moderate (60/40)'][i] = new_moderate
        
        with cols[4]:
            new_balanced = st.number_input(
                f"Balanced {asset_class}", 
                value=allocation_df.loc[i, 'Balanced (40/60)'],
                min_value=0,
                max_value=100,
                step=1,
                label_visibility="collapsed",
                key=f"bal_{i}"
            )
            st.session_state.strategic_asset_allocation['Balanced (40/60)'][i] = new_balanced
        
        with cols[5]:
            new_growth = st.number_input(
                f"Growth {asset_class}", 
                value=allocation_df.loc[i, 'Growth (20/80)'],
                min_value=0,
                max_value=100,
                step=1,
                label_visibility="collapsed",
                key=f"gro_{i}"
            )
            st.session_state.strategic_asset_allocation['Growth (20/80)'][i] = new_growth
        
        with cols[6]:
            new_high_growth = st.number_input(
                f"High Growth {asset_class}", 
                value=allocation_df.loc[i, 'High Growth (0/100)'],
                min_value=0,
                max_value=100,
                step=1,
                label_visibility="collapsed",
                key=f"hg_{i}"
            )
            st.session_state.strategic_asset_allocation['High Growth (0/100)'][i] = new_high_growth
        
        with cols[7]:
            if st.button(f"Reset", key=f"reset_{i}"):
                # Reset to default values
                defaults = {
                    'Cash': {'Defensive (100/0)': 70, 'Conservative (80/20)': 20, 'Moderate (60/40)': 15, 'Balanced (40/60)': 5, 'Growth (20/80)': 2, 'High Growth (0/100)': 2},
                    'Australian Fixed Interest': {'Defensive (100/0)': 30, 'Conservative (80/20)': 40, 'Moderate (60/40)': 30, 'Balanced (40/60)': 25, 'Growth (20/80)': 12, 'High Growth (0/100)': 0},
                    'International Fixed Interest': {'Defensive (100/0)': 0, 'Conservative (80/20)': 20, 'Moderate (60/40)': 15, 'Balanced (40/60)': 10, 'Growth (20/80)': 6, 'High Growth (0/100)': 0},
                    'Australian Equities': {'Defensive (100/0)': 0, 'Conservative (80/20)': 8, 'Moderate (60/40)': 18, 'Balanced (40/60)': 28, 'Growth (20/80)': 38, 'High Growth (0/100)': 48},
                    'International Equities': {'Defensive (100/0)': 0, 'Conservative (80/20)': 6, 'Moderate (60/40)': 12, 'Balanced (40/60)': 20, 'Growth (20/80)': 26, 'High Growth (0/100)': 34},
                    'Property': {'Defensive (100/0)': 0, 'Conservative (80/20)': 3, 'Moderate (60/40)': 5, 'Balanced (40/60)': 6, 'Growth (20/80)': 8, 'High Growth (0/100)': 8},
                    'Alternatives': {'Defensive (100/0)': 0, 'Conservative (80/20)': 3, 'Moderate (60/40)': 5, 'Balanced (40/60)': 6, 'Growth (20/80)': 8, 'High Growth (0/100)': 8}
                }
                
                if asset_class in defaults:
                    for profile, value in defaults[asset_class].items():
                        st.session_state.strategic_asset_allocation[profile][i] = value
                st.rerun()
        
        # Add spacing between rows
        st.markdown("")
    
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
            'Asset Class': ['Cash', 'Australian Fixed Interest', 'International Fixed Interest', 'Australian Equities', 'International Equities', 'Property', 'Alternatives'],
            'Type': ['Income', 'Income', 'Income', 'Growth', 'Growth', 'Income and Growth', 'Income and Growth'],
            'Defensive (100/0)': [70, 30, 0, 0, 0, 0, 0],
            'Conservative (80/20)': [20, 40, 20, 8, 6, 3, 3],
            'Moderate (60/40)': [15, 30, 15, 18, 12, 5, 5],
            'Balanced (40/60)': [5, 25, 10, 28, 20, 6, 6],
            'Growth (20/80)': [2, 12, 6, 38, 26, 8, 8],
            'High Growth (0/100)': [2, 0, 0, 48, 34, 8, 8]
        }
        st.rerun()

# Morningstar Category to Asset Class Mapping
st.header("🏷️ Morningstar Category Mapping")

st.markdown("""
The following table maps Morningstar fund categories to the asset classes used in portfolio allocation analysis. 
You can modify these mappings to customize how different fund types are categorized.
""")

with st.expander("Morningstar Category to Asset Class Mapping", expanded=True):
    st.subheader("Category Mapping Configuration")
    
    # Asset class options
    asset_class_options = [
        'Cash', 
        'Australian Fixed Interest', 
        'International Fixed Interest', 
        'Australian Equities', 
        'International Equities', 
        'Property', 
        'Alternatives'
    ]
    
    # Display mapping table
    st.markdown("**Morningstar Category → Asset Class Assignment**")
    st.markdown("---")
    
    # Create columns for header
    header_cols = st.columns([3, 2, 1])
    with header_cols[0]:
        st.write("**Morningstar Category**")
    with header_cols[1]:
        st.write("**Asset Class**")
    with header_cols[2]:
        st.write("**Actions**")
    
    st.markdown("---")
    
    # Display each mapping with dropdown
    for category, current_asset_class in st.session_state.morningstar_asset_class_mapping.items():
        cols = st.columns([3, 2, 1])
        
        with cols[0]:
            st.write(category)
        
        with cols[1]:
            try:
                current_index = asset_class_options.index(current_asset_class)
            except ValueError:
                current_index = 0
            
            new_asset_class = st.selectbox(
                f"Asset class for {category}",
                asset_class_options,
                index=current_index,
                key=f"mapping_{category}",
                label_visibility="collapsed"
            )
            
            # Update session state if changed
            if new_asset_class != current_asset_class:
                st.session_state.morningstar_asset_class_mapping[category] = new_asset_class
        
        with cols[2]:
            if st.button("Reset", key=f"reset_mapping_{category}"):
                # Reset to default mapping
                default_mappings = {
                    'Alternative - Private Equity': 'Alternatives',
                    'Australia Equity Income': 'Australian Equities',
                    'Australian Cash': 'Cash',
                    'Bonds - Australia': 'Australian Fixed Interest',
                    'Equity Australia Large Blend': 'Australian Equities',
                    'Equity Australia Large Growth': 'Australian Equities',
                    'Equity Australia Large Value': 'Australian Equities',
                    'Equity Australia Mid/Small Growth': 'Australian Equities',
                    'Equity Australia Real Estate': 'Property',
                    'Equity Emerging Markets': 'International Equities',
                    'Equity Region Emerging Markets': 'International Equities',
                    'Equity Sector Global - Real Estate': 'Property',
                    'Equity World - Currency Hedged': 'International Equities',
                    'Equity World Large Blend': 'International Equities',
                    'Equity World Large Growth': 'International Equities',
                    'Equity World Large Value': 'International Equities',
                    'Equity World Mid/Small': 'International Equities',
                    'Global Bond': 'International Fixed Interest'
                }
                if category in default_mappings:
                    st.session_state.morningstar_asset_class_mapping[category] = default_mappings[category]
                st.rerun()
    
    # Reset all mappings button
    if st.button("Reset All Category Mappings to Defaults"):
        st.session_state.morningstar_asset_class_mapping = {
            'Alternative - Private Equity': 'Alternatives',
            'Australia Equity Income': 'Australian Equities',
            'Australian Cash': 'Cash',
            'Bonds - Australia': 'Australian Fixed Interest',
            'Equity Australia Large Blend': 'Australian Equities',
            'Equity Australia Large Growth': 'Australian Equities',
            'Equity Australia Large Value': 'Australian Equities',
            'Equity Australia Mid/Small Growth': 'Australian Equities',
            'Equity Australia Real Estate': 'Property',
            'Equity Emerging Markets': 'International Equities',
            'Equity Region Emerging Markets': 'International Equities',
            'Equity Sector Global - Real Estate': 'Property',
            'Equity World - Currency Hedged': 'International Equities',
            'Equity World Large Blend': 'International Equities',
            'Equity World Large Growth': 'International Equities',
            'Equity World Large Value': 'International Equities',
            'Equity World Mid/Small': 'International Equities',
            'Global Bond': 'International Fixed Interest'
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