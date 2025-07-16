import streamlit as st
import pandas as pd

# Set page config
st.set_page_config(
    page_title="Assumptions - Investment Selection Tool",
    page_icon="📋",
    layout="wide",
)

st.title("📋 Assumptions")

st.markdown("""
This page outlines the key assumptions and methodology used in the investment selection tool.
""")

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