import threading
import socket
import json
import time
from dash import Dash, dcc, html
from dash.dependencies import Output, Input

# UDP Configuration
UDP_IP = "127.0.0.1"
UDP_PORT = 50055

# Shared data and lock
shared_telemetry_data = {
    "position": {"x": "N/A", "y": "N/A"},
    "battery_level": "N/A",
    "ultrasound_distance": "N/A",
    "heading": "N/A"
}
data_lock = threading.Lock()

# Dash App Initialization
app = Dash(__name__)

# Layout
app.layout = html.Div([
    html.H1("Telemetry Dashboard", style={"textAlign": "center"}),
    html.Div(
        id="connection-status",
        style={
            "width": "120px",
            "height": "40px",
            "border": "1px solid black",
            "borderRadius": "5px",
            "textAlign": "center",
            "lineHeight": "40px",
            "margin": "10px auto",
        },
    ),
    html.Div([
        html.Div([
            html.H4("Position (X, Y):"),
            html.P(id="position-data", style={"fontSize": "18px"}),
        ], style={"marginBottom": "20px"}),
        html.Div([
            html.H4("Battery Level:"),
            html.P(id="battery-data", style={"fontSize": "18px"}),
        ], style={"marginBottom": "20px"}),
        html.Div([
            html.H4("Ultrasound Distance:"),
            html.P(id="ultrasound-data", style={"fontSize": "18px"}),
        ], style={"marginBottom": "20px"}),
        html.Div([
            html.H4("Heading:"),
            html.P(id="heading-data", style={"fontSize": "18px"}),
        ], style={"marginBottom": "20px"}),
    ], style={"textAlign": "center"}),
    dcc.Interval(id="update-interval", interval=1000, n_intervals=0)
])

# Dash Callback
@app.callback(
    [
        Output("connection-status", "children"),
        Output("connection-status", "style"),
        Output("position-data", "children"),
        Output("battery-data", "children"),
        Output("ultrasound-data", "children"),
        Output("heading-data", "children"),
    ],
    [Input("update-interval", "n_intervals")]
)
def update_dashboard(n_intervals):
    # Debugging: Log callback trigger and interval
    print(f"Dashboard callback triggered at interval: {n_intervals}")

    # Access shared data
    with data_lock:
        telemetry_data = shared_telemetry_data.copy()

    # Debugging: Log current shared data
    print(f"Current shared data: {telemetry_data}")

    # Extract data
    position = telemetry_data["position"]
    battery_level = telemetry_data["battery_level"]
    ultrasound_distance = telemetry_data["ultrasound_distance"]
    heading = telemetry_data["heading"]

    # Update connection status
    is_connected = position != {"x": "N/A", "y": "N/A"}
    connection_status = "Connected" if is_connected else "Disconnected"
    connection_style = {"backgroundColor": "green" if is_connected else "red", "color": "white"}

    # Update dashboard data
    position_data = f"X: {position['x']}, Y: {position['y']}" if is_connected else "N/A"
    battery_data = f"{battery_level}%" if is_connected else "N/A"
    ultrasound_data = f"{ultrasound_distance} m" if is_connected else "N/A"
    heading_data = f"{heading}°" if is_connected else "N/A"

    return connection_status, connection_style, position_data, battery_data, ultrasound_data, heading_data

# UDP Listener
def udp_listener():
    """Listen for incoming UDP messages and update shared data."""
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as client_socket:
        client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        try:
            client_socket.bind((UDP_IP, UDP_PORT))
            print(f"Listening on {UDP_IP}:{UDP_PORT}")
        except OSError as e:
            print(f"Error binding to port {UDP_PORT}: {e}")
            return

        while True:
            try:
                data, addr = client_socket.recvfrom(1024)
                telemetry_data = json.loads(data.decode("utf-8"))
                # Debugging: Log received data
                print(f"Received data: {telemetry_data}")

                with data_lock:
                    shared_telemetry_data.update(telemetry_data)

                # Debugging: Log shared data update
                print(f"Updated shared data: {shared_telemetry_data}")
            except Exception as e:
                # Debugging: Log any listener errors
                print(f"Error in UDP listener: {e}")

# Start the UDP Listener in a Thread
listener_thread = threading.Thread(target=udp_listener, daemon=True)
listener_thread.start()

# Run the Dash App
if __name__ == "__main__":
    app.run_server(debug=True)