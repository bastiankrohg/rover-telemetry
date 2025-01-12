import dash
from dash import html, dcc, Input, Output
import plotly.graph_objs as go
import random

# Initialize Dash app
app = dash.Dash(__name__)
app.title = "Mars Rover Dashboard"

# Simulated telemetry state
telemetry_state = {
    "position": (0, 0),
    "heading": 90,  # Degrees
    "battery": 75,  # Percentage
    "proximity": 50,  # Distance in cm
    "path_trace": [(0, 0)],  # List of past positions
}

# Navbar
navbar = html.Div(
    children=[
        dcc.Location(id="url", refresh=False),
        html.Nav(
            children=[
                dcc.Link("Dashboard", href="/", className="nav-link"),
                dcc.Link("Manual Control", href="/manual", className="nav-link"),
                dcc.Link("Settings", href="/settings", className="nav-link"),
            ],
            className="navbar",
            style={"display": "flex", "gap": "20px", "padding": "10px", "background-color": "#333", "color": "#fff"},
        ),
    ]
)

# Dashboard layout
dashboard_layout = html.Div(
    children=[
        html.H1("Mars Rover Dashboard", style={"text-align": "center"}),

        # Split layout: Video feed (left) and telemetry (right)
        html.Div(
            children=[
                # Left: Video feed placeholder
                html.Div(
                    children=[
                        html.H3("Video Feed"),
                        html.Div(
                            style={
                                "background-color": "#000",
                                "height": "400px",
                                "border": "2px solid #333",
                                "display": "flex",
                                "align-items": "center",
                                "justify-content": "center",
                                "color": "#fff",
                            },
                            children="Video Placeholder",
                        ),
                    ],
                    style={"width": "50%", "padding": "10px"},
                ),

                # Right: Telemetry data
                html.Div(
                    children=[
                        html.Div(
                            children=[
                                html.H3("Position"),
                                html.P(id="position-display"),
                            ],
                            style={"padding": "10px"},
                        ),
                        html.Div(
                            children=[
                                html.H3("Heading"),
                                html.P(id="heading-display"),
                            ],
                            style={"padding": "10px"},
                        ),
                        html.Div(
                            children=[
                                html.H3("Battery"),
                                dcc.Graph(id="battery-bar"),
                            ],
                            style={"padding": "10px"},
                        ),
                        html.Div(
                            children=[
                                html.H3("Proximity"),
                                dcc.Graph(id="proximity-gauge"),
                            ],
                            style={"padding": "10px"},
                        ),
                        html.Div(
                            children=[
                                dcc.Graph(id="path-trace"),
                            ],
                            style={"padding": "10px"},
                        ),
                    ],
                    style={"width": "50%", "padding": "10px"},
                ),
            ],
            style={"display": "flex"},
        ),

        # Interval for periodic updates
        dcc.Interval(id="update-interval", interval=1000, n_intervals=0),
    ]
)

# Manual control layout (placeholder)
manual_control_layout = html.Div(
    children=[
        html.H1("Manual Control", style={"text-align": "center"}),
        html.P("Placeholder for manual control interface."),
        dcc.Link("Go back to Dashboard", href="/", className="nav-link"),
    ]
)

# Settings layout (placeholder)
settings_layout = html.Div(
    children=[
        html.H1("Settings", style={"text-align": "center"}),
        html.P("Placeholder for settings interface."),
        dcc.Link("Go back to Dashboard", href="/", className="nav-link"),
    ]
)

# App layout
app.layout = html.Div(
    children=[
        navbar,
        html.Div(id="page-content"),
    ]
)

# Callback to update telemetry dashboard
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


# Callback to manage page navigation
@app.callback(
    Output("page-content", "children"),
    [Input("url", "pathname")],
)
def display_page(pathname):
    if pathname == "/manual":
        return manual_control_layout
    elif pathname == "/settings":
        return settings_layout
    else:
        return dashboard_layout


# Run the app
if __name__ == "__main__":
    app.run_server(debug=True)