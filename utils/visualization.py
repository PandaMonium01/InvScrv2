import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def create_asset_class_chart(asset_class_df):
    """
    Create a visualization for asset class averages (by Morningstar Category).
    
    Parameters:
    asset_class_df (DataFrame): DataFrame with asset class averages
    
    Returns:
    Figure: Plotly figure object
    """
    if asset_class_df is None or asset_class_df.empty:
        return None
    
    try:
        if asset_class_df is None or asset_class_df.empty:
            # Return an empty figure if no data
            return go.Figure().update_layout(
                title="No data available for visualization",
                height=400,
                margin=dict(l=50, r=50, t=80, b=50)
            )
            
        # Reset index to get Morningstar Category as a column
        df = asset_class_df.reset_index()
        
        # Select only available metrics from the ones we're interested in
        all_metrics = [
            '3 Years Annualised (%)', 
            'Investment Management Fee(%)', 
            '3 Year Beta',
            '3 Year Standard Deviation', 
            '3 Year Sharpe Ratio'
        ]
        metrics = [m for m in all_metrics if m in df.columns]
        
        # If no metrics are available, return an empty figure
        if not metrics:
            return go.Figure().update_layout(
                title="No numeric data available for visualization",
                height=400,
                margin=dict(l=50, r=50, t=80, b=50)
            )
        
        metric_titles = {
            '3 Years Annualised (%)': 'Annualised Return (%)', 
            'Investment Management Fee(%)': 'Management Fee (%)',
            '3 Year Beta': 'Beta',
            '3 Year Standard Deviation': 'Standard Deviation',
            '3 Year Sharpe Ratio': 'Sharpe Ratio'
        }
        
        # Create a subplot with multiple metrics
        fig = make_subplots(rows=1, cols=len(metrics), 
                           subplot_titles=[metric_titles[m] for m in metrics],
                           shared_yaxes=True)
        
        # Add a bar chart for each metric
        for i, metric in enumerate(metrics):
            # Make sure data is numeric for plotting
            y_values = pd.to_numeric(df[metric], errors='coerce')
            
            # Format text values for display
            text_values = []
            for val in y_values:
                if pd.notna(val):
                    text_values.append(str(round(float(val), 4)))
                else:
                    text_values.append("")
            
            fig.add_trace(
                go.Bar(
                    x=df['Morningstar Category'],
                    y=y_values,
                    name=metric_titles[metric],
                    text=text_values,
                    textposition='auto',
                ),
                row=1, col=i+1
            )
        
        # Update layout
        fig.update_layout(
            title="Morningstar Category Performance Metrics",
            height=400,
            showlegend=False,
            margin=dict(l=50, r=50, t=80, b=50)
        )
        
        return fig
    
    except Exception as e:
        print(f"Error creating asset class chart: {str(e)}")
        return None

def create_selection_comparison_chart(asset_class_averages, filtered_selection):
    """
    Create a comparison chart between overall averages and filtered selection.
    
    Parameters:
    asset_class_averages (DataFrame): Morningstar Category averages DataFrame
    filtered_selection (DataFrame): Filtered selection DataFrame
    
    Returns:
    Figure: Plotly figure object
    """
    if asset_class_averages is None or asset_class_averages.empty or filtered_selection is None or filtered_selection.empty:
        return None
    
    try:
        # Calculate averages for the filtered selection by Morningstar Category
        selection_averages = filtered_selection.groupby('Morningstar Category').mean()
        
        # Find common Morningstar Categories between the two DataFrames
        common_categories = set(asset_class_averages.index).intersection(set(selection_averages.index))
        
        if not common_categories:
            # If no common categories, create a different visualization
            return create_selection_summary_chart(filtered_selection)
        
        # Filter to only include common categories
        overall_avg = asset_class_averages.loc[list(common_categories)]
        selection_avg = selection_averages.loc[list(common_categories)]
        
        # Select only available metrics from the ones we're interested in
        all_metrics = [
            '3 Years Annualised (%)', 
            'Investment Management Fee(%)', 
            '3 Year Beta',
            '3 Year Standard Deviation', 
            '3 Year Sharpe Ratio'
        ]
        # Find intersection of metrics available in both dataframes
        metrics = [m for m in all_metrics if m in overall_avg.columns and m in selection_avg.columns]
        
        metric_titles = {
            '3 Years Annualised (%)': 'Return (%)', 
            'Investment Management Fee(%)': 'Fee (%)',
            '3 Year Beta': 'Beta',
            '3 Year Standard Deviation': 'Std Dev',
            '3 Year Sharpe Ratio': 'Sharpe'
        }
        
        # Create subplots
        fig = make_subplots(
            rows=len(common_categories), 
            cols=1,
            subplot_titles=[f"{category} Comparison" for category in common_categories],
            vertical_spacing=0.1
        )
        
        # Add traces for each Morningstar Category
        for i, category in enumerate(common_categories):
            for j, metric in enumerate(metrics):
                # Ensure values are numeric
                try:
                    # Overall average - ensure it's a numeric value
                    overall_val = pd.to_numeric(overall_avg.loc[category, metric], errors='coerce')
                    if pd.notna(overall_val):  # Only plot if it's a valid number
                        # Format text value using Python's built-in round function
                        text_val = str(round(float(overall_val), 4)) if pd.notna(overall_val) else ""
                        
                        fig.add_trace(
                            go.Bar(
                                x=[metric_titles[metric]], 
                                y=[overall_val],
                                name=f"Overall Avg",
                                marker_color='lightblue',
                                text=text_val,
                                textposition='auto',
                                legendgroup="Overall",
                                showlegend=True if i == 0 and j == 0 else False,
                            ),
                            row=i+1, col=1
                        )
                    
                    # Selection average - ensure it's a numeric value
                    selection_val = pd.to_numeric(selection_avg.loc[category, metric], errors='coerce')
                    if pd.notna(selection_val):  # Only plot if it's a valid number
                        # Format text value using Python's built-in round function
                        text_val = str(round(float(selection_val), 4)) if pd.notna(selection_val) else ""
                        
                        fig.add_trace(
                            go.Bar(
                                x=[metric_titles[metric]], 
                                y=[selection_val],
                                name=f"Selection",
                                marker_color='coral',
                                text=text_val,
                                textposition='auto',
                                legendgroup="Selection",
                                showlegend=True if i == 0 and j == 0 else False,
                            ),
                            row=i+1, col=1
                        )
                except Exception as e:
                    # Skip this metric if it causes errors
                    print(f"Error plotting {metric} for {category}: {str(e)}")
        
        # Update layout
        fig.update_layout(
            title="Comparison: Overall vs. Selected Investments",
            height=300 * len(common_categories),
            barmode='group',
            bargap=0.15,
            bargroupgap=0.1,
            margin=dict(l=50, r=50, t=80, b=50)
        )
        
        return fig
    
    except Exception as e:
        print(f"Error creating selection comparison chart: {str(e)}")
        return None

def create_selection_summary_chart(filtered_selection):
    """
    Create a summary chart for the filtered selection.
    
    Parameters:
    filtered_selection (DataFrame): Filtered selection DataFrame
    
    Returns:
    Figure: Plotly figure object
    """
    if filtered_selection is None or filtered_selection.empty:
        return None
    
    try:
        # Group by Morningstar Category and count
        category_counts = filtered_selection['Morningstar Category'].value_counts().reset_index()
        category_counts.columns = ['Morningstar Category', 'count']
        
        # Create a pie chart of asset allocation
        fig = px.pie(
            category_counts,
            values='count',
            names='Morningstar Category',
            title='Asset Allocation in Selected Investments'
        )
        
        # Update layout
        fig.update_layout(
            height=500,
            margin=dict(l=50, r=50, t=80, b=50)
        )
        
        return fig
    
    except Exception as e:
        print(f"Error creating selection summary chart: {str(e)}")
        return None

def create_risk_return_scatter(df):
    """
    Create a risk-return scatter plot for investments.
    
    Parameters:
    df (DataFrame): DataFrame containing investment data
    
    Returns:
    Figure: Plotly figure object
    """
    if df is None or df.empty:
        # Return empty figure with a message
        return go.Figure().update_layout(
            title="No data available for Risk-Return plot",
            height=600,
            margin=dict(l=50, r=50, t=80, b=50)
        )
    
    try:
        # Check if required columns exist
        required_cols = ['3 Year Standard Deviation', '3 Years Annualised (%)', 
                         'Morningstar Category', 'Investment Management Fee(%)', 'Name']
        
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            # Return message about missing columns
            return go.Figure().update_layout(
                title=f"Missing required columns for Risk-Return plot: {', '.join(missing_cols)}",
                height=600,
                margin=dict(l=50, r=50, t=80, b=50)
            )
            
        # Convert to numeric and handle missing values
        df_clean = df.copy()
        for col in ['3 Year Standard Deviation', '3 Years Annualised (%)', 'Investment Management Fee(%)']:
            if col in df.columns:
                df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')
        
        # Drop rows where either risk or return is missing
        df_clean = df_clean.dropna(subset=['3 Year Standard Deviation', '3 Years Annualised (%)'])
        
        if df_clean.empty:
            # Return message if no valid data after cleaning
            return go.Figure().update_layout(
                title="No valid data points for Risk-Return plot after removing missing values",
                height=600,
                margin=dict(l=50, r=50, t=80, b=50)
            )
            
        # Create scatter plot
        fig = px.scatter(
            df_clean,
            x='3 Year Standard Deviation',
            y='3 Years Annualised (%)',
            color='Morningstar Category',
            size='Investment Management Fee(%)' if 'Investment Management Fee(%)' in df_clean.columns else None,
            hover_name='Name',
            size_max=15,
            opacity=0.7,
            title='Risk-Return Analysis'
        )
        
        # Try to add efficient frontier line if we have enough data points
        if len(df_clean) >= 3:
            try:
                min_risk = df_clean['3 Year Standard Deviation'].min()
                max_risk = df_clean['3 Year Standard Deviation'].max()
                
                if not pd.isna(min_risk) and not pd.isna(max_risk) and min_risk < max_risk:
                    risk_range = np.linspace(min_risk, max_risk, 100)
                    
                    min_return = df_clean['3 Years Annualised (%)'].min()
                    max_return = df_clean['3 Years Annualised (%)'].max()
                    
                    if not pd.isna(min_risk) and not pd.isna(max_risk) and not pd.isna(min_return) and not pd.isna(max_return):
                        # Simple model: return = a * sqrt(risk) + b
                        risk_sqrt_diff = (np.sqrt(max_risk) - np.sqrt(min_risk))
                        
                        if risk_sqrt_diff > 0:
                            a = (max_return - min_return) / risk_sqrt_diff
                            b = min_return - a * np.sqrt(min_risk)
                            efficient_return = a * np.sqrt(risk_range) + b
                            
                            fig.add_trace(
                                go.Scatter(
                                    x=risk_range,
                                    y=efficient_return,
                                    mode='lines',
                                    line=dict(color='rgba(0,0,0,0.3)', dash='dash'),
                                    name='Theoretical Efficient Frontier'
                                )
                            )
            except Exception as e:
                print(f"Error creating efficient frontier: {str(e)}")
                # Continue without the frontier line
        
        # Update layout
        fig.update_layout(
            height=600,
            xaxis_title='Standard Deviation (Risk)',
            yaxis_title='Annualized Return (%)',
            margin=dict(l=50, r=50, t=80, b=50)
        )
        
        return fig
    
    except Exception as e:
        print(f"Error creating risk-return scatter: {str(e)}")
        # Return empty figure with error message
        return go.Figure().update_layout(
            title=f"Error creating Risk-Return plot: {str(e)}",
            height=600,
            margin=dict(l=50, r=50, t=80, b=50)
        )
