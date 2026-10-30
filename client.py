import cv2
import numpy as np
import socket
import struct
import time

SERVER_IP = '127.0.0.1'
PORT = 8080
def make_test_video(VIDEO_PATH):
    # TODO 1: Define variables to build a 5-second video with 320*240 frames.
   FPS = 30
    SECONDS = 5
    W, H = 320, 240
    
    writer = cv2.VideoWriter(VIDEO_PATH, cv2.VideoWriter_fourcc(*"mp4v"), FPS, (W, H))
    for i in range(FPS * SECONDS):
        frame = np.full((H, W, 3), (i * 3) % 255, dtype=np.uint8)
        cv2.putText(frame, f"frame {i}", (60, 125), cv2.FONT_HERSHEY_SIMPLEX,
                    1, (255, 255, 255), 2)
        writer.write(frame)
    writer.release()
    print(f"Wrote {VIDEO_PATH}")

def run_client():
    # TODO 2: Prepare the test video indicated by a specific video path.
    VIDEO_PATH = "test_video.mp4"
    make_test_video(VIDEO_PATH)
 
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((SERVER_IP, PORT))
    print(f"Connected to server at {SERVER_IP}:{PORT}")

    cap = cv2.VideoCapture(VIDEO_PATH)
    frame_id = 0
    
    try:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            frame = cv2.resize(frame, (640, 480))
            success, encoded_image = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 60])
            if not success:
                continue

            payload = encoded_image.tobytes()
            payload_length = len(payload)
            
            # TODO 3: Capture high-resolution timestamp for latency tracking
            send_timestamp = int(time.time() * 1000)
         
            # TODO 4: Construct fixed-size header (e.g., 4 bytes length, 4 bytes frame_id, 8 bytes timestamp in milliseconds) that is prefixing the video frame payload using struct.pack()
            header = struct.pack("!IIQ", payload_length, frame_id, send_timestamp)

            # TODO 5: Transmit header + payload securely using socket.sendall()
            client_socket.sendall(header + payload)

            frame_id += 1
            time.sleep(0.03)  # Frame pacing (~30 FPS)

    finally:
        cap.release()
        client_socket.close()

if __name__ == '__main__':
    run_client()