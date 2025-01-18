import asyncio
import grpc
import math
from telemetry_proto.telemetry_pb2 import TelemetryData, Resource, Position
from telemetry_proto.telemetry_pb2_grpc import TelemetryServiceServicer, add_TelemetryServiceServicer_to_server

class DummyTelemetryService(TelemetryServiceServicer):
    def __init__(self):
        self.time = 0
        self.position_x = 0.0
        self.position_y = 0.0
        self.heading = 0.0
        self.odometer = 0.0
        self.battery_status = 100.0
        self.resources_found = []

    async def StreamTelemetry(self, request, context):
        while True:
            self.time += 1

            # Simulate movement in a circular path
            self.position_x = 10 * math.cos(self.time / 10)
            self.position_y = 10 * math.sin(self.time / 10)
            self.heading = (self.time * 10) % 360  # Simulated heading in degrees
            self.odometer += 0.1  # Simulated distance traveled
            self.battery_status = max(0.0, self.battery_status - 0.01)  # Simulated battery drain

            # Simulate resources found at certain intervals
            if self.time % 50 == 0:
                resource = Resource(
                    type="rock",
                    location=Position(x=self.position_x, y=self.position_y)
                )
                self.resources_found.append(resource)

            telemetry_data = TelemetryData(
                ultrasound_distance=5.0,  # Simulated constant ultrasound measurement
                odometer=self.odometer,
                position=Position(x=self.position_x, y=self.position_y),
                heading=self.heading,
                search_mode=0,  # 0 = Pattern Pursuit
                resources_found=self.resources_found,
                battery_level=self.battery_status,
            )

            await asyncio.sleep(0.1)  # Throttling updates to every 100ms
            yield telemetry_data

async def serve():
    server = grpc.aio.server()
    add_TelemetryServiceServicer_to_server(DummyTelemetryService(), server)
    listen_addr = "[::]:50051"
    server.add_insecure_port(listen_addr)
    print(f"Dummy server running on {listen_addr}")

    await server.start()

    try:
        await server.wait_for_termination()
    except asyncio.CancelledError:
        print("Shutting down server...")
        await server.shutdown()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(serve())
    except KeyboardInterrupt:
        print("Received termination signal. Exiting...")
    finally:
        pending = asyncio.all_tasks(loop)
        for task in pending:
            task.cancel()
        loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()