# 翻墙服务器端
# 加解密，高计算量需要最大化使用CPU，多进程使用多核
# 数据包转发，IO操作，在每个进程中使用线程池
# TODO 支持epoll？直接用gevent撸server；这段代码只适合client跨平台？

from multiprocessing import Pool, Queue, Process, Manager
from multiprocessing.pool import ThreadPool
import multiprocessing, socket, logging, os

logging.basicConfig(level=logging.DEBUG)


def threadHandle(connection, address, logger):
    try:
        logger.debug("Connected %r at %r", connection, address)
        while True:
            data = connection.recv(1024)
            if data == b"":
                logger.debug("Socket closed remotely")
                break
            logger.debug("Received data %r", data)
            connection.sendall(data)
            logger.debug("Sent data")
    except:
        logger.exception("Problem handling request")
    finally:
        logger.debug("Closing socket")
        connection.close()


def callBack(p):
    logging.debug('callback %r', p)


def proHandle(q):
    logger = logging.getLogger("process-%r" % (os.getpid(),))
    tp = ThreadPool()
    while True:
        (connection, address) = q.get()
        logger.debug("proHandle get connection from Queue")
        tp.apply_async(threadHandle, (connection, address, logger), callback=callBack)


class Server(object):
    def __init__(self, hostname, port):
        self.logger = logging.getLogger("server")
        self.hostname = hostname
        self.port = port

    def start(self, q):
        self.logger.debug("listening")
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.hostname, self.port))
        self.socket.listen()

        while True:
            self.logger.debug("Waiting connection")
            conn, address = self.socket.accept()
            self.logger.debug("Got connection and Send it to Queue")
            q.put((conn, address), False)


if __name__ == "__main__":
    server = Server("0.0.0.0", 19000)

    try:
        m = Manager()
        q = m.Queue()
        for i in range(multiprocessing.cpu_count()):
            p = Process(target=proHandle, args=(q,))
            p.start()
        logging.info("Server Start")
        server.start(q)
    except:
        logging.exception("Unexpected exception")
    finally:
        logging.info("Shutting down")

    logging.info("All done")
