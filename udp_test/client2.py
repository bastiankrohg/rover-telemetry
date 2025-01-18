import threading
import socket
import json
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

# Initialize Dash app with Bootstrap theme
app = Dash(__name__, external_stylesheets=["https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css"])
app.title = "Rover Telemetry Dashboard"

# Buffer for path and telemetry data
path_history = deque(maxlen=1000)
data_buffer = {"x": [], "y": [], "battery": [], "ultrasound": [], "heading": []}

# Dashboard Layout
app.layout = html.Div([
    dcc.Interval(id='update-interval', interval=1000, n_intervals=0),
    html.Div(
        dbc.Container([
            dbc.Row([
                dbc.Col([
                    html.Div("Video Feed", style={"text-align": "center", "font-size": "1.5em", "font-weight": "bold"}),
                    html.Div(id='video-feed', style={"text-align": "center", "height": "360px", "background": "#f0f0f0"})
                ], width=6),
                dbc.Col([
                    dcc.Graph(id="path-trace", style={"height": "360px"}),
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
                ], width=6),
                dbc.Col([
                    html.Div("Backend Status", style={"font-weight": "bold", "font-size": "1.2em"}),
                    html.Div(id="backend-status", style={"padding": "10px", "color": "red"}, children="Disconnected"),
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
        Output("video-feed", "children"),
        Output("backend-status", "children"),
        Output("backend-status", "style"),
    ],
    [Input("update-interval", "n_intervals")]
)
def update_dashboard(n_intervals):
    try:
        # Connect to local UDP to fetch data
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as client_socket:
            client_socket.settimeout(1.0)
            client_socket.bind((LOCAL_UDP_IP, LOCAL_UDP_PORT))
            data, _ = client_socket.recvfrom(1024)
            telemetry_data = json.loads(data.decode("utf-8"))

        # Update buffers
        position = telemetry_data["position"]
        data_buffer["x"].append(position["x"])
        data_buffer["y"].append(position["y"])
        data_buffer["battery"].append(telemetry_data["battery_level"])
        data_buffer["ultrasound"].append(telemetry_data["ultrasound_distance"])
        data_buffer["heading"].append(telemetry_data["heading"])
        path_history.append((position["x"], position["y"]))

        # Update backend status
        backend_status_text = "Connected"
        backend_status_style = {"color": "green"}

        # Path trace figure
        path_trace_figure = {
            "data": [
                {
                    "x": [p[0] for p in path_history],
                    "y": [p[1] for p in path_history],
                    "type": "scatter",
                    "mode": "lines+markers",
                }
            ],
            "layout": {"title": "Path Trace", "xaxis": {"range": [-20, 20]}, "yaxis": {"range": [-20, 20]}},
        }

        # Placeholder for video feed
        video_feed = html.Div("Video feed placeholder (to be implemented)", style={"text-align": "center"})

        return (
            path_trace_figure,
            "System State: OK",
            f"x: {position['x']:.2f}, y: {position['y']:.2f}",
            f"{telemetry_data['heading']:.2f}°",
            f"{telemetry_data['battery_level']:.2f}%",
            f"{telemetry_data['ultrasound_distance']:.2f} m",
            video_feed,
            backend_status_text,
            backend_status_style,
        )

    except socket.timeout:
        # Handle timeout or no data
        backend_status_text = "Disconnected"
        backend_status_style = {"color": "red"}
        return (
            {"data": [], "layout": {"title": "Path Trace"}},
            "No telemetry data available",
            "N/A",
            "N/A",
            "N/A",
            "N/A",
            html.Div("No video feed available", style={"text-align": "center", "color": "red"}),
            backend_status_text,
            backend_status_style,
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