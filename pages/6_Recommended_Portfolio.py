import streamlit as st
import pandas as pd
import numpy as np
import io

# Set page configuration
st.set_page_config(
    page_title="Recommended Portfolio - Investment Selection Tool",
    page_icon="📊",
    layout="wide",
)

# Initialize session state variables if needed
if 'recommended_portfolio' not in st.session_state:
    st.session_state.recommended_portfolio = {}

# Initialize portfolio allocations if needed
if 'portfolio_allocations' not in st.session_state:
    st.session_state.portfolio_allocations = {}

# Initialize combined_data if needed
if 'combined_data' not in st.session_state:
    st.session_state.combined_data = None

# Initialize asset class mapping if needed
if 'asset_class_mapping' not in st.session_state:
    st.session_state.asset_class_mapping = {}

st.title("Recommended Portfolio")

# Function to convert the portfolio dictionary to a DataFrame
def portfolio_to_dataframe():
    if not st.session_state.recommended_portfolio:
        return None
    
    # Convert dictionary to DataFrame
    portfolio_data = list(st.session_state.recommended_portfolio.values())
    portfolio_df = pd.DataFrame(portfolio_data)
    
    # Ensure we have the right columns, even if some data is missing
    required_columns = ['Name', 'APIR Code', 'Morningstar Category', 'Comments']
    for col in required_columns:
        if col not in portfolio_df.columns:
            portfolio_df[col] = ""
    
    return portfolio_df

# Function to remove a fund from the portfolio
def remove_from_portfolio(apir_code):
    if apir_code in st.session_state.recommended_portfolio:
        fund_name = st.session_state.recommended_portfolio[apir_code]['Name']
        del st.session_state.recommended_portfolio[apir_code]
        # Also remove the allocation
        if apir_code in st.session_state.portfolio_allocations:
            del st.session_state.portfolio_allocations[apir_code]
        st.success(f"Removed {fund_name} from your recommended portfolio")
        # Rerun to update the UI
        st.rerun()

# Check if portfolio is empty
if not st.session_state.recommended_portfolio:
    st.info("""
    Your recommended portfolio is currently empty. 
    
    To add funds to your portfolio, go to the Formula Filtering page, 
    filter the investments based on your criteria, and select individual funds to add.
    """)
    st.stop()

# Convert portfolio to DataFrame for display
portfolio_df = portfolio_to_dataframe()

# No longer displaying individual fund details here - they're now in the allocation table

# Portfolio allocation table
st.header("Portfolio Allocation")

if portfolio_df is not None:
    st.write("Set the percentage allocation for each fund in your portfolio:")
    
    # Create the allocation table
    allocation_data = []
    total_allocation = 0.0
    
    for apir, fund in st.session_state.recommended_portfolio.items():
        # Get current allocation or default to empty
        current_allocation = st.session_state.portfolio_allocations.get(apir, "")
        
        allocation_data.append({
            'Allocation %': current_allocation,
            'Fund Name': fund['Name'],
            'APIR Code': apir,
            'Category': fund['Morningstar Category']
        })
        
        # Calculate total if allocation is a valid number
        try:
            if current_allocation:
                total_allocation += float(current_allocation)
        except ValueError:
            pass
    
    # Create DataFrame for the allocation table
    allocation_df = pd.DataFrame(allocation_data)
    
    # Display the allocation table using custom input fields for better navigation
    st.write("**Portfolio Allocation Table**")
    st.write("💡 **Tip:** Use Tab key to move between allocation fields for quick data entry")
    st.info("ℹ️ **Asset classes are automatically mapped** from Morningstar categories using the settings in the Assumptions page")
    
    # Create a table-like layout with individual input fields
    # Header row
    col1, col2, col3, col4, col5, col6 = st.columns([1, 3, 2, 2, 2, 1])
    with col1:
        st.write("**Allocation %**")
    with col2:
        st.write("**Fund Name**")
    with col3:
        st.write("**APIR Code**")
    with col4:
        st.write("**Category**")
    with col5:
        st.write("**Asset Class**")
    with col6:
        st.write("**Action**")
    
    # Data rows with individual input fields
    # Asset class options
    asset_classes = [
        'Cash', 
        'Australian Fixed Interest', 
        'International Fixed Interest', 
        'Australian Equities', 
        'International Equities', 
        'Property', 
        'Alternatives'
    ]
    
    for idx, (apir, fund) in enumerate(st.session_state.recommended_portfolio.items()):
        col1, col2, col3, col4, col5, col6 = st.columns([1, 3, 2, 2, 2, 1])
        
        with col1:
            # Get current allocation
            current_allocation = st.session_state.portfolio_allocations.get(apir, "")
            # Convert to float for number input, or use None if empty
            allocation_value = float(current_allocation) if current_allocation and current_allocation != "" else None
            
            # Create number input with unique key
            new_allocation = st.number_input(
                label=f"Allocation for {fund['Name']}",
                min_value=0.0,
                max_value=100.0,
                value=allocation_value,
                step=0.1,
                format="%.1f",
                key=f"allocation_{apir}",
                label_visibility="collapsed"
            )
            
            # Update session state with new allocation
            st.session_state.portfolio_allocations[apir] = new_allocation if new_allocation is not None else ""
        
        with col2:
            st.write(fund['Name'])
            # Show comments if available
            if 'Comments' in fund and fund['Comments']:
                st.caption(f"💬 {fund['Comments']}")
        
        with col3:
            st.write(apir)
        
        with col4:
            st.write(fund['Morningstar Category'])
        
        with col5:
            # Get asset class from Morningstar category mapping
            morningstar_category = fund.get('Morningstar Category', '')
            
            # Initialize Morningstar category mapping if not present
            if 'morningstar_asset_class_mapping' not in st.session_state:
                st.session_state.morningstar_asset_class_mapping = {
                    'Alternative - Private Equity': 'Alternatives',
                    'Alternative - Multistrategy': 'Alternatives',
                    'Australia Equity Income': 'Australian Equities',
                    'Australian Cash': 'Cash',
                    'Bonds - Australia': 'Australian Fixed Interest',
                    'Bonds - Global': 'International Fixed Interest',
                    'Equity Australia Large Blend': 'Australian Equities',
                    'Equity Australia Large Growth': 'Australian Equities',
                    'Equity Australia Large Value': 'Australian Equities',
                    'Equity Australia Mid/Small Growth': 'Australian Equities',
                    'Equity Australia Real Estate': 'Property',
                    'Equity Emerging Markets': 'International Equities',
                    'Equity Global Real Estate': 'Property',
                    'Equity Region Emerging Markets': 'International Equities',
                    'Equity Sector Global - Real Estate': 'Property',
                    'Equity World - Currency Hedged': 'International Equities',
                    'Equity World Large Blend': 'International Equities',
                    'Equity World Large Growth': 'International Equities',
                    'Equity World Large Value': 'International Equities',
                    'Equity World Mid/Small': 'International Equities',
                    'Global Bond': 'International Fixed Interest'
                }
            
            # Get mapped asset class
            mapped_asset_class = st.session_state.morningstar_asset_class_mapping.get(
                morningstar_category, 'Cash'  # Default to Cash if category not found
            )
            
            # Display the mapped asset class (read-only)
            st.write(f"**{mapped_asset_class}**")
            st.caption("*Auto-mapped*")
            
            # Update the asset class mapping in session state for backward compatibility
            st.session_state.asset_class_mapping[apir] = mapped_asset_class
        
        with col6:
            # Add remove button for each fund
            if st.button("Remove", key=f"remove_{apir}", use_container_width=True):
                remove_from_portfolio(apir)
    
    # Calculate and display total allocation
    total_allocation = 0.0
    for apir in st.session_state.recommended_portfolio.keys():
        try:
            allocation = st.session_state.portfolio_allocations.get(apir, "")
            if allocation and allocation != "":
                total_allocation += float(allocation)
        except (ValueError, TypeError):
            pass
    
    # Display allocation summary
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Allocation", f"{total_allocation:.1f}%")
    with col2:
        remaining = 100.0 - total_allocation
        st.metric("Remaining", f"{remaining:.1f}%")
    with col3:
        if abs(total_allocation - 100.0) < 0.1:
            st.success("✅ Portfolio Complete")
        elif total_allocation > 100.0:
            st.error("⚠️ Over-allocated")
        else:
            st.info("📝 Allocation in progress")
    
    # Portfolio Asset Class Allocation Analysis
    st.header("Portfolio Asset Class Allocation")
    
    if not st.session_state.recommended_portfolio:
        st.info("Add funds to your portfolio to see asset class allocation analysis")
    else:
        # Get detailed fund data for asset class analysis
        if st.session_state.combined_data is not None and not st.session_state.combined_data.empty:
            portfolio_apirs = list(st.session_state.recommended_portfolio.keys())
            detailed_portfolio = st.session_state.combined_data[
                st.session_state.combined_data['APIR Code'].isin(portfolio_apirs)
            ]
            
            if not detailed_portfolio.empty:
                # Asset class options
                asset_classes = [
                    'Cash', 
                    'Australian Fixed Interest', 
                    'International Fixed Interest', 
                    'Australian Equities', 
                    'International Equities', 
                    'Property', 
                    'Alternatives'
                ]
                
                # Calculate portfolio asset class allocations using Morningstar mapping
                asset_class_allocations = {ac: 0.0 for ac in asset_classes}
                total_allocated = 0.0
                
                for apir in portfolio_apirs:
                    # Get allocation percentage
                    allocation = st.session_state.portfolio_allocations.get(apir, "")
                    allocation_pct = 0.0
                    if allocation and allocation != "":
                        try:
                            allocation_pct = float(allocation)
                            total_allocated += allocation_pct
                        except (ValueError, TypeError):
                            allocation_pct = 0.0
                    
                    # Get fund details to find Morningstar category
                    fund_info = detailed_portfolio[detailed_portfolio['APIR Code'] == apir]
                    if not fund_info.empty:
                        morningstar_category = fund_info.iloc[0].get('Morningstar Category', '')
                        
                        # Get asset class from Morningstar mapping
                        if 'morningstar_asset_class_mapping' in st.session_state:
                            selected_asset_class = st.session_state.morningstar_asset_class_mapping.get(
                                morningstar_category, 'Cash'  # Default to Cash if not found
                            )
                        else:
                            # Fallback to manual mapping if Morningstar mapping not available
                            selected_asset_class = st.session_state.asset_class_mapping.get(apir, asset_classes[0])
                        
                        # Add to asset class total
                        if selected_asset_class in asset_class_allocations:
                            asset_class_allocations[selected_asset_class] += allocation_pct
                
                # Portfolio vs Target Allocation Analysis
                st.subheader("Portfolio vs Target Allocation")
                
                # Get target allocation from assumptions page (use Balanced as default)
                target_profile = st.selectbox(
                    "Select target risk profile for comparison:",
                    ['Defensive (100/0)', 'Conservative (80/20)', 'Moderate (60/40)', 'Balanced (40/60)', 'Growth (20/80)', 'High Growth (0/100)'],
                    index=3,  # Default to Balanced
                    key="target_profile_select",
                    help="Select a risk profile to compare your portfolio allocation against the strategic target allocation"
                )
                
                # Force rerun when profile changes
                if 'previous_target_profile' not in st.session_state:
                    st.session_state.previous_target_profile = target_profile
                elif st.session_state.previous_target_profile != target_profile:
                    st.session_state.previous_target_profile = target_profile
                    st.rerun()
                
                # Initialize session state for strategic asset allocation if not present
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
                
                # Initialize Morningstar category mapping if not present
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
                
                # Get target allocations from assumptions page
                target_allocations = {}
                asset_class_names = st.session_state.strategic_asset_allocation['Asset Class']
                
                # Get target values for the selected profile
                if target_profile in st.session_state.strategic_asset_allocation:
                    target_values = st.session_state.strategic_asset_allocation[target_profile]
                    
                    # Map assumption page asset classes to our asset classes
                    asset_class_mapping = {
                        'Cash': 'Cash',
                        'Fixed Interest': 'Australian Fixed Interest',
                        'International Fixed Interest': 'International Fixed Interest',
                        'Australian Shares': 'Australian Equities',
                        'International Shares': 'International Equities',
                        'Property': 'Property',
                        'Alternatives': 'Alternatives'
                    }
                    
                    # Build target allocations dictionary
                    for i, assumption_asset_class in enumerate(asset_class_names):
                        mapped_class = asset_class_mapping.get(assumption_asset_class, assumption_asset_class)
                        if mapped_class in target_allocations:
                            target_allocations[mapped_class] += target_values[i]
                        else:
                            target_allocations[mapped_class] = target_values[i]
                else:
                    # Fallback if profile not found
                    target_allocations = {
                        'Cash': 5,
                        'Australian Fixed Interest': 25,
                        'International Fixed Interest': 10,
                        'Australian Equities': 28,
                        'International Equities': 20,
                        'Property': 6,
                        'Alternatives': 6
                    }
                
                # Display current profile being compared
                st.info(f"Comparing against **{target_profile}** target allocation")
                
                # Create DataFrame for proper table display that will refresh
                allocation_comparison_data = []
                for asset_class in asset_classes:
                    portfolio_pct = asset_class_allocations.get(asset_class, 0.0)
                    target_pct = target_allocations.get(asset_class, 0.0)
                    variance = portfolio_pct - target_pct
                    
                    variance_str = f"+{variance:.1f}%" if variance > 0 else f"{variance:.1f}%" if variance < 0 else "0.0%"
                    
                    allocation_comparison_data.append({
                        'Asset Class': asset_class,
                        'Portfolio %': f"{portfolio_pct:.1f}%",
                        'Target %': f"{target_pct:.1f}%",
                        'Variance': variance_str
                    })
                
                # Display as a dataframe which will refresh properly
                comparison_df = pd.DataFrame(allocation_comparison_data)
                st.dataframe(comparison_df, use_container_width=True, hide_index=True)
                
                # Summary metrics
                st.markdown("---")
                summary_cols = st.columns(3)
                with summary_cols[0]:
                    st.metric("Total Allocated", f"{total_allocated:.1f}%")
                with summary_cols[1]:
                    total_variance = sum(abs(asset_class_allocations[ac] - target_allocations.get(ac, 0)) for ac in asset_classes)
                    st.metric("Total Absolute Variance", f"{total_variance:.1f}%")
                with summary_cols[2]:
                    if total_allocated > 0:
                        tracking_error = (total_variance / len(asset_classes))
                        st.metric("Average Tracking Error", f"{tracking_error:.1f}%")
                    else:
                        st.metric("Average Tracking Error", "N/A")
            else:
                st.warning("Unable to retrieve detailed fund data for asset class analysis")
        else:
            st.info("No data available for asset class analysis")
    
    # Calculate portfolio-level metrics
    st.header("Portfolio Metrics")
    
    # Get detailed fund data for metric calculations
    portfolio_metrics = None
    if st.session_state.combined_data is not None and not st.session_state.combined_data.empty:
        portfolio_apirs = list(st.session_state.recommended_portfolio.keys())
        detailed_portfolio = st.session_state.combined_data[
            st.session_state.combined_data['APIR Code'].isin(portfolio_apirs)
        ]
        
        if not detailed_portfolio.empty:
            # Calculate weighted portfolio metrics
            weighted_stddev = 0.0
            weighted_beta = 0.0
            weighted_sharpe = 0.0
            weighted_mer = 0.0
            weighted_return = 0.0
            total_weight = 0.0
            
            for apir in portfolio_apirs:
                allocation = st.session_state.portfolio_allocations.get(apir, "")
                if allocation and allocation != "":
                    try:
                        weight = float(allocation) / 100.0  # Convert percentage to decimal
                        fund_data = detailed_portfolio[detailed_portfolio['APIR Code'] == apir]
                        
                        if not fund_data.empty:
                            fund_row = fund_data.iloc[0]
                            
                            # Get metrics, handle NaN values
                            stddev = fund_row.get('3 Year Standard Deviation', 0)
                            beta = fund_row.get('3 Year Beta', 0)
                            sharpe = fund_row.get('3 Year Sharpe Ratio', 0)
                            mer = fund_row.get('Investment Management Fee(%)', 0)
                            return_3yr = fund_row.get('3 Years Annualised (%)', 0)
                            
                            # Only include in calculation if values are not NaN
                            if pd.notna(stddev):
                                weighted_stddev += weight * float(stddev)
                            if pd.notna(beta):
                                weighted_beta += weight * float(beta)
                            if pd.notna(sharpe):
                                weighted_sharpe += weight * float(sharpe)
                            if pd.notna(mer):
                                weighted_mer += weight * float(mer)
                            if pd.notna(return_3yr):
                                weighted_return += weight * float(return_3yr)
                            
                            total_weight += weight
                    except (ValueError, TypeError):
                        continue
            
            # Display portfolio metrics
            if total_weight > 0:
                col1, col2, col3, col4, col5 = st.columns(5)
                
                with col1:
                    st.metric("Portfolio 3Yr Return", f"{weighted_return:.2f}%")
                
                with col2:
                    st.metric("Portfolio StdDev", f"{weighted_stddev:.2f}")
                
                with col3:
                    st.metric("Portfolio Beta", f"{weighted_beta:.2f}")
                
                with col4:
                    st.metric("Portfolio Sharpe Ratio", f"{weighted_sharpe:.2f}")
                
                with col5:
                    st.metric("Portfolio MER", f"{weighted_mer:.2f}%")
                
                # Show allocation coverage
                coverage_pct = total_weight * 100
                if coverage_pct < 100:
                    st.info(f"Portfolio metrics calculated based on {coverage_pct:.1f}% of allocated funds")
            else:
                st.info("Portfolio metrics will be calculated when allocations are set")
        else:
            st.warning("Unable to retrieve detailed fund data for portfolio metrics")
    else:
        st.info("No data available for portfolio metric calculations")
    
    # Download portfolio with allocations and comprehensive data
    st.subheader("Download Portfolio Report")
    
    # Initialize session state for excel data
    if 'excel_data' not in st.session_state:
        st.session_state.excel_data = None
    
    # Create comprehensive Excel file with multiple sheets
    if st.button("Download Portfolio Report"):
        with st.spinner("Generating portfolio report..."):
            # Create an Excel file with multiple sheets
            output = io.BytesIO()
            
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                # Sheet 1: All Formula Filtered Data
                if st.session_state.filtered_selection is not None and not st.session_state.filtered_selection.empty:
                    st.session_state.filtered_selection.to_excel(writer, sheet_name='All Formula Filtered Data', index=False)
                elif st.session_state.combined_data is not None and not st.session_state.combined_data.empty:
                    st.session_state.combined_data.to_excel(writer, sheet_name='All Combined Data', index=False)
                
                # Sheet 2: Portfolio Analysis
                portfolio_sheet_data = []
                
                # Add portfolio funds with allocations
                portfolio_with_allocations = portfolio_df.copy()
                portfolio_with_allocations['Allocation %'] = portfolio_with_allocations['APIR Code'].map(
                    lambda x: st.session_state.portfolio_allocations.get(x, "")
                )
                
                # Get detailed fund information for portfolio
                if st.session_state.combined_data is not None and not st.session_state.combined_data.empty:
                    portfolio_apirs = list(st.session_state.recommended_portfolio.keys())
                    detailed_portfolio = st.session_state.combined_data[
                        st.session_state.combined_data['APIR Code'].isin(portfolio_apirs)
                    ]
                
                    if not detailed_portfolio.empty:
                        # Merge portfolio allocations with detailed data
                        detailed_with_allocations = detailed_portfolio.copy()
                        detailed_with_allocations['Allocation %'] = detailed_with_allocations['APIR Code'].map(
                            lambda x: st.session_state.portfolio_allocations.get(x, "")
                        )
                        detailed_with_allocations['Asset Class'] = detailed_with_allocations['APIR Code'].map(
                            lambda x: st.session_state.asset_class_mapping.get(x, "")
                        )
                        
                        # Reorder columns to have Allocation % as second column and APIR Code as third
                        columns = detailed_with_allocations.columns.tolist()
                        
                        # Remove the columns we want to reorder
                        if 'Allocation %' in columns:
                            columns.remove('Allocation %')
                        if 'APIR Code' in columns:
                            columns.remove('APIR Code')
                        
                        # Create new column order: Name, Allocation %, APIR Code, then rest
                        new_columns = []
                        if 'Name' in columns:
                            new_columns.append('Name')
                            columns.remove('Name')
                        
                        new_columns.extend(['Allocation %', 'APIR Code'])
                        new_columns.extend(columns)
                        
                        # Reorder the dataframe
                        detailed_with_allocations = detailed_with_allocations[new_columns]
                        
                        # Create a clean portfolio analysis sheet with separate sections
                        
                        # Section 1: Portfolio Funds with Allocations
                        portfolio_funds_section = detailed_with_allocations.copy()
                        portfolio_funds_section.to_excel(writer, sheet_name='Portfolio Analysis', index=False, startrow=0)
                        
                        # Get the starting row for the next section
                        current_row = len(portfolio_funds_section) + 3
                        
                        # Section 2: Portfolio Metrics
                        total_weight = 0.0
                        weighted_return = 0.0
                        weighted_stddev = 0.0
                        weighted_beta = 0.0
                        weighted_sharpe = 0.0
                        weighted_mer = 0.0
                        
                        for apir in portfolio_apirs:
                            allocation = st.session_state.portfolio_allocations.get(apir, "")
                            if allocation and allocation != "":
                                try:
                                    weight = float(allocation) / 100.0
                                    fund_data = detailed_portfolio[detailed_portfolio['APIR Code'] == apir]
                                    
                                    if not fund_data.empty:
                                        fund_row = fund_data.iloc[0]
                                        
                                        return_3yr = fund_row.get('3 Years Annualised (%)', 0)
                                        stddev = fund_row.get('3 Year Standard Deviation', 0)
                                        beta = fund_row.get('3 Year Beta', 0)
                                        sharpe = fund_row.get('3 Year Sharpe Ratio', 0)
                                        mer = fund_row.get('Investment Management Fee(%)', 0)
                                        
                                        if pd.notna(return_3yr):
                                            weighted_return += weight * float(return_3yr)
                                        if pd.notna(stddev):
                                            weighted_stddev += weight * float(stddev)
                                        if pd.notna(beta):
                                            weighted_beta += weight * float(beta)
                                        if pd.notna(sharpe):
                                            weighted_sharpe += weight * float(sharpe)
                                        if pd.notna(mer):
                                            weighted_mer += weight * float(mer)
                                        
                                        total_weight += weight
                                except (ValueError, TypeError):
                                    continue
                        
                        # Create metrics dataframe with clean structure
                        metrics_data = pd.DataFrame([
                            ['Portfolio 3Yr Return (%)', f"{weighted_return:.2f}"],
                            ['Portfolio Standard Deviation', f"{weighted_stddev:.2f}"],
                            ['Portfolio Beta', f"{weighted_beta:.2f}"],
                            ['Portfolio Sharpe Ratio', f"{weighted_sharpe:.2f}"],
                            ['Portfolio MER (%)', f"{weighted_mer:.2f}"],
                            ['Total Portfolio Weight (%)', f"{total_weight * 100:.1f}"]
                        ], columns=['Metric', 'Value'])
                        
                        metrics_data.to_excel(writer, sheet_name='Portfolio Analysis', index=False, startrow=current_row)
                        current_row += len(metrics_data) + 3
                        
                        # Section 3: Asset Class Allocation Analysis
                        asset_classes = ['Cash', 'Australian Fixed Interest', 'International Fixed Interest', 
                                       'Australian Equities', 'International Equities', 'Property', 'Alternatives']
                        asset_class_allocations = {ac: 0.0 for ac in asset_classes}
                        
                        for apir in portfolio_apirs:
                            allocation = st.session_state.portfolio_allocations.get(apir, "")
                            if allocation and allocation != "":
                                try:
                                    allocation_pct = float(allocation)
                                    selected_asset_class = st.session_state.asset_class_mapping.get(apir, asset_classes[0])
                                    if selected_asset_class in asset_class_allocations:
                                        asset_class_allocations[selected_asset_class] += allocation_pct
                                except (ValueError, TypeError):
                                    continue
                        
                        # Get target allocations
                        target_profile = "Balanced (40/60)"  # Default
                        target_allocations = {}
                        
                        if 'strategic_asset_allocation' in st.session_state:
                            asset_class_names = st.session_state.strategic_asset_allocation['Asset Class']
                            target_values = st.session_state.strategic_asset_allocation[target_profile]
                            
                            asset_class_mapping = {
                                'Cash': 'Cash',
                                'Fixed Interest': 'Australian Fixed Interest',
                                'International Fixed Interest': 'International Fixed Interest',
                                'Australian Shares': 'Australian Equities',
                                'International Shares': 'International Equities',
                                'Property': 'Property',
                                'Alternatives': 'Alternatives'
                            }
                            
                            for i, assumption_asset_class in enumerate(asset_class_names):
                                mapped_class = asset_class_mapping.get(assumption_asset_class, assumption_asset_class)
                                if mapped_class in target_allocations:
                                    target_allocations[mapped_class] += target_values[i]
                                else:
                                    target_allocations[mapped_class] = target_values[i]
                        else:
                            # Default target allocations
                            target_allocations = {
                                'Cash': 5, 'Australian Fixed Interest': 25, 'International Fixed Interest': 10,
                                'Australian Equities': 28, 'International Equities': 20, 'Property': 6, 'Alternatives': 6
                            }
                        
                        # Create allocation comparison data
                        allocation_comparison = []
                        for asset_class in asset_classes:
                            portfolio_pct = asset_class_allocations.get(asset_class, 0.0)
                            target_pct = target_allocations.get(asset_class, 0.0)
                            variance = portfolio_pct - target_pct
                            allocation_comparison.append([asset_class, portfolio_pct, target_pct, variance])
                        
                        allocation_df = pd.DataFrame(allocation_comparison, 
                                                   columns=['Asset Class', 'Portfolio %', 'Target %', 'Variance'])
                        
                        allocation_df.to_excel(writer, sheet_name='Portfolio Analysis', index=False, startrow=current_row)
                    else:
                        # Fallback if no detailed data available
                        portfolio_with_allocations.to_excel(writer, sheet_name='Portfolio Analysis', index=False)
                else:
                    # Fallback if no main data available
                    portfolio_with_allocations.to_excel(writer, sheet_name='Portfolio Analysis', index=False)
        
            # Prepare the file for download
            output.seek(0)
            st.session_state.excel_data = output.read()
            
            st.success("Portfolio report generated successfully! The Excel file contains two sheets: 'All Formula Filtered Data' and 'Portfolio Analysis'.")
            st.rerun()  # Refresh to show the download button
    
    # Show download button if excel data is available
    if st.session_state.excel_data is not None:
        st.download_button(
            label="📥 Download Portfolio Report (Excel)",
            data=st.session_state.excel_data,
            file_name="recommended_portfolio_report.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        
        # Clear the excel data after download button is shown
        if st.button("Generate New Report"):
            st.session_state.excel_data = None
            st.rerun()
    
    # Optional: Also provide CSV download
    st.subheader("Alternative Download Options")
    portfolio_with_allocations = portfolio_df.copy()
    portfolio_with_allocations['Allocation %'] = portfolio_with_allocations['APIR Code'].map(
        lambda x: st.session_state.portfolio_allocations.get(x, "")
    )
    
    csv_portfolio = portfolio_with_allocations.to_csv(index=False)
    st.download_button(
        label="Download Portfolio with Allocations (CSV)",
        data=csv_portfolio,
        file_name="recommended_portfolio_with_allocations.csv",
        mime="text/csv",
    )
    
    # Get detailed fund information
    if st.button("Generate Detailed Portfolio Report"):
        st.subheader("Detailed Portfolio Report")
        
        # Attempt to get full details for each fund from the main data
        if st.session_state.combined_data is not None and not st.session_state.combined_data.empty:
            # Get list of APIR codes in the portfolio
            portfolio_apirs = list(st.session_state.recommended_portfolio.keys())
            
            # Filter the main data to get only the selected funds
            if 'APIR Code' in st.session_state.combined_data.columns:
                detailed_portfolio = st.session_state.combined_data[
                    st.session_state.combined_data['APIR Code'].isin(portfolio_apirs)
                ]
                
                if not detailed_portfolio.empty:
                    # Display the detailed portfolio data
                    st.dataframe(detailed_portfolio, use_container_width=True)
                    
                    # Export detailed portfolio
                    csv_detailed = detailed_portfolio.to_csv(index=False)
                    st.download_button(
                        label="Download Detailed Portfolio Report",
                        data=csv_detailed,
                        file_name="recommended_portfolio_detailed.csv",
                        mime="text/csv",
                    )
                else:
                    st.warning("Could not retrieve detailed information for the selected funds.")