import logging
from pathlib import Path
import os
import json

from src.utils.simple_server.simple_server import MyHTTPHandler

from src.core.actions import AddServerHandler
from src.core.start import Pocket


logger = logging.getLogger(__name__)
MAX_POST_BYTES = 2**14


def init(pocket: Pocket):
    asset_dir = Path(__file__).parent / 'frontend'
    pocket.set(__name__, {
        'asset_dir': asset_dir,
        'asset_files': os.listdir(asset_dir)
    })
    pocket.store.dispatch(AddServerHandler('get', '/testapp/', handle_asset))
    pocket.store.dispatch(AddServerHandler('post', '/testapp/', handle_post))


class InternalServerError(Exception):
    def __init__(self, status=500, message="Internal Server Error"):
        self.status = status
        self.message = message
        super().__init__(self.message)


def handle_asset(self: MyHTTPHandler):
    """ Handle assets requested through GET method """
    try:
        asset_name, *rest_of_path = self.path.split('/')[2:]
        if len(rest_of_path) > 0:
            raise InternalServerError(message='Invalid asset request')
        if asset_name == '':
            asset_name = 'index.html'
        dict_ = self.pocket.get(__name__)
        if asset_name not in dict_.get('asset_files'):
            raise InternalServerError(message='Unable to find requested asset')
        with open(dict_.get('asset_dir') / asset_name, 'rb') as f:
            resp = f.read()
    except InternalServerError as e:
        self.send_response(e.status)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({'status': e.status, 'error': e.message}).encode('utf-8'))
        return
    except Exception as e:
        self.send_response(500)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({'status': 500, 'error': 'Exception occured. Check logs'}).encode('utf-8'))
        return
    self.send_response(200)
    self.send_header('Content-type', 'text/html')
    self.end_headers()
    self.wfile.write(resp)


def handle_post(self: MyHTTPHandler):
    """ handle api calls through the POST method """
    try:
        post_data = parse_post_data(self)
        api_path = self.path.split('/')[2:]
        resp = handle_api(api_path, post_data)
        resp = json.dumps(resp).encode('utf-8')
    except InternalServerError as e:
        self.send_response(e.status)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({'status': e.status, 'error': e.message}).encode('utf-8'))
        return
    except Exception as e:
        self.send_response(500)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({'status': 500, 'error': 'Exception occured. Check logs'}).encode('utf-8'))
        return
    self.send_response(200)
    self.send_header('Content-type', 'application/json')
    self.end_headers()
    self.wfile.write(resp)


def parse_post_data(self: MyHTTPHandler):
    # read post data
    content_length = int(self.headers['Content-Length'])
    if content_length > MAX_POST_BYTES:
        raise InternalServerError(message='Max post data exceeded')
    post_data = self.rfile.read(content_length).decode("utf-8")
    return json.loads(post_data)


def handle_api(api_path, post_data):
    if len(api_path) <= 1 or api_path[0] != 'api':
        raise InternalServerError(message='API root path not recognized')

    controller_name = api_path[1]
    header_params = api_path[2:]

    if controller_name == 'tree':
        return handle_tree(header_params, post_data)
    elif controller_name == 'node':
        return handle_node(header_params, post_data)

    raise InternalServerError(message='API requested controller not recognized')


def handle_tree(params, data):
    result = data
    for p in params:
        result[p] = len(result)
    result['handle_tree'] = 'CALLED'
    return result


def handle_node(params, data):
    result = data
    for p in params:
        result[p] = 'TEST'
    result['handle_node'] = 'CALLED'
    return result
