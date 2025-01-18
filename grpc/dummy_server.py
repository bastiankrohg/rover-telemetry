import asyncio
import grpc
from telemetry_proto.telemetry_pb2 import TelemetryData, Resource
from telemetry_proto.telemetry_pb2_grpc import TelemetryServiceServicer, add_TelemetryServiceServicer_to_server
import random
import time


class DummyTelemetryServer(TelemetryServiceServicer):
    def __init__(self, throttle_delay=1.0):
        self.throttle_delay = throttle_delay  # seconds

    async def StreamTelemetry(self, request, context):
        try:
            while True:
                # Generate dummy telemetry data
                telemetry_data = TelemetryData(
                    ultrasound_distance=random.uniform(0.5, 10.0),  # Random distance values
                    odometer=random.uniform(10.0, 200.0),  # Random odometer values
                    current_position=f"x: {random.uniform(-10, 10):.2f}, y: {random.uniform(-10, 10):.2f}",
                    heading=random.uniform(0, 360),  # Random heading
                    search_mode=random.choice(["Pattern Pursuit", "Resource Seeking"]),
                    battery_status=f"{random.randint(50, 100)}%",
                    resources_found=[
                        Resource(type="water", x_coordinate=random.uniform(-10, 10), y_coordinate=random.uniform(-10, 10)),
                        Resource(type="rock", x_coordinate=random.uniform(-10, 10), y_coordinate=random.uniform(-10, 10)),
                    ]
                )
                yield telemetry_data
                await asyncio.sleep(self.throttle_delay)
        except Exception as e:
            print(f"Error streaming telemetry: {e}")
            raise

async def serve():
    server = grpc.aio.server()
    add_TelemetryServiceServicer_to_server(DummyTelemetryServer(), server)
    server.add_insecure_port("[::]:50052")
    print("DummyTelemetryServer running on port 50052...")
    await server.start()
    await server.wait_for_termination()


if __name__ == "__main__":
    asyncio.run(serve())