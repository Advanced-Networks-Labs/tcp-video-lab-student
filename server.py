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

    try:
        while True:
            # TODO 7: Unpack payload length, frame ID, and send timestamp using struct.unpack
           
           ##

            header_bytes = recv_exact(conn, HEADER_SIZE)
            if not header_bytes:
                break

            payload_length, frame_id, timestamp = struct.unpack("!I I Q", header_bytes)

            payload = recv_exact(conn, payload_length)
            if not payload:
                break
            ##
            
          
          # TODO 6: Calculate and log performance metrics (Latency, FPS, Throughput KB/s)
        
        ##

            total_bytes += payload_length
            current_time = int(time.time() * 1000)
            latency = current_time - timestamp

            elapsed_time = time.time() - start_time
            fps = frame_count / elapsed_time if elapsed_time > 0 else 0
            throughput_kbps = (total_bytes / 1024) / elapsed_time if elapsed_time > 0 else 0
            
          
            print(f"Frame ID: {frame_id} | Size: {payload_length} bytes | Latency: {latency} ms | FPS: {fps:.2f} | Throughput: {throughput_kbps:.2f} KB/s")
          
            np_arr = np.frombuffer(payload, dtype=np.uint8)
            frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
            frame_count += 1

    finally:
        conn.close()
        server_socket.close()
        cv2.destroyAllWindows()

        ##

if __name__ == '__main__':
    run_server()