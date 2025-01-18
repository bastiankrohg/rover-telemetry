import threading
import socket
import json
from dash import Dash, dcc, html
from dash.dependencies import Output, Input

# External UDP Configuration
EXTERNAL_UDP_IP = "127.0.0.1"
EXTERNAL_UDP_PORT = 50055

# Local UDP Configuration for Dashboard
LOCAL_UDP_IP = "127.0.0.1"
LOCAL_UDP_PORT = 60000

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
    # Connect to the local UDP socket to fetch data
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as client_socket:
            client_socket.settimeout(1.0)  # Timeout after 1 second
            client_socket.bind((LOCAL_UDP_IP, LOCAL_UDP_PORT))
            data, _ = client_socket.recvfrom(1024)
            telemetry_data = json.loads(data.decode("utf-8"))

        # Extract telemetry data
        position = telemetry_data["position"]
        battery_level = telemetry_data["battery_level"]
        ultrasound_distance = telemetry_data["ultrasound_distance"]
        heading = telemetry_data["heading"]

        # Connection status
        connection_status = "Connected"
        connection_style = {"backgroundColor": "green", "color": "white"}

        # Dashboard data
        position_data = f"X: {position['x']}, Y: {position['y']}"
        battery_data = f"{battery_level}%"
        ultrasound_data = f"{ultrasound_distance} m"
        heading_data = f"{heading}°"

    except socket.timeout:
        # No data received
        connection_status = "Disconnected"
        connection_style = {"backgroundColor": "red", "color": "white"}
        position_data = battery_data = ultrasound_data = heading_data = "N/A"

    return connection_status, connection_style, position_data, battery_data, ultrasound_data, heading_data


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
                    telemetry_data = json.loads(data.decode("utf-8"))

                    # Forward data to local UDP port
                    local_socket.sendto(data, (LOCAL_UDP_IP, LOCAL_UDP_PORT))
                    print(f"Forwarded telemetry data: {telemetry_data}")

                except Exception as e:
                    print(f"Error in UDP listener: {e}")


# Start the UDP Listener in a Thread
listener_thread = threading.Thread(target=udp_listener, daemon=True)
listener_thread.start()

# Run the Dash App
if __name__ == "__main__":
    app.run_server(debug=True)