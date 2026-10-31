
import cv2
import numpy as np
import socket
import struct
import time

PORT = 8080
HEADER_SIZE = 16


# TODO 6: Receive exactly n bytes
def recv_exact(sock, n):
    data = b''

    while len(data) < n:
        packet = sock.recv(n - len(data))

        if not packet:
            return None

        data += packet

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

            # TODO 7: Unpack header
            payload_length, frame_id, timestamp = struct.unpack(
                '!IIQ', header_bytes
            )

            frame_bytes = recv_exact(conn, payload_length)
            if not frame_bytes:
                break

            total_bytes += HEADER_SIZE + payload_length

            # TODO 6: Calculate performance metrics
            latency = time.time_ns() // 1000000 - timestamp

            frame_count += 1
            elapsed = time.time() - start_time

            fps = frame_count / elapsed
            throughput = total_bytes / 1024 / elapsed

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


if __name__ == '__main__':
    run_server()
