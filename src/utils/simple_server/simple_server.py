#!/usr/bin/env python3
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, HTTPServer
from http.cookies import SimpleCookie, Morsel
from socketserver import ThreadingTCPServer
from typing import List, Type, Union, Tuple
from urllib.parse import quote
import json
import html
import threading
from socket import SocketType
import logging


logger = logging.getLogger(__name__)


class InternalServerError(Exception):
    def __init__(self, status=HTTPStatus.INTERNAL_SERVER_ERROR, user_message='', cause=''):
        self.status = status
        self.user_message = user_message
        if len(cause) > 0:
            self.cause = cause
        else:
            self.cause = self.user_message
        super().__init__(self.cause)


class HTTPResponse:
    """
    This class is needed since the order of assignment of parameters in BaseHTTPRequestHandler is critical.
    Thus, this class helps collect all the parameters in any order then assign all in proper order at the end
    """
    def __init__(self, response_code: int = HTTPStatus.INTERNAL_SERVER_ERROR,
                 headers: List[Tuple[str, str]] = None, data: Union[bytearray, bytes] = b''):
        self._response_code: int = response_code
        self._headers = []
        if headers is not None:
            self._headers = headers
        self._data: bytearray = bytearray(data)

    def set_response_code(self, response_code: int):
        self._response_code = response_code

    def add_header(self, key: str, val: str):
        self._headers.append((key, val))

    def set_data(self, data: Union[bytearray, bytes, str]):
        if isinstance(data, str):
            self._data = bytearray(data.encode())
        else:
            self._data = bytearray(data)

    def append_data(self, data: Union[bytearray, bytes, str]):
        if isinstance(data, str):
            self._data.extend(data.encode())
        else:
            self._data.extend(data)

    def set_simple_cookie(self, sc: SimpleCookie):
        for morsel in sc.values():
            self.add_header("Set-Cookie", morsel.OutputString())


class MyHTTPHandler(BaseHTTPRequestHandler):
    logger = None
    sessionManager = None
    pocket = None
    session = None

    # connection/socket parameters
    socket_timeout = None
    # performs ssl handshakes if needed
    ssl_wrapper_func = None
    pre_ssl_socket_timeout = None

    def __init__(self, request_socket: SocketType, *args, **kwargs):
        self.path_split: List[str] = []
        self.response = HTTPResponse()
        if self.ssl_wrapper_func is not None:
            request_socket.settimeout(self.pre_ssl_socket_timeout)
            request_socket = self.ssl_wrapper_func(request_socket)

        request_socket.settimeout(self.socket_timeout)
        super().__init__(request_socket, *args, **kwargs)

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

    def version_string(self):
        return 'nginx'  # we do a little trolling

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

    # noinspection PyProtectedMember
    def assign_response_data(self):
        """Takes the response object from MyHTTPHandler and assigns its data properly to BaseHTTPRequestHandler"""
        resp = self.response

        super().send_response(resp._response_code)
        if resp._response_code < 400:  # non-error response
            for (k, v) in resp._headers:
                super().send_header(k, v)

        elif resp._response_code >= 400:  # error response
            super().send_header('Connection', 'close')
            if self.command == 'GET' and resp._response_code == 404:  # GET and 404, close the connection with no data
                super().send_header("Content-Type", "text/html")
                resp.set_data(b'')
            elif self.command == 'GET' and resp._response_code != 404:  # GET: prepare html page with error explanation
                super().send_header("Content-Type", "text/html;charset=utf-8")
                try:
                    message = self.responses[resp._response_code][0]
                except KeyError:
                    message = '???'
                resp.set_data(
                    (self.error_message_format % {
                        'code': resp._response_code,
                        'message': html.escape(message, quote=False),
                        'explain': html.escape(resp._data.decode(), quote=False)
                    }).encode('UTF-8', 'replace')
                )
            elif self.command == 'POST':  # POST: prepare a json response with error explanation
                super().send_header("Content-Type", "application/json")
                resp.set_data(json.dumps(
                        {'response': resp._response_code, 'error': resp._data.decode()}
                    ).encode('utf-8'))
            else:
                super().send_header("Content-Type", "text/html")
                resp.set_data(b'')
                logger.warning('Unknown HTTP command. This should never happen.')

        super().send_header('Content-Length', str(len(resp._data)))
        super().end_headers()
        self.wfile.write(resp._data)

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


def start_server(handler: Type[BaseHTTPRequestHandler], hostname: str = None, localhost: bool = False,
                 port: int = 8049) -> ThreadingTCPServer:
    if hostname is None:
        if localhost:
            hostname = 'localhost'
        else:
            # don't used socket.gethostname(), will not work on wsl for some reason. '' is 0.0.0.0
            hostname = ''

    webserver = ThreadingTCPServer((hostname, port), handler)
    thread = threading.Thread(target=webserver.serve_forever)
    thread.daemon = True
    thread.start()
    return webserver


def close_server(server: ThreadingTCPServer) -> None:
    server.shutdown()
    server.server_close()


def main():
    class Child(MyHTTPHandler):
        logger = type('l', (), {'info': print})()
    # webserver = ThreadingTCPServer((socket.gethostname(), 8092), Child)
    webserver = ThreadingTCPServer(('0.0.0.0', 8091), Child)
    # import ssl
    # webserver.socket = ssl.wrap_socket(webserver.socket, server_side=True, certfile=_get_cert_path(),
    #                                    keyfile=__get_key_path(), ssl_version=ssl.PROTOCOL_TLSv1_2)
    webserver.serve_forever()


if __name__ == '__main__':
    main()
