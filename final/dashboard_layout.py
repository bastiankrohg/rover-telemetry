from dash import Dash, dcc, html
import dash_bootstrap_components as dbc

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Rover Telemetry Dashboard"

app.layout = html.Div([
    dcc.Interval(id="update-interval", interval=1000, n_intervals=0),
    dbc.Container([
        html.H1("Rover Telemetry Dashboard", className="text-center my-4"),
        html.Div(id="backend-status", className="text-center my-2", style={"font-size": "1.5em", "font-weight": "bold"}),
        dbc.Row([
            dbc.Col(dcc.Graph(id="path-trace", style={"height": "360px"}), width=6),
            dbc.Col(html.Div([
                html.Div("Live Video Feed", style={"text-align": "center", "font-size": "20px"}),
                html.Img(
                    src="http://127.0.0.1:8081/",
                    style={"width": "100%", "height": "auto", "border": "2px solid black"}
                ),
            ], style={"height": "360px", "background-color": "lightgray"}), width=6),
        ]),
        dbc.Row([
            dbc.Col(html.Div(id="system-state-display"), width=3),
            dbc.Col(html.Div(id="position-display"), width=3),
            dbc.Col(html.Div(id="heading-display"), width=3),
            dbc.Col(html.Div(id="battery-visual"), width=3),
        ], className="mb-3"),
        dbc.Row([
            dbc.Col(html.Div(id="proximity-indicator"), width=6),
        ]),
        html.Hr(),
        html.H3("Sensor Measurement History", className="text-center my-4", style={"font-weight": "bold"}),
        dbc.Row([
            dbc.Col(dcc.Graph(id="battery-graph", style={"height": "400px"}), width=6),
            dbc.Col(dcc.Graph(id="ultrasound-graph", style={"height": "400px"}), width=6),
        ]),
    ], fluid=True),
])

# Callback to update the dashboard
from dash.dependencies import Output, Input
import json

@app.callback(
    [
        Output("backend-status", "children"),
        Output("path-trace", "figure"),
        Output("system-state-display", "children"),
        Output("position-display", "children"),
        Output("heading-display", "children"),
        Output("battery-visual", "children"),
        Output("proximity-indicator", "children"),
        Output("battery-graph", "figure"),
        Output("ultrasound-graph", "figure"),
    ],
    [Input("update-interval", "n_intervals")]
)
def update_dashboard(n_intervals):
    from udp_listener import last_received_data

    try:
        telemetry_data = json.loads(last_received_data)

        # Process telemetry data
        position = telemetry_data["position"]
        heading = telemetry_data["heading"]
        battery = telemetry_data["battery_level"]
        ultrasound = telemetry_data["ultrasound_distance"]

        # Update the dashboard components
        return (
            "🟢 Backend Connected",
            {"data": [{"x": [0], "y": [0], "type": "scatter"}], "layout": {"title": "Path Trace"}},
            f"System State: OK",
            f"x: {position['x']:.2f}, y: {position['y']:.2f}",
            f"{heading:.2f}°",
            f"{battery:.2f}%",
            f"{ultrasound:.2f} m",
            {"data": [], "layout": {"title": "Battery Over Time"}},
            {"data": [], "layout": {"title": "Ultrasound Over Time"}},
        )

    except Exception as e:
        print(f"Error updating dashboard: {e}")
        return (
            "🔴 Backend Disconnected",
            {},
            "No telemetry data available",
            "N/A",
            "N/A",
            "N/A",
            "N/A",
            {},
            {},
        )