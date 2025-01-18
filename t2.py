from dash import Dash, html, dcc
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import asyncio
import threading

from simple_client import TelemetryClient

# Initialize Dash app
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Rover Telemetry Dashboard"

# Define the layout
app.layout = html.Div([
    dcc.Interval(id='update-interval', interval=1000, n_intervals=0),
    html.Div(id='telemetry-data'),
    html.Div(id='backend-status', style={'color': 'red'})
])

# Initialize the telemetry client
telemetry_client = TelemetryClient(host="localhost:50051")  # Replace with your server address

# Variable to store the most recent telemetry data
latest_telemetry = None
backend_status = {"connected": False}

# Function to stream telemetry data asynchronously
async def telemetry_stream_task():
    global latest_telemetry, backend_status
    try:
        await telemetry_client.connect()
        backend_status["connected"] = True
        async for telemetry_data in telemetry_client.stream_telemetry():
            latest_telemetry = telemetry_data
    except Exception as e:
        print(f"Error in telemetry stream: {e}")
        backend_status["connected"] = False
    finally:
        await telemetry_client.close()

# Start the telemetry stream in a separate thread
def start_telemetry_stream():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(telemetry_stream_task())

threading.Thread(target=start_telemetry_stream, daemon=True).start()

# Dash callback to update the dashboard
@app.callback(
    [Output('telemetry-data', 'children'),
     Output('backend-status', 'children'),
     Output('backend-status', 'style')],
    [Input('update-interval', 'n_intervals')]
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
        telemetry_display = f"Telemetry Data: {latest_telemetry}"
    else:
        telemetry_display = "No telemetry data available."

    return telemetry_display, backend_status_text, backend_status_style

if __name__ == '__main__':
    app.run_server(debug=True)