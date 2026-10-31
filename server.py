
import cv2
import numpy as np
import socket
import struct
import time

PORT = 8080
HEADER_SIZE = 16

def recv_exact(sock, n):
    """Read exactly n bytes from TCP stream."""
    data = b''

    while len(data) < n:
        packet = sock.recv(n - len(data))

        if not packet:
            return None

        data += packet

    return data


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

            # TODO 6: Read header
            header_bytes = recv_exact(conn, HEADER_SIZE)

            if not header_bytes:
                break

            # TODO 7: Unpack header
            payload_length, frame_id, send_timestamp = struct.unpack(
                '!IIQ', header_bytes
            )

            # Receive image
            frame_bytes = recv_exact(conn, payload_length)

            if not frame_bytes:
                break

            total_bytes += HEADER_SIZE + payload_length

            # Performance metrics
            current_time = time.time()

            latency = current_time * 1000 - send_timestamp

            elapsed_time = current_time - start_time

            fps = frame_count / elapsed_time if elapsed_time > 0 else 0

            throughput = (
                total_bytes / 1024 / elapsed_time
                if elapsed_time > 0 else 0
            )

            print(
                f"Frame: {frame_id} | "
                f"Latency: {latency:.2f} ms | "
                f"FPS: {fps:.2f} | "
                f"Throughput: {throughput:.2f} KB/s"
            )

            # Decode image
            np_arr = np.frombuffer(
                frame_bytes,
                dtype=np.uint8
            )

            frame = cv2.imdecode(
                np_arr,
                cv2.IMREAD_COLOR
            )

            if frame is not None:
                cv2.imshow("Video Streaming Server", frame)

            frame_count += 1

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    finally:

        conn.close()
        server_socket.close()
        cv2.destroyAllWindows()


if __name__ == '__main__':
    run_server()
