from dash import Dash, dcc, html, Input, Output
import pandas as pd
import plotly.graph_objects as go
import pickle
import io
import base64

# Initialize the app
app = Dash(__name__, suppress_callback_exceptions=True)  # Add this line to suppress callback exceptions

# Load industry lists and covariance matrix from pickled files
with open("sorted_industries.pkl", "rb") as f:
    industry_lists = pickle.load(f)
sigma_sorted = pd.read_pickle("sorted_covariance.pkl")

# Define vmin and vmax for color scale limits
overall_mean = sigma_sorted.values.mean()
overall_std = sigma_sorted.values.std()
vmin = overall_mean - 2 * overall_std
vmax = overall_mean + 2 * overall_std

# Prepare options for the dropdown
dropdown_options = [{'label': industry, 'value': industry} for industry in industry_lists.keys()]

# Color scales options
color_scales = ['Viridis', 'Cividis', 'Blues', 'YlGnBu', 'RdBu']

# Store the color scale selections for each heatmap
color_scale_dict = {}

# Layout definition
app.layout = html.Div(
    [
        html.Div(
            [
                html.H1(
                    "Industry Covariance Heatmaps",
                    style={
                        'text-align': 'center',
                        'font-size': '2.5em',
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
                    multi=True,
                    placeholder="Select one or more industries",
                    style={
                        'width': '100%',
                        'margin-bottom': '20px',
                        'font-size': '1em'
                    }
                ),
                html.Label(
                    "Select Color Scale:",
                    style={
                        'font-size': '1.2em',
                        'margin-bottom': '10px',
                        'display': 'block'
                    }
                ),
                dcc.Dropdown(
                    id='color-dropdown',
                    options=[{'label': cs, 'value': cs} for cs in color_scales],
                    value='Viridis',  # Default color scale
                    style={
                        'width': '100%',
                        'margin-bottom': '20px',
                        'font-size': '1em'
                    }
                ),
                html.Div(
                    id='heatmap-container',
                    style={
                        'margin-top': '30px'
                    }
                ),  # Display heatmaps here
                html.Div(
                    id='download-container',
                    style={
                        'margin-top': '30px'
                    }
                )  # Display download buttons here
            ],
            style={
                'maxWidth': '80%',
                'margin': '0 auto',
                'padding': '20px',
                'box-shadow': '0 4px 8px rgba(0, 0, 0, 0.2)',
                'border-radius': '8px',
                'background-color': '#f9f9f9'
            }
        )
    ],
    style={
        'background-color': '#eef2f7',
        'padding': '20px 0'
    }
)


@app.callback(
    [Output('heatmap-container', 'children'),
     Output('download-container', 'children')],
    [Input('industry-dropdown', 'value'),
     Input('color-dropdown', 'value')]
)
def update_heatmap_and_color_scale(selected_industries, selected_color_scale):
    if not selected_industries:
        return html.Div("Select industries to view heatmaps."), []

    # Store the selected color scale for each industry
    for industry in selected_industries:
        color_scale_dict[industry] = selected_color_scale

    from plotly.subplots import make_subplots
    import plotly.graph_objects as go

    # Prepare subplots for multiple heatmaps (2 per row)
    num_industries = len(selected_industries)
    cols = 2
    rows = (num_industries + cols - 1) // cols
    fig = make_subplots(rows=rows, cols=cols, subplot_titles=selected_industries)

    heatmaps = []
    download_buttons = []

    # Generate the heatmaps and corresponding download buttons
    for idx, industry in enumerate(selected_industries):
        tickers = industry_lists.get(industry)
        if tickers:
            submatrix = sigma_sorted.loc[tickers, tickers]
            
            # Set color scale from the dict, default to 'Viridis'
            current_color_scale = color_scale_dict.get(industry, 'Viridis')
            
            heatmap = go.Heatmap(
                z=submatrix.values,
                x=tickers,
                y=tickers,
                colorscale=current_color_scale,
                zmin=vmin,
                zmax=vmax
            )
            row, col = divmod(idx, cols)
            fig.add_trace(heatmap, row=row + 1, col=col + 1)

            # Create a download button for this heatmap
            download_buttons.append(
                html.Div(
                    [
                        html.A(
                            'Download CSV',
                            id=f'download-button-{industry}',
                            href=f"/download/{industry}",
                            download=f'{industry}_covariance_matrix.csv',
                            style={
                                'display': 'block',
                                'margin-top': '10px',
                                'text-align': 'center',
                                'padding': '10px',
                                'background-color': '#007BFF',
                                'color': 'white',
                                'border-radius': '5px',
                                'text-decoration': 'none'
                            }
                        )
                    ],
                    style={
                        'display': 'flex',
                        'flex-direction': 'column',
                        'align-items': 'center',
                        'margin-top': '10px',
                    }
                )
            )
    
    # Update layout and return the graph along with download buttons
    fig.update_layout(
        title="Industry Covariance Heatmaps",
        width=1000,
        height=500 * rows,
        showlegend=False,
        margin=dict(t=50, b=50, l=50, r=50),
    )
    heatmap_layout = dcc.Graph(figure=fig)

    return heatmap_layout, download_buttons


# Callback to generate CSV file for download
@app.server.route('/download/<industry>')
def download_csv(industry):
    # Generate CSV for the selected industry
    tickers = industry_lists.get(industry)
    if tickers:
        submatrix = sigma_sorted.loc[tickers, tickers]
        # Convert to CSV
        csv_string = submatrix.to_csv(index=True, header=True)

        # Create response with CSV content
        response = app.server.response_class(
            csv_string,
            mimetype='text/csv',
            content_disposition=f'attachment; filename={industry}_covariance_matrix.csv'
        )
        return response
    return "Industry not found"

# Run the app
if __name__ == "__main__":
    app.run_server(debug=True)
