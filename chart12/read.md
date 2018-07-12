##非阻塞IO
操作系统提供的文件读写操作默认都是同步的， 必须等到数据就绪后才能返回，如果数据没有就绪，它会阻塞当前的线程.
为了解决以上问题， 操作系统给文件读写提供了非阻塞选项。读写文件时提供一个O_NONBLOCK 选项，读写操作就不会阻塞

内核套接字的ReadBuffer 有多少字节，read操作就会返回多少字节。内核套接字的 WriteBuffer 有多少剩余字节空间，write 操作就写多少字节。我们通过读写的返回值就可以知道读写了多少数据。



```
socket = socket.socket()
socket.setblocking(0)  # 开启非阻塞模式
socket.read()  # 有多少读多少
socket.write()  # 能写多少是多少
```


##事件轮询
操作系统提供了事件轮询的API, 我们使用这个API来查询相关套接字是否有相应的读写事件，如果有的话该API会立即携带事件列表返回，如果没有事件， 该API会阻塞
阻塞多长时间通过参数设置， 阻塞看起来似乎不太好。如果服务器没什么事可以干，那睡大觉就是节省资源的最佳方式

调用事件轮询API拿到读写事件之后， 就可以接着对事件相关的套接字进行读写操作了， 这时候读写操作都是正常进行的， 不会浪费CPU空读空写

```
read_events, write_events = select.select(read_fds, write_fds, timeout)
for event in read_events:
    handle_read(event)
for event in write_events:
    handle_write(event)

```

现代操作系统往往都提供了多种事件轮询API,从古典的select 和poll系统调用进化到如今的epoll和kqueue 系统调用。 古典的使用简单， 性能差， 现代的使用复杂，性能超好。


##用户进程读写缓冲区

因为读是非阻塞的，意味着当我们想要读取 100 个字节时，我们可能经历了多次 read 调用，第一次读了 10 个字节，第二次读了 30 个字节，然后又读了 80 个字节。凑够了 100 个字节时，我们就可以解码出一个完整的请求对象进行处理了，还剩余的 20 个字节又是后面请求消息的一部分。这就是所谓的半包问题。

非阻塞 IO 要求用户程序为每个套接字维持一个 ReadBuffer，它和操作系统内核区的 ReadBuffer 不是同一个东西。用户态的 ReadBuffer 是由用户代码来进行控制。它的作用就是保留当前的半包消息，如果消息的内容完整了，就可以从 ReadBuffer 中取出来进行处理。

因为写是非阻塞的，意味着当我们想要写 100 个字节时，我们可能经历了多次 write 调用，第一次 write 了 10 个字节，第二次 write 了 30 个字节，最后才把剩余的 40 个字节写出去了。这就要求用户程序为每个套接字维护一个写缓冲区，把剩下的没写完的字节都放在里面，以便后续可写事件到来时，能继续把没写完的写下去。


##String IO
Python 内置的类库，类似于 Java 的 ByteArrayInputStream 和 ByteArrayOutputStream 的合体，将字符串当成一个文件一样使用，具备和文件一样的 read 和 write 操作。
Python 提供两个实现， 一个是纯Python实现的StringIO, 一个是底层C的实现cStringIO

from StringIO import StringIO  # 纯 python 的实现
from cStringIO import StringIO  # C 实现

s = StringIO()
s.write("hello, ireader")
s.seek(0)
s.read(1024)

#####asyncore
Python 内置的异步 IO 库。考虑到编写原生的事件轮询和异步读写的逻辑比较复杂，要考虑的细节非常多。所以 Python 对这一块的逻辑代码做了一层封装，简化了异步逻辑的处理，使用起来非常方便。asyncore负责socket事件轮询，用户编写代码时只需要提供回调方法即可，asyncore会在相应的事件到来时，调用用户提供的回调方法。比如当serversocket的read事件到来时，会自动调用handle_accept方法， 当socket的read事件到来时，调用handle_read方法。



