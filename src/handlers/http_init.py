import logging
from functools import partial

from src.core.actions import Terminate, AddServerHandler
from src.core.start import Pocket
from src.utils.simple_server import MyHTTPHandler, start_server, close_server

logger = logging.getLogger(__name__)
pocket_dict_name = 'http_handler_dict'


def init(pocket: Pocket):
    if not pocket.config.getboolean('SERVER', 'start'):
        return
    pocket.set(pocket_dict_name, {})

    # create HTTP Handler and bind functionality to it
    handler = MyHTTPHandler(logger=logger)
    handler.pocket = pocket
    for func in (do_POST, do_GET):
        handler.bind(func)

    # Attempt to start server at port given in config file
    server_port = int(pocket.config['SERVER']['port'])
    try:
        http_server = start_server(handler, port=server_port)
    except Exception:
        logger.exception('Failed to start HTTP server at port %d', server_port)

    # Register Handlers for adding functionality to the server and terminating the server
    pocket.reducer.register_handler(trigger=Terminate, callback=lambda _: close_server(http_server))
    pocket.reducer.register_handler(trigger=AddServerHandler, callback=partial(add_server_handler, pocket=pocket))


def add_server_handler(action: AddServerHandler, pocket: Pocket):
    """This is called when an AddServerHandler action is dispatched and this function will add a new HTTP Handler"""
    module_dict: dict = pocket.get(pocket_dict_name)
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

def call_appropriate_handler(self: MyHTTPHandler, method: str):
    module_dict: dict = self.pocket.get(pocket_dict_name)
    handlers = module_dict.get(method)
    if handlers is None:
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        return
    for prefix, handler in handlers:
        if self.path.startswith(prefix):
            try:
                handler(self)
            except Exception:
                logger.exception('Exception when handling HTTP request')
            return


def do_GET(self: MyHTTPHandler):
    call_appropriate_handler(self, 'GET')


def do_POST(self: MyHTTPHandler):
    call_appropriate_handler(self, 'POST')
