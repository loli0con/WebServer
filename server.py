from socket import *
from time import ctime

HOST = ""
PORT = 22223
BUFSIZ = 1024
ADDR = (HOST, PORT)


class Server:
    def __init__(self):
        self.tcp_server_socket = socket(AF_INET, SOCK_STREAM)
        self.tcp_server_socket.bind(ADDR)
        self.tcp_server_socket.listen(5)

    def run(self):
        try:
            while True:
                print("waiting for connection...")
                tcp_client_socket, cli_addr = self.tcp_server_socket.accept()
                print("...connected from:", cli_addr)
                while True:
                    data = tcp_client_socket.recv(BUFSIZ)
                    if not data:
                        break
                    print("get data '{}' from {}".format(data.decode("utf8"), cli_addr))
                    response = "I get '{}' at {}".format(data.decode("utf8"), ctime())
                    tcp_client_socket.send(response.encode("utf8"))
                tcp_client_socket.close()
        except KeyboardInterrupt:
            self.tcp_server_socket.close()
            exit()
        finally:
            print("\nserver is closed.")


if __name__ == '__main__':
    s = Server()
    s.run()
