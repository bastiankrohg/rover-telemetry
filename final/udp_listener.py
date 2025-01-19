import socket
import threading

# Configuration for external and local UDP communication
EXTERNAL_UDP_IP = "127.0.0.1"
EXTERNAL_UDP_PORT = 50055
LOCAL_UDP_IP = "127.0.0.1"
LOCAL_UDP_PORT = 60000

# Shared variable to store the latest received data
last_received_data = None

def start_udp_listener():
    """Listen for incoming UDP messages and update the global last_received_data."""
    global last_received_data

    # Create an external socket to listen for data
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as external_socket:
        external_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            external_socket.bind((EXTERNAL_UDP_IP, EXTERNAL_UDP_PORT))
            print(f"Listening for external UDP on {EXTERNAL_UDP_IP}:{EXTERNAL_UDP_PORT}")
        except OSError as e:
            print(f"Error binding to external port: {e}")
            return

        while True:
            try:
                data, _ = external_socket.recvfrom(1024)
                last_received_data = data.decode("utf-8")
                print(f"Received telemetry data: {last_received_data}")
            except Exception as e:
                print(f"Error in UDP listener: {e}")