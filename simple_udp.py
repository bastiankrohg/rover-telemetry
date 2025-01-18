import socket
import json
import threading

UDP_IP = "127.0.0.1"
UDP_PORT = 50054

def udp_listener():
    """Listen for incoming UDP messages."""
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as client_socket:
        client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        client_socket.bind((UDP_IP, UDP_PORT))
        print(f"Listening on {UDP_IP}:{UDP_PORT}")

        while True:
            data, addr = client_socket.recvfrom(1024)
            telemetry_data = json.loads(data.decode('utf-8'))
            print(f"Received from {addr}: {telemetry_data}")

if __name__ == "__main__":
    listener_thread = threading.Thread(target=udp_listener, daemon=True)
    listener_thread.start()
    listener_thread.join()