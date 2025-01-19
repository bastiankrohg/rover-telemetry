# Rover Telemetry System

This project is a telemetry system for visualizing real-time data from a rover. It includes components for gathering system metrics, transmitting data via UDP, and visualizing telemetry through an interactive dashboard.

## Project Structure

```
├── main_dash.py         # UDP client that visualizes the dashboard
├── main_server.py       # UDP server that gathers telemetry data (now includes system status info)
├── dummy_server.py      # Test server with dummy data for dashboard testing
├── test/                # Folder containing all tests during development
│   ├── grpc/            # Tests for gRPC implementations
│   ├── udp/             # Tests for UDP components
│   └── various/         # Alternative approaches and exploratory tests
├── telemetry_env/       # Virtual environment for running the system (Mac setup, will adapt for Pi Zero)
└── README.md            # Project documentation
```

## Components

1. Dashboard (main_dash.py)

The interactive dashboard is the main visualization tool for telemetry data. It uses Dash with the following features:
	•	Path Trace Visualization: Tracks the rover’s movement over time, with an indicator for heading.
	•	Real-Time System Metrics:
	•	CPU Usage
	•	Memory Usage
	•	Disk Usage
	•	System Temperature
	•	Uptime
	•	Sensor Measurements: Displays battery levels and ultrasound readings over time.

2. Telemetry Server (main_server.py)

The UDP server collects and broadcasts telemetry data. It now integrates system status metrics using the psutil library and Raspberry Pi-specific tools for system temperature. Key functionalities:
	•	Sends telemetry data such as position, heading, battery level, and ultrasound distance.
	•	Monitors system metrics (e.g., CPU, memory, disk usage, temperature).
	•	Includes a placeholder for fetching actual rover data.

3. Dummy Server (dummy_server.py)

A simplified server used during development to test the dashboard without connecting to actual rover hardware. It generates dummy telemetry data and sends it over UDP.

4. Tests (test/)

This folder contains tests developed during experimentation, including:
	•	gRPC vs. UDP performance tests.
	•	Tests for different telemetry formats.
	•	Simulations for client-server communication.

5. Virtual Environment (telemetry_env/)

A Python virtual environment for managing dependencies. The current version is configured for macOS. A new environment should be created for deployment on the Raspberry Pi Zero.

## Installation
1.	Clone the repository:
```bash
git clone https://github.com/your-repo-name/rover-telemetry.git
cd rover-telemetry
```

2.	Set up a virtual environment:
```bash
python3 -m venv telemetry_env
source telemetry_env/bin/activate  # macOS/Linux
telemetry_env\Scripts\activate     # Windows
```

3.	Install dependencies:
```bash
pip install -r requirements.txt
```

4.	If running on a Raspberry Pi, ensure psutil and vcgencmd are available:

```bash
sudo apt update
sudo apt install python3-psutil
```

## Usage

1. Run the Telemetry Server
```bash
python3 main_server.py
```

2. Run the Dashboard
```bash
python3 main_dash.py
```

3. Test with Dummy Server

To test the dashboard with simulated data:
```bash
python3 dummy_server.py
```
## Telemetry Data Format

The telemetry data broadcast by the server is in JSON format:
```json
{
    "position": {"x": 10.0, "y": 5.0},
    "heading": 123.45,
    "battery_level": 85.0,
    "ultrasound_distance": 2.5,
    "system_state": {
        "cpu_usage": 23.5,
        "memory_available": 256.0,
        "memory_total": 512.0,
        "disk_usage": 42.1,
        "temperature": 45.2,
        "uptime": 12345.6
    }
}
```

Next Steps
	1.	Complete main_server.py:
	•	Replace placeholders with actual rover telemetry data.
	•	Test system metrics collection on the Raspberry Pi Zero.
	2.	Adapt Virtual Environment for Pi Zero:
	•	Recreate the virtual environment on the Pi Zero to account for its architecture.
	3.	Systemctl Service:
	•	Configure main_server.py as a systemctl service for reliability and auto-restart on crashes.

