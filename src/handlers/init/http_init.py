import logging
from functools import partial
import os
from pathlib import Path

from src.core.actions import Terminate, AddServerHandler
from src.core.start import Pocket
from src.utils.simple_server.simple_server import MyHTTPHandler, start_server, close_server

logger = logging.getLogger(__name__)
DICT_NAME = 'http_handler_dict'


def init(pocket: Pocket):
    if not pocket.config.getboolean('SERVER', 'start', fallback=False):
        return
    pocket.set(DICT_NAME, {})

    # create HTTP Handler and bind functionality to it
    handler = MyHTTPHandler(logger=logger)
    handler.pocket = pocket
    handler.bind(log_message, as_name='log_message')
    handler.bind(lambda self: handle_http_request(self, 'POST'), as_name='do_POST')
    handler.bind(lambda self: handle_http_request(self, 'GET'), as_name='do_GET')

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
        fullchain = sorted([f for f in pem_files if f.startswith('fullchain')])[-1]
        privkey = sorted([f for f in pem_files if f.startswith('privkey')])[-1]
        ssl_cert_key_paths = [website_dir / fullchain, website_dir / privkey]

    try:
        http_server = start_server(handler, localhost=localhost, port=server_port,
                                   ssl_cert_key_paths=ssl_cert_key_paths, timeout=timeout)
    except Exception:
        logger.exception('Failed to start HTTP server at port %d', server_port)
        return

    # Register Handlers for adding functionality to the server and terminating the server
    pocket.reducer.register_handler(trigger=Terminate, callback=lambda _: close_server(http_server))
    pocket.reducer.register_handler(trigger=AddServerHandler, callback=partial(add_server_handler, pocket=pocket))


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


# Methods to be bound to MyHTTPHandler

def handle_http_request(self: MyHTTPHandler, method: str):
    module_dict: dict = self.pocket.get(DICT_NAME)
    handlers = module_dict.get(method)
    if handlers is None:
        send404(self)
        return
    path = self.path
    if not path.endswith('/'):
        path += '/'
    for prefix, handler in handlers:
        if path.startswith(prefix):
            try:
                handler(self)
            except Exception:
                logger.exception('Exception when handling HTTP request')
            return

    send404(self)
    logger.info("No HTTP handler for %s: %s [from %s:%s]", method, path, self.client_address[0], self.client_address[1])


def send404(self: MyHTTPHandler):
    self.send_response(404)
    self.send_header('Content-type', 'text/plain')
    self.end_headers()


def log_message(self: MyHTTPHandler, format_: str, *args: any) -> None:
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
    except Exception as e:
        # log the default issue below
        pass
    self.logger.warning(format_, *args)
