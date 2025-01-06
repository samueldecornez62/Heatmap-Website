from dash import Dash, dcc, html, Input, Output, State, MATCH
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pickle

# Initialize the app
app = Dash(__name__)

# Import data
with open("sorted_industries.pkl", "rb") as f:
    industry_lists = pickle.load(f)
sigma_sorted = pd.read_pickle("sorted_covariance.pkl")

# Calculate vmin and vmax
overall_mean = sigma_sorted.values.mean()
overall_std = sigma_sorted.values.std()
vmin = overall_mean - 2 * overall_std
vmax = overall_mean + 2 * overall_std

# Prepare dropdown options
dropdown_options = [{'label': industry, 'value': industry} for industry in industry_lists.keys()]

# Define layout
app.layout = html.Div(
    [
        html.Div(
            [
                html.H1("Industry Covariance Heatmaps", style={'text-align': 'center'}),
                html.Label("Select Industries:"),
                dcc.Dropdown(
                    id='industry-dropdown',
                    options=dropdown_options,
                    multi=True,
                    placeholder="Select one or more industries",
                    style={'width': '100%', 'margin-bottom': '20px'}
                ),
                html.Div(id='heatmap-container', style={'margin-top': '30px'})
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
    style={'background-color': '#eef2f7', 'padding': '20px 0'}
)

@app.callback(
    Output('heatmap-container', 'children'),
    [Input('industry-dropdown', 'value')]
)
def update_heatmaps(selected_industries):
    if not selected_industries:
        return html.Div("Select industries to view heatmaps.")
    
    heatmaps = []
    for industry in selected_industries:
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
            fig = go.Figure(data=[heatmap])
            fig.update_layout(
                title=f"Covariance Heatmap: {industry}",
                width=500,
                height=500,
                margin=dict(t=50, b=50, l=50, r=50)
            )

            # Add heatmap and corresponding checkbox
            heatmaps.append(
                html.Div(
                    [
                        dcc.Graph(id={'type': 'heatmap', 'index': industry}, figure=fig),
                        dcc.Checklist(
                            options=[{'label': 'Show Covariance Values', 'value': 'show_numbers'}],
                            id={'type': 'checkbox', 'index': industry},
                            inline=True,
                            style={'margin-top': '10px'}
                        )
                    ]
                )
            )

    return heatmaps

@app.callback(
    Output({'type': 'heatmap', 'index': State({'type': 'checkbox', 'index': MATCH}, 'index')}, 'figure'),
    [Input({'type': 'checkbox', 'index': MATCH}, 'value')],
    [State({'type': 'heatmap', 'index': MATCH}, 'figure')],
)
def toggle_annotations(checkbox_values, current_figure):
    fig = go.Figure(current_figure)
    if 'show_numbers' in checkbox_values:
        # Add annotations
        z_values = fig.data[0].z
        x_labels = fig.data[0].x
        y_labels = fig.data[0].y
        annotations = [
            dict(
                x=x_labels[j],
                y=y_labels[i],
                text=str(round(z_values[i][j], 2)),
                showarrow=False,
                font=dict(color="black")
            )
            for i in range(len(y_labels))
            for j in range(len(x_labels))
        ]
        fig.update_layout(annotations=annotations)
    else:
        fig.update_layout(annotations=[])

    return fig

# Run the app
if __name__ == "__main__":
    app.run_server(debug=True)
