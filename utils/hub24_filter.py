import re
import PyPDF2
import pandas as pd
import streamlit as st

def extract_apir_codes_from_pdf(pdf_file):
    """
    Extract APIR codes from a PDF file.
    
    Parameters:
    pdf_file (file): PDF file to extract APIR codes from
    
    Returns:
    list: List of APIR codes found in the PDF
    """
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

def filter_investments_by_apir(df, apir_codes):
    """
    Filter investments by APIR codes.
    
    Parameters:
    df (DataFrame): DataFrame containing investment data
    apir_codes (list): List of APIR codes to filter by
    
    Returns:
    DataFrame: Filtered DataFrame
    """
    if df is None or df.empty or not apir_codes:
        return df
    
    # Check if 'APIR Code' column exists
    if 'APIR Code' not in df.columns:
        st.warning("No 'APIR Code' column found in the data")
        return df
    
    # Filter the DataFrame to only include rows with APIR codes in the list
    filtered_df = df[df['APIR Code'].isin(apir_codes)]
    return filtered_df