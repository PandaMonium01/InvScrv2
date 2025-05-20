import streamlit as st
import pandas as pd
import numpy as np
import re
import PyPDF2
from utils.visualization import create_risk_return_scatter

# Set page configuration
st.set_page_config(
    page_title="HUB24 Filter - Investment Selection Tool",
    page_icon="📊",
    layout="wide",
)

st.title("HUB24 Platform Filter")

# Initialize the session state variables if they don't exist
if 'combined_data' not in st.session_state:
    st.session_state['combined_data'] = None
if 'hub24_filtered' not in st.session_state:
    st.session_state['hub24_filtered'] = None

# Extract APIR codes from a PDF file
def extract_apir_codes_from_pdf(pdf_file):
    try:
        # Create a PDF reader object
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        
        # Define APIR code patterns - covering various formats found in HUB24 documentation
        # Standard format: 3 letters + 4-9 alphanumeric characters, often ending with AU
        standard_pattern = r'\b[A-Z]{3}[0-9A-Z]{2,9}(?:AU)?\b'
        
        # Some APIR codes might be separated by spaces or have special formatting
        # For example: "ABC 123 AU", "ABC-123AU", etc.
        # This pattern will capture these with spaces/hyphens removed during processing
        special_pattern = r'\b[A-Z]{3}[\s\-]?[0-9A-Z]{2,6}[\s\-]?(?:AU)?\b'
        
        all_apir_codes = set()
        
        # Extract text from each page and find APIR codes
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            text = page.extract_text()
            
            # Find all matches using both patterns
            standard_codes = re.findall(standard_pattern, text)
            special_codes = re.findall(special_pattern, text)
            
            # Process special format codes to remove spaces/hyphens
            cleaned_special_codes = []
            for code in special_codes:
                cleaned_code = code.replace(" ", "").replace("-", "")
                if cleaned_code not in standard_codes:  # Avoid duplicates
                    cleaned_special_codes.append(cleaned_code)
            
            # Add all found codes to the set
            all_apir_codes.update(standard_codes)
            all_apir_codes.update(cleaned_special_codes)
        
        # Filter out any obvious false positives (common in PDFs)
        filtered_codes = [code for code in all_apir_codes if len(code) >= 5 and not code.isalpha()]
        
        return filtered_codes
    
    except Exception as e:
        st.error(f"Error extracting APIR codes from PDF: {str(e)}")
        return []

# Filter investments by APIR codes
def filter_investments_by_apir(df, apir_codes):
    if df is None or df.empty or not apir_codes:
        return df
    
    # Check if 'APIR Code' column exists
    if 'APIR Code' not in df.columns:
        st.warning("No 'APIR Code' column found in the data")
        return df
    
    # Filter the DataFrame to only include rows with APIR codes in the list
    filtered_df = df[df['APIR Code'].isin(apir_codes)]
    return filtered_df

# Check if data is available using dictionary access for better persistence
if st.session_state['combined_data'] is None or st.session_state['combined_data'].empty:
    st.warning("No data available for filtering. Please import data first on the 'Data Import' page.")
    st.stop()

st.markdown("""
This page allows you to filter your investment list using a HUB24 platform PDF document.
Upload a PDF containing the list of investment options available on the HUB24 platform.
The application will extract APIR codes from the PDF and filter your investment list to only
show options that are available on the HUB24 platform.
""")

st.header("Upload HUB24 PDF")

# PDF uploader for HUB24 investment options
hub24_pdf = st.file_uploader(
    "Upload HUB24 Investment Options PDF", 
    type="pdf",
    help="Upload a PDF containing the list of investment options available on the HUB24 platform."
)

# If HUB24 codes are already in session state, show info about previous upload
if len(st.session_state['hub24_apir_codes']) > 0 and hub24_pdf is None:
    st.success(f"Using previously uploaded HUB24 data with {len(st.session_state['hub24_apir_codes'])} APIR codes.")
    if 'hub24_pdf_name' in st.session_state and 'hub24_last_updated' in st.session_state:
        st.info(f"HUB24 data was last updated on: {st.session_state['hub24_last_updated']} from file: {st.session_state['hub24_pdf_name']}")
    
    # Still show the Filter button for convenience
    if st.button("Filter by HUB24 Options", use_container_width=True):
        with st.spinner("Filtering investments by HUB24 options..."):
            # Filter the investments by APIR codes
            hub24_filtered = filter_investments_by_apir(st.session_state['combined_data'], st.session_state['hub24_apir_codes'])
            st.session_state['hub24_filtered'] = hub24_filtered
            
            if hub24_filtered.empty:
                st.warning("No investments match the HUB24 platform options.")
            else:
                st.success(f"Found {len(hub24_filtered)} investments available on HUB24 platform.")

# Show interface for new PDF upload
if hub24_pdf is not None:
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if st.button("Extract APIR Codes", use_container_width=True):
            with st.spinner("Extracting APIR codes from PDF..."):
                # Extract APIR codes from the PDF
                apir_codes = extract_apir_codes_from_pdf(hub24_pdf)
                st.session_state['hub24_apir_codes'] = apir_codes
                
                # Store PDF file name and timestamp
                st.session_state['hub24_pdf_name'] = hub24_pdf.name
                st.session_state['hub24_last_updated'] = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
                
                if apir_codes:
                    st.success(f"Successfully extracted {len(apir_codes)} APIR codes from the PDF.")
                    
                    # Show sample of extracted codes
                    with st.expander("View sample of extracted APIR codes"):
                        st.write(apir_codes[:20])
                        
                    st.session_state.hub24_filtered = None  # Reset any previous filtering
                else:
                    st.warning("No APIR codes found in the PDF. Make sure the PDF contains valid APIR codes.")
    
    with col2:
        # Filter by HUB24 APIR codes
        if len(st.session_state.hub24_apir_codes) > 0:
            if st.button("Filter by HUB24 Options", use_container_width=True):
                with st.spinner("Filtering investments by HUB24 options..."):
                    # Filter the investments by APIR codes
                    hub24_filtered = filter_investments_by_apir(st.session_state.combined_data, st.session_state.hub24_apir_codes)
                    st.session_state.hub24_filtered = hub24_filtered
                    
                    if hub24_filtered.empty:
                        st.warning("No investments match the HUB24 platform options.")
                    else:
                        st.success(f"Found {len(hub24_filtered)} investments available on HUB24 platform.")

# Provide guidance to the user after filtering
st.markdown("---")
if st.session_state.hub24_filtered is not None:
    if st.session_state.hub24_filtered.empty:
        st.warning("No investments in your list are available on the HUB24 platform based on the uploaded PDF.")
    else:
        st.success(f"Your data has been filtered to show only the {len(st.session_state.hub24_filtered)} investments available on the HUB24 platform.")
        st.info("Go to the **Data Analysis** page to view the filtered results and performance metrics.")
        
        # Export functionality is still useful to keep
        if 'APIR Code' in st.session_state.hub24_filtered.columns:
            # Define the column order with specified columns first
            ordered_columns = [
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
            existing_columns = list(st.session_state.hub24_filtered.columns)
            
            # Keep only columns that exist in the actual dataframe
            ordered_columns = [col for col in ordered_columns if col in existing_columns]
            
            # Add any remaining columns that weren't specified in the order
            remaining_columns = [col for col in existing_columns if col not in ordered_columns]
            final_column_order = ordered_columns + remaining_columns
            
            # Reorder the dataframe columns for export
            reordered_df = st.session_state.hub24_filtered[final_column_order].copy()
            
            # Export HUB24 filtered investments
            csv_hub24 = reordered_df.to_csv(index=False)
            st.download_button(
                label="Download HUB24 Available Investments",
                data=csv_hub24,
                file_name="hub24_available_investments.csv",
                mime="text/csv",
            )