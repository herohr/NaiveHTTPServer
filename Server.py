import socket
import threading
import logging
logging.basicConfig(level=logging.DEBUG)  # 设置日志级别


class Response:  # 基础响应对象
    def __init__(self, status_num=200, status_notes="OK", header=None, content=""):
        self.status_num = status_num
        self.status_notes = status_notes
        self.header = header
        self.content = content

        self.status_str = 'HTTP/1.1 {} {}\r\n'.format(status_num, status_notes)
        header = header if header else {}
        # 将header字典中的数据变为字符串
        self.header_str = ''.join(["{}: {}\r\n".format(key, value) for key, value in header.items()] + ["\r\n"])
        self.content_str = content

    def package(self):  # 对象需要打包之后才能够返回给客户端
        return ''.join([self.status_str, self.header_str, self.content_str]).encode("utf-8")


class Handler:  # 解析模块
    def __init__(self, server_socket=None):  # 这里传入socket对象，不能传入server对象
        self.server_socket = server_socket
        self.route_dic = {}

    def set_server_socket(self, server_socket):
        self.server_socket = server_socket

    def request_resolve(self, request_sock, address):  # 解析请求并执行响应函数并返回
        data = request_sock.recv(2048).decode('utf-8')
        data = data.split("\r\n")
        header = data[0]
        method, url, verison = header.split()
        logging.info("{} ====>> {}".format(address, url))

        handle_func = self.route_dic.get(url)  # 获取相应的响应函数
        if handle_func:
            request_sock.send(handle_func())
        else:
            request_sock.send(self.not_found().package())
        request_sock.close()

    def route(self, url):  # 模仿flask中的装饰器模式，对函数用装饰器封装，并设置URL映射
        this = self

        def route_decorator(function):
            def _handle(*args, **kwargs):
                response = function(*args, **kwargs)
                return response.package()

            this.route_dic[url] = _handle
            return _handle

        return route_decorator

    @staticmethod
    def not_found():
        return Response(status_num=404, status_notes="Not Found")


class NaiveServer:  # 对socket进行封装
    def __init__(self, host='localhost', port=23333):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((host, port))
        self.handler = Handler(self.server_socket)

    def run(self):
        if self.server_socket and self.handler:
            logging.info("Server is running on {}:{}".format(self.host, self.port))
            self.server_socket.listen()
            while True:
                sock, address = self.server_socket.accept()
                logging.info("A new request from : {}:{}".format(address[0], address[1]))
                threading.Thread(target=self.handler.request_resolve, args=(sock, address)).start()

    def route(self, url):
        return self.handler.route(url)
if __name__ == "__main__":
    server = NaiveServer('0.0.0.0', 80)


    @server.route('/')
    def index():
        return Response(content="Hello World!")


    @server.route('/i-want-something')
    def redirect():
        return Response(status_num=302, status_notes="Go to index", header={"Location": "/something"})


    @server.route('/something')
    def something():
        return Response(content="Here are something you want")

    server.run()
