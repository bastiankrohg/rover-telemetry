import threading
from udp_listener import start_udp_listener
from dashboard_layout import app
from mjpeg_server import start_mjpeg_server

def start_mjpeg():
    """Start the MJPEG server for video streaming."""
    try:
        print("Starting MJPEG server...")
        start_mjpeg_server(port=8081)  # MJPEG server on port 8081
    except Exception as e:
        print(f"Error starting MJPEG server: {e}")

def start_dash():
    """Start the Dash app for the telemetry dashboard."""
    print("Starting Dash app...")
    app.run_server(debug=True)

if __name__ == "__main__":
    print(f"Main process ID (PID): {threading.get_ident()}")

    # Start the MJPEG server in a separate thread
    mjpeg_thread = threading.Thread(target=start_mjpeg, daemon=True)
    mjpeg_thread.start()

    # Start the UDP listener in a separate thread
    udp_thread = threading.Thread(target=start_udp_listener, daemon=True)
    udp_thread.start()

    # Start the Dash app
    start_dash()