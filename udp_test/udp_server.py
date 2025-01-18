import socket
import json
import time
import math

class TelemetryUDPServer:
    def __init__(self, host="0.0.0.0", port=8000):
        self.host = host
        self.port = port
        self.time = 0
        self.position_x = 0.0
        self.position_y = 0.0
        self.heading = 0.0
        self.odometer = 0.0
        self.battery_status = 100

    def generate_telemetry(self):
        self.time += 1

        # Simulate movement in a circular path
        self.position_x = 10 * math.cos(self.time / 10)
        self.position_y = 10 * math.sin(self.time / 10)
        self.heading = (self.time % 360)
        self.odometer += 0.1
        self.battery_status = max(0, self.battery_status - 0.01)

        telemetry = {
            "ultrasound_distance": 5.0,
            "position": {"x": self.position_x, "y": self.position_y},
            "heading": self.heading,
            "odometer": self.odometer,
            "battery_level": self.battery_status,
        }
        return telemetry

    def start(self):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as server_socket:
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            server_socket.bind((self.host, self.port))
            print(f"UDP server started on {self.host}:{self.port}")

            while True:
                telemetry = self.generate_telemetry()
                telemetry_json = json.dumps(telemetry)
                server_socket.sendto(telemetry_json.encode(), ('<broadcast>', self.port))
                time.sleep(0.1)  # Throttle to 10 Hz