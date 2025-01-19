from dash import Dash, dcc, html
import dash_bootstrap_components as dbc
from dash.dependencies import Output, Input
import json
import time
from queue import Empty
from collections import deque
from udp_listener import telemetry_queue  # Correct import

# Initialize Dash app
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Rover Telemetry Dashboard"

# Global variable to cache the last valid telemetry data
last_valid_data = None
last_valid_time = 0
DATA_TIMEOUT = 5  # seconds

# Buffers for telemetry data
battery_buffer = deque(maxlen=1000)  # Battery history buffer
ultrasound_buffer = deque(maxlen=1000)  # Ultrasound history buffer
cpu_buffer = deque(maxlen=1000)  # CPU usage history buffer
path_history = deque(maxlen=1000)

app.layout = html.Div([
    dcc.Interval(id="update-interval", interval=1000, n_intervals=0),
    dbc.Container([
        html.H1("Rover Telemetry Dashboard", className="text-center my-4"),
        html.Div(id="backend-status", className="text-center my-2", style={"font-size": "1.5em", "font-weight": "bold"}),
        dbc.Row([
            dbc.Col(dcc.Graph(id="path-trace", style={"height": "500px"}), width=6),
            dbc.Col(html.Div([
                html.Div("Live Video Feed", style={"text-align": "center", "font-size": "20px", "margin-bottom": "10px"}),
                html.Div(
                    html.Img(
                        src="http://127.0.0.1:8081/",
                        style={"width": "100%", "height": "100%", "object-fit": "contain"}
                    ),
                    style={"height": "520px", "background-color": "lightgray"}
                )
            ]), width=6),
        ], className="mb-4"),
        dbc.Row([
            dbc.Col(html.Div(id="system-state-display", style={"padding": "10px"}), width=3),
            dbc.Col(html.Div(id="position-display", style={"padding": "10px"}), width=3),
            dbc.Col(html.Div(id="heading-display", style={"padding": "10px"}), width=3),
            dbc.Col(html.Div(id="battery-visual", style={"padding": "10px"}), width=3),
        ], className="mb-3"),
        dbc.Row([
            dbc.Col(html.Div(id="proximity-indicator", style={"padding": "10px"}), width=6),
        ]),
        html.Hr(),
        html.H3("Sensor Measurement History", className="text-center my-4", style={"font-weight": "bold"}),
        dbc.Row([
            dbc.Col(dcc.Graph(id="battery-graph", style={"height": "400px"}), width=6),
            dbc.Col(dcc.Graph(id="ultrasound-graph", style={"height": "400px"}), width=6),
        ]),
        dbc.Row([
            dbc.Col(dcc.Graph(id="cpu-graph", style={"height": "400px"}), width=6),  # Added CPU graph
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
        Output("cpu-graph", "figure"),
    ],
    [Input("update-interval", "n_intervals")]
)
def update_dashboard(n_intervals):
    global last_valid_data, last_valid_time

    try:
        telemetry_data = None
        try:
            telemetry_data = telemetry_queue.get_nowait()
            last_valid_data = json.loads(telemetry_data)
            last_valid_time = time.time()
        except Empty:
            if time.time() - last_valid_time > DATA_TIMEOUT:
                raise ValueError("No telemetry data available yet.")

        telemetry_data = last_valid_data

        # Extract telemetry data
        position = telemetry_data["position"]
        heading = telemetry_data["heading"]
        battery = telemetry_data["battery_level"]
        ultrasound = telemetry_data["ultrasound_distance"]
        system_state = telemetry_data.get("system_state", {})

        # Append data to buffers
        battery_buffer.append(battery)
        ultrasound_buffer.append(ultrasound)
        cpu_usage = system_state.get("cpu_usage", 0)
        cpu_buffer.append(cpu_usage)
        path_history.append((position["x"], position["y"]))

        # Center path trace toggle
        center_path = n_intervals % 2 == 0  # Example toggle logic
        if center_path:
            x_range = [position["x"] - 10, position["x"] + 10]
            y_range = [position["y"] - 10, position["y"] + 10]
        else:
            x_range = [-20, 20]
            y_range = [-20, 20]

        # Path trace figure
        path_trace_figure = {
            "data": [
                {
                    "x": [p[0] for p in path_history],
                    "y": [p[1] for p in path_history],
                    "type": "scatter",
                    "mode": "lines+markers",
                    "line": {"color": "blue"},
                    "name": "Path History",
                },
                {
                    "x": [position["x"]],
                    "y": [position["y"]],
                    "type": "scatter",
                    "mode": "markers",
                    "marker": {"color": "red", "size": 10},
                    "name": "Current Position",
                },
            ],
            "layout": {
                "title": "Path Trace",
                "xaxis": {"range": x_range, "title": "X Position"},
                "yaxis": {"range": y_range, "title": "Y Position"},
            },
        }

        # Battery graph
        battery_graph = {
            "data": [
                {"x": list(range(len(battery_buffer))), "y": list(battery_buffer), "type": "line", "name": "Battery Level"}
            ],
            "layout": {"title": "Battery Over Time", "xaxis": {"title": "Time"}, "yaxis": {"title": "%", "range": [0, 100]}},
        }

        # Ultrasound graph
        ultrasound_graph = {
            "data": [
                {"x": list(range(len(ultrasound_buffer))), "y": list(ultrasound_buffer), "type": "line", "name": "Ultrasound Distance"}
            ],
            "layout": {"title": "Ultrasound Over Time", "xaxis": {"title": "Time"}, "yaxis": {"title": "Distance (m)"}},
        }

        # CPU graph
        cpu_graph = {
            "data": [
                {"x": list(range(len(cpu_buffer))), "y": list(cpu_buffer), "type": "line", "name": "CPU Usage"}
            ],
            "layout": {"title": "CPU Usage Over Time", "xaxis": {"title": "Time"}, "yaxis": {"title": "Usage (%)", "range": [0, 100]}},
        }

        # System state display
        system_state_display = html.Div([
            html.Div(f"CPU Usage: {cpu_usage}%", style={"font-size": "16px", "font-weight": "bold"}),
            html.Div(f"Memory Available: {system_state.get('memory_available', 'N/A')} MB", style={"font-size": "16px"}),
            html.Div(f"Disk Usage: {system_state.get('disk_usage', 'N/A')}%", style={"font-size": "16px"}),
        ])

        # Proximity indicator
        proximity_indicator = html.Div(
            f"Ultrasound Proximity: {ultrasound:.2f} m",
            style={
                "text-align": "center",
                "padding": "10px",
                "font-size": "20px",
                "font-weight": "bold",
                "color": "green" if ultrasound > 1.0 else "red",
            },
        )

        # Return updates for dashboard
        return (
            "🟢 Backend Connected",
            path_trace_figure,
            system_state_display,
            f"x: {position['x']:.2f}, y: {position['y']:.2f}",
            f"{heading:.2f}°",
            f"{battery:.2f}%",
            proximity_indicator,
            battery_graph,
            ultrasound_graph,
            cpu_graph,
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
            html.Div("No data", style={"text-align": "center"}),
            {"data": [], "layout": {"title": "Battery Over Time"}},
            {"data": [], "layout": {"title": "Ultrasound Over Time"}},
            {"data": [], "layout": {"title": "CPU Usage Over Time"}},
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
            html.Div("No data", style={"text-align": "center"}),
            {"data": [], "layout": {"title": "Battery Over Time"}},
            {"data": [], "layout": {"title": "Ultrasound Over Time"}},
            {"data": [], "layout": {"title": "CPU Usage Over Time"}},
        )