from dash import Dash, html

# Dash App Initialization
app = Dash(__name__)
app.title = "Rover Telemetry Dashboard"

# MJPEG Stream Layout
app.layout = html.Div([
    html.H1("Rover Telemetry Dashboard", style={"text-align": "center"}),
    html.Div("Live Video Feed", style={"text-align": "center", "font-size": "20px"}),
    html.Img(
        src="http://127.0.0.1:8080/",  # Replace with your MJPEG server URL
        style={"width": "640px", "height": "480px", "display": "block", "margin": "auto"},
    )
])

if __name__ == "__main__":
    app.run_server(debug=True)