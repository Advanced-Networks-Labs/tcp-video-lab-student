import cv2
import numpy as np
import socket
import struct
import time

PORT = 8080
HEADER_SIZE = 16  # 4 bytes length + 4 bytes frame_id + 8 bytes timestamp

def recv_exact(sock, n):
    """TODO 6: Implement a robust helper to read exactly n bytes from the TCP stream."""
    data = b''
    while len(data) < n:
        chunk = sock.recv(n - len(data))
        if not chunk:  # connection closed by the client
            return None
        data += chunk
    return data

def run_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('0.0.0.0', PORT))
    server_socket.listen(1)
    
    print(f"Server listening on port {PORT}...")
    conn, addr = server_socket.accept()
    
    frame_count = 0
    total_bytes = 0
    start_time = time.time()

    try:
        while True:
            header_bytes = recv_exact(conn, HEADER_SIZE)
            if not header_bytes:
                break

            # TODO 7: Unpack payload length, frame ID, and send timestamp using struct.unpack
            payload_length, frame_id, send_timestamp_ms = struct.unpack('!IIQ', header_bytes)

            frame_bytes = recv_exact(conn, payload_length)
            if frame_bytes is None:
                break
            total_bytes += HEADER_SIZE + payload_length

            # TODO 6: Calculate and log performance metrics (Latency, FPS, Throughput KB/s)
            now = time.time()
            latency_ms = now * 1000 - send_timestamp_ms
            elapsed = now - start_time
            fps = (frame_count + 1) / elapsed if elapsed > 0 else 0.0
            throughput_kbps = (total_bytes / 1024) / elapsed if elapsed > 0 else 0.0
            print(f"Frame {frame_id:4d} | size {payload_length / 1024:6.1f} KB | "
                  f"latency {latency_ms:6.2f} ms | FPS {fps:5.1f} | "
                  f"throughput {throughput_kbps:8.1f} KB/s")

            np_arr = np.frombuffer(frame_bytes, dtype=np.uint8)
            frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
            frame_count += 1

    finally:
        elapsed = time.time() - start_time
        if frame_count:
            print(f"\nDone: {frame_count} frames, {total_bytes / 1024:.1f} KB in {elapsed:.2f}s "
                  f"(avg {frame_count / elapsed:.1f} FPS, {total_bytes / 1024 / elapsed:.1f} KB/s)")
        conn.close()
        server_socket.close()
        cv2.destroyAllWindows()

if __name__ == '__main__':
    run_server()
