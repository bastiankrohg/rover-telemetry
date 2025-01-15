import grpc
import logging
from telemetry_proto.telemetry_pb2 import EmptyRequest
from telemetry_proto.telemetry_pb2_grpc import TelemetryServiceStub

# Configure logging
logging.basicConfig(
    filename="client_errors.log",  # Log file
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

class TelemetryClient:
    def __init__(self, host="127.0.0.1", port=50051):
    #def __init__(self, host="127.0.0.1", port=50052):
        self.channel = grpc.aio.insecure_channel(f"{host}:{port}")
        self.stub = TelemetryServiceStub(self.channel)

    async def stream_telemetry(self):
        try:
            # Use the empty request for streaming
            async for response in self.stub.StreamTelemetry(EmptyRequest()):
                # Process telemetry data
                yield {
                    "ultrasound_distance": response.ultrasound_distance,
                    "odometer": response.odometer,
                    "current_position": response.current_position,
                    "heading": response.heading,
                    "search_mode": response.search_mode,
                    "resources_found": [
                        {"type": r.type, "x": r.x_coordinate, "y": r.y_coordinate}
                        for r in response.resources_found
                    ],
                    "battery_status": response.battery_status,
                }
        except grpc.RpcError as e:
            print(f"gRPC error: {e}")
            logging.error(f"gRPC error: {e}")
            raise


    async def close(self):
        await self.channel.close()