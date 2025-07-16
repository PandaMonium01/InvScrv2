import streamlit as st
import pandas as pd
import numpy as np
from utils.visualization import (
    create_asset_class_chart, 
    create_risk_return_scatter,
    create_fee_distribution_chart,
    create_performance_risk_chart,
    create_category_comparison_chart,
    create_portfolio_comparison_chart,
    create_multi_metric_comparison_chart
)

# Set page configuration
st.set_page_config(
    page_title="Data Analysis - Investment Selection Tool",
    page_icon="📊",
    layout="wide",
)

st.title("Data Analysis")

# Check if data is available
if st.session_state.combined_data is None or st.session_state.combined_data.empty:
    st.warning("No data available for analysis. Please import data first on the 'Data Import' page.")
    st.stop()

# Determine which data to display based on filter status
display_data = None
if st.session_state.filtered_selection is not None and not st.session_state.filtered_selection.empty:
    display_data = st.session_state.filtered_selection
    data_status = "Formula Filtered Data"
elif st.session_state.hub24_filtered is not None and not st.session_state.hub24_filtered.empty:
    display_data = st.session_state.hub24_filtered
    data_status = "HUB24 Filtered Data"
else:
    display_data = st.session_state.combined_data
    data_status = "Combined Data (No Filters Applied)"

# Create tabs for different views
tabs = st.tabs(["Current Data View", "Category Averages", "Risk-Return Plot"])

with tabs[0]:
    st.header(data_status)
    
    # Add filter status information
    if st.session_state.hub24_filtered is not None and not st.session_state.hub24_filtered.empty:
        st.info(f"HUB24 Filter: {len(st.session_state.hub24_filtered)} investments available on HUB24 platform")
    
    if st.session_state.filtered_selection is not None and not st.session_state.filtered_selection.empty:
        st.info(f"Formula Filter: {len(st.session_state.filtered_selection)} investments matched your formula criteria")
    
    # Initialize recommended_portfolio in session state if it doesn't exist
    if 'recommended_portfolio' not in st.session_state:
        st.session_state.recommended_portfolio = {}
        
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
    
    # Ensure the dataframe displays the specified columns first
    if display_data is not None and not display_data.empty:
        st.markdown("### Investment Data Table")
        st.write("Check the boxes in the 'Select' column to add funds to your recommended portfolio.")
        
        # Create a comments field
        if 'portfolio_comments' not in st.session_state:
            st.session_state.portfolio_comments = {}
        
        # Create selection controls
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            # Create a form for comments
            comment_input = st.text_input(
                "Comments for selected fund(s)", 
                help="Enter any comments for the fund(s) you are adding to the portfolio"
            )
        
        with col2:
            # Add button to unselect all options
            if st.button("Unselect All", use_container_width=True):
                # Clear the recommended portfolio
                st.session_state.recommended_portfolio = {}
                st.rerun()  # Rerun the app to refresh the table
                
        with col3:
            # Show number of currently selected items
            num_selected = len(st.session_state.recommended_portfolio)
            st.markdown(f"**Selected: {num_selected}**")
        
        # Create a dataframe with a selection column
        # First, create a copy of the display data
        selection_df = display_data.copy()
        
        # Add a new "Select" column at the beginning
        # Initialize with whether the fund is already in the portfolio
        selection_df.insert(
            0, 
            "Select", 
            selection_df['APIR Code'].apply(lambda x: x in st.session_state.recommended_portfolio)
        )
        
        # Calculate category averages from the CURRENT filtered dataset, not the original full dataset
        current_data_averages = None
        if display_data is not None and not display_data.empty:
            # Calculate averages from the currently displayed data
            avg_fields = ['3 Year Beta', '3 Year Standard Deviation', '3 Year Sharpe Ratio']
            existing_fields = [f for f in avg_fields if f in display_data.columns]
            if existing_fields and 'Morningstar Category' in display_data.columns:
                subset_for_avg = display_data[['Morningstar Category'] + existing_fields].copy()
                current_data_averages = subset_for_avg.groupby('Morningstar Category').mean(numeric_only=True)
                


        # Add a new column that calculates category avg 3 Year Beta minus fund's 3 Year Beta
        if '3 Year Beta' in selection_df.columns and 'Morningstar Category' in selection_df.columns:
            # Use current data averages instead of original full dataset averages
            if current_data_averages is not None and '3 Year Beta' in current_data_averages.columns:
                # Create a dictionary mapping category to average beta
                category_betas = current_data_averages['3 Year Beta'].to_dict()
                
                # Function to calculate the difference
                def calc_beta_diff(row):
                    # If fund doesn't have 3 Year Beta data, return None (will show as N/A)
                    if pd.isna(row['3 Year Beta']):
                        return None
                    
                    category = row['Morningstar Category']
                    if category in category_betas and not pd.isna(category_betas[category]):
                        category_avg = category_betas[category]
                        fund_beta = row['3 Year Beta']
                        
                        return category_avg - fund_beta
                    return None
                
                # Apply the function to create the new column
                selection_df['Category Avg Beta - Fund Beta'] = selection_df.apply(calc_beta_diff, axis=1)
            else:
                # If asset class averages aren't available, add empty column
                selection_df['Category Avg Beta - Fund Beta'] = None
        
        # Add a new column that calculates fund's 3 Year Sharpe Ratio minus category avg 3 Year Sharpe Ratio
        if '3 Year Sharpe Ratio' in selection_df.columns and 'Morningstar Category' in selection_df.columns:
            # Use current data averages instead of original full dataset averages
            if current_data_averages is not None and '3 Year Sharpe Ratio' in current_data_averages.columns:
                # Create a dictionary mapping category to average sharpe ratio
                category_sharpes = current_data_averages['3 Year Sharpe Ratio'].to_dict()
                
                # Function to calculate the difference
                def calc_sharpe_diff(row):
                    # If fund doesn't have 3 Year Sharpe Ratio data, return None (will show as N/A)
                    if pd.isna(row['3 Year Sharpe Ratio']):
                        return None
                    
                    category = row['Morningstar Category']
                    if category in category_sharpes and not pd.isna(category_sharpes[category]):
                        category_avg = category_sharpes[category]
                        return row['3 Year Sharpe Ratio'] - category_avg
                    return None
                
                # Apply the function to create the new column
                selection_df['Fund Sharpe - Category Avg Sharpe'] = selection_df.apply(calc_sharpe_diff, axis=1)
            else:
                # If asset class averages aren't available, add empty column
                selection_df['Fund Sharpe - Category Avg Sharpe'] = None
        
        # Add a new column that calculates fund's 3 Year Standard Deviation minus category avg 3 Year Standard Deviation
        if '3 Year Standard Deviation' in selection_df.columns and 'Morningstar Category' in selection_df.columns:
            # Use current data averages instead of original full dataset averages
            if current_data_averages is not None and '3 Year Standard Deviation' in current_data_averages.columns:
                # Create a dictionary mapping category to average standard deviation
                category_stdevs = current_data_averages['3 Year Standard Deviation'].to_dict()
                
                # Function to calculate the difference
                def calc_stdev_diff(row):
                    # If fund doesn't have 3 Year Standard Deviation data, return None (will show as N/A)
                    if pd.isna(row['3 Year Standard Deviation']):
                        return None
                    
                    category = row['Morningstar Category']
                    if category in category_stdevs and not pd.isna(category_stdevs[category]):
                        category_avg = category_stdevs[category]
                        return row['3 Year Standard Deviation'] - category_avg
                    return None
                
                # Apply the function to create the new column
                selection_df['Fund StdDev - Category Avg StdDev'] = selection_df.apply(calc_stdev_diff, axis=1)
            else:
                # If asset class averages aren't available, add empty column
                selection_df['Fund StdDev - Category Avg StdDev'] = None

        # Add a new column with the composite formula: ((Fund StdDev - Category Avg StdDev) / 10) + (Fund Sharpe - Category Avg Sharpe) + (Category Avg Beta - Fund Beta)
        if all(col in selection_df.columns for col in ['Fund StdDev - Category Avg StdDev', 'Fund Sharpe - Category Avg Sharpe', 'Category Avg Beta - Fund Beta']):
            def calc_composite_score(row):
                # Check if all required values are present (not None/NaN)
                stdev_diff = row['Fund StdDev - Category Avg StdDev']
                sharpe_diff = row['Fund Sharpe - Category Avg Sharpe']
                beta_diff = row['Category Avg Beta - Fund Beta']
                
                if pd.isna(stdev_diff) or pd.isna(sharpe_diff) or pd.isna(beta_diff):
                    return None
                
                # Apply the formula: ((Fund StdDev - Category Avg StdDev) / 10) + (Fund Sharpe - Category Avg Sharpe) + (Category Avg Beta - Fund Beta)
                composite_score = (stdev_diff / 10) + sharpe_diff + beta_diff
                return composite_score
            
            # Apply the function to create the new column
            selection_df['Composite Score'] = selection_df.apply(calc_composite_score, axis=1)
        else:
            # If required columns aren't available, add empty column
            selection_df['Composite Score'] = None
        
        # Define the column order with "Select" first and the new calculation last
        ordered_columns = [
            'Select',
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
        existing_columns = list(selection_df.columns)
        
        # Keep only columns that exist in the actual dataframe
        ordered_columns = [col for col in ordered_columns if col in existing_columns]
        
        # Add any remaining columns that weren't specified in the order (except the special columns)
        special_columns = ['Select', 'Category Avg Beta - Fund Beta', 'Fund Sharpe - Category Avg Sharpe', 'Fund StdDev - Category Avg StdDev', 'Composite Score']
        remaining_columns = [col for col in existing_columns 
                             if col not in ordered_columns 
                             and col not in special_columns]
        
        # Create the final column order with the calculated columns at the end
        final_column_order = ordered_columns + remaining_columns
        
        # Add the calculated columns at the very end if they exist
        if 'Category Avg Beta - Fund Beta' in existing_columns:
            final_column_order.append('Category Avg Beta - Fund Beta')
        if 'Fund Sharpe - Category Avg Sharpe' in existing_columns:
            final_column_order.append('Fund Sharpe - Category Avg Sharpe')
        if 'Fund StdDev - Category Avg StdDev' in existing_columns:
            final_column_order.append('Fund StdDev - Category Avg StdDev')
        if 'Composite Score' in existing_columns:
            final_column_order.append('Composite Score')
        
        # Reorder the dataframe columns
        reordered_df = selection_df[final_column_order].copy()
        
        # Group by Morningstar Category
        if 'Morningstar Category' in reordered_df.columns:
            # Get unique categories
            categories = reordered_df['Morningstar Category'].dropna().unique()
            
            # Create tabs for "All" and individual categories
            category_tabs = ["All Categories"] + list(categories)
            tabs = st.tabs(category_tabs)
            
            # All categories tab
            with tabs[0]:
                edited_df = st.data_editor(
                    reordered_df,
                    column_config={
                        "Select": st.column_config.CheckboxColumn(
                            "Select",
                            help="Check to add to portfolio",
                            default=False,
                        )
                    },
                    use_container_width=True,
                    hide_index=True,
                )
            
            # Individual category tabs
            for i, category in enumerate(categories):
                with tabs[i+1]:
                    # Filter dataframe for this category
                    category_df = reordered_df[reordered_df['Morningstar Category'] == category].copy()
                    
                    # Only show if there's data for this category
                    if not category_df.empty:
                        st.markdown(f"### {category}")
                        st.write(f"{len(category_df)} investments in this category")
                        
                        # Display editable dataframe for this category
                        cat_edited_df = st.data_editor(
                            category_df,
                            column_config={
                                "Select": st.column_config.CheckboxColumn(
                                    "Select",
                                    help="Check to add to portfolio",
                                    default=False,
                                )
                            },
                            use_container_width=True,
                            hide_index=True,
                        )
                        
                        # Merge edited values back to the main edited_df
                        for idx, row in cat_edited_df.iterrows():
                            if idx in edited_df.index:
                                edited_df.loc[idx, 'Select'] = row['Select']
                    else:
                        st.info(f"No investments in the {category} category")
        else:
            # If no category column, just display the regular table
            edited_df = st.data_editor(
                reordered_df,
                column_config={
                    "Select": st.column_config.CheckboxColumn(
                        "Select",
                        help="Check to add to portfolio",
                        default=False,
                    )
                },
                use_container_width=True,
                hide_index=True,
            )
        
        # Process the edited dataframe
        changed_rows = []
        
        # Get newly selected funds
        for idx, row in edited_df.iterrows():
            fund_name = row['Name']
            fund_apir = row['APIR Code']
            fund_category = row['Morningstar Category'] if 'Morningstar Category' in row else "Unknown"
            is_selected = row['Select']
            is_in_portfolio = fund_apir in st.session_state.recommended_portfolio
            
            # Check if selection status changed
            if is_selected and not is_in_portfolio:
                # Add to portfolio
                add_to_portfolio(fund_name, fund_apir, fund_category, comment_input)
                changed_rows.append(fund_name)
            elif not is_selected and is_in_portfolio:
                # Remove from portfolio
                del st.session_state.recommended_portfolio[fund_apir]
                changed_rows.append(fund_name)
        
        # Show portfolio status
        if st.session_state.recommended_portfolio:
            num_selected = len(st.session_state.recommended_portfolio)
            st.success(f"You have {num_selected} funds in your recommended portfolio.")
            
            if changed_rows:
                st.info(f"Updated portfolio status for: {', '.join(changed_rows[:3])}{'...' if len(changed_rows) > 3 else ''}")
                
            st.info("Go to the **Recommended Portfolio** page to view and manage your selections.")
        
        # Export data
        csv_data = reordered_df.to_csv(index=False)
        st.download_button(
            label=f"Download {data_status}",
            data=csv_data,
            file_name="investment_data.csv",
            mime="text/csv",
        )
        
        # Additional Analysis Section
        st.header("Additional Analysis")
        
        # Category averages table for all numerical columns
        st.subheader("Category Averages - All Numerical Columns")
        if not reordered_df.empty and 'Morningstar Category' in reordered_df.columns:
            # Get all numerical columns from the data
            numerical_cols = reordered_df.select_dtypes(include=[np.number]).columns.tolist()
            
            # Remove non-investment data columns if they exist
            exclude_cols = ['Select']  # Add any other columns to exclude
            numerical_cols = [col for col in numerical_cols if col not in exclude_cols]
            
            if numerical_cols:
                # Calculate averages by category
                category_averages = reordered_df.groupby('Morningstar Category')[numerical_cols].mean()
                
                # Round to 2 decimal places for better display
                category_averages = category_averages.round(2)
                
                # Display the table
                st.dataframe(category_averages, use_container_width=True)
                
                # Add count of investments per category
                st.subheader("Investment Count by Category")
                category_counts = reordered_df['Morningstar Category'].value_counts().sort_index()
                count_df = pd.DataFrame({
                    'Category': category_counts.index,
                    'Number of Investments': category_counts.values
                })
                st.dataframe(count_df, use_container_width=True)
                
                # Download category averages
                category_csv = category_averages.to_csv()
                st.download_button(
                    label="Download Category Averages",
                    data=category_csv,
                    file_name="category_averages_all_columns.csv",
                    mime="text/csv",
                )
            else:
                st.info("No numerical columns found in the data for category analysis")
        else:
            st.info("No category data available or data is empty")
        
        # Visualization section
        st.subheader("Category Comparison Charts")
        
        if not reordered_df.empty and numerical_cols and 'Morningstar Category' in reordered_df.columns:
            # Create visualizations for key metrics
            key_metrics = ['3 Years Annualised (%)', 'Investment Management Fee(%)', 
                          '3 Year Beta', '3 Year Standard Deviation', '3 Year Sharpe Ratio']
            
            # Filter to available key metrics
            available_key_metrics = [col for col in key_metrics if col in numerical_cols]
            
            if available_key_metrics:
                # Create multiple bar charts in a grid layout
                cols = st.columns(2)
                
                for i, metric in enumerate(available_key_metrics):
                    with cols[i % 2]:
                        # Create individual bar chart for each metric
                        fig_metric = create_category_comparison_chart(reordered_df, [metric])
                        st.plotly_chart(fig_metric, use_container_width=True)
                
                # Create a comprehensive comparison chart with multiple metrics
                if len(available_key_metrics) > 1:
                    st.subheader("Multi-Metric Category Comparison")
                    fig_multi = create_multi_metric_comparison_chart(category_averages, available_key_metrics)
                    st.plotly_chart(fig_multi, use_container_width=True)
            
            # Selected vs All comparison
            if st.session_state.recommended_portfolio and len(st.session_state.recommended_portfolio) > 0:
                st.subheader("Selected Portfolio vs All Funds")
                selected_apirs = list(st.session_state.recommended_portfolio.keys())
                selected_funds = reordered_df[reordered_df['APIR Code'].isin(selected_apirs)]
                
                if not selected_funds.empty and available_key_metrics:
                    fig_comparison = create_portfolio_comparison_chart(reordered_df, selected_funds, available_key_metrics)
                    st.plotly_chart(fig_comparison, use_container_width=True)
        else:
            st.info("No numerical data or category data available for visualization")
    else:
        st.info("No data available to display")

with tabs[1]:
    st.header("Category Averages")
    
    # Use filtered data averages instead of full dataset averages
    if current_data_averages is not None:
        st.info(f"Category averages calculated from {data_status.lower()} ({len(display_data)} funds)")
        st.dataframe(current_data_averages, use_container_width=True)
        
        # Create visualization for Morningstar Category averages
        fig = create_asset_class_chart(current_data_averages)
        st.plotly_chart(fig, use_container_width=True)
        
        # Export category averages
        csv_averages = current_data_averages.to_csv()
        st.download_button(
            label="Download Category Averages (Filtered Data)",
            data=csv_averages,
            file_name="category_averages_filtered.csv",
            mime="text/csv",
        )
    else:
        st.info("No category averages data available")
            
with tabs[2]:
    st.header("Risk-Return Analysis")
    
    # Create risk-return scatter plot using the same data source as the main view
    if display_data is not None and not display_data.empty:
        st.subheader(f"Risk-Return Analysis: {data_status}")
        risk_return_fig = create_risk_return_scatter(display_data)
        st.plotly_chart(risk_return_fig, use_container_width=True)
    else:
        st.info("No data available for risk-return analysis")