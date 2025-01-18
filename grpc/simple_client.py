import asyncio
import grpc

from telemetry_proto.telemetry_pb2 import EmptyRequest
from telemetry_proto import telemetry_pb2_grpc

class TelemetryClient:
    def __init__(self, host: str):
        self.host = host
        self.channel = None
        self.stub = None

    async def connect(self):
        """
        Establishes the gRPC connection and initializes the stub.
        """
        self.channel = grpc.aio.insecure_channel(self.host)
        self.stub = telemetry_pb2_grpc.TelemetryServiceStub(self.channel)

    async def stream_telemetry(self):
        """
        Streams telemetry data from the server.
        Yields telemetry data as they arrive.
        """
        try:
            request = EmptyRequest()  # Adjust based on your .proto definition
            # Initiate the stream
            response_stream = self.stub.StreamTelemetry(request)
            
            # Iterate over the streamed responses
            async for telemetry_data in response_stream:
                yield telemetry_data

        except grpc.aio.AioRpcError as e:
            print(f"gRPC error: {e}")

    async def close(self):
        """
        Closes the gRPC connection.
        """
        if self.channel:
            await self.channel.close()

# Example usage
async def main():
    client = TelemetryClient(host="localhost:50051")
    await client.connect()

    print("Streaming telemetry data:")
    try:
        async for telemetry_data in client.stream_telemetry():
            print(f"Received telemetry: {telemetry_data}")
    except Exception as e:
        print(f"Error during telemetry streaming: {e}")
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(main())