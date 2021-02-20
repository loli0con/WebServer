from socket import *
from time import ctime
from select import select
from queue import Queue

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

        self.input_list = []
        self.output_list = []

        self.readable = []
        self.writable = []
        self.exceptional = []

        self.message_queue = {}  # tcp_client_socket : Queue[message1,message2,...]

        self.input_list.append(self.tcp_server_socket)

    def run(self):
        print("waiting for connection...")
        try:
            while True:
                self.readable, self.writable, self.exceptional = select(self.input_list, self.output_list,
                                                                        self.input_list)
                self.read()
                self.write()
                self.repair()
        except KeyboardInterrupt:
            print("\nserver is going to closing...")
            self.tcp_server_socket.close()
            for sock in self.input_list + self.output_list:
                if sock == self.tcp_server_socket:
                    continue
                self._clean_after_client_close(sock)
                exit()
        finally:
            self.check_unknown_error()
            print("\nserver is closed.")

    def read(self):
        for sock in self.readable:  # 遍历所有可读的sock
            if sock == self.tcp_server_socket:  # sock为server自己
                tcp_client_socket, cli_addr = self.tcp_server_socket.accept()
                print("...connected from:", cli_addr)
                self.input_list.append(tcp_client_socket)
                self.message_queue[tcp_client_socket] = Queue()

            else:  # sock为client
                try:
                    recv_data = sock.recv(BUFSIZ)
                    if recv_data:  # 收到client传来的数据
                        print("get data '{}' from {}".format(recv_data.decode("utf8"), sock.getpeername()))
                        response_data = "I get '{}' at {}".format(recv_data.decode("utf8"), ctime())
                        self.message_queue[sock].put(response_data)
                        if sock not in self.output_list:
                            self.output_list.append(sock)
                    else:  # client主动关闭
                        print(sock.getpeername(), 'is going to closing...')
                        self.input_list.remove(sock)  # 关闭读通道
                        if self.message_queue[sock].empty():
                            self._clean_after_client_close(sock)

                except ConnectionError as e:  # client 异常关闭。ps：能力有限，测试不到这种情况
                    print(e)
                    self._clean_after_client_close(sock)

    def write(self):
        for sock in self.writable:
            try:
                if not self.message_queue[sock].empty():  # 将队列中的消息发送给client，一次只发一条，尽可能少占用缓冲区
                    message = self.message_queue[sock].get()
                    sock.send(message.encode("utf8"))
                else:
                    self.output_list.remove(sock)
                    if sock not in self.input_list:  # 发送完数据后，如果不再从sock中读取数据，即意味着sock已经关闭了
                        self._clean_after_client_close(sock)

            except ConnectionError as e:  # client 异常关闭。ps：能力有限，测试不到这种情况
                print(e)
                self._clean_after_client_close(sock)

    def repair(self):
        if self.exceptional:
            print('has error!repairing...')
        for sock in self.exceptional:
            print('exception condition on', sock.getpeername())
            sock.cloese()
            self._clean_after_client_close(sock)

    def _clean_after_client_close(self, sock):
        if sock in self.input_list:
            self.input_list.remove(sock)
        if sock in self.output_list:
            self.output_list.remove(sock)
        if sock in self.message_queue:
            del self.message_queue[sock]
        print(sock.getpeername(), "closed")

    def check_unknown_error(self):
        if len(self.input_list) != 1:
            print('input_list', self.input_list, 'has error')
        if len(self.output_list) != 0:
            print('output_list', self.output_list, 'has error')
        if len(self.message_queue) != 0:
            print('message_queue', self.message_queue, 'has error')


if __name__ == '__main__':
    s = Server()
    s.run()
