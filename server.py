 
import cv2
import numpy as np
import socket
import struct
import time

PORT = 8080
HEADER_SIZE = 16  # 4 + 4 + 8 bytes


def recv_exact(sock, n):
    """Read exactly n bytes from the TCP stream."""
    data = bytearray()

    while len(data) < n:
        packet = sock.recv(n - len(data))

        if not packet:
            if len(data) == 0:
                return b''
            raise ConnectionError("Incomplete data received.")

        data.extend(packet)

    return bytes(data)


def run_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    server_socket.bind(('0.0.0.0', PORT))
    server_socket.listen(1)

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

            # TODO 7: Unpack header information
            payload_length, frame_id, timestamp_ms = struct.unpack(
                '!IIQ', header_bytes
            )

            # Receive frame payload
            frame_bytes = recv_exact(conn, payload_length)

            if not frame_bytes:
                break

            total_bytes += HEADER_SIZE + payload_length

            # TODO 6: Calculate performance metrics
            current_time_ms = int(time.time() * 1000)
            latency = current_time_ms - timestamp_ms

            frame_count += 1

            elapsed_time = time.time() - start_time

            fps = frame_count / elapsed_time if elapsed_time > 0 else 0

            throughput = (
                total_bytes / 1024 / elapsed_time
                if elapsed_time > 0 else 0
            )

            print(
                f"Frame ID: {frame_id} | "
                f"Latency: {latency} ms | "
                f"FPS: {fps:.2f} | "
                f"Throughput: {throughput:.2f} KB/s"
            )

            # Decode received frame
            np_arr = np.frombuffer(frame_bytes, dtype=np.uint8)
            frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

            # Display disabled for WSL compatibility
            if frame is not None:
                pass

    except ConnectionError as e:
        print(f"Connection error: {e}")

    finally:
        conn.close()
        server_socket.close()
        cv2.destroyAllWindows()

        print("Server stopped.")
        print(f"Total frames received: {frame_count}")
        print(f"Total data received: {total_bytes / 1024:.2f} KB")


if __name__ == '__main__':
    run_server()
