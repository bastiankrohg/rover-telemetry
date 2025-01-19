import socket
import threading
import json

# Configuration for external and local UDP communication
EXTERNAL_UDP_IP = "127.0.0.1"
EXTERNAL_UDP_PORT = 50055
LOCAL_UDP_IP = "127.0.0.1"
LOCAL_UDP_PORT = 60000

# Shared variable to store the latest received data
last_received_data = json.dumps({
    "position": {"x": 0.0, "y": 0.0},
    "heading": 0.0,
    "battery_level": 100.0,
    "ultrasound_distance": 0.0,
    "system_state": {
        "cpu_usage": 0.0,
        "memory_available": 0.0,
        "memory_total": 0.0,
        "disk_usage": 0.0,
        "temperature": "N/A",
        "uptime": "N/A",
    }
})


def forward_data(data, local_socket):
    """Forward received data to the local socket."""
    try:
        local_socket.sendto(data, (LOCAL_UDP_IP, LOCAL_UDP_PORT))
    except Exception as e:
        print(f"Error forwarding data: {e}")


def start_udp_listener():
    """Listen for external UDP messages and forward them locally."""
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

        # Create a local socket for forwarding data
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as local_socket:
            while True:
                try:
                    # Receive data from the external source
                    data, addr = external_socket.recvfrom(1024)

                    # Decode and store the data
                    decoded_data = data.decode("utf-8")
                    last_received_data = decoded_data

                    # Forward the data locally
                    forward_data(data, local_socket)

                except socket.error as e:
                    print(f"Socket error in UDP listener: {e}")
                except Exception as e:
                    print(f"Error in UDP listener: {e}")


# Run the UDP listener in a separate thread when this script is executed
if __name__ == "__main__":
    listener_thread = threading.Thread(target=start_udp_listener, daemon=True)
    listener_thread.start()