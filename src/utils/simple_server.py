from http.server import BaseHTTPRequestHandler, HTTPServer
import threading


class MyHTTPHandler(BaseHTTPRequestHandler):
    # noinspection PyMissingConstructor
    def __init__(self):
        # do not call super yet.
        pass

    def __call__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

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


def start_server(handler: MyHTTPHandler, server_port: int = 8049, localhost: bool = False) -> HTTPServer:
    if localhost:
        hostname = 'localhost'
    else:
        hostname = ''

    webserver = HTTPServer((hostname, server_port), handler)
    thread = threading.Thread(target=webserver.serve_forever)
    thread.daemon = True
    thread.start()
    return webserver


def close_server(server: HTTPServer) -> None:
    server.shutdown()
    server.server_close()
