import socket
import json
import time

UDP_IP = "127.0.0.1"
UDP_PORT = 50054

def generate_dummy_data():
    """Generate dummy telemetry data."""
    return {
        "ultrasound_distance": 5.0,
        "odometer": 12.3,
        "position": {"x": 10.5, "y": -3.2},
        "heading": 45.0,
        "search_mode": 0,
        "resources_found": [{"type": "rock", "location": {"x": 7.2, "y": -1.5}}],
        "battery_level": 87.5
    }

def start_dummy_udp_server():
    """Start a dummy UDP server to send telemetry data."""
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as server_socket:
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        print(f"Dummy UDP server running on {UDP_IP}:{UDP_PORT}")
        while True:
            dummy_data = json.dumps(generate_dummy_data()).encode('utf-8')
            server_socket.sendto(dummy_data, (UDP_IP, UDP_PORT))
            print(f"Sent: {dummy_data.decode('utf-8')}")
            time.sleep(1)

if __name__ == "__main__":
    start_dummy_udp_server()