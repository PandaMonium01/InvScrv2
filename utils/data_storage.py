import streamlit as st
import pandas as pd
import pickle
import base64
import os
import io

# Function to convert dataframe to binary data for storage in session state
def dataframe_to_bytes(df):
    """Convert dataframe to bytes for storage in session state"""
    if df is None:
        return None
    return pickle.dumps(df)

# Function to convert binary data back to dataframe
def bytes_to_dataframe(bytes_data):
    """Convert bytes back to dataframe"""
    if bytes_data is None:
        return None
    return pickle.loads(bytes_data)

# Function to initialize or retrieve data from session state
def get_data(key, default=None):
    """Get data from session state with dictionary access for better persistence"""
    return st.session_state.get(key, default)

# Function to store data in session state
def store_data(key, value):
    """Store data in session state using dictionary access for better persistence"""
    st.session_state[key] = value
    
# Function to store dataframe in session state
def store_dataframe(key, df):
    """Store dataframe in session state, converting to bytes if needed"""
    if df is not None:
        # For small dataframes, store directly
        if len(df) < 1000:  # Arbitrary threshold for "small"
            st.session_state[key] = df
        else:
            # For larger dataframes, convert to bytes
            bytes_data = dataframe_to_bytes(df)
            st.session_state[key + "_bytes"] = bytes_data
            # Store a flag to indicate bytes storage is used
            st.session_state[key + "_is_bytes"] = True
    else:
        st.session_state[key] = None

# Function to get dataframe from session state
def get_dataframe(key, default=None):
    """Get dataframe from session state, handling bytes conversion if needed"""
    # Check if the dataframe was stored as bytes
    if st.session_state.get(key + "_is_bytes", False):
        bytes_data = st.session_state.get(key + "_bytes")
        return bytes_to_dataframe(bytes_data) if bytes_data else default
    
    # Otherwise retrieve normally
    return st.session_state.get(key, default)

# Function to clear all data in session state
def clear_all_data():
    """Clear all data in session state"""
    for key in list(st.session_state.keys()):
        del st.session_state[key]
        
# Function to store the timestamp of last update
def update_timestamp(key):
    """Update the timestamp for a specific data category"""
    st.session_state[key + "_last_updated"] = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
    
# Function to get the timestamp of last update
def get_timestamp(key):
    """Get the timestamp for a specific data category"""
    return st.session_state.get(key + "_last_updated", None)