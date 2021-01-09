from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
import socket
from logging import Logger


class MyHTTPHandler(BaseHTTPRequestHandler):
    """
    This class can be used with an HTTPServer as if it is a BaseHTTPRequestHandler
    The difference is that an HTTPServer creates a new instance of BaseHTTPRequestHandler for every request
    which means that no variables can persist throughout the request handler instance.
    This class helps with that by allowing it to be initialized then can store instance variables,
    and each time httpserver attempts to initialize the request handler (__call__ will be invoked).
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


def start_server(handler: MyHTTPHandler, hostname: str = None, localhost: bool = False, port: int = 8049) -> HTTPServer:
    if hostname is None:
        if localhost:
            hostname = 'localhost'
        else:
            hostname = socket.gethostname()

    webserver = HTTPServer((hostname, port), handler)
    thread = threading.Thread(target=webserver.serve_forever)
    thread.daemon = True
    thread.start()
    return webserver


def close_server(server: HTTPServer) -> None:
    server.shutdown()
    server.server_close()


if __name__ == '__main__':
    start_server(MyHTTPHandler())
    print('Waiting...')
    cond = threading.Condition()
    with cond:
        cond.wait(threading.TIMEOUT_MAX)
