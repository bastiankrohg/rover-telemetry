import socket
import json
import time
import math
from system_monitor import get_system_state  # Import system state monitoring module

# UDP Configuration
UDP_IP = "127.0.0.1"  # TODO LG Replace with the actual IP address
UDP_PORT = 50055  # TODO LG Replace with the actual port

# Create a UDP socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Allow socket reuse

try:
    print(f"Starting server on {UDP_IP}:{UDP_PORT}")
    while True:
        # TODO LG Fetch actual telemetry data
            # TODO LG Position
            # TODO LG Heading
            # TODO LG Battery Level
            # TODO LG Ultrasound
            # TODO LG Anything else?

        # Generate telemetry data
        telemetry_data = {
            "position": {"x": 10 * math.cos(time.time()), "y": 10 * math.sin(time.time())},  # TODO LG Replace
            "heading": (time.time() * 10) % 360,  # TODO LG Replace
            "battery_level": 100 - (time.time() % 100),  # TODO LG Replace
            "ultrasound_distance": 5.0,  # TODO LG Replace
            "system_state": get_system_state(),  # Include system state data
        }

        # Send telemetry data over UDP
        server_socket.sendto(json.dumps(telemetry_data).encode("utf-8"), (UDP_IP, UDP_PORT))
        time.sleep(1)  # Send updates every second

except KeyboardInterrupt:
    print("Shutting down telemetry server.")
finally:
    server_socket.close()