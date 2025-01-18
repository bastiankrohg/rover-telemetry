import asyncio
import grpc
from telemetry_proto.telemetry_pb2 import TelemetryData
from telemetry_proto.telemetry_pb2_grpc import TelemetryServiceServicer, add_TelemetryServiceServicer_to_server

# Mock data generator for telemetry
def generate_telemetry_data():
    return TelemetryData(
        ultrasound_distance=1.5,
        odometer=12.34,
        position="x: 5.0, y: 3.0",
        heading=45.0,
        search_mode="Pattern Pursuit",
        resources_found=[],
        battery_status="85%",
    )

class TelemetryService(TelemetryServiceServicer):
    async def StreamTelemetry(self, request, context):
        while True:
            telemetry_data = generate_telemetry_data()
            await asyncio.sleep(1)  # Throttle the updates
            yield telemetry_data

async def serve():
    server = grpc.aio.server()
    add_TelemetryServiceServicer_to_server(TelemetryService(), server)
    listen_addr = "[::]:50051"
    server.add_insecure_port(listen_addr)
    print(f"Server running on {listen_addr}")

    await server.start()

    # Graceful shutdown
    try:
        await server.wait_for_termination()
    except asyncio.CancelledError:
        print("Server shutting down gracefully...")
        await server.shutdown()

def main():
    loop = asyncio.get_event_loop()

    try:
        # Run the server in the event loop
        loop.run_until_complete(serve())
    except KeyboardInterrupt:
        print("Received termination signal. Shutting down...")
    finally:
        # Ensure all pending tasks are cancelled and the loop is closed properly
        pending = asyncio.all_tasks(loop)
        for task in pending:
            task.cancel()

        loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()

if __name__ == "__main__":
    main()