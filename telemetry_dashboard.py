import dash
from dash import html, dcc, Output, Input
import plotly.graph_objs as go
#import plotly.graph_objects as go
import random

app = dash.Dash(__name__)

app.layout = html.Div([
    dcc.Graph(id='live-update-graph'),
    dcc.Interval(
        id='interval-component',
        interval=1*1000,  # Update every second
        n_intervals=0
    )
])

@app.callback(
    Output('live-update-graph', 'figure'),
    Input('interval-component', 'n_intervals')
)
def update_graph_live(n):
    # Replace with actual telemetry data fetching
    x_data = list(range(10))
    y_data = [random.randint(0, 10) for _ in range(10)]

    fig = go.Figure(
        data=[go.Scatter(x=x_data, y=y_data, mode='lines+markers')]
    )
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)