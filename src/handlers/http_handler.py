import logging
from functools import partial

from src.core.actions import Terminate, AddServerHandler
from src.core.start import Pocket
from src.utils.simple_server import MyHTTPHandler, start_server, close_server

logger = logging.getLogger(__name__)
pocket_dict_name = 'http_handler_dict'


def init(pocket: Pocket):
    pocket.set(pocket_dict_name, {})
    handler = MyHTTPHandler()
    handler.pocket = pocket
    for func in (do_POST, do_GET):
        handler.bind(func)
    http_server = start_server(handler, server_port=int(pocket.config['SERVER']['port']))

    pocket.reducer.register_handler(trigger=Terminate, callback=lambda _: close_server(http_server))
    pocket.reducer.register_handler(trigger=AddServerHandler, callback=partial(add_server_handler, pocket=pocket))


def add_server_handler(action: AddServerHandler, pocket: Pocket):
    module_inner_pocket: dict = pocket.get(pocket_dict_name)
    method = action.method.upper()
    if method not in ('POST', 'GET'):
        logger.error('UNKNOWN METHOD: %s', method)
        return
    for other_prefix, _ in module_inner_pocket.setdefault(method, []):
        if action.prefix_to_handle.startswith(other_prefix) or other_prefix.startswith(action.prefix_to_handle):
            logger.error('Attempted to register server handler with a conflicting prefix old:(%s) new:(%s)',
                         other_prefix, action.prefix_to_handle)
            return
    t = (action.prefix_to_handle, action.handler)
    module_inner_pocket.setdefault(method, []).append(t)


# Methods to be bound to MyHTTPHandler

def call_appropriate_handler(self: MyHTTPHandler, method: str):
    module_inner_pocket: dict = self.pocket.get(pocket_dict_name)
    handlers = module_inner_pocket.get(method)
    if handlers is None:
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        return
    for prefix, handler in handlers:
        if self.path.startswith(prefix):
            handler(self)
            return


def do_GET(self: MyHTTPHandler):
    call_appropriate_handler(self, 'GET')


def do_POST(self: MyHTTPHandler):
    call_appropriate_handler(self, 'POST')
