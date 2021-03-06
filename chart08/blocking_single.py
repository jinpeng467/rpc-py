#coding utf8


import json
import  struct
import  socket


def handdle_conn(conn, addr, handlers):
    print addr, "comes"
    while True:
        length_prefix = conn.recv(4)
        if not length_prefix:
            print addr, "bye"
            conn.close()
            break
        length, = struct.unpack("I", length_prefix)
        boddy = conn.recv(length)
        request = json.loads(body)
        in_ = request['in']
        params = request['params']
        print in_, params
        handler = handlers[in_]
        handler(conn, params)


def loop(sock. handlers):
    while True:
        conn, addr = sock.acept()
        handdle_conn(conn,addr,handlers)





def ping(conn, params):
    sennd_result(conn, "pong", params)



def send_result(conn,out, result):
    response = json.dump({"out" : out, "result" : result})
    length_prefix = struct.pack("I", len(response))
    conn.send(length_prefix)
    conn.sendall(response)


if __name__ == '__main__':
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind("localhost", 8080)
    sock.listen(1)
    hadlers = {
        "ping" : ping
    }
    loop(sock, handlers)

