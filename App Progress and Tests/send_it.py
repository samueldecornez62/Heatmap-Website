from dash import Dash, dcc, html, Input, Output
import pandas as pd
import plotly.graph_objects as go
import pickle
import io
import base64
import zipfile

# Initialize the app
app = Dash(__name__)

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

                # New section for downloading CSVs
                html.Div(
                    [
                        html.H3("Download Selected Industries as CSV"),
                        html.Label(
                            "Select Industries for CSV download:",
                            style={
                                'font-size': '1.2em',
                                'margin-bottom': '10px',
                                'display': 'block'
                            }
                        ),
                        dcc.Checklist(
                            id='industry-csv-dropdown',
                            options=dropdown_options,
                            value=[],
                            labelStyle={'display': 'block'},
                            style={
                                'font-size': '1em',
                                'margin-bottom': '20px'
                            }
                        ),
                        html.A(
                            "Download CSVs",
                            id="download-csv-button",
                            download="selected_industries.zip",
                            href="",
                            target="_blank",
                            style={'display': 'none', 'margin-top': '20px', 'text-align': 'center'}
                        )
                    ],
                    style={
                        'maxWidth': '80%',
                        'margin': '0 auto',
                        'padding': '20px',
                        'box-shadow': '0 4px 8px rgba(0, 0, 0, 0.2)',
                        'border-radius': '8px',
                        'background-color': '#f9f9f9',
                        'margin-top': '50px'
                    }
                )

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
    Output('heatmap-container', 'children'),
    [Input('industry-dropdown', 'value'),
     Input('color-dropdown', 'value')]
)
def update_heatmap_and_color_scale(selected_industries, selected_color_scale):
    if not selected_industries:
        return html.Div("Select industries to view heatmaps.")
    
    # Store the selected color scale for each industry
    for industry in selected_industries:
        color_scale_dict[industry] = selected_color_scale

    from plotly.subplots import make_subplots
    import plotly.graph_objects as go

    heatmap_elements = []

    # Prepare subplots for multiple heatmaps (2 per row)
    cols = 2
    num_industries = len(selected_industries)
    rows = (num_industries + cols - 1) // cols  # Calculate number of rows
    fig = make_subplots(rows=rows, cols=cols, subplot_titles=selected_industries)

    # Generate the heatmaps
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

            # Add the download button for the current heatmap
            csv_data = create_csv(tickers, submatrix)
            encoded_csv = base64.b64encode(csv_data.encode()).decode()

            heatmap_elements.append(
                html.Div([
                    dcc.Graph(figure=fig),
                    html.A(
                        "Download CSV",
                        id=f"download-{industry}",
                        href=f"data:text/csv;base64,{encoded_csv}",
                        download=f"{industry}_covariance_matrix.csv",
                        target="_blank",
                        style={'display': 'block', 'margin-top': '10px', 'text-align': 'center'}
                    )
                ])
            )
    
    return heatmap_elements


@app.callback(
    Output('download-csv-button', 'href'),
    [Input('industry-csv-dropdown', 'value')]
)
def generate_zip(selected_industries):
    if not selected_industries:
        return ""
    
    # Create a zip file in memory
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for industry in selected_industries:
            tickers = industry_lists.get(industry)
            if tickers:
                submatrix = sigma_sorted.loc[tickers, tickers]
                csv_data = create_csv(tickers, submatrix)
                zip_file.writestr(f"{industry}_covariance_matrix.csv", csv_data)

    # Create a base64 encoded string of the zip file
    zip_buffer.seek(0)
    zip_base64 = base64.b64encode(zip_buffer.read()).decode()

    return f"data:application/zip;base64,{zip_base64}"


def create_csv(tickers, submatrix):
    """Create CSV file with tickers and covariance matrix data"""
    csv_data = "," + ",".join(tickers) + "\n"  # First row with empty cell
    for i, ticker in enumerate(tickers):
        row = [ticker] + submatrix.iloc[i].tolist()
        csv_data += ",".join(map(str, row)) + "\n"
    return csv_data


# Run the app
if __name__ == "__main__":
    app.run_server(debug=True)
