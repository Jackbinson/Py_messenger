import threading
import socket

class Server(threading.Thread):
    def __init__(self, host, port):
        super().__init__()
        self.host = host
        self.port = port
        self.connections = []

    def run(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((self.host, self.port))
        sock.listen(5)  # Cho phép tối đa 5 kết nối
        print("Listening at", sock.getsockname())

        try:
            while True:
                sc, sockname = sock.accept()
                print(f"Accepted a new connection from {sc.getpeername()} to {sc.getsockname()}")
                self.connections.append(sc)

                # Tạo một thread để xử lý client
                client_thread = threading.Thread(target=self.handle_client, args=(sc,))
                client_thread.start()
        except KeyboardInterrupt:
            print("Server shutting down...")
        finally:
            sock.close()

    def handle_client(self, sc):
        while True:
            try:
                message = sc.recv(1024).decode('ascii')
                if not message:
                    break
                print(f"Received: {message}")

                # Gửi lại tin nhắn cho tất cả client
                for conn in self.connections:
                    if conn != sc:
                        conn.sendall(message.encode('ascii'))
            except:
                break
        sc.close()
        self.connections.remove(sc)

if __name__ == "__main__":
    server = Server("127.0.0.1", 12345)
    server.start()
