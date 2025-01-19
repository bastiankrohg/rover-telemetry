import cv2
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

VIDEO_SOURCE = "http://192.168.0.37:4747/video"  # DroidCam stream URL
frame_lock = threading.Lock()
current_frame = None

class MJPEGHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "multipart/x-mixed-replace; boundary=frame")
        self.end_headers()

        global current_frame
        while True:
            with frame_lock:
                if current_frame is None:
                    continue
                frame_data = cv2.imencode(".jpg", current_frame)[1].tobytes()
            try:
                self.wfile.write(b"--frame\r\n")
                self.wfile.write(b"Content-Type: image/jpeg\r\n\r\n")
                self.wfile.write(frame_data)
                self.wfile.write(b"\r\n")
            except BrokenPipeError:
                break

def start_mjpeg_server(port=8081):
    """Start the MJPEG server."""
    server = HTTPServer(("0.0.0.0", port), MJPEGHandler)
    print(f"Starting MJPEG server on port {port}")
    server.serve_forever()

def start_camera_stream():
    """Capture frames from the camera."""
    global current_frame
    cap = cv2.VideoCapture(VIDEO_SOURCE)
    if not cap.isOpened():
        print(f"Error: Could not open video source {VIDEO_SOURCE}")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Failed to fetch frame.")
            break
        with frame_lock:
            current_frame = frame

if __name__ == "__main__":
    threading.Thread(target=start_camera_stream, daemon=True).start()
    start_mjpeg_server(port=8081)