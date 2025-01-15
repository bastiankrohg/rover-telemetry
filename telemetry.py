import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import random

# Create the Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Rover Telemetry Dashboard"

# Dummy telemetry data
path_trace = [(0, 0)]
battery_level = 75  # Percentage
proximity_status = 1.5  # Distance in meters
heading = 45.0  # Dummy heading value

# Define layout
app.layout = dbc.Container(
    [
        html.H1("Rover Telemetry Dashboard", className="text-center my-4"),
        dbc.Row(
            [
                # Left section: telemetry and mapping
                dbc.Col(
                    [
                        # Telemetry (Battery and Proximity)
                        dbc.Row(
                            [
                                dbc.Col(html.Div(id="battery-visual"), width=6),
                                dbc.Col(html.Div(id="proximity-indicator"), width=6),
                            ],
                            className="mb-3",
                        ),
                        # System state and telemetry details
                        dbc.Row(
                            [
                                dbc.Col(html.Div(id="system-state-display"), width=4),
                                dbc.Col(html.Div(id="position-display"), width=4),
                                dbc.Col(html.Div(id="heading-display"), width=4),
                            ],
                            className="mb-3",
                        ),
                        # Path trace visualization
                        dbc.Row(
                            [
                                dbc.Col(
                                    dcc.Graph(
                                        id="path-trace",
                                        config={"displayModeBar": False},
                                    ),
                                    width=12,
                                ),
                            ]
                        ),
                    ],
                    width=6,
                ),
                # Right section: video feed
                dbc.Col(
                    html.Div(
                        id="video-feed",
                        style={
                            "height": "100%",
                            "background-color": "lightgray",
                            "text-align": "center",
                            "line-height": "100%",
                            "border": "2px solid black",
                        },
                        children=["Video Feed Placeholder"],
                    ),
                    width=6,
                ),
            ],
            style={"height": "100vh"},  # Full height layout
        ),
        dcc.Interval(id="update-interval", interval=1000, n_intervals=0),
    ],
    fluid=True,
)

@app.callback(
    [
        Output("path-trace", "figure"),
        Output("system-state-display", "children"),
        Output("position-display", "children"),
        Output("heading-display", "children"),
        Output("battery-visual", "children"),
        Output("proximity-indicator", "children"),
    ],
    [Input("update-interval", "n_intervals")],
)
def update_dashboard(n_intervals):
    global path_trace, battery_level, proximity_status, heading

    # Update path trace with dummy movement
    x, y = path_trace[-1]
    new_position = (x + random.uniform(-1, 1), y + random.uniform(-1, 1))
    path_trace.append(new_position)

    # Path trace figure
    trace_fig = go.Figure()
    trace_fig.add_trace(
        go.Scatter(
            x=[p[0] for p in path_trace],
            y=[p[1] for p in path_trace],
            mode="lines+markers",
            line=dict(color="blue"),
            marker=dict(size=8),
            name="Path",
        )
    )
    trace_fig.update_layout(
        title="Path Trace",
        xaxis=dict(range=[-20, 20], title="X Position"),
        yaxis=dict(range=[-20, 20], title="Y Position"),
        height=500,
        margin=dict(l=10, r=10, t=30, b=10),
        xaxis_scaleanchor="y",  # Keep X and Y scales identical
        xaxis_constrain="domain",
        yaxis_constrain="domain",
    )

    # System state and telemetry data
    system_state = "System State: Running"
    position = f"Position: ({new_position[0]:.2f}, {new_position[1]:.2f})"
    heading_text = f"Heading: {heading:.2f}°"

    # Battery visual
    battery_segments = 5
    filled_segments = int((battery_level / 100) * battery_segments)
    battery_children = [
        html.Div(
            style={
                "background-color": "green" if i < filled_segments else "lightgray",
                "height": "20px",
                "width": "20px",
                "border": "1px solid black",
                "margin": "1px",
                "display": "inline-block",
            }
        )
        for i in range(battery_segments)
    ]
    battery_children.append(
        html.Div(
            style={
                "background-color": "black",
                "height": "20px",
                "width": "5px",
                "margin-left": "2px",
                "display": "inline-block",
            }
        )
    )
    battery_div = html.Div(
        children=[
            html.Div("Battery", style={"text-align": "center"}),
            html.Div(battery_children, style={"display": "flex", "justify-content": "center", "margin-top": "10px"}),
        ]
    )

    # Proximity indicator
    proximity_color = "green" if proximity_status > 2 else "orange" if proximity_status > 1 else "red"
    proximity_div = html.Div(
        children=[
            html.Div("Proximity", style={"text-align": "center"}),
            html.Div(
                style={
                    "background-color": proximity_color,
                    "height": "50px",
                    "width": "50px",
                    "border-radius": "25px",
                    "margin": "10px auto",
                },
            ),
            html.Div(f"{proximity_status:.2f} m", style={"text-align": "center", "margin-top": "10px"}),
        ]
    )

    return trace_fig, system_state, position, heading_text, battery_div, proximity_div


if __name__ == "__main__":
    app.run_server(debug=True)