import json
import time
import struct
import socket


def rpc(sock, in_, params):
    request = json.dump({"in" : in_, "parms" : params}) #将Python对象编码成Json字符串
    length_prefix = struct.pack("I", len(request)) #struct对象， struct.pack(fmt, v1, v2,...) 返回一个字节流对象, 是参数按照fmt数据格式组合而成
    sock.send(length_prefix);  # 
    sock.sendall(request);
    length_prefix = sock.recv(4);
    length, = struct.unpack('I', length_prefix) #按照给定数据格式解开 （通常都是由struct pack进行打包的数据） 返回值是一个tuple
    body = sock.recv(length);
    response =  json.loads(body) #对数据进行解码， 将JSON对象转换为Python 字典
    return response["out"], response["result"];


if __name__ == '__main_':
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect("localhost", 8080);
    for i in range(10):
        out, result = rpc(s,"ping", "ireader % d" % i)
        print out, result
        time.sleep(1)
    s.close


