from socket import *
from time import ctime

HOST = ""
PORT = 22222
BUFSIZ = 1024
ADDR = (HOST, PORT)


class Server:
    def __init__(self):
        self.tcp_server_socket = socket(AF_INET, SOCK_STREAM)
        self.tcp_server_socket.bind(ADDR)
        self.tcp_server_socket.listen(5)
        self.tcp_server_socket.setblocking(False)

        self.alive_client_list = []
        self.dead_client_list = []

    def accept(self):
        try:
            client_info = self.tcp_server_socket.accept()
        except BlockingIOError:
            pass
        else:
            print("...connected from:", client_info[1])
            client_info[0].setblocking(False)
            self.alive_client_list.append(client_info)

    def communicate(self):
        for tcp_client_socket, cli_addr in self.alive_client_list:
            try:
                data = tcp_client_socket.recv(BUFSIZ)
                if data:
                    print("get data '{}' from {}".format(data.decode("utf8"), cli_addr))
                    response = "I get '{}' at {}".format(data.decode("utf8"), ctime())
                    tcp_client_socket.send(response.encode("utf8"))
                else:
                    tcp_client_socket.close()
                    self.dead_client_list.append((tcp_client_socket, cli_addr))
                    print(cli_addr, "closed")
            except BlockingIOError:
                pass

    def clean(self):
        for client in self.dead_client_list:
            self.alive_client_list.remove(client)
        self.dead_client_list.clear()

    def run(self):
        try:
            print("waiting for connection...")
            while True:
                self.accept()
                self.communicate()
                self.clean()
        except KeyboardInterrupt:
            print("\nserver is going to closing...")
            self.tcp_server_socket.close()
            for tcp_client_socket, cli_addr in self.alive_client_list:
                tcp_client_socket.close()
                print(cli_addr, "closed")
            exit()
        finally:
            print("\nserver is closed.")


if __name__ == '__main__':
    s = Server()
    s.run()
