import streamlit as st
import pandas as pd
import numpy as np

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

# Display the recommended portfolio
st.header("Selected Investments")

# Display each selected fund with its details and comments
for apir, fund in st.session_state.recommended_portfolio.items():
    # Create a container for each fund with a border
    with st.container():
        st.markdown("---")
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.subheader(fund['Name'])
            st.markdown(f"**APIR Code:** {fund['APIR Code']}")
            st.markdown(f"**Category:** {fund['Morningstar Category']}")
            
            # Display comments if available
            if 'Comments' in fund and fund['Comments']:
                st.markdown("### Selection Rationale")
                st.write(fund['Comments'])
        
        with col2:
            # Add remove button
            if st.button("Remove", key=f"remove_{apir}"):
                remove_from_portfolio(apir)

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
    
    # Display the editable allocation table
    st.write("**Portfolio Allocation Table**")
    st.write("💡 **Tip:** Use Tab key to move between allocation fields for quick data entry")
    
    edited_allocation_df = st.data_editor(
        allocation_df,
        column_config={
            "Allocation %": st.column_config.NumberColumn(
                "Allocation %",
                width="small",
                min_value=0,
                max_value=100,
                step=0.1,
                format="%.1f",
                help="Enter the percentage allocation for this fund (use Tab to move to next field)"
            ),
            "Fund Name": st.column_config.TextColumn(
                "Fund Name",
                width="large",
                disabled=True
            ),
            "APIR Code": st.column_config.TextColumn(
                "APIR Code",
                width="medium",
                disabled=True
            ),
            "Category": st.column_config.TextColumn(
                "Category",
                width="medium",
                disabled=True
            )
        },
        use_container_width=True,
        hide_index=True,
        key="allocation_editor"
    )
    
    # Update session state with edited allocations
    for idx, row in edited_allocation_df.iterrows():
        apir = row['APIR Code']
        allocation = row['Allocation %']
        st.session_state.portfolio_allocations[apir] = allocation if pd.notna(allocation) else ""
    
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
    
    # Download portfolio with allocations
    portfolio_with_allocations = portfolio_df.copy()
    portfolio_with_allocations['Allocation %'] = portfolio_with_allocations['APIR Code'].map(
        lambda x: st.session_state.portfolio_allocations.get(x, "")
    )
    
    csv_portfolio = portfolio_with_allocations.to_csv(index=False)
    st.download_button(
        label="Download Portfolio with Allocations",
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