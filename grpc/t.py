import threading
import asyncio
from dash import Dash, html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
from test.layout import create_layout
from grpc.grpc_client import TelemetryClient
import cv2
import base64
from collections import deque

# Initialize Dash app
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Rover Telemetry Dashboard"
app.layout = create_layout()

# Initialize gRPC client
telemetry_client = TelemetryClient(host="127.0.0.1")  # Dummy server address
path_history = deque(maxlen=1000)  # Store up to 1000 points
backend_connected = False  # Track backend connection
latest_telemetry_data = {}  # Store the latest telemetry data globally
stop_event = asyncio.Event()  # Event to signal stopping the telemetry stream


async def telemetry_stream_task():
    """
    Coroutine to fetch telemetry data from the gRPC server.
    """
    global backend_connected, latest_telemetry_data
    while not stop_event.is_set():
        try:
            async for telemetry_data in telemetry_client.stream_telemetry():
                latest_telemetry_data = telemetry_data
                backend_connected = True
        except Exception as e:
            print(f"Error in telemetry stream: {e}")
            backend_connected = False
        await asyncio.sleep(1)  # Throttle to reduce CPU usage


def start_telemetry_stream():
    """
    Function to start the telemetry stream task in a dedicated event loop.
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(telemetry_stream_task())
    finally:
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()


def fetch_video_frame(rtsp_url):
    """
    Fetch video frame from RTSP stream.
    """
    cap = cv2.VideoCapture(rtsp_url)
    ret, frame = cap.read()
    if not ret:
        cap.release()
        return None
    frame = cv2.resize(frame, (640, 360))
    _, buffer = cv2.imencode(".jpg", frame)
    cap.release()
    return base64.b64encode(buffer).decode("utf-8")


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
    [Input("update-interval", "n_intervals")],
)
def update_dashboard(n_intervals):
    global backend_connected

    # Default telemetry data (if the backend is disconnected)
    telemetry_data = {
        "ultrasound_distance": 1.5,
        "odometer": 5.0,
        "current_position": "x: 10.0, y: -5.0",
        "heading": 90.0,
        "search_mode": "Pattern Pursuit",
        "resources_found": [{"type": "rock", "x_coordinate": 12.0, "y_coordinate": -3.0}],
        "battery_status": "85%",
    }

    # Use live telemetry if available
    if backend_connected and latest_telemetry_data:
        telemetry_data = latest_telemetry_data

    # Parse telemetry data
    position_str = telemetry_data["current_position"]
    position_parts = position_str.replace("x:", "").replace("y:", "").split(",")
    try:
        position = (float(position_parts[0]), float(position_parts[1]))
        path_history.append(position)
    except (ValueError, IndexError):
        position = (0.0, 0.0)

    heading = telemetry_data["heading"]
    battery_status = telemetry_data["battery_status"]
    proximity_distance = telemetry_data["ultrasound_distance"]

    # Path trace visualization
    path_trace_figure = {
        "data": [
            {
                "x": [p[0] for p in path_history],
                "y": [p[1] for p in path_history],
                "type": "scatter",
                "mode": "lines+markers",
            }
        ],
        "layout": {
            "xaxis": {"range": [-20, 20]},
            "yaxis": {"range": [-20, 20]},
            "title": "Path Trace",
        },
    }

    # Battery visual
    battery_visual = html.Div(
        children=[
            html.Div("Battery:", style={"font-weight": "bold"}),
            html.Div(f"{battery_status}", style={"font-size": "1.5em"}),
        ],
        style={
            "text-align": "center",
            "padding": "10px",
            "border": "2px solid black",
            "border-radius": "10px",
            "background-color": "#cce5ff" if "100" in battery_status else "#f8d7da",
        },
    )

    # Proximity indicator
    proximity_color = (
        "green" if proximity_distance > 2 else "orange" if proximity_distance > 1 else "red"
    )
    proximity_indicator = html.Div(
        f"Proximity: {proximity_distance:.2f}m",
        style={
            "color": proximity_color,
            "font-size": "1.5em",
            "text-align": "center",
        },
    )

    # Fetch video feed
    rtsp_url = "rtsp://192.168.0.169:5054/cam"
    frame = fetch_video_frame(rtsp_url)
    video_feed = (
        html.Img(
            src=f"data:image/jpeg;base64,{frame}",
            style={"width": "100%", "height": "100%", "object-fit": "contain"},
        )
        if frame
        else html.Div(
            "No video feed available",
            style={"text-align": "center", "font-size": "1.5em", "color": "red"},
        )
    )

    # Backend connection status
    backend_status = "Connected" if backend_connected else "Disconnected"
    backend_status_style = {
        "color": "green" if backend_connected else "red",
        "font-size": "1.5em",
        "text-align": "center",
    }

    return (
        path_trace_figure,
        f"System State: OK",
        f"Position: {position}",
        f"Heading: {heading}°",
        battery_visual,
        proximity_indicator,
        video_feed,
        backend_status,
        backend_status_style,
    )


if __name__ == "__main__":
    # Start the telemetry stream in a separate thread
    threading.Thread(target=start_telemetry_stream, daemon=True).start()

    # Start the Dash server
    app.run_server(debug=True)