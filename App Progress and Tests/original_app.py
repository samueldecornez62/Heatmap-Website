from dash import Dash, dcc, html, Input, Output
import pandas as pd
import plotly.graph_objects as go
from new_plotter import plot_industries_with_zoom  # Import your plotting function
import pickle

# Initialize the app
app = Dash(__name__)

## Import industry lists and covariance matrix from Jupyter notebook, via pickled files 
# from website_builder_1 import industry_lists, sigma_sorted
with open("sorted_industries.pkl", "rb") as f:
    industry_lists = pickle.load(f)
sigma_sorted = pd.read_pickle("sorted_covariance.pkl")

#Define vmin and vmax, plot ranges around mean as done previously in other project 
# Calculate overall mean and standard deviation
overall_mean = sigma_sorted.values.mean()
overall_std = sigma_sorted.values.std()

# Set vmin and vmax to -2 and +2 standard deviations
vmin = overall_mean - 2 * overall_std
vmax = overall_mean + 2 * overall_std



# Prepare options for the dropdown
dropdown_options = [{'label': industry, 'value': industry} for industry in industry_lists.keys()]

# # Define layout
# app.layout = html.Div([
#     html.H1("Industry Covariance Heatmaps", style={'text-align': 'center'}),
#     html.Label("Select Industries:"),
#     dcc.Dropdown(
#         id='industry-dropdown',
#         options=dropdown_options,
#         multi=True,  # Allow selecting multiple industries
#         style={'width': '50%'}
#     ),
#     html.Div(id='heatmap-container')  # This will display the plots
# ])

# ========================================================================================================================
# ========================================================================================================================
# ========================================================================================================================

#New layout definition
# Define layout
app.layout = html.Div(
    [
        html.Div(
            [
                html.H1(
                    "Industry Covariance Heatmaps",
                    style={
                        'text-align': 'center',
                        'font-size': '2.5em',  # Adjust font size for larger headings
                        'margin-bottom': '20px'
                    }
                ),
                html.Label(
                    "Select Industries:",
                    style={
                        'font-size': '1.2em',
                        'margin-bottom': '10px',
                        'display': 'block'
                    }
                ),
                dcc.Dropdown(
                    id='industry-dropdown',
                    options=dropdown_options,
                    multi=True,  # Allow selecting multiple industries
                    placeholder="Select one or more industries",
                    style={
                        'width': '100%',  # Full width for better responsiveness
                        'margin-bottom': '20px',
                        'font-size': '1em'
                    }
                ),
                html.Div(
                    id='heatmap-container',
                    style={
                        'margin-top': '30px'
                    }
                )  # This will display the plots
            ],
            style={
                'maxWidth': '80%',  # Constrain max width for better readability
                'margin': '0 auto',  # Center the content horizontally
                'padding': '20px',  # Add some padding for better appearance
                'box-shadow': '0 4px 8px rgba(0, 0, 0, 0.2)',  # Light shadow for a polished look
                'border-radius': '8px',  # Rounded corners
                'background-color': '#f9f9f9'  # Subtle background color
            }
        )
    ],
    style={
        'background-color': '#eef2f7',  # Light background for the entire page
        'padding': '20px 0'  # Add padding around the whole page
    }
)

# ========================================================================================================================
# ========================================================================================================================
# ========================================================================================================================


@app.callback(
    Output('heatmap-container', 'children'),
    [Input('industry-dropdown', 'value')]
)
def update_heatmap(selected_industries):
    if not selected_industries:
        return html.Div("Select industries to view heatmaps.")
    
    # Generate the heatmap using the plot_industries_with_zoom function
    from plotly.subplots import make_subplots
    import plotly.graph_objects as go

    # Prepare subplots for multiple heatmaps
    num_industries = len(selected_industries)
    cols = min(2, num_industries)
    rows = (num_industries + cols - 1) // cols
    fig = make_subplots(rows=rows, cols=cols, subplot_titles=selected_industries)

    for idx, industry in enumerate(selected_industries):
        tickers = industry_lists.get(industry)
        if tickers:
            submatrix = sigma_sorted.loc[tickers, tickers]
            heatmap = go.Heatmap(
                z=submatrix.values,
                x=tickers,
                y=tickers,
                colorscale='Viridis',
                zmin=vmin,
                zmax=vmax
            )
            row, col = divmod(idx, cols)
            fig.add_trace(heatmap, row=row + 1, col=col + 1)

    # Update layout and return
    fig.update_layout(
        title="Industry Covariance Heatmaps",
        width=1000,
        height=500 * rows,
        showlegend=False,
        margin=dict(t=50, b=50, l=50, r=50),
    )
    return dcc.Graph(figure=fig)

# Run the app
if __name__ == "__main__":
    app.run_server(debug=True)