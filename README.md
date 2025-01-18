# Rover Telemetry Dashboard

This repository provides a lightweight solution for visualizing telemetry data from a rover system using UDP communication. The project includes a simple UDP server to simulate telemetry data, a UDP client to receive and forward data for visualization, and a responsive Dash-based telemetry dashboard.

## Key Components

1. client.py (UDP Client)

The UDP client serves as the bridge between the rover’s telemetry data and the visualization dashboard. It listens for incoming telemetry data, processes it, and forwards it to the dashboard for real-time visualization.

## Features:
	•	UDP Communication:
	•	Listens on a local UDP port for incoming telemetry data.
	•	Processes JSON-encoded telemetry data from the rover (or the dummy server).
	•	Forwards data to the Dash dashboard for visualization.
	•	Thread-Safe Design:
	•	Runs as a daemon thread to ensure non-blocking operation with the dashboard.
	•	Error Handling:
	•	Handles socket binding errors and timeouts gracefully to ensure stability.

## Configuration:
	•	External UDP Server:
	•	IP: 127.0.0.1
	•	Port: 50055
	•	Local UDP Port for Dashboard:
	•	IP: 127.0.0.1
	•	Port: 60000

## Usage:
	1.	Start the dummy2.py server to simulate telemetry data.
	2.	Run client.py to listen for and forward telemetry data.
	3.	The dashboard will render real-time telemetry metrics.

2. dummy2.py (UDP Server)

The UDP server simulates a telemetry data stream from a rover, sending JSON-encoded data packets over UDP.

## Features:
	•	Simulated Telemetry Data:
	•	Periodically sends telemetry data, including:
	•	Position: x, y coordinates.
	•	Heading: Rover’s orientation in degrees.
	•	Battery Level: Remaining charge percentage.
	•	Ultrasound Distance: Distance from obstacles in meters.
	•	Configurable Frequency:
	•	The server sends data packets at regular intervals (1 second by default).

## Configuration:
	•	Target UDP Client:
	•	IP: 127.0.0.1
	•	Port: 50055

## Usage:
	1.	Run dummy2.py to start the server.
	2.	Observe the console output to verify the data being sent.

3. GRPC Aspects

This project initially explored gRPC for transmitting telemetry data. However, due to the lightweight nature and efficiency of UDP communication, gRPC has been deprecated in favor of this simpler approach.

## Reasons for Transition:
	•	Lower Overhead: UDP’s simplicity eliminates the need for gRPC’s complex infrastructure.
	•	Lightweight Design: Ideal for real-time telemetry updates where packet loss is tolerable.
	•	Ease of Implementation: Straightforward setup without requiring additional gRPC libraries or server configurations.

## System Architecture

[ Dummy UDP Server (dummy2.py) ]
             ↓
   (UDP Packets over 127.0.0.1:50055)
             ↓
[ UDP Client (client.py) ]
             ↓
 (UDP Packets forwarded to 127.0.0.1:60000)
             ↓
[ Dash Dashboard ]

## How to Run

## Prerequisites
	•	Python 3.8 or later
	•	Required Python libraries:
	•	dash
	•	plotly
	•	dash-bootstrap-components

## Install dependencies using:
```bash
pip install dash plotly dash-bootstrap-components
```

## Steps
	1.	Start the UDP Server:
Run dummy2.py to simulate telemetry data:
```bash
python dummy2.py
```

	2.	Run the UDP Client:
Start client.py to listen for telemetry data and forward it to the dashboard:
```bash
python client.py
```

	3.	Open the Dashboard:
Access the telemetry dashboard at http://127.0.0.1:8050.

## Dashboard Features
	•	Real-Time Telemetry Visualization:
	•	Dynamic path trace visualization.
	•	Metrics including position, heading, battery level, and proximity.
	•	Connection Status:
	•	Title displays a 🟢 or 🔴 emoji based on the backend connection status.
	•	Toggle Orientation:
	•	Switch between “North-Up” and “Heading-Up” views for the path trace.

## Future Enhancements
	•	Integration of live video feed for a comprehensive rover control system.
	•	Extending the dashboard to include additional sensors or telemetry data streams.
	•	Deployment-ready packaging for cross-platform usage.

This lightweight solution is ideal for real-time visualization of telemetry data in resource-constrained environments. Feedback and contributions are welcome! 🚀