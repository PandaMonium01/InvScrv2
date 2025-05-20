import streamlit as st
import pandas as pd
import numpy as np
from utils.data_storage import get_data, store_data, get_dataframe, store_dataframe

# Set page configuration
st.set_page_config(
    page_title="Investment Selection Tool",
    page_icon="📊",
    layout="wide",
)

# Initialize session state variables if they don't exist
if 'combined_data' not in st.session_state:
    st.session_state['combined_data'] = None
if 'hub24_filtered' not in st.session_state:
    st.session_state['hub24_filtered'] = None
if 'filtered_selection' not in st.session_state:
    st.session_state['filtered_selection'] = None
if 'last_formula' not in st.session_state:
    st.session_state['last_formula'] = ""
if 'portfolio' not in st.session_state:
    st.session_state['portfolio'] = {}

def main():
    st.title("Investment Selection Tool")
    
    st.markdown("""
    ## Welcome to the Investment Selection Tool
    
    This application helps you analyze and select investments based on custom criteria.
    
    ### How to use:
    
    1. **Upload File** - Simple CSV file upload (recommended if having issues with Data Import page)
    2. **Data Import** - Advanced CSV upload with multiple files
    3. **HUB24 Filter** - Filter investments available on the HUB24 platform
    4. **Formula Filtering** - Apply custom formulas to filter investments
    5. **Data Analysis** - Analyze the filtered investments
    6. **Recommended Portfolio** - View and manage your selected portfolio
    
    ### Data Status:
    """)
    
    # Display data status
    col1, col2 = st.columns(2)
    
    with col1:
        if st.session_state['combined_data'] is not None and not isinstance(st.session_state['combined_data'], pd.DataFrame) or \
           (isinstance(st.session_state['combined_data'], pd.DataFrame) and not st.session_state['combined_data'].empty):
            data_count = len(st.session_state['combined_data']) if isinstance(st.session_state['combined_data'], pd.DataFrame) else "Unknown"
            st.success(f"✅ Combined Data: {data_count} investments loaded")
        else:
            st.warning("❌ No data loaded. Please go to Data Import page.")
            
        if st.session_state['hub24_filtered'] is not None and not isinstance(st.session_state['hub24_filtered'], pd.DataFrame) or \
           (isinstance(st.session_state['hub24_filtered'], pd.DataFrame) and not st.session_state['hub24_filtered'].empty):
            hub_count = len(st.session_state['hub24_filtered']) if isinstance(st.session_state['hub24_filtered'], pd.DataFrame) else "Unknown"
            st.success(f"✅ HUB24 Filter: {hub_count} investments available on HUB24")
        else:
            st.info("ℹ️ No HUB24 filter applied")
    
    with col2:
        if st.session_state['filtered_selection'] is not None and not isinstance(st.session_state['filtered_selection'], pd.DataFrame) or \
           (isinstance(st.session_state['filtered_selection'], pd.DataFrame) and not st.session_state['filtered_selection'].empty):
            formula_count = len(st.session_state['filtered_selection']) if isinstance(st.session_state['filtered_selection'], pd.DataFrame) else "Unknown"
            st.success(f"✅ Formula Filter: {formula_count} investments selected")
            
            if st.session_state['last_formula']:
                st.code(st.session_state['last_formula'], language="python")
        else:
            st.info("ℹ️ No formula filter applied")
            
        if st.session_state['portfolio'] and len(st.session_state['portfolio']) > 0:
            st.success(f"✅ Portfolio: {len(st.session_state['portfolio'])} investments selected")
        else:
            st.info("ℹ️ No portfolio created yet")
            
    # Add clear data option
    st.header("Reset Data")
    if st.button("Clear All Data", use_container_width=True):
        for key in ['combined_data', 'hub24_filtered', 'filtered_selection', 'last_formula', 'portfolio', 'selected_categories']:
            if key in st.session_state:
                del st.session_state[key]
        st.success("All data has been cleared")
        st.rerun()

if __name__ == "__main__":
    main()