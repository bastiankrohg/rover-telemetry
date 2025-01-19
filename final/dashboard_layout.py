# dashboard_layout.py
from dash import Dash, dcc, html
import dash_bootstrap_components as dbc
from dash.dependencies import Output, Input
from udp_listener import last_received_data
import json

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Rover Telemetry Dashboard"

# Updated layout definition in dashboard_layout.py
app.layout = html.Div([
    dcc.Interval(id="update-interval", interval=1000, n_intervals=0),
    dbc.Container([
        html.H1("Rover Telemetry Dashboard", className="text-center my-4"),
        html.Div(id="backend-status", className="text-center my-2", style={"font-size": "1.5em", "font-weight": "bold"}),
        dbc.Row([
            dbc.Col(dcc.Graph(id="path-trace", style={"height": "360px"}), width=6),  # Add path-trace
            dbc.Col(html.Div([
                html.Div("Live Video Feed", style={"text-align": "center", "font-size": "20px"}),
                html.Img(
                    src="http://127.0.0.1:8081/",  # MJPEG server URL
                    style={"width": "100%", "height": "auto", "border": "2px solid black"}
                ),
            ], style={"height": "360px", "background-color": "lightgray"}), width=6),
        ]),
        dbc.Row([
            dbc.Col(html.Div(id="system-state-display"), width=3),  # Add system-state-display
            dbc.Col(html.Div(id="position-display"), width=3),      # Add position-display
            dbc.Col(html.Div(id="heading-display"), width=3),       # Add heading-display
            dbc.Col(html.Div(id="battery-visual"), width=3),        # Add battery-visual
        ], className="mb-3"),
        dbc.Row([
            dbc.Col(html.Div(id="proximity-indicator"), width=6),   # Add proximity-indicator
        ]),
        html.Hr(),
        html.H3("Sensor Measurement History", className="text-center my-4", style={"font-weight": "bold"}),
        dbc.Row([
            dbc.Col(dcc.Graph(id="battery-graph", style={"height": "400px"}), width=6),  # Add battery-graph
            dbc.Col(dcc.Graph(id="ultrasound-graph", style={"height": "400px"}), width=6),  # Add ultrasound-graph
        ]),
    ], fluid=True),
])

@app.callback(
    [
        Output("backend-status", "children"),
        Output("path-trace", "figure"),
        Output("system-state-display", "children"),
        Output("position-display", "children"),
        Output("heading-display", "children"),
        Output("battery-visual", "children"),
        Output("proximity-indicator", "children"),
        Output("battery-graph", "figure"),
        Output("ultrasound-graph", "figure"),
    ],
    [Input("update-interval", "n_intervals")]
)
def update_dashboard(n_intervals):
    try:
        if not last_received_data:
            raise ValueError("No telemetry data available yet.")

        telemetry_data = json.loads(last_received_data)

        # Extract telemetry data
        position = telemetry_data["position"]
        heading = telemetry_data["heading"]
        battery = telemetry_data["battery_level"]
        ultrasound = telemetry_data["ultrasound_distance"]
        system_state = telemetry_data.get("system_state", {})

        # Prepare data for dashboard components
        path_trace_figure = {
            "data": [
                {
                    "x": [position["x"]],
                    "y": [position["y"]],
                    "type": "scatter",
                    "mode": "lines+markers",
                    "name": "Path",
                },
            ],
            "layout": {
                "title": "Path Trace",
                "xaxis": {"range": [-20, 20]},
                "yaxis": {"range": [-20, 20]}
            },
        }

        battery_graph = {
            "data": [{"x": list(range(len([battery]))), "y": [battery], "type": "line"}],
            "layout": {"title": "Battery Over Time", "xaxis": {"title": "Time"}, "yaxis": {"title": "%"}},
        }

        ultrasound_graph = {
            "data": [{"x": list(range(len([ultrasound]))), "y": [ultrasound], "type": "line"}],
            "layout": {"title": "Ultrasound Over Time", "xaxis": {"title": "Time"}, "yaxis": {"title": "Distance (m)"}},
        }

        system_state_display = (
            f"CPU: {system_state.get('cpu_usage', 'N/A')}% | "
            f"Memory: {system_state.get('memory_available', 'N/A')} MB | "
            f"Disk: {system_state.get('disk_usage', 'N/A')}%"
        )

        # Return updates for dashboard
        return (
            "🟢 Backend Connected",
            path_trace_figure,
            system_state_display,
            f"x: {position['x']:.2f}, y: {position['y']:.2f}",
            f"{heading:.2f}°",
            f"{battery:.2f}%",
            f"{ultrasound:.2f} m",
            battery_graph,
            ultrasound_graph,
        )

    except ValueError as ve:
        print(f"Dashboard update warning: {ve}")
        return (
            "🔴 No data received",
            {"data": [], "layout": {"title": "Path Trace"}},
            "No system state available",
            "N/A",
            "N/A",
            "N/A",
            "N/A",
            {"data": [], "layout": {"title": "Battery Over Time"}},
            {"data": [], "layout": {"title": "Ultrasound Over Time"}},
        )
    except Exception as e:
        print(f"Error updating dashboard: {e}")
        return (
            "🔴 Backend Disconnected",
            {"data": [], "layout": {"title": "Path Trace"}},
            "No system state available",
            "N/A",
            "N/A",
            "N/A",
            "N/A",
            {"data": [], "layout": {"title": "Battery Over Time"}},
            {"data": [], "layout": {"title": "Ultrasound Over Time"}},
        )