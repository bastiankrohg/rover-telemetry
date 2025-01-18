import socket
import json
import threading
from dash import Dash, html, dcc
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc

# UDP Configuration
UDP_IP = "127.0.0.1"
UDP_PORT = 50054
latest_telemetry = None
backend_status = {"connected": False}

# Start Dash app
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Rover Telemetry Dashboard"

# Layout
app.layout = html.Div(
    [
        dcc.Interval(id="update-interval", interval=1000, n_intervals=0),
        html.Div(
            [
                html.Div(id="backend-status", style={"font-size": "1.2em", "margin-bottom": "20px"}),
                html.Div(id="telemetry-data", style={"font-size": "1.1em"}),
            ]
        ),
        dcc.Graph(id="path-trace", style={"height": "60vh"}),
    ]
)

# Path trace storage
path_trace = {"x": [], "y": []}

# UDP Listener
def udp_listener():
    global latest_telemetry, backend_status
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as client_socket:
            client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            client_socket.bind((UDP_IP, UDP_PORT))
            print(f"Listening for telemetry on {UDP_IP}:{UDP_PORT}")
            backend_status["connected"] = True

            while True:
                data, addr = client_socket.recvfrom(1024)
                latest_telemetry = json.loads(data.decode("utf-8"))
    except Exception as e:
        print(f"UDP listener error: {e}")
        backend_status["connected"] = False

# Start UDP listener in a separate thread
listener_thread = threading.Thread(target=udp_listener, daemon=True)
listener_thread.start()

# Dash callback to update the dashboard
@app.callback(
    [Output("backend-status", "children"),
     Output("backend-status", "style"),
     Output("telemetry-data", "children"),
     Output("path-trace", "figure")],
    [Input("update-interval", "n_intervals")],
)
def update_dashboard(n_intervals):
    global latest_telemetry, path_trace, backend_status

    # Update backend connection status
    if backend_status["connected"]:
        backend_status_text = "Connected to UDP Backend"
        backend_status_style = {"color": "green", "font-weight": "bold"}
    else:
        backend_status_text = "Disconnected from UDP Backend"
        backend_status_style = {"color": "red", "font-weight": "bold"}

    # Process telemetry data
    if latest_telemetry:
        position = latest_telemetry.get("position", {"x": 0, "y": 0})
        heading = latest_telemetry.get("heading", 0)
        battery_level = latest_telemetry.get("battery_level", 100)
        ultrasound_distance = latest_telemetry.get("ultrasound_distance", 0)

        telemetry_display = html.Div(
            [
                html.P(f"Position: x={position['x']:.2f}, y={position['y']:.2f}"),
                html.P(f"Heading: {heading:.2f}°"),
                html.P(f"Battery Level: {battery_level:.2f}%"),
                html.P(f"Ultrasound Distance: {ultrasound_distance:.2f}m"),
            ]
        )

        # Update path trace
        path_trace["x"].append(position["x"])
        path_trace["y"].append(position["y"])
    else:
        telemetry_display = html.Div("No telemetry data available.")

    # Create the path trace figure
    path_trace_figure = {
        "data": [
            {
                "x": path_trace["x"],
                "y": path_trace["y"],
                "type": "scatter",
                "mode": "lines+markers",
                "name": "Path",
            }
        ],
        "layout": {
            "xaxis": {"title": "X Position", "range": [-20, 20]},
            "yaxis": {"title": "Y Position", "range": [-20, 20]},
            "title": "Path Trace",
        },
    }

    return backend_status_text, backend_status_style, telemetry_display, path_trace_figure

if __name__ == "__main__":
    app.run_server(debug=True)