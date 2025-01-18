import socket
import json
import threading
from queue import Queue

from dash import Dash, dcc, html
from dash.dependencies import Output, Input
import plotly.graph_objs as go
import dash_bootstrap_components as dbc

# UDP Configuration
UDP_IP = "127.0.0.1"
UDP_PORT = 50054
telemetry_queue = Queue()  # Shared queue for communication

# Buffer for plotting
data_buffer = {
    "x": [],
    "y": [],
    "battery": [],
    "ultrasound": [],
    "heading": []
}


def udp_listener():
    """Listen for incoming UDP messages."""
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as client_socket:
        client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # Attempt to bind to the specified port
        try:
            client_socket.bind((UDP_IP, UDP_PORT))
            print(f"Listening on {UDP_IP}:{UDP_PORT}")
        except OSError as e:
            print(f"Port {UDP_PORT} is in use. Trying a different port...")
            client_socket.bind((UDP_IP, 0))  # Bind to an available port
            print(f"Listening on {client_socket.getsockname()}")

        while True:
            data, addr = client_socket.recvfrom(1024)
            telemetry_data = json.loads(data.decode("utf-8"))
            telemetry_queue.put(telemetry_data)  # Push data to the queue
            print(f"Received from {addr}: {telemetry_data}")


# Start UDP listener in a separate thread
listener_thread = threading.Thread(target=udp_listener, daemon=True)
listener_thread.start()

# Create a Dash app
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Define the layout of the dashboard
app.layout = html.Div([
    html.H1("Telemetry Dashboard", style={"textAlign": "center"}),
    html.Div([
        dcc.Graph(id="position_graph", style={"display": "inline-block", "width": "48%"}),
        dcc.Graph(id="battery_graph", style={"display": "inline-block", "width": "48%"})
    ]),
    html.Div([
        dcc.Graph(id="ultrasound_graph", style={"display": "inline-block", "width": "48%"}),
        dcc.Graph(id="heading_graph", style={"display": "inline-block", "width": "48%"})
    ]),
    dcc.Interval(id="update_interval", interval=1000, n_intervals=0)  # Update every second
])


@app.callback(
    [
        Output("position_graph", "figure"),
        Output("battery_graph", "figure"),
        Output("ultrasound_graph", "figure"),
        Output("heading_graph", "figure")
    ],
    [Input("update_interval", "n_intervals")]
)
def update_graphs(n_intervals):
    while not telemetry_queue.empty():
        telemetry_data = telemetry_queue.get()
        # Update buffers
        data_buffer["x"].append(telemetry_data["position"]["x"])
        data_buffer["y"].append(telemetry_data["position"]["y"])
        data_buffer["battery"].append(telemetry_data["battery_level"])
        data_buffer["ultrasound"].append(telemetry_data["ultrasound_distance"])
        data_buffer["heading"].append(telemetry_data["heading"])

        # Limit buffer size
        for key in data_buffer:
            if len(data_buffer[key]) > 100:  # Keep only the latest 100 data points
                data_buffer[key].pop(0)

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

    return position_fig, battery_fig, ultrasound_fig, heading_fig


if __name__ == "__main__":
    app.run_server(debug=True)