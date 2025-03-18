import threading
import socket

class ServerSocket(threading.Thread):
    def __init__(self, sc, sockname, server):
        super().__init__()
        self.sc = sc
        self.sockname = sockname
        self.server = server
        self.running = True

    def run(self):
        print(f"New connection from {self.sockname}")
        try:
            while self.running:
                data = self.sc.recv(1024)
                if not data:
                    break
                print(f"Received: {data.decode()} from {self.sockname}")
                self.sc.sendall(b"Message received")  # Gửi phản hồi

        except Exception as e:
            print(f"Error: {e}")
        finally:
            self.sc.close()
            print(f"Connection {self.sockname} closed")

class Server(threading.Thread):
    def __init__(self, host, port):
        super().__init__()
        self.host = host
        self.port = port

    def run(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((self.host, self.port))
        sock.listen(5)
        print("Listening at", sock.getsockname())

        try:
            while True:
                sc, sockname = sock.accept()
                print(f"Accepted a new connection from {sc.getpeername()} to {sc.getsockname()}")
                server_socket = ServerSocket(sc, sockname, self)
                server_socket.start()
                self.connections.append(server_socket)
                print("Ready to recieve mesages from", sc.getpeername())
        except KeyboardInterrupt:
            print("Server shutting down...")
        finally:
            sock.close()
    def broadcast(self,message,source):
        for connection in self.connections:
            if connection.socknaame != source:
                connection.send(message)
    def remove_connection(self,connection):
        self.connection.remove(connection)

if __name__ == "__main__":
    server = Server("0.0.0.0", 12345)
    server.start()
