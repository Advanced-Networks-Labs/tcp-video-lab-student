
import cv2
import numpy as np
import socket
import struct
import time

PORT = 8080
HEADER_SIZE = 16  # 4 bytes length + 4 bytes frame_id + 8 bytes timestamp


# TODO 6: Receive exactly n bytes from the TCP stream
def recv_exact(sock, n):
    data = bytearray()

    while len(data) < n:
        chunk = sock.recv(n - len(data))

        if not chunk:
            return None

        data.extend(chunk)

    return bytes(data)


def run_server():
    server_socket = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    )

    server_socket.setsockopt(
        socket.SOL_SOCKET,
        socket.SO_REUSEADDR,
        1
    )

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

            # Receive the fixed-size header
            header_bytes = recv_exact(conn, HEADER_SIZE)

            if header_bytes is None:
                break

            # TODO 7: Unpack the header
            payload_length, frame_id, timestamp_ms = struct.unpack(
                '!IIQ',
                header_bytes
            )

            # Basic validation of payload size
            if payload_length == 0 or payload_length > 10_000_000:
                print("Invalid payload length.")
                break

            # Receive the complete image
            frame_bytes = recv_exact(conn, payload_length)

            if frame_bytes is None:
                print("Incomplete frame received.")
                break

            total_bytes += HEADER_SIZE + payload_length

            # Decode the JPEG image
            np_arr = np.frombuffer(
                frame_bytes,
                dtype=np.uint8
            )

            frame = cv2.imdecode(
                np_arr,
                cv2.IMREAD_COLOR
            )

            if frame is None:
                print(f"Could not decode frame {frame_id}")
                continue

            frame_count += 1

            # TODO 6: Calculate performance metrics
            current_time = time.time()
            elapsed_time = current_time - start_time

            latency_ms = (
                time.time_ns() // 1_000_000
            ) - timestamp_ms

            fps = frame_count / elapsed_time if elapsed_time > 0 else 0

            throughput_kbs = (
                total_bytes / 1024 / elapsed_time
                if elapsed_time > 0 else 0
            )

            print(
                f"Frame ID: {frame_id} | "
                f"Latency: {latency_ms} ms | "
                f"FPS: {fps:.2f} | "
                f"Throughput: {throughput_kbs:.2f} KB/s"
            )

    except (ConnectionError, OSError) as error:
        print(f"Network error: {error}")

    finally:
        conn.close()
        server_socket.close()
        cv2.destroyAllWindows()

        print("\nServer closed.")
        print(f"Total frames received: {frame_count}")
        print(f"Total data received: {total_bytes} bytes")


if __name__ == '__main__':
    run_server()