from http.server import BaseHTTPRequestHandler, HTTPServer
from http.cookies import SimpleCookie
import threading
import socket
from logging import Logger


class MyHTTPHandler(BaseHTTPRequestHandler):
    """
    This class can be used with an HTTPServer as if it is a BaseHTTPRequestHandler
    The difference is that an HTTPServer creates a new instance of BaseHTTPRequestHandler for every request
    which means that no variables can persist throughout the request handler instance.
    This class helps by allowing it to be initialized and be assigned instance variables,
    whenever httpserver attempts to initialize the request handler (__call__ will be invoked).
    This only works because super().__init__ is safe to be invoked multiple times.
    This can be thought of as a metaclass except it's not.
    """
    # noinspection PyMissingConstructor
    def __init__(self, logger: Logger = None):
        # do not call super yet.
        self.logger = logger

    def __call__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        return self

    def bind(self, func, as_name: str = None) -> None:
        """
        Bind the function *func* to *self*, with either provided name *as_name*
        or the existing name of *func*. The provided *func* should accept the
        instance as the first argument, i.e. "self".
        """
        if as_name is None:
            as_name = func.__name__
        bound_method = func.__get__(self, self.__class__)
        setattr(self, as_name, bound_method)

    def log_message(self, format_: str, *args: any) -> None:
        if self.logger is not None:
            self.logger.info(format_, *args)

    def read_simple_cookie(self) -> SimpleCookie:
        sc = SimpleCookie()
        if self.headers.get('Cookie') is not None:
            sc.load(self.headers.get('Cookie'))
        return sc

    def set_simple_cookie(self, sc: SimpleCookie) -> None:
        for morsel in sc.values():
            self.send_header("Set-Cookie", morsel.OutputString())


def start_server(handler: MyHTTPHandler, hostname: str = None,
                 localhost: bool = False, port: int = 8049, ssl: bool = False) -> HTTPServer:
    if hostname is None:
        if localhost:
            hostname = 'localhost'
        else:
            hostname = socket.gethostname()

    webserver = HTTPServer((hostname, port), handler)
    if ssl:
        import ssl
        webserver.socket = ssl.wrap_socket(webserver.socket, certfile=_get_cert_path(), keyfile=__get_key_path(),
                                           server_side=True, ssl_version=ssl.PROTOCOL_TLSv1_2)
    thread = threading.Thread(target=webserver.serve_forever)
    thread.daemon = True
    thread.start()
    return webserver


def close_server(server: HTTPServer) -> None:
    server.shutdown()
    server.server_close()


def _get_cert_path():
    from pathlib import Path
    return Path(__file__).parent / 'fullchain1.pem'


def __get_key_path():
    from pathlib import Path
    return Path(__file__).parent / 'privkey1.pem'


def main():
    o = type('l', (), {'info': print})()
    webserver = HTTPServer((socket.gethostname(), 8049), MyHTTPHandler(logger=o))
    import ssl
    webserver.socket = ssl.wrap_socket(webserver.socket, server_side=True, certfile=_get_cert_path(),
                                       keyfile=__get_key_path(), ssl_version=ssl.PROTOCOL_TLSv1_2)
    webserver.serve_forever()


if __name__ == '__main__':
    main()
