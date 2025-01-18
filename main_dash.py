import threading
import socket
import json
import time
import math
from collections import deque
from dash import Dash, dcc, html
from dash.dependencies import Output, Input
import dash_bootstrap_components as dbc
import plotly.graph_objs as go

# External UDP Configuration
EXTERNAL_UDP_IP = "127.0.0.1"
EXTERNAL_UDP_PORT = 50055

# Local UDP Configuration for Dashboard
LOCAL_UDP_IP = "127.0.0.1"
LOCAL_UDP_PORT = 60000

# Initialize Dash app
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Rover Telemetry Dashboard"

# Buffers for telemetry data
path_history = deque(maxlen=1000)
data_buffer = {"x": [], "y": [], "battery": [], "ultrasound": [], "heading": []}
last_update_time = {"timestamp": None}

# Telemetry Dashboard Layout
app.layout = html.Div(
    [
        dcc.Interval(id="update-interval", interval=1000, n_intervals=0),
        dbc.Container(
            [
                html.H1("Rover Telemetry Dashboard", className="text-center my-4"),
                html.Div(
                    id="backend-status",
                    className="text-center my-2",
                    style={"font-size": "1.5em", "font-weight": "bold"},
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            dcc.Graph(id="path-trace", style={"height": "360px"}), width=6
                        ),
                        dbc.Col(
                            html.Div(
                                id="video-feed",
                                style={
                                    "height": "360px",
                                    "background-color": "lightgray",
                                    "border": "2px solid black",
                                    "text-align": "center",
                                },
                            ),
                            width=6,
                        ),
                    ],
                    className="mb-4",
                ),
                dbc.Row(
                    [
                        dbc.Col(html.Div(id="system-state-display"), width=3),
                        dbc.Col(html.Div(id="position-display"), width=3),
                        dbc.Col(html.Div(id="heading-display"), width=3),
                        dbc.Col(html.Div(id="battery-visual"), width=3),
                    ],
                    className="mb-3",
                ),
                dbc.Row(
                    [
                        dbc.Col(html.Div(id="proximity-indicator"), width=6),
                    ]
                ),
                html.Hr(),
                # Sensor Measurement History Section
                html.H3(
                    "Sensor Measurement History",
                    className="text-center my-4",
                    style={"font-weight": "bold"},
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            dcc.Graph(id="battery-graph", style={"height": "400px"}), width=6
                        ),
                        dbc.Col(
                            dcc.Graph(id="ultrasound-graph", style={"height": "400px"}), width=6
                        ),
                    ],
                ),
            ],
            fluid=True,
        ),
    ]
)

# Dash Callback
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
    [
        Input("update-interval", "n_intervals"),
    ],
)
def update_dashboard(n_intervals):
    global last_update_time
    try:
        # Connect to local UDP to fetch data
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as client_socket:
            client_socket.settimeout(1.0)
            client_socket.bind((LOCAL_UDP_IP, LOCAL_UDP_PORT))
            data, _ = client_socket.recvfrom(1024)
            telemetry_data = json.loads(data.decode("utf-8"))

        # Update buffers
        position = telemetry_data["position"]
        heading = telemetry_data["heading"]
        battery = telemetry_data["battery_level"]
        ultrasound = telemetry_data["ultrasound_distance"]
        data_buffer["x"].append(position["x"])
        data_buffer["y"].append(position["y"])
        data_buffer["battery"].append(battery)
        data_buffer["ultrasound"].append(ultrasound)
        data_buffer["heading"].append(heading)
        path_history.append((position["x"], position["y"]))

        # Update last update time
        last_update_time["timestamp"] = time.time()

        # Backend status
        backend_status = "🟢 Rover Telemetry Dashboard"

        # Path trace figure
        x_start, y_start = position["x"], position["y"]
        heading_rad = math.radians(heading)
        x_end = x_start + 5 * math.sin(heading_rad)
        y_end = y_start + 5 * math.cos(heading_rad)

        x_range = [x_start - 10, x_start + 10]
        y_range = [y_start - 10, y_start + 10]

        path_trace_figure = {
            "data": [
                {"x": [p[0] for p in path_history], "y": [p[1] for p in path_history], "type": "scatter", "mode": "lines+markers"},
                {"x": [x_start, x_end], "y": [y_start, y_end], "type": "scatter", "mode": "lines", "line": {"color": "red"}},
            ],
            "layout": {"title": "Path Trace", "xaxis": {"range": x_range}, "yaxis": {"range": y_range}},
        }

        # Battery graph
        battery_fig = {
            "data": [
                {
                    "x": list(range(len(data_buffer["battery"]))),
                    "y": data_buffer["battery"],
                    "type": "line",
                    "name": "Battery",
                }
            ],
            "layout": {"title": "Battery Over Time", "xaxis": {"title": "Time"}, "yaxis": {"title": "%"}},
        }

        # Ultrasound graph
        ultrasound_fig = {
            "data": [
                {
                    "x": list(range(len(data_buffer["ultrasound"]))),
                    "y": data_buffer["ultrasound"],
                    "type": "line",
                    "name": "Ultrasound",
                }
            ],
            "layout": {"title": "Ultrasound Over Time", "xaxis": {"title": "Time"}, "yaxis": {"title": "Distance (m)"}},
        }

        return backend_status, path_trace_figure, "System State: OK", f"x: {x_start:.2f}, y: {y_start:.2f}", f"{heading:.2f}°", f"{battery:.2f}%", f"{ultrasound:.2f} m", battery_fig, ultrasound_fig

    except socket.timeout:
        backend_status = "🔴 Rover Telemetry Dashboard"
        path_trace_figure = {"data": [], "layout": {"title": "Path Trace"}}
        battery_fig = {"data": [], "layout": {"title": "Battery Over Time"}}
        ultrasound_fig = {"data": [], "layout": {"title": "Ultrasound Over Time"}}
        return backend_status, path_trace_figure, "No telemetry data available", "N/A", "N/A", "N/A", "N/A", battery_fig, ultrasound_fig


# UDP Listener Thread
def udp_listener():
    """Listen for incoming UDP messages and forward them locally."""
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as external_socket:
        external_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            external_socket.bind((EXTERNAL_UDP_IP, EXTERNAL_UDP_PORT))
        except OSError as e:
            print(f"Error binding to external port: {e}")
            return

        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as local_socket:
            while True:
                try:
                    data, addr = external_socket.recvfrom(1024)
                    local_socket.sendto(data, (LOCAL_UDP_IP, LOCAL_UDP_PORT))
                except Exception as e:
                    print(f"Error in UDP listener: {e}")


# Start the UDP Listener
listener_thread = threading.Thread(target=udp_listener, daemon=True)
listener_thread.start()

# Run the Dash App
if __name__ == "__main__":
    app.run_server(debug=True)