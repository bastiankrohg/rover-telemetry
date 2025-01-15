import asyncio
import grpc
from telemetry_proto.telemetry_pb2 import TelemetryData, Resource
from telemetry_proto.telemetry_pb2_grpc import TelemetryServiceServicer, add_TelemetryServiceServicer_to_server
import random
import time


class RoverTelemetryServer(TelemetryServiceServicer):
    def __init__(self, throttle_delay=1.0):
        self.throttle_delay = throttle_delay  # seconds

    async def StreamTelemetry(self, request, context):
        while True:
            # Simulate actual data collection
            telemetry_data = TelemetryData(
                ultrasound_distance=random.uniform(0.2, 5.0),  # Simulated sensor range
                odometer=random.uniform(0.0, 100.0),
                current_position=f"x: {random.uniform(-20, 20):.2f}, y: {random.uniform(-20, 20):.2f}",
                heading=random.uniform(0, 360),
                search_mode="Resource Seeking",
                battery_status=f"{random.randint(0, 100)}%",
                resources_found=[
                    Resource(type="rock", x_coordinate=12.5, y_coordinate=18.3)
                ]
            )
            yield telemetry_data
            await asyncio.sleep(self.throttle_delay)


async def serve():
    server = grpc.aio.server()
    add_TelemetryServiceServicer_to_server(RoverTelemetryServer(), server)
    server.add_insecure_port("[::]:50051")
    print("RoverTelemetryServer running on port 50051...")
    await server.start()
    await server.wait_for_termination()


if __name__ == "__main__":
    asyncio.run(serve())