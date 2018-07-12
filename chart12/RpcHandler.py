#coding: utf8

import json
import struct
import socket
import asyncore


from cStringIO import StringIO

class RPCHandler(asyncore.dispatcher_with_send):
    def __init__(self, sock, addr):
        asyncore.dispatcher_with_send.__init__(self, sock=sock)
        self.addr = addr
        self.handlers = {
            "ping" : self.ping
        }
        self.rbuf = StringIO()

    def handdle_connect(self): #新的连接被accept 后回调的方法
        print self.addr, "comes"

    def handdle_close(self):
        print self.addr, "bye"
        self.close()

    def handle_read(self):
        while True:
            content = self.recv(1024)
            if content:
                self.rbuf.write(content)
            if len(content) < 1024:
                break
        self.handle_rpc()


    def handle_rpc(self):
        while True: #可能一次性收到了多个请求消息， 所以要循环处理
            self.rbuf.seek(0)
            length_prefix = self.rbuf.read(4)
            if len(length_prefix) < 4:  #不足一个消息
                break
            lenth, = struct.unpack("I", length_prefix)
            body = self.rbuf.read(lenth)
            if len(body) < lenth:
                break
            request = json.loads(body)
            in_ = request['in']
            params = request['params']
            print in_, params
            handler(params)
            left = self.rbuf.getvalue()[lenth + 4:]  #消息处理完了，缓冲区要截断
            self.rbuf = StringIO()
            self.rbuf.write(left)

        self.rbuf.seek(0, 2) #将游标挪到文件的结尾， 以便后续读到的内容直接追加

    def ping(self, params):
        self.send_result("pong", params)

    def send_result(self, out, result):
        response = {"out": out, "result" : result}
        body = json.dump(response)
        length_prefix = struct.pack("I", len(body))
        self.send(length_prefix) #写入缓冲区
        self.send(body) #写入缓冲区


class RPCServer(asyncore.dispatcher):
     def __int__(self, host, port):
         asyncore.dispatcher.__init__(self)
         self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
         self.set_reuse_addr()
         self.bind((host, port))
         self.listen(1)

     def handle_accept(self):
         pair = self.accept()
         if pair is not None:
             sock, addr = pair
             RPCHandler(sock, addr) #处理连接





 if __name__ == '__main__':
     RPCServer("localhost", 8080)
     asyncore.loop()
