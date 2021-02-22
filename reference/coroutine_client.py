# https://www.bilibili.com/video/BV1N4411S7BP

# callback-based async framework
# * non-blocking socket
# * callbacks
# * event loop
# -> coroutines!
# * Future
# * generators
# * Task is responsible for calling next() on generators

import socket
import time
from selectors import DefaultSelector, EVENT_READ, EVENT_WRITE

selector = DefaultSelector()
n_tasks = 0


class Future:  # future类代表着一些我们正在等待但尚未完成的事件
    def __init__(self):
        self.callbacks = []  # 一个事件发生时将要被执行的回调列表

    def resolve(self):  # 当事件发生时，会调用resolve函数
        for c in self.callbacks:
            c()


class Task:
    def __init__(self, gen):
        self.gen = gen
        self.step()

    def step(self):
        try:
            f = next(self.gen)
        except StopIteration:
            return
        f.callbacks.append(self.step())


def get(path):
    global n_tasks
    n_tasks += 1
    s = socket.socket()
    s.setblocking(False)
    try:
        s.connect(('localhost', 5000))
    except BlockingIOError:
        pass

    request = 'GET %s HTTP/1.0\r\n\r\n' % path

    f = Future()
    selector.register(s.fileno(), EVENT_WRITE, data=f)

    # need to pause until s is writable...
    yield f  # resumes here
    selector.unregister(s.fileno())
    # s is writable!
    s.send(request.encode())

    chunks = []
    f = Future()
    while True:
        selector.register(s.fileno(), EVENT_READ, data=f)
        yield f
        # s is readable!
        selector.unregister(s.fileno())
        chunk = s.recv(1000)
        if chunk:
            chunks.append(chunk)
        else:
            body = (b''.join(chunks)).decode()
            print(body.split('\n')[0])
            n_tasks -= 1
            return


start = time.time()
Task(get('/foo'))
Task(get('/bar'))

while n_tasks:
    events = selector.select()
    for event, mask in events:
        fut = event.data
        fut.resolve()

print('took %.1f sec' % (time.time() - start))
