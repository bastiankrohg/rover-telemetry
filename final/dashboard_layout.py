from dash import Dash, dcc, html
import dash_bootstrap_components as dbc
from dash.dependencies import Output, Input
import json
import time
from queue import Empty
from udp_listener import telemetry_queue  # Correct import

# Initialize Dash app
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Rover Telemetry Dashboard"

# Global variable to cache the last valid telemetry data
last_valid_data = None
last_valid_time = 0
DATA_TIMEOUT = 5  # seconds

# Define the app layout
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
    global last_valid_data, last_valid_time

    try:
        # Attempt to retrieve data from the queue
        telemetry_data = None
        try:
            telemetry_data = telemetry_queue.get_nowait()
            last_valid_data = json.loads(telemetry_data)  # Parse JSON data
            last_valid_time = time.time()  # Update the last valid data time
        except Empty:
            # If no new data, check if cached data is still valid
            if time.time() - last_valid_time > DATA_TIMEOUT:
                raise ValueError("No telemetry data available yet.")

        # Use the latest valid data
        telemetry_data = last_valid_data

        # Extract telemetry data
        position = telemetry_data["position"]
        heading = telemetry_data["heading"]
        battery = telemetry_data["battery_level"]
        ultrasound = telemetry_data["ultrasound_distance"]
        system_state = telemetry_data.get("system_state", {})

        # Prepare data for dashboard components
        path_trace_figure = {
            "data": [
                {
                    "x": [position["x"]],
                    "y": [position["y"]],
                    "type": "scatter",
                    "mode": "lines+markers",
                    "name": "Path",
                },
            ],
            "layout": {
                "title": "Path Trace",
                "xaxis": {"range": [-20, 20]},
                "yaxis": {"range": [-20, 20]}
            },
        }

        battery_graph = {
            "data": [{"x": [0], "y": [battery], "type": "line"}],
            "layout": {"title": "Battery Over Time", "xaxis": {"title": "Time"}, "yaxis": {"title": "%"}},
        }

        ultrasound_graph = {
            "data": [{"x": [0], "y": [ultrasound], "type": "line"}],
            "layout": {"title": "Ultrasound Over Time", "xaxis": {"title": "Time"}, "yaxis": {"title": "Distance (m)"}},
        }

        system_state_display = (
            f"CPU: {system_state.get('cpu_usage', 'N/A')}% | "
            f"Memory: {system_state.get('memory_available', 'N/A')} MB | "
            f"Disk: {system_state.get('disk_usage', 'N/A')}%"
        )

        # Return updates for dashboard
        return (
            "🟢 Backend Connected",
            path_trace_figure,
            system_state_display,
            f"x: {position['x']:.2f}, y: {position['y']:.2f}",
            f"{heading:.2f}°",
            f"{battery:.2f}%",
            f"{ultrasound:.2f} m",
            battery_graph,
            ultrasound_graph,
        )

    except ValueError as ve:
        print(f"Dashboard update warning: {ve}")
        return (
            "🔴 No data received",
            {"data": [], "layout": {"title": "Path Trace"}},
            "No system state available",
            "N/A",
            "N/A",
            "N/A",
            "N/A",
            {"data": [], "layout": {"title": "Battery Over Time"}},
            {"data": [], "layout": {"title": "Ultrasound Over Time"}},
        )
    except Exception as e:
        print(f"Error updating dashboard: {e}")
        return (
            "🔴 Backend Disconnected",
            {"data": [], "layout": {"title": "Path Trace"}},
            "No system state available",
            "N/A",
            "N/A",
            "N/A",
            "N/A",
            {"data": [], "layout": {"title": "Battery Over Time"}},
            {"data": [], "layout": {"title": "Ultrasound Over Time"}},
        )