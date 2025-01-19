import socket
import threading
import json

# External UDP Configuration
EXTERNAL_UDP_IP = "127.0.0.1"
EXTERNAL_UDP_PORT = 50055

# Local UDP Configuration for Dashboard
LOCAL_UDP_IP = "127.0.0.1"
LOCAL_UDP_PORT = 60000

# Global variable to store the last received telemetry data
last_received_data = json.dumps({})  # Initialize as an empty JSON object

def start_udp_listener():
    global last_received_data

    def forward_data():
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as external_socket:
            external_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                external_socket.bind((EXTERNAL_UDP_IP, EXTERNAL_UDP_PORT))
                print(f"Listening on {EXTERNAL_UDP_IP}:{EXTERNAL_UDP_PORT}")
            except OSError as e:
                print(f"Error binding to external port: {e}")
                return

            with socket.socket(socket.SOCK_DGRAM) as local_socket:
                while True:
                    try:
                        data, addr = external_socket.recvfrom(1024)  # Receive data
                        last_received_data = data.decode("utf-8")  # Update global variable
                        print(f"Received data: {last_received_data}")  # Debugging
                        local_socket.sendto(data, (LOCAL_UDP_IP, LOCAL_UDP_PORT))  # Forward data
                    except Exception as e:
                        print(f"Error in UDP listener: {e}")

    # Start the forwarding loop in a separate thread
    threading.Thread(target=forward_data, daemon=True).start()