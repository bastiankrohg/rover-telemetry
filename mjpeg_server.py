import cv2
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

# URL of the DroidCam stream
VIDEO_SOURCE = "http://192.168.0.37:4747/video"

# Shared resource for frames
frame_lock = threading.Lock()
current_frame = None

class MJPEGHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests to serve the MJPEG stream."""
        self.send_response(200)
        self.send_header("Content-Type", "multipart/x-mixed-replace; boundary=frame")
        self.end_headers()

        global current_frame
        while True:
            with frame_lock:
                if current_frame is None:
                    continue  # Skip if no frame is available
                frame_data = cv2.imencode(".jpg", current_frame)[1].tobytes()
            try:
                self.wfile.write(b"--frame\r\n")
                self.wfile.write(b"Content-Type: image/jpeg\r\n\r\n")
                self.wfile.write(frame_data)
                self.wfile.write(b"\r\n")
            except BrokenPipeError:
                print("Client disconnected from MJPEG server.")
                break
            except Exception as e:
                print(f"Error in MJPEGHandler: {e}")
                break

def start_mjpeg_server(port=8081):
    """Start the MJPEG server in a separate thread."""
    def server_thread():
        server = HTTPServer(("0.0.0.0", port), MJPEGHandler)
        print(f"Starting MJPEG server on port {port}")
        try:
            server.serve_forever()
        except Exception as e:
            print(f"Error in MJPEG server: {e}")

    thread = threading.Thread(target=server_thread, daemon=True)
    thread.start()

def start_camera_stream():
    """Capture frames from the video source and update the shared frame."""
    global current_frame
    cap = cv2.VideoCapture(VIDEO_SOURCE)

    if not cap.isOpened():
        print(f"Error: Could not open video source {VIDEO_SOURCE}")
        return

    print("Camera stream started.")
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Failed to fetch frame.")
            break
        with frame_lock:
            current_frame = frame

    cap.release()

if __name__ == "__main__":
    # Start the camera stream and MJPEG server
    threading.Thread(target=start_camera_stream, daemon=True).start()
    start_mjpeg_server(port=8081)