import cv2
import numpy as np
import socket
import struct
import time

PORT = 8080
HEADER_SIZE = 16  # 4 bytes length + 4 bytes frame_id + 8 bytes timestamp

def recv_exact(sock, n):
    """TODO 6: Implement a robust helper to read exactly n bytes from the TCP stream."""
    pass

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
            payload_length, frame_id, timestamp = struct.unpack ("IIQ",header_bytes)
            
            

            frame_bytes = recv_exact(conn, payload_length)
            total_bytes += HEADER_SIZE + payload_length

            # TODO 6: Calculate and log performance metrics (Latency, FPS, Throughput KB/s)
            timesec = time.time() - start_time
            throughput = (total_bytes / 1024) / timesec

            fps = (frame_count + 1) / timesec

            recv_time = time.time () * 1000
            latency = recv_time - timestamp

            print(f"FRAME {frame_id} | LATENCY : {latency} ms | FPS : {fps} | THROUGHPUT : {throughput} KB/s")

            np_arr = np.frombuffer(frame_bytes, dtype=np.uint8)
            frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
            frame_count += 1

    finally:
        conn.close()
        server_socket.close()
        cv2.destroyAllWindows()

if __name__ == '__main__':
    run_server()
