import plotly.graph_objects as go
from plotly.subplots import make_subplots

def plot_industries_with_zoom(industries, industry_tickers, covariance_matrix, vmin, vmax):
    """
    Plots zoomable heatmaps for a flexible number of subindustries.

    Parameters:
    - industries: List of industry names to plot
    - industry_tickers: Dictionary with industries as keys and ticker lists as values
    - covariance_matrix: The full covariance matrix (DataFrame)
    - vmin: Minimum value for heatmap color scale
    - vmax: Maximum value for heatmap color scale
    """
    num_industries = len(industries)
    
    # Determine subplot grid layout dynamically based on number of industries
    cols = min(2, num_industries)  # Limit to 3 columns per row
    rows = (num_industries + cols - 1) // cols  # Calculate number of rows needed

    # Create subplot grid dynamically
    fig = make_subplots(rows=rows, cols=cols, subplot_titles=industries)

    for idx, industry_name in enumerate(industries):
        tickers = industry_tickers.get(industry_name)
        if tickers:
            industry_cov_matrix = covariance_matrix.loc[tickers, tickers]

            heatmap = go.Heatmap(
                z=industry_cov_matrix.values,
                x=tickers,
                y=tickers,
                colorscale='Viridis',
                zmin=vmin,
                zmax=vmax,
                colorbar=dict(title='Covariance')  # Optional: Add colorbar title
            )

            row = idx // cols + 1
            col = idx % cols + 1
            fig.add_trace(heatmap, row=row, col=col)

    # Adjust layout for square shape and smaller plot size
    fig.update_layout(
        title="Subindustry Covariance Heatmaps",
        width=1000, height=500 * rows,
        dragmode='zoom',
        showlegend=False,
        autosize=False,  # Disable automatic resizing
        margin=dict(t=50, b=50, l=50, r=50),  # Set margins to avoid clipping
        updatemenus=[dict(
            type="buttons",
            direction="left",
            buttons=[dict(
                args=[{'xaxis.autorange': True, 'yaxis.autorange': True}],
                label="Reset Zoom",
                method="relayout"
            )],
            pad={"r": 10, "t": 10},
            showactive=False,
            x=0.15,
            xanchor="left",
            y=1.15,
            yanchor="top"
        )]
    )

    fig.show()

    
    
# # Example usage
# industries_to_plot = ["Energy", "Manufacturing", "Technology"]
# plot_industries_with_zoom(
#     industries=industries_to_plot,
#     industry_tickers=industry_lists,  # Use industry tickers dictionary
#     covariance_matrix=sigma_sorted,  # Covariance matrix sorted by tickers
#     vmin=vmin,
#     vmax=vmax
# )
