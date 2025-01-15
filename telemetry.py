from dash import Dash, html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
from layout import create_layout
from grpc_client import TelemetryClient
import asyncio
import cv2
import base64

# Initialize Dash app
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Rover Telemetry Dashboard"
app.layout = create_layout()

# Initialize gRPC client
telemetry_client = TelemetryClient(host="<pi-ip-address>")

# Coroutine for streaming telemetry
async def stream_telemetry():
    async for telemetry_data in telemetry_client.stream_telemetry():
        yield telemetry_data

# Function to fetch video frame
def fetch_video_frame(rtsp_url):
    cap = cv2.VideoCapture(rtsp_url)
    ret, frame = cap.read()
    if not ret:
        cap.release()
        return None
    frame = cv2.resize(frame, (640, 360))
    _, buffer = cv2.imencode(".jpg", frame)
    cap.release()
    return base64.b64encode(buffer).decode("utf-8")

# Callback to update dashboard
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
    # Telemetry data defaults
    default_data = {
        "ultrasound_distance": 0.0,
        "odometer": 0.0,
        "current_position": "x: 0.0, y: 0.0",
        "heading": 0.0,
        "search_mode": "N/A",
        "resources_found": [],
        "battery_status": "100%",
    }

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    # Fetch telemetry data
    try:
        telemetry_data = loop.run_until_complete(
            telemetry_client.stream_telemetry().__anext__()
        )
    except StopIteration:
        telemetry_data = default_data

    # Extract telemetry data
    position = telemetry_data["current_position"]
    heading = telemetry_data["heading"]
    battery_status = telemetry_data["battery_status"]
    proximity_distance = telemetry_data["ultrasound_distance"]

    # Generate visualizations
    path_trace_figure = {
        "data": [
            {
                "x": [float(position.split(",")[0].split(":")[1])],
                "y": [float(position.split(",")[1].split(":")[1])],
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
    battery_visual = f"Battery: {battery_status}"
    proximity_indicator = html.Div(
        f"Proximity: {proximity_distance:.2f}m",
        style={
            "color": "green" if proximity_distance > 2 else "orange" if proximity_distance > 1 else "red",
        },
    )

    # Fetch video feed
    rtsp_url = "rtsp://<pi-ip-address>:5054/cam"
    frame = fetch_video_frame(rtsp_url)
    video_feed = html.Img(
        src=f"data:image/jpeg;base64,{frame}" if frame else "",
        style={"width": "100%", "height": "100%", "object-fit": "contain"},
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