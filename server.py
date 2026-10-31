import cv2 import numpy as np import socket import struct import time
PORT = 8080 HEADER_SIZE = 16
def recv_exact(sock, n): """Read exactly n bytes from the TCP stream.""" data = b''
while len(data) < n:
    packet = sock.recv(n - len(data))

    if not packet:
        return None

    data += packet

return data
def run_server(): server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) server_socket.bind(('0.0.0.0', PORT)) server_socket.listen(1)
print(f"Server listening on port {PORT}...")
conn, addr = server_socket.accept()
print(f"Connected by {addr}")

frame_count = 0
total_bytes = 0
start_time = time.time()

try:
    while True:
        header_bytes = recv_exact(conn, HEADER_SIZE)

        if not header_bytes:
            break

        # Unpack the header
        payload_length, frame_id, timestamp_ms = struct.unpack(
            "!IIQ", header_bytes
        )

        frame_bytes = recv_exact(conn, payload_length)

        if not frame_bytes:
            break

        total_bytes += HEADER_SIZE + payload_length

        # Calculate performance metrics
        current_time_ms = time.time_ns() // 1_000_000
        latency = current_time_ms - timestamp_ms

        frame_count += 1
        elapsed_time = time.time() - start_time

        if elapsed_time > 0:
            fps = frame_count / elapsed_time
            throughput = (total_bytes / 1024) / elapsed_time
        else:
            fps = 0
            throughput = 0

        print(
            f"Frame: {frame_id} | "
            f"Latency: {latency} ms | "
            f"FPS: {fps:.2f} | "
            f"Throughput: {throughput:.2f} KB/s"
        )

        np_arr = np.frombuffer(frame_bytes, dtype=np.uint8)
        frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

finally:
    conn.close()
    server_socket.close()
    cv2.destroyAllWindows()
if name == 'main': run_server()