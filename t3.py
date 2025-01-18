from dash import Dash, html, dcc
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import asyncio
import threading
import base64
from collections import deque

from simple_client import TelemetryClient

# Initialize Dash app
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Rover Telemetry Dashboard"

# Layout with placeholders for telemetry and dashboard elements
app.layout = html.Div([
    dcc.Interval(id='update-interval', interval=1000, n_intervals=0),
    dbc.Container([
        dbc.Row([
            dbc.Col([
                html.Div("Video Feed", style={"text-align": "center", "font-size": "1.5em", "font-weight": "bold"}),
                html.Div(id='video-feed', children="Loading video...", style={"text-align": "center", "height": "360px"})
            ], width=6),
            dbc.Col([
                html.Div(id='path-trace', children="Path trace loading..."),
                html.Div(id='system-state-display', children="System state loading..."),
                html.Div(id='position-display', children="Position loading..."),
                html.Div(id='heading-display', children="Heading loading..."),
                html.Div(id='battery-visual', children="Battery loading..."),
                html.Div(id='proximity-indicator', children="Proximity loading..."),
                html.Div(id='backend-status', style={'padding': '10px', 'color': 'red'}, children="Disconnected")
            ], width=6)
        ])
    ])
])

# Initialize the telemetry client
telemetry_client = TelemetryClient(host="localhost:50051")  # Replace with your server address

# Variable to store telemetry data
latest_telemetry = None
backend_status = {"connected": False}

# Maintain a deque to store path history
path_history = deque(maxlen=1000)

# Function to fetch video frame
def fetch_video_frame(rtsp_url):
    try:
        import cv2
        cap = cv2.VideoCapture(rtsp_url)
        ret, frame = cap.read()
        if not ret:
            raise ValueError("Failed to fetch video frame.")
        frame = cv2.resize(frame, (640, 360))
        _, buffer = cv2.imencode(".jpg", frame)
        cap.release()
        return base64.b64encode(buffer).decode("utf-8")
    except Exception as e:
        print(f"Error fetching video frame: {e}")
        return None

# Asynchronous telemetry stream task
async def telemetry_stream_task():
    global latest_telemetry, backend_status
    try:
        await telemetry_client.connect()
        backend_status["connected"] = True
        async for telemetry_data in telemetry_client.stream_telemetry():
            latest_telemetry = telemetry_data
            if telemetry_data.position:
                path_history.append((telemetry_data.position.x, telemetry_data.position.y))
    except Exception as e:
        print(f"Error in telemetry stream: {e}")
        backend_status["connected"] = False
    finally:
        await telemetry_client.close()

# Start telemetry streaming in a separate thread
def start_telemetry_stream():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(telemetry_stream_task())

threading.Thread(target=start_telemetry_stream, daemon=True).start()

# Dash callback to update the dashboard
@app.callback(
    [
        Output("path-trace", "children"),
        Output("system-state-display", "children"),
        Output("position-display", "children"),
        Output("heading-display", "children"),
        Output("battery-visual", "children"),
        Output("proximity-indicator", "children"),
        Output("video-feed", "children"),
        Output("backend-status", "children"),
        Output("backend-status", "style")
    ],
    [Input("update-interval", "n_intervals")]
)
def update_dashboard(n_intervals):
    global latest_telemetry, backend_status
    if backend_status["connected"]:
        backend_status_text = "Connected"
        backend_status_style = {'color': 'green'}
    else:
        backend_status_text = "Disconnected"
        backend_status_style = {'color': 'red'}

    if latest_telemetry:
        position = latest_telemetry.position
        telemetry_display = {
            "position": f"x: {position.x:.2f}, y: {position.y:.2f}",
            "heading": f"{latest_telemetry.heading:.2f}°",
            "battery": f"{latest_telemetry.battery_level:.2f}%",
            "proximity": f"{latest_telemetry.ultrasound_distance:.2f}m",
        }
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
        video_feed = html.Img(
            src=f"data:image/jpeg;base64,{fetch_video_frame('rtsp://localhost:5054/cam')}",
            style={"width": "100%", "height": "100%", "object-fit": "contain"}
        )
    else:
        telemetry_display = "No telemetry data available."
        path_trace_figure = {"data": [], "layout": {"xaxis": {"range": [-20, 20]}, "yaxis": {"range": [-20, 20]}}}
        video_feed = html.Div("No video feed available", style={"text-align": "center", "color": "red"})

    return (
        dcc.Graph(figure=path_trace_figure),
        f"System State: OK",
        telemetry_display["position"],
        telemetry_display["heading"],
        telemetry_display["battery"],
        telemetry_display["proximity"],
        video_feed,
        backend_status_text,
        backend_status_style
    )

if __name__ == '__main__':
    app.run_server(debug=True)