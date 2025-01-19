import cv2
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
import time

# Camera source
VIDEO_SOURCE = "http://192.168.0.37:4747/video"  # DroidCam stream URL

# Shared frame storage for MJPEG server
frame_lock = threading.Lock()
current_frame = None

# MJPEG server handler
class MJPEGHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "multipart/x-mixed-replace; boundary=frame")
        self.end_headers()

        global current_frame
        while True:
            with frame_lock:
                if current_frame is None:
                    continue  # Wait if no frame is available
                frame_data = cv2.imencode(".jpg", current_frame)[1].tobytes()

            try:
                self.wfile.write(b"--frame\r\n")
                self.wfile.write(b"Content-Type: image/jpeg\r\n\r\n")
                self.wfile.write(frame_data)
                self.wfile.write(b"\r\n")
                time.sleep(0.05)  # ~20 FPS
            except BrokenPipeError:
                print("Client disconnected")
                break

def start_mjpeg_server(port=8081):
    """Start the MJPEG server in a separate thread."""
    server = HTTPServer(("0.0.0.0", port), MJPEGHandler)
    print(f"Starting MJPEG server on port {port}")
    threading.Thread(target=server.serve_forever, daemon=True).start()

def start_camera_stream():
    """Start capturing frames from the camera."""
    global current_frame
    cap = cv2.VideoCapture(VIDEO_SOURCE)
    if not cap.isOpened():
        print(f"Error: Could not open video source {VIDEO_SOURCE}")
        return

    print("Press 'q' to exit.")
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Failed to fetch frame.")
            break

        # Store the frame for MJPEG server
        with frame_lock:
            current_frame = frame

        # Display the frame locally (optional)
        cv2.imshow("Camera Stream", frame)

        # Exit on 'q' key press
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()