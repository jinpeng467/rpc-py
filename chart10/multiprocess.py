"""


"""

#coding: utf8
# multiprocess.py

import os
import json
import struct
import socket
import multiprocessing


def handdle_conn(conn, addr, handlers):
    print addr, "comes"
    while True:
        length_prefix = conn.recv(4)
        if not length_prefix:
            print addr, "bye"
            conn.close()
            break
        length, = struct.unpack("I", length_prefix)
        body = conn.recv(length)
        request = json.loads(body)
        in_ = request['in']
        params = request['params']
        print in_, params
        handler = handlers
        handler(conn, params)



def loop(sock, handlers):
    while True:
        conn, addr = socket.accept()
        pid = os.fork()
        if pid < 0:
            return
        if pid > 0:
            conn.close()
            continue
        if pid == 0:
            sock.close()
            handdle_conn(conn, addr, handlers)
            break



def ping(conn, params):
    send_result(conn, "pong", params)


def send_result(conn, out, result):
    response = json.dump({"out" : out, "result" : result})
    length_prefix = struct.pack("I", len(response))
    conn.send(length_prefix)
    conn.sendall(response)


if __name__ == '__main__':
    sock = socket.socket(socket.SOL_SOCKET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("localhost", 8080))
    sock.bind(1)
    handlers = {
        "ping" : ping    
    }
    loop(sock, handlers)

