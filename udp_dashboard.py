import threading
import socket
import json
from dash import Dash, dcc, html
from dash.dependencies import Output, Input
import plotly.graph_objs as go

# External UDP Configuration
EXTERNAL_UDP_IP = "127.0.0.1"
EXTERNAL_UDP_PORT = 50055

# Local UDP Configuration for Dashboard
LOCAL_UDP_IP = "127.0.0.1"
LOCAL_UDP_PORT = 60000

# Dash App Initialization
app = Dash(__name__)

# Buffer for plotting (up to 100 data points)
data_buffer = {
    "x": [],
    "y": [],
    "battery": [],
    "ultrasound": [],
    "heading": []
}

# Layout with Improved GUI
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
        dcc.Graph(id="position-graph", style={"display": "inline-block", "width": "48%"}),
        dcc.Graph(id="battery-graph", style={"display": "inline-block", "width": "48%"}),
    ]),
    html.Div([
        dcc.Graph(id="ultrasound-graph", style={"display": "inline-block", "width": "48%"}),
        dcc.Graph(id="heading-graph", style={"display": "inline-block", "width": "48%"}),
    ]),
    dcc.Interval(id="update-interval", interval=1000, n_intervals=0)
])

# Dash Callback for GUI Updates
@app.callback(
    [
        Output("connection-status", "children"),
        Output("connection-status", "style"),
        Output("position-graph", "figure"),
        Output("battery-graph", "figure"),
        Output("ultrasound-graph", "figure"),
        Output("heading-graph", "figure"),
    ],
    [Input("update-interval", "n_intervals")]
)
def update_dashboard(n_intervals):
    try:
        # Connect to the local UDP socket to fetch data
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

        # Append data to the buffer
        data_buffer["x"].append(position["x"])
        data_buffer["y"].append(position["y"])
        data_buffer["battery"].append(battery_level)
        data_buffer["ultrasound"].append(ultrasound_distance)
        data_buffer["heading"].append(heading)

        # Limit buffer size to 100 data points
        for key in data_buffer:
            if len(data_buffer[key]) > 100:
                data_buffer[key].pop(0)

        # Connection status
        connection_status = "Connected"
        connection_style = {"backgroundColor": "green", "color": "white"}

    except socket.timeout:
        # No data received
        connection_status = "Disconnected"
        connection_style = {"backgroundColor": "red", "color": "white"}

    # Position graph
    position_fig = go.Figure(data=go.Scatter(
        x=data_buffer["x"],
        y=data_buffer["y"],
        mode="lines+markers",
        name="Position"
    ))
    position_fig.update_layout(title="Position (X, Y)", xaxis_title="X", yaxis_title="Y")

    # Battery graph
    battery_fig = go.Figure(data=go.Scatter(
        x=list(range(len(data_buffer["battery"]))),
        y=data_buffer["battery"],
        mode="lines+markers",
        name="Battery Level"
    ))
    battery_fig.update_layout(title="Battery Level (%)", xaxis_title="Time", yaxis=dict(range=[0, 100]))

    # Ultrasound graph
    ultrasound_fig = go.Figure(data=go.Scatter(
        x=list(range(len(data_buffer["ultrasound"]))),
        y=data_buffer["ultrasound"],
        mode="lines+markers",
        name="Ultrasound Distance"
    ))
    ultrasound_fig.update_layout(title="Ultrasound Distance (m)", xaxis_title="Time", yaxis_title="Distance")

    # Heading graph
    heading_fig = go.Figure(data=go.Scatter(
        x=list(range(len(data_buffer["heading"]))),
        y=data_buffer["heading"],
        mode="lines+markers",
        name="Heading"
    ))
    heading_fig.update_layout(title="Heading (°)", xaxis_title="Time", yaxis_title="Degrees")

    return connection_status, connection_style, position_fig, battery_fig, ultrasound_fig, heading_fig


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