from dash import html, dcc
import dash_bootstrap_components as dbc

def create_layout():
    return dbc.Container(
        [
            html.H1("Rover Telemetry Dashboard", className="text-center my-4"),
            dbc.Row(
                [
                    # Left section: telemetry and mapping
                    dbc.Col(
                        [
                            # Battery and proximity
                            dbc.Row(
                                [
                                    dbc.Col(html.Div(id="battery-visual"), width=6),
                                    dbc.Col(html.Div(id="proximity-indicator"), width=6),
                                ],
                                className="mb-3",
                            ),
                            # Position, heading, and system state
                            dbc.Row(
                                [
                                    dbc.Col(html.Div(id="system-state-display"), width=4),
                                    dbc.Col(html.Div(id="position-display"), width=4),
                                    dbc.Col(html.Div(id="heading-display"), width=4),
                                ],
                                className="mb-3",
                            ),
                            # Path trace visualization
                            dcc.Graph(
                                id="path-trace",
                                config={"displayModeBar": False},
                                style={"height": "500px"},
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
                                "border": "2px solid black",
                            },
                        ),
                        width=6,
                    ),
                ],
                style={"height": "100vh"},
            ),
            dcc.Interval(id="update-interval", interval=1000, n_intervals=0),
        ],
        fluid=True,
    )