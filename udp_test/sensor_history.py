from dash import html, dcc
import dash_bootstrap_components as dbc

def create_sensor_page():
    return dbc.Container(
        [
            html.H1("Sensor Measurements", className="text-center my-4"),
            dbc.Row(
                [
                    # Battery and ultrasound graphs
                    dbc.Col(
                        dcc.Graph(id="battery-graph", style={"height": "400px"}), width=6
                    ),
                    dbc.Col(
                        dcc.Graph(id="ultrasound-graph", style={"height": "400px"}), width=6
                    ),
                ],
                className="mb-4",
            ),
            dbc.Row(
                [
                    dbc.Col(html.H4("Detected Resources"), width=12),
                    dbc.Col(
                        dbc.Table(
                            id="resource-table",
                            striped=True,
                            bordered=True,
                            hover=True,
                        ),
                        width=12,
                    ),
                ],
                className="mb-4",
            ),
        ],
        fluid=True,
    )