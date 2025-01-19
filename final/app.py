import threading
from udp_listener import start_udp_listener
from dashboard_layout import app
from mjpeg_server import start_mjpeg_server

# Start MJPEG server in a thread
def start_mjpeg():
    try:
        print("Starting MJPEG server...")
        start_mjpeg_server(port=8081)  # MJPEG server on port 8081
    except Exception as e:
        print(f"Error starting MJPEG server: {e}")

# Start Dash app in a thread
def start_dash():
    print("Starting Dash app...")
    app.run_server(debug=True)

if __name__ == "__main__":
    print(f"Main process ID (PID): {threading.get_ident()}")

    # Start the MJPEG server
    mjpeg_thread = threading.Thread(target=start_mjpeg, daemon=True)
    mjpeg_thread.start()

    # Start the UDP listener
    udp_thread = threading.Thread(target=start_udp_listener, daemon=True)
    udp_thread.start()

    # Start the Dash app
    start_dash()