import socket
import time
import math
import json
from collections import deque

# Local UDP configuration
LOCAL_UDP_IP = "127.0.0.1"
LOCAL_UDP_PORT = 60000

# Buffers for telemetry data
path_history = deque(maxlen=1000)
data_buffer = {"x": [], "y": [], "battery": [], "ultrasound": [], "heading": []}
last_update_time = {"timestamp": None}


def fetch_and_process_telemetry_data():
    """Fetch telemetry data from UDP and process it for the dashboard."""
    global last_update_time
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.settimeout(1.0)
            sock.bind((LOCAL_UDP_IP, LOCAL_UDP_PORT))
            print(f"Listening for telemetry on {LOCAL_UDP_IP}:{LOCAL_UDP_PORT}")
            data, _ = sock.recvfrom(1024)
            telemetry_data = json.loads(data.decode("utf-8"))

            # Debug: Print received telemetry data
            print("Received telemetry data:", telemetry_data)

        # Process telemetry data
        position = telemetry_data["position"]
        heading = telemetry_data["heading"]
        battery = telemetry_data["battery_level"]
        ultrasound = telemetry_data["ultrasound_distance"]

        data_buffer["x"].append(position["x"])
        data_buffer["y"].append(position["y"])
        data_buffer["battery"].append(battery)
        data_buffer["ultrasound"].append(ultrasound)
        data_buffer["heading"].append(heading)
        path_history.append((position["x"], position["y"]))

        # Update last update time
        last_update_time["timestamp"] = time.time()

        # Prepare dashboard components
        backend_status = "🟢 Rover Telemetry Dashboard"
        path_trace_figure = {
            "data": [
                {
                    "x": [p[0] for p in path_history],
                    "y": [p[1] for p in path_history],
                    "type": "scatter",
                    "mode": "lines+markers",
                },
            ],
            "layout": {"title": "Path Trace"},
        }

        return (
            backend_status,
            path_trace_figure,
            "System State: OK",
            f"x: {position['x']:.2f}, y: {position['y']:.2f}",
            f"{heading:.2f}°",
            f"{battery:.2f}%",
            f"{ultrasound:.2f} m",
            {},  # Placeholder for additional data
            {},  # Placeholder for additional data
        )

    except socket.timeout:
        print("No telemetry data received (timeout).")
        return (
            "🔴 No telemetry data available",
            {"data": [], "layout": {"title": "Path Trace"}},
            "No data",
            "N/A",
            "N/A",
            "N/A",
            "N/A",
            {"data": [], "layout": {"title": "Battery Over Time"}},
            {"data": [], "layout": {"title": "Ultrasound Over Time"}},
        )