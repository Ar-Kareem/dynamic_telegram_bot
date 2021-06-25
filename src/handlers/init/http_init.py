import logging
from functools import partial
import os
import base64
import secrets
from http import HTTPStatus

from src.core.actions import Terminate, AddServerHandler
from src.core.pocket import Pocket
from src.utils.simple_server.simple_server import MyHTTPHandler, start_server, close_server, HTTPResponse, \
    InternalServerError

logger = logging.getLogger(__name__)
DICT_NAME = 'http_handler_dict'


def init(pocket: Pocket):
    if not pocket.config.getboolean('SERVER', 'start', fallback=False):
        return
    pocket.set(DICT_NAME, {})

    localhost = pocket.config.getboolean('SERVER', 'localhost', fallback=False)
    server_port = pocket.config.getint('SERVER', 'port', fallback=8049)
    use_ssl = pocket.config.getboolean('SERVER', 'SSL', fallback=False)
    ssl_cert_key_paths = None
    timeout = pocket.config.getfloat('SERVER', 'timeout', fallback=None)
    if use_ssl:
        pem_files = pocket.database_dir / 'ssl' / 'pem_files'
        if not pem_files.exists():
            logger.warning('Cant deploy server with ssl, certificates not found in database')
            return
        website_dir = pem_files / os.listdir(pem_files)[0]
        pem_files = os.listdir(website_dir)
        full_chain = sorted([f for f in pem_files if f.startswith('fullchain')])[-1]
        private_key = sorted([f for f in pem_files if f.startswith('privkey')])[-1]
        ssl_cert_key_paths = [website_dir / full_chain, website_dir / private_key]

    pocket_to_inject = pocket  # have to rename the variable before injecting (cant do pocket=pocket inside class)

    class Handler(CustomHandler):
        pocket = pocket_to_inject

    try:
        http_server = start_server(Handler, localhost=localhost, port=server_port,
                                   ssl_cert_key_paths=ssl_cert_key_paths, timeout=timeout)
    except Exception:
        logger.exception('Failed to start HTTP server at port %d', server_port)
        return

    # Register Handlers for adding functionality to the server and terminating the server
    pocket.reducer.register_handler(trigger=Terminate, callback=lambda _: close_server(http_server))
    pocket.reducer.register_handler(trigger=AddServerHandler, callback=partial(add_server_handler, pocket=pocket))


class CustomHandler(MyHTTPHandler):
    """Custom handler to route requests, implement sessions, and track ips"""
    logger = logger
    pocket: Pocket

    def do_POST(self):
        self.handle_http_request('POST')

    def do_GET(self):
        self.handle_http_request('GET')

    def handle_http_request(self, method: str):
        module_dict: dict = self.pocket.get(DICT_NAME)
        handlers = module_dict.setdefault(method, [])  # dict from path to dynamically attached controller
        path = self.path
        if not path.endswith('/'):
            path += '/'
        self.path_split = path.split('/')  # helpful variable is a list of the requested path
        for prefix, handler in handlers:
            if path.startswith(prefix):  # valid path found
                self.capture_statistics(True)
                # self.new_request()
                try:
                    handler(self)
                except InternalServerError as e:
                    self.response.set_response_code(e.status)
                    self.response.set_data(e.user_message)
                    logger.warning('Internal server error. [from %s] [to %s]. Cause: %s',
                                   self.client_address[0], self.path, e.cause)
                except Exception as e:
                    self.response.set_response_code(HTTPStatus.INTERNAL_SERVER_ERROR)
                    self.response.set_data(b'UNEXPECTED INTERNAL SERVER ERROR.')
                    logger.exception('Unexpected exception when handling HTTP request [from %s] [to %s]',
                                     self.client_address[0], self.path)
                self.assign_response_data()
                return

        self.capture_statistics(False)
        self.response.set_response_code(HTTPStatus.NOT_FOUND)
        self.assign_response_data()
        logger.warning("No HTTP handler for %s: %s [from %s:%s]",
                       method, path, self.client_address[0], self.client_address[1])

    def new_request(self):
        sc = self.read_simple_cookie()
        if 'sess' not in sc:
            morsel = get_new_sess_morsel()  # get a new session token
            self.response.add_header("Set-Cookie", morsel.OutputString())  # assign it to request
            return
        sess = sc['sess']
        print(sess)

    def capture_statistics(self, hit: bool):
        print(self.client_address[0], hit)

    def log_message(self, format_: str, *args: any) -> None:
        try:
            if len(args) >= 1 and isinstance(args[0], str):
                if args[0].startswith('GET ') or args[0].startswith('POST '):
                    # supported method, no issue
                    return
                else:
                    self.logger.warning('Unsupported method: %s. [from %s:%s]',
                                        args[0], self.client_address[0], self.client_address[1])
                    return
            elif len(args) >= 2 and isinstance(args[1], str) and args[1].startswith('Unsupported method ('):
                # server logs twice if unsupported method, once handled above and the other is ignored here
                return
            self.logger.warning(format_, *args)
        except Exception as e:
            self.logger.exception(e)


def add_server_handler(action: AddServerHandler, pocket: Pocket):
    """This is called when an AddServerHandler action is dispatched and this function will add a new HTTP Handler"""
    module_dict: dict = pocket.get(DICT_NAME)
    method = action.method.upper()
    if method not in ('POST', 'GET'):
        logger.error('UNKNOWN METHOD: %s', method)
        return
    for other_prefix, _ in module_dict.setdefault(method, []):
        if action.prefix_to_handle.startswith(other_prefix) or other_prefix.startswith(action.prefix_to_handle):
            logger.error('Attempted to register server handler with a conflicting prefix old:(%s) new:(%s)',
                         other_prefix, action.prefix_to_handle)
            return
    t = (action.prefix_to_handle, action.handler)
    module_dict.setdefault(method, []).append(t)


def get_new_sess_morsel():
    noise = secrets.token_bytes(42)
    b64 = base64.b64encode(noise).decode()
    b64 = b64.replace('+', '-')  # http will need to encode + so just replace with -
    return MyHTTPHandler.get_morsel('sess', b64, expires=60, path='/')
