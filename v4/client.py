from socket import *

HOST = "localhost"
PORT = 22222
BUFSIZ = 1024
ADDR = (HOST, PORT)


class Client:
    def __init__(self):
        self.tcp_client_socket = socket(AF_INET, SOCK_STREAM)

    def run(self):
        self.tcp_client_socket.connect(ADDR)
        while True:
            data = input(">")
            if not data:
                break
            self.tcp_client_socket.send(data.encode("utf8"))
            data = self.tcp_client_socket.recv(BUFSIZ)
            if not data:
                print("recv nothing, probably server is closed.")
                break
            print(data.decode("utf8"))
        self.tcp_client_socket.close()
        print("client is closed.")


if __name__ == '__main__':
    c = Client()
    c.run()
