import grpc
from telemetry_proto.telemetry_pb2 import EmptyRequest
from telemetry_proto import telemetry_pb2_grpc


def run():
    with grpc.insecure_channel("localhost:50051") as channel:
        stub = telemetry_pb2_grpc.TelemetryServiceStub(channel)
        print("Connected to telemetry server.")
        try:
            for telemetry in stub.StreamTelemetry(EmptyRequest()):
                print(f"Received Telemetry Data:")
                print(f"  Ultrasound Distance: {telemetry.ultrasound_distance} meters")
                print(f"  Odometer: {telemetry.odometer} meters")
                print(f"  Current Position: {telemetry.current_position}")
                print(f"  Heading: {telemetry.heading} degrees")
                print(f"  Search Mode: {telemetry.search_mode}")
                print(f"  Battery Status: {telemetry.battery_status}")
                print(f"  Resources Found:")
                for resource in telemetry.resources_found:
                    print(f"    - Type: {resource.type}, Coordinates: ({resource.x_coordinate}, {resource.y_coordinate})")
                print("-" * 40)
        except grpc.RpcError as e:
            print(f"gRPC Error: {e}")


if __name__ == "__main__":
    run()