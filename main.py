import threading
import socket
import json
import time
from collections import deque
from dash import Dash, dcc, html
from dash.dependencies import Output, Input
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
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)
app.title = "Rover Telemetry Dashboard"

# Buffers for telemetry data
path_history = deque(maxlen=1000)
data_buffer = {"battery": [], "ultrasound": []}
resource_list = []

# Navbar
navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dcc.Link("Telemetry Dashboard", href="/", className="nav-link")),
        dbc.NavItem(dcc.Link("Sensor Measurements", href="/sensors", className="nav-link")),
    ],
    brand="Rover Dashboard",
    color="primary",
    dark=True,
)

# Telemetry Dashboard Layout
def telemetry_dashboard():
    return dbc.Container(
        [
            html.H1("Rover Telemetry Dashboard", className="text-center my-4"),
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
        ],
        fluid=True,
    )

# Sensor Measurements Layout
def sensor_measurements():
    return dbc.Container(
        [
            html.H1("Sensor Measurements", className="text-center my-4"),
            dbc.Row(
                [
                    dbc.Col(
                        dcc.Graph(id="battery-graph", style={"height": "400px"}), width=6
                    ),
                    dbc.Col(
                        dcc.Graph(id="ultrasound-graph", style={"height": "400px"}), width=6
                    ),
                ],
                className="mb-4",
            ),
            dbc.Row(
                [
                    dbc.Col(html.H4("Detected Resources"), width=12),
                    dbc.Col(
                        dbc.Table(
                            id="resource-table",
                            striped=True,
                            bordered=True,
                            hover=True,
                        ),
                        width=12,
                    ),
                ],
                className="mb-4",
            ),
        ],
        fluid=True,
    )

# App Layout
app.layout = html.Div(
    [
        dcc.Location(id="url", refresh=False),  # For navigation
        navbar,
        html.Div(id="page-content"),  # Content updated dynamically
        dcc.Interval(id="update-interval", interval=1000, n_intervals=0),
    ]
)

# Page Content Callback
@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def display_page(pathname):
    if pathname == "/sensors":
        return sensor_measurements()
    else:
        return telemetry_dashboard()

# Sensor Measurements Callback
@app.callback(
    [
        Output("battery-graph", "figure"),
        Output("ultrasound-graph", "figure"),
        Output("resource-table", "children"),
    ],
    [Input("update-interval", "n_intervals")],
)
def update_sensor_page(n_intervals):
    global resource_list

    # Dummy resource list
    resource_list = [{"Resource": f"Resource {i+1}", "Coordinates": f"({i}, {i+1})"} for i in range(len(data_buffer["battery"]))]

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

    # Resource table
    resource_table = [
        html.Thead(html.Tr([html.Th("Resource"), html.Th("Coordinates")])),
        html.Tbody(
            [
                html.Tr([html.Td(resource["Resource"]), html.Td(resource["Coordinates"])])
                for resource in resource_list
            ]
        ),
    ]

    return battery_fig, ultrasound_fig, resource_table


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
                    # Append telemetry data to buffers
                    data_buffer["battery"].append(telemetry_data["battery_level"])
                    data_buffer["ultrasound"].append(telemetry_data["ultrasound_distance"])

                    # Limit buffer size
                    for key in data_buffer:
                        if len(data_buffer[key]) > 100:
                            data_buffer[key].pop(0)

                    local_socket.sendto(data, (LOCAL_UDP_IP, LOCAL_UDP_PORT))
                except Exception as e:
                    print(f"Error in UDP listener: {e}")


# Start the UDP Listener
listener_thread = threading.Thread(target=udp_listener, daemon=True)
listener_thread.start()

# Run the Dash App
if __name__ == "__main__":
    app.run_server(debug=True)