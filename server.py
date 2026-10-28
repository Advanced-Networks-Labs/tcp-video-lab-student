import cv2
import numpy as np
import socket
import struct
import time

PORT = 8080
HEADER_SIZE = 16  # 4 bytes length + 4 bytes frame_id + 8 bytes timestamp

def recv_exact(sock, n):
    """TODO 6: Implement a robust helper to read exactly n bytes from the TCP stream."""

    data = bytearray()
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data.extend(packet)
    return bytes(data)

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
    expected_frame_id = 0
    lost_frames = 0
    latencies = []

    try:
        while True:
            header_bytes = recv_exact(conn, HEADER_SIZE)
            if not header_bytes:
                break

            # TODO 7: Unpack payload length, frame ID, and send timestamp using struct.unpack
            payload_length, frame_id, send_ts_ms = struct.unpack('!IId', header_bytes)
            frame_bytes = recv_exact(conn, payload_length)
            total_bytes += HEADER_SIZE + payload_length

            # I added this line for Detect lost/dropped frames by checking gaps in frame_id sequence
            if frame_id > expected_frame_id:
                lost_frames += (frame_id - expected_frame_id)
            expected_frame_id = frame_id + 1

            # TODO 6: Calculate and log performance metrics (Latency, FPS, Throughput KB/s)
            current_time = time.time()
            latency_ms = (current_time * 1000.0) - send_ts_ms
            latencies.append(latency_ms)

            elapsed = current_time - start_time
            fps = (frame_count + 1) / elapsed if elapsed > 0 else 0.0
            throughput_kbps = (total_bytes / 1024.0) / elapsed if elapsed > 0 else 0.0
            print(f"[Frame {frame_id:04d}] Latency: {latency_ms:6.2f} ms | FPS: {fps:5.2f} | Throughput: {throughput_kbps:8.2f} KB/s")

            np_arr = np.frombuffer(frame_bytes, dtype=np.uint8)
            frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
            frame_count += 1

            if frame is not None:
                cv2.imshow("Server Video Stream", frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break   

        # Final Performance & Loss Evaluation Summary
        total_expected = frame_count + lost_frames
        loss_rate = (lost_frames / total_expected * 100.0) if total_expected > 0 else 0.0
        avg_latency = (sum(latencies) / len(latencies)) if latencies else 0.0
        total_time = time.time() - start_time
        avg_fps = frame_count / total_time if total_time > 0 else 0.0
        avg_throughput = (total_bytes / 1024.0) / total_time if total_time > 0 else 0.0

        print("\n" + "=" * 50)
        print("           FINAL PERFORMANCE & LOSS REPORT       ")
        print("=" * 50)
        print(f"Total Frames Expected  : {total_expected}")
        print(f"Total Frames Received  : {frame_count}")
        print(f"Lost / Dropped Frames  : {lost_frames}")
        print(f"Frame Loss Rate        : {loss_rate:.2f}%")
        print(f"Total Data Received    : {total_bytes / 1024:.2f} KB")
        print(f"Total Duration         : {total_time:.2f} s")
        print(f"Average Latency        : {avg_latency:.2f} ms")
        print(f"Average FPS            : {avg_fps:.2f} frames/s")
        print(f"Average Throughput     : {avg_throughput:.2f} KB/s")
        print("=" * 50)

    finally:
        conn.close()
        server_socket.close()
        cv2.destroyAllWindows()

if __name__ == '__main__':
    run_server()
