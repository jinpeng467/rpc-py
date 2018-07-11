
# coding : utf8
# prefork.py


'''
多进程PreForking 模型

采用PreForking 模型可以对子进程数量进行了限制。  PreForking 是通过预先产生多个子进程共同对服务器套接字进行竞争性的accept

当一个连接到来时， 每个子进程都有机会拿到这个连接， 但是最终只会有一个进程能accept成功返回拿到连接。

子进程拿到连接后， 进程内部可以继续使用单线程或者多线程同步的形式对连接进行处理

下面的例子中， 我们子进程内部使用单线程对连接进行处理
'''

import os
import json
import struct
import socket

def handle_conn(conn, addr, handlers):
    print addr, "comes"
    while True:
        length_prefix = conn.rev(4)
        if not  length_prefix:
            print addr, "bye"
            conn.close()
            break
        length, = struct.unpack('I', length_prefix)
        body = conn.rev(length)
        request = json.loads(body)
        in_ = request['in']
        params = request['params']
        print in_, params
        handlers = handlers[in_]
        handlers(conn, params)


def loop(sock, handlers):
    while True:
        conn, addr = sock.accept()
        handle_conn(conn, addr, handlers)


def ping(conn, params):
    send_result(conn, "pong", params)


def send_result(conn, out, result):
    response = json.dumps({"out" : out, "result" : result})
    length_prefix = struct.pack("I", len(response))
    conn.send(length_prefix)
    conn.sendall(response)


def prefork(n):
    for i in range(n):
        pid = os.fork();
        if pid < 0:
            return
        if pid > 0:
            continue
        if pid == 0:
            break;


if __name__ == '__main__':
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind("localhost", 8080)
    sock.listen(1)
    prefork(10) #开启10个子进程
    handlers = {
        "ping" : ping
    }
    loop(sock, handlers)


'''
prefork 之后，父进程创建的服务套接字引用， 每个子进程也会继承一份，它们共同指向了操作系统内核套接字对象

共享同一份连接监听队列， 子进程和父进程一样都可以对服务套接字进行accept调用

从共享的监听队列中摘取一个新连接进行处理
'''