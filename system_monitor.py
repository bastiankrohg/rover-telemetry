import os
import psutil

def get_temperature():
    """Get the CPU temperature from the Raspberry Pi."""
    try:
        with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
            return int(f.read().strip()) / 1000.0  # Convert millidegrees to degrees
    except FileNotFoundError:
        return "N/A"  # Temperature sensor not available

def get_system_state():
    """Gather system metrics."""
    return {
        "cpu_usage": psutil.cpu_percent(interval=1),  # CPU usage percentage
        "memory_available": psutil.virtual_memory().available / (1024 * 1024),  # Available memory in MB
        "memory_total": psutil.virtual_memory().total / (1024 * 1024),  # Total memory in MB
        "disk_usage": psutil.disk_usage('/').percent,  # Disk usage percentage
        "temperature": get_temperature(),  # CPU temperature in Celsius
        "uptime": get_uptime(),  # System uptime in seconds
    }

def get_uptime():
    """Calculate system uptime."""
    try:
        with open("/proc/uptime", "r") as f:
            uptime_seconds = float(f.readline().split()[0])
            return uptime_seconds
    except Exception as e:
        return "N/A"

# For testing the script independently
if __name__ == "__main__":
    import time
    while True:
        print(get_system_state())
        time.sleep(2)  # Monitor every 2 seconds