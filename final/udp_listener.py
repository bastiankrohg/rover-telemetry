import socket

EXTERNAL_UDP_IP = "127.0.0.1"
EXTERNAL_UDP_PORT = 50055
LOCAL_UDP_IP = "127.0.0.1"
LOCAL_UDP_PORT = 60000

def start_udp_listener():
    """Listen for external UDP messages and forward them locally."""
    print("Starting UDP listener...")
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as external_socket:
        external_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            external_socket.bind((EXTERNAL_UDP_IP, EXTERNAL_UDP_PORT))
            print(f"Listening on {EXTERNAL_UDP_IP}:{EXTERNAL_UDP_PORT}")
        except OSError as e:
            print(f"Error binding to external port: {e}")
            return

        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as local_socket:
            while True:
                try:
                    data, addr = external_socket.recvfrom(1024)
                    print(f"Received data: {data.decode('utf-8')}")
                    local_socket.sendto(data, (LOCAL_UDP_IP, LOCAL_UDP_PORT))
                except Exception as e:
                    print(f"Error in UDP listener: {e}")