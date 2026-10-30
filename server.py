import cv2
import numpy as np
import socket
import struct
import time

PORT = 8080
HEADER_SIZE = 16  # 4 bytes length + 4 bytes frame_id + 8 bytes timestamp

def recv_exact(sock, n):
    """TODO 6: Implement a robust helper to read exactly n bytes from the TCP stream."""
    # التعديل: قراءة البيانات تدريجياً لضمان استقبال الحجم المطلوب كاملاً (n بايت) دون ضياع أي جزء
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
            header_bytes = recv_exact(conn, HEADER_SIZE)
            if not header_bytes:
                break

            # TODO 7: Unpack payload length, frame ID, and send timestamp using struct.unpack
            # التعديل: فك تشفير ترويسة الحجم (16 بايت) باستخدام '!IIQ' 
            # (! للترتيب الشبكي، I لطول البيانات ورقم الإطار، Q للزمن بحجم 8 بايت)
            payload_length, frame_id, send_timestamp = struct.unpack("!IIQ", header_bytes)

            frame_bytes = recv_exact(conn, payload_length)
            if not frame_bytes:
                break
            total_bytes += HEADER_SIZE + payload_length

            # TODO 6: Calculate and log performance metrics (Latency, FPS, Throughput KB/s)
            # التعديل: حساب قياسات الأداء (التأخير، عدد الإطارات في الثانية، ومعدل نقل البيانات)
            current_time = time.time()
            latency = (current_time * 1000) - (send_timestamp / 1000.0) # حساب التأخير بالميلي ثانية
            
            elapsed_time = current_time - start_time
            fps = frame_count / elapsed_time if elapsed_time > 0 else 0
            throughput = (total_bytes / 1024) / elapsed_time if elapsed_time > 0 else 0

            print(f"Frame {frame_id}: Latency={latency:.2f}ms, FPS={fps:.2f}, Throughput={throughput:.2f} KB/s")

            np_arr = np.frombuffer(frame_bytes, dtype=np.uint8)
            frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
            frame_count += 1
            
            # عرض الفيديو المستلم (اختياري لكن مفيد للتحقق المرئي)
            if frame is not None:
                cv2.imshow("Video Stream", frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

    finally:
        conn.close()
        server_socket.close()
        cv2.destroyAllWindows()

if __name__ == '__main__':
    run_server()