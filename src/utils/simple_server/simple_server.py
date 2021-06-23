#!/usr/bin/env python3

from http.server import BaseHTTPRequestHandler, HTTPServer
from http.cookies import SimpleCookie, Morsel
from typing import List, Type
from urllib.parse import quote
import threading
import socket
import logging


logger = logging.getLogger(__name__)


class MyHTTPHandler(BaseHTTPRequestHandler):
    pocket = None
    logger = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.path_split: List[str] = []

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
        """Default implementation of logger. This should be overridden by a logger implementation"""
        if self.logger is None:
            super().log_message(format_, *args)
        else:
            self.logger.info(format_, *args)

    def read_simple_cookie(self) -> SimpleCookie:
        sc = SimpleCookie()
        if self.headers.get('Cookie') is not None:
            sc.load(self.headers.get('Cookie'))
        return sc

    def set_simple_cookie(self, sc: SimpleCookie) -> None:
        for morsel in sc.values():
            self.send_header("Set-Cookie", morsel.OutputString())

    @staticmethod
    def get_morsel(name, value, expires=-1, domain=None,
                   secure=False, httponly=False, path=None):
        morsel = Morsel()
        morsel.set(name, value, quote(value))
        if expires < 0:
            expires = -1000000000
        morsel['expires'] = expires
        morsel['path'] = path
        if domain:
            morsel['domain'] = domain
        if secure:
            morsel['secure'] = secure
        value = morsel.OutputString()
        if httponly:
            value += '; httponly'
        return morsel


def start_server(handler: Type[BaseHTTPRequestHandler], hostname: str = None,
                 localhost: bool = False, port: int = 8049,
                 ssl_cert_key_paths: list = None, timeout: int = None) -> HTTPServer:
    if hostname is None:
        if localhost:
            hostname = 'localhost'
        else:
            # don't used socket.gethostname(), will not work on wsl for some reason. '' is 0.0.0.0
            hostname = ''

    if timeout is not None:
        __set_timeout(timeout)

    webserver = HTTPServer((hostname, port), handler)

    if ssl_cert_key_paths is not None:
        import ssl
        webserver.socket = ssl.wrap_socket(webserver.socket,
                                           certfile=ssl_cert_key_paths[0], keyfile=ssl_cert_key_paths[1],
                                           server_side=True, ssl_version=ssl.PROTOCOL_TLSv1_2)
    thread = threading.Thread(target=webserver.serve_forever)
    thread.daemon = True
    thread.start()
    return webserver


def close_server(server: HTTPServer) -> None:
    server.shutdown()
    server.server_close()


# need to warn user if timeout is set multiple times since socket default timeout only supports single value overall
__timeout_value = -999.25


def __set_timeout(timeout):
    socket.setdefaulttimeout(timeout)
    global __timeout_value
    if __timeout_value != -999.25:
        logger.warning("timeout has been set multiple times. Overwriting and only taking latest value. "
                       "(no support for multiple servers with different timeouts)")
    __timeout_value = timeout


def main():
    class Child(MyHTTPHandler):
        logger = type('l', (), {'info': print})()
    # webserver = HTTPServer((socket.gethostname(), 8092), Child)
    webserver = HTTPServer(('0.0.0.0', 8091), Child)
    # import ssl
    # webserver.socket = ssl.wrap_socket(webserver.socket, server_side=True, certfile=_get_cert_path(),
    #                                    keyfile=__get_key_path(), ssl_version=ssl.PROTOCOL_TLSv1_2)
    webserver.serve_forever()


if __name__ == '__main__':
    main()
