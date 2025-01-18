from dash import Dash, html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
from test.layout import create_layout
from grpc.grpc_client import TelemetryClient
import asyncio
import cv2
import base64
from collections import deque

# Initialize Dash app
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Rover Telemetry Dashboard"
app.layout = create_layout()

# Initialize gRPC client
telemetry_client = TelemetryClient(host="<pi-ip-address>")

# Maintain a deque to store path history for the path trace visualization
path_history = deque(maxlen=1000)  # Store up to 1000 points


def fetch_telemetry_sync():
    """
    Fetch telemetry synchronously using asyncio.run.
    """
    try:
        return asyncio.run(telemetry_client.stream_telemetry().__anext__())
    except Exception as e:
        print(f"Error fetching telemetry: {e}")
        return None


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
    ],
    [Input("update-interval", "n_intervals")],
)
def update_dashboard(n_intervals):
    # Fetch telemetry data
    telemetry_data = fetch_telemetry_sync()
    if not telemetry_data:
        telemetry_data = {
            "ultrasound_distance": 0.0,
            "odometer": 0.0,
            "current_position": "x: 0.0, y: 0.0",
            "heading": 0.0,
            "search_mode": "N/A",
            "resources_found": [],
            "battery_status": "100%",
        }

    # Parse telemetry data
    position_str = telemetry_data["current_position"]
    position_parts = position_str.replace("x:", "").replace("y:", "").split(",")
    try:
        position = (float(position_parts[0]), float(position_parts[1]))
        path_history.append(position)  # Append position to path history
    except (ValueError, IndexError):
        position = (0.0, 0.0)

    heading = telemetry_data["heading"]
    battery_status = telemetry_data["battery_status"]
    proximity_distance = telemetry_data["ultrasound_distance"]

    # Generate path trace
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
    #rover2 = "rtsp://rover2.local:5054/cam"
    #rtsp_url = "rtsp://192.168.0.168:5054/cam"
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

    return (
        path_trace_figure,
        f"System State: OK",
        f"Position: {position}",
        f"Heading: {heading}°",
        battery_visual,
        proximity_indicator,
        video_feed,
    )


if __name__ == "__main__":
    app.run_server(debug=True)