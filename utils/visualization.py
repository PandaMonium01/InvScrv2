import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def create_asset_class_chart(asset_class_df):
    """
    Create a visualization for asset class averages.
    
    Parameters:
    asset_class_df (DataFrame): DataFrame with asset class averages
    
    Returns:
    Figure: Plotly figure object
    """
    if asset_class_df is None or asset_class_df.empty:
        return None
    
    try:
        # Reset index to get asset_class as a column
        df = asset_class_df.reset_index()
        
        # Select relevant columns for visualization
        metrics = ['return', 'risk', 'expense_ratio']
        metric_titles = {'return': 'Return', 'risk': 'Risk', 'expense_ratio': 'Expense Ratio'}
        
        # Create a subplot with multiple metrics
        fig = make_subplots(rows=1, cols=len(metrics), 
                           subplot_titles=[metric_titles[m] for m in metrics],
                           shared_yaxes=True)
        
        # Add a bar chart for each metric
        for i, metric in enumerate(metrics):
            fig.add_trace(
                go.Bar(
                    x=df['asset_class'],
                    y=df[metric],
                    name=metric_titles[metric],
                    text=df[metric].round(4),
                    textposition='auto',
                ),
                row=1, col=i+1
            )
        
        # Update layout
        fig.update_layout(
            title="Asset Class Performance Metrics",
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
    asset_class_averages (DataFrame): Asset class averages DataFrame
    filtered_selection (DataFrame): Filtered selection DataFrame
    
    Returns:
    Figure: Plotly figure object
    """
    if asset_class_averages is None or asset_class_averages.empty or filtered_selection is None or filtered_selection.empty:
        return None
    
    try:
        # Calculate averages for the filtered selection by asset class
        selection_averages = filtered_selection.groupby('asset_class').mean()
        
        # Find common asset classes between the two DataFrames
        common_asset_classes = set(asset_class_averages.index).intersection(set(selection_averages.index))
        
        if not common_asset_classes:
            # If no common asset classes, create a different visualization
            return create_selection_summary_chart(filtered_selection)
        
        # Filter to only include common asset classes
        overall_avg = asset_class_averages.loc[list(common_asset_classes)]
        selection_avg = selection_averages.loc[list(common_asset_classes)]
        
        # Select metrics for comparison
        metrics = ['return', 'risk', 'expense_ratio']
        
        # Create subplots
        fig = make_subplots(
            rows=len(common_asset_classes), 
            cols=1,
            subplot_titles=[f"{asset_class} Comparison" for asset_class in common_asset_classes],
            vertical_spacing=0.1
        )
        
        # Add traces for each asset class
        for i, asset_class in enumerate(common_asset_classes):
            for j, metric in enumerate(metrics):
                # Overall average
                fig.add_trace(
                    go.Bar(
                        x=[metric], 
                        y=[overall_avg.loc[asset_class, metric]],
                        name=f"Overall Avg",
                        marker_color='lightblue',
                        text=round(overall_avg.loc[asset_class, metric], 4),
                        textposition='auto',
                        legendgroup="Overall",
                        showlegend=True if i == 0 and j == 0 else False,
                    ),
                    row=i+1, col=1
                )
                
                # Selection average
                fig.add_trace(
                    go.Bar(
                        x=[metric], 
                        y=[selection_avg.loc[asset_class, metric]],
                        name=f"Selection",
                        marker_color='coral',
                        text=round(selection_avg.loc[asset_class, metric], 4),
                        textposition='auto',
                        legendgroup="Selection",
                        showlegend=True if i == 0 and j == 0 else False,
                    ),
                    row=i+1, col=1
                )
        
        # Update layout
        fig.update_layout(
            title="Comparison: Overall vs. Selected Investments",
            height=300 * len(common_asset_classes),
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
        # Group by asset class and count
        asset_class_counts = filtered_selection['asset_class'].value_counts().reset_index()
        asset_class_counts.columns = ['asset_class', 'count']
        
        # Create a pie chart of asset allocation
        fig = px.pie(
            asset_class_counts,
            values='count',
            names='asset_class',
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
        return None
    
    try:
        fig = px.scatter(
            df,
            x='risk',
            y='return',
            color='asset_class',
            size='expense_ratio',
            hover_name='investment_name',
            size_max=15,
            opacity=0.7,
            title='Risk-Return Analysis'
        )
        
        # Add a line representing the efficient frontier (simplified)
        min_risk = df['risk'].min()
        max_risk = df['risk'].max()
        risk_range = np.linspace(min_risk, max_risk, 100)
        # Simple model: return = a * sqrt(risk) + b
        a = (df['return'].max() - df['return'].min()) / (np.sqrt(max_risk) - np.sqrt(min_risk))
        b = df['return'].min() - a * np.sqrt(min_risk)
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
        
        # Update layout
        fig.update_layout(
            height=600,
            xaxis_title='Risk',
            yaxis_title='Return',
            margin=dict(l=50, r=50, t=80, b=50)
        )
        
        return fig
    
    except Exception as e:
        print(f"Error creating risk-return scatter: {str(e)}")
        return None
