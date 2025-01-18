import threading
import socket
import json
import time
from collections import deque
from dash import Dash, dcc, html
from dash.dependencies import Output, Input, State
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import math

# External UDP Configuration
EXTERNAL_UDP_IP = "127.0.0.1"
EXTERNAL_UDP_PORT = 50055

# Local UDP Configuration for Dashboard
LOCAL_UDP_IP = "127.0.0.1"
LOCAL_UDP_PORT = 60000

# Initialize Dash app
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Rover Telemetry Dashboard"

# Buffer for path and telemetry data
path_history = deque(maxlen=1000)
data_buffer = {"x": [], "y": [], "battery": [], "ultrasound": [], "heading": []}

# Track the last update time
last_update_time = {"timestamp": None}

# Dashboard Layout
app.layout = html.Div([
    dcc.Interval(id='update-interval', interval=1000, n_intervals=0),
    html.Div(
        dbc.Container([
            dbc.Row([
                dbc.Col([
                    html.H1("Rover Telemetry Dashboard", style={"text-align": "center", "font-weight": "bold"})
                ], width=12)
            ]),
            dbc.Row([
                dbc.Col([
                    html.Div("Video Feed", style={"text-align": "center", "font-size": "1.5em", "font-weight": "bold"}),
                    html.Div(id='video-feed', style={"text-align": "center", "height": "360px", "background": "#f0f0f0"})
                ], width=6),
                dbc.Col([
                    dcc.Graph(id="path-trace", style={"height": "360px"}),
                    html.Div([
                        html.Label("Path Trace Centering:"),
                        dcc.RadioItems(
                            id="orientation-toggle",
                            options=[
                                {"label": "Center on Rover", "value": "rover"},
                                {"label": "Center on Origin", "value": "origin"},
                            ],
                            value="rover",
                            inline=True
                        ),
                    ], style={"text-align": "center", "margin-top": "10px"})
                ], width=6)
            ]),
            dbc.Row([
                dbc.Col([
                    html.Div("System State", style={"font-weight": "bold", "font-size": "1.2em"}),
                    html.Div(id="system-state-display", children="Loading..."),
                ], width=3),
                dbc.Col([
                    html.Div("Position", style={"font-weight": "bold", "font-size": "1.2em"}),
                    html.Div(id="position-display", children="Loading..."),
                ], width=3),
                dbc.Col([
                    html.Div("Heading", style={"font-weight": "bold", "font-size": "1.2em"}),
                    html.Div(id="heading-display", children="Loading..."),
                ], width=3),
                dbc.Col([
                    html.Div("Battery Level", style={"font-weight": "bold", "font-size": "1.2em"}),
                    html.Div(id="battery-visual", children="Loading..."),
                ], width=3),
            ]),
            dbc.Row([
                dbc.Col([
                    html.Div("Proximity", style={"font-weight": "bold", "font-size": "1.2em"}),
                    html.Div(id="proximity-indicator", children="Loading..."),
                ], width=6)
            ])
        ])
    )
])

# Dash Callback
@app.callback(
    [
        Output("path-trace", "figure"),
        Output("system-state-display", "children"),
        Output("position-display", "children"),
        Output("heading-display", "children"),
        Output("battery-visual", "children"),
        Output("proximity-indicator", "children"),
    ],
    [
        Input("update-interval", "n_intervals"),
        Input("orientation-toggle", "value"),
    ]
)
def update_dashboard(n_intervals, centering_option):
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
        data_buffer["x"].append(position["x"])
        data_buffer["y"].append(position["y"])
        data_buffer["battery"].append(telemetry_data["battery_level"])
        data_buffer["ultrasound"].append(telemetry_data["ultrasound_distance"])
        data_buffer["heading"].append(heading)
        path_history.append((position["x"], position["y"]))

        # Update the last update time
        last_update_time["timestamp"] = time.time()

                # Path trace figure with heading indicator
        x_start, y_start = position["x"], position["y"]
        heading_rad = math.radians(heading)  # Convert heading to radians

        # Adjust for 0° = North (up) and clockwise rotation
        x_end = x_start + 5 * math.sin(heading_rad)  # X-coordinate
        y_end = y_start + 5 * math.cos(heading_rad)  # Y-coordinate

        if centering_option == "rover":
            # Center the graph around the rover's last position
            x_center, y_center = x_start, y_start
            x_range = [x_center - 10, x_center + 10]
            y_range = [y_center - 10, y_center + 10]
        else:  # Center on Origin
            x_range = [-20, 20]
            y_range = [-20, 20]

        path_trace_figure = {
            "data": [
                {
                    "x": [p[0] for p in path_history],
                    "y": [p[1] for p in path_history],
                    "type": "scatter",
                    "mode": "lines+markers",
                    "name": "Path",
                },
                {
                    "x": [x_start, x_end],
                    "y": [y_start, y_end],
                    "type": "scatter",
                    "mode": "lines",
                    "line": {"color": "red", "width": 2},
                    "name": "Heading",
                }
            ],
            "layout": {
                "title": "Path Trace",
                "xaxis": {"range": x_range},
                "yaxis": {"range": y_range},
            },
        }

        return (
            path_trace_figure,
            "System State: OK",
            f"x: {x_start:.2f}, y: {y_start:.2f}",
            f"{heading:.2f}°",
            f"{telemetry_data['battery_level']:.2f}%",
            f"{telemetry_data['ultrasound_distance']:.2f} m",
        )

    except socket.timeout:
        # Handle timeout or no data
        path_trace_figure = {"data": [], "layout": {"title": "Path Trace"}}
        return (
            path_trace_figure,
            "No telemetry data available",
            "N/A",
            "N/A",
            "N/A",
            "N/A",
        )


# UDP Listener Thread
def udp_listener():
    """Listen for incoming UDP messages and forward them locally."""
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as external_socket:
        external_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            external_socket.bind((EXTERNAL_UDP_IP, EXTERNAL_UDP_PORT))
            print(f"Listening on {EXTERNAL_UDP_IP}:{EXTERNAL_UDP_PORT} for external data")
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


# Start the UDP Listener in a Thread
listener_thread = threading.Thread(target=udp_listener, daemon=True)
listener_thread.start()

# Run the Dash App
if __name__ == "__main__":
    app.run_server(debug=True)