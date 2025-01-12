import dash
from dash import html, dcc, Input, Output
import plotly.graph_objs as go
import random
from datetime import datetime

# Initialize Dash app
app = dash.Dash(__name__)

# Simulated telemetry state
telemetry_state = {
    "position": (0, 0),
    "heading": 90,  # Degrees
    "battery": 75,  # Percentage
    "proximity": 50,  # Distance in cm
    "path_trace": [(0, 0)],  # List of past positions
}

# Layout of the dashboard
app.layout = html.Div(
    children=[
        html.H1("Mars Rover Telemetry Dashboard", style={"text-align": "center"}),
        
        # Row 1: Key metrics
        html.Div(
            children=[
                html.Div(
                    children=[
                        html.H3("Position"),
                        html.P(id="position-display"),
                    ],
                    style={"width": "20%", "display": "inline-block"},
                ),
                html.Div(
                    children=[
                        html.H3("Heading"),
                        html.P(id="heading-display"),
                    ],
                    style={"width": "20%", "display": "inline-block"},
                ),
                html.Div(
                    children=[
                        html.H3("Battery"),
                        dcc.Graph(id="battery-bar"),
                    ],
                    style={"width": "20%", "display": "inline-block"},
                ),
                html.Div(
                    children=[
                        html.H3("Proximity"),
                        dcc.Graph(id="proximity-gauge"),
                    ],
                    style={"width": "20%", "display": "inline-block"},
                ),
            ],
            style={"display": "flex", "justify-content": "space-around"},
        ),

        # Row 2: Path trace (local map visualization)
        html.Div(
            children=[
                dcc.Graph(id="path-trace"),
            ],
            style={"margin-top": "20px"},
        ),

        # Hidden interval for periodic updates
        dcc.Interval(id="update-interval", interval=1000, n_intervals=0),
    ]
)

# Callback to update dashboard metrics
@app.callback(
    [
        Output("position-display", "children"),
        Output("heading-display", "children"),
        Output("battery-bar", "figure"),
        Output("proximity-gauge", "figure"),
        Output("path-trace", "figure"),
    ],
    [Input("update-interval", "n_intervals")],
)
def update_dashboard(n_intervals):
    # Simulate telemetry updates
    telemetry_state["position"] = (
        telemetry_state["position"][0] + random.uniform(-1, 1),
        telemetry_state["position"][1] + random.uniform(-1, 1),
    )
    telemetry_state["heading"] = (telemetry_state["heading"] + random.uniform(-10, 10)) % 360
    telemetry_state["battery"] = max(telemetry_state["battery"] - random.uniform(0, 1), 0)
    telemetry_state["proximity"] = random.uniform(10, 100)
    telemetry_state["path_trace"].append(telemetry_state["position"])

    # Position display
    position_text = f"X: {telemetry_state['position'][0]:.2f}, Y: {telemetry_state['position'][1]:.2f}"

    # Heading display
    heading_text = f"{telemetry_state['heading']:.2f}°"

    # Battery bar visualization
    battery_fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=telemetry_state["battery"],
            title={"text": "Battery (%)"},
            gauge={"axis": {"range": [0, 100]}, "bar": {"color": "green"}},
        )
    )

    # Proximity gauge visualization
    proximity_fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=telemetry_state["proximity"],
            title={"text": "Proximity (cm)"},
            gauge={
                "axis": {"range": [0, 100]},
                "steps": [
                    {"range": [0, 20], "color": "red"},
                    {"range": [20, 50], "color": "yellow"},
                    {"range": [50, 100], "color": "green"},
                ],
            },
        )
    )

    # Path trace visualization
    path_x, path_y = zip(*telemetry_state["path_trace"])
    path_trace_fig = go.Figure(
        data=go.Scatter(x=path_x, y=path_y, mode="lines+markers", name="Path Trace")
    )
    path_trace_fig.update_layout(
        title="Local Map",
        xaxis_title="X Position",
        yaxis_title="Y Position",
        xaxis=dict(scaleanchor="y"),
    )

    return position_text, heading_text, battery_fig, proximity_fig, path_trace_fig


# Run the app
if __name__ == "__main__":
    app.run_server(debug=True)