import logging
import os
import json

from src.utils.simple_server.simple_server import MyHTTPHandler, InternalServerError

from src.core.actions import AddServerHandler
from src.core.pocket import Pocket


logger = logging.getLogger(__name__)
MAX_POST_BYTES = 2**14


def init(pocket: Pocket):
    asset_dir = pocket.database_dir / 'frontend_testapp'
    if not asset_dir.exists():
        logger.warning('Cant deploy testapp, does not exist on database')
        return
    pocket.set(__name__, {
        'asset_dir': asset_dir,
        'asset_files': os.listdir(asset_dir),
        'asset_files_cache': {},
    })
    pocket.store.dispatch(AddServerHandler('get', '/testapp/', handle_asset))
    pocket.store.dispatch(AddServerHandler('post', '/testapp/', handle_post))


def handle_asset(self: MyHTTPHandler):
    """ Handle assets requested through GET method """
    # try:
    asset_name, *rest_of_path = self.path.split('/')[2:]
    if len(rest_of_path) > 0:
        raise InternalServerError(user_message='Invalid asset request')
    if asset_name == '':
        asset_name = 'index.html'
    dict_ = self.pocket.get(__name__)
    if asset_name not in dict_.get('asset_files'):
        raise InternalServerError(user_message='Unable to find requested asset')

    # assets exists, check cache then check physical dir
    if asset_name in dict_.get('asset_files_cache'):
        resp = dict_.get('asset_files_cache')[asset_name]
    else:  # must read from file
        with open(dict_.get('asset_dir') / asset_name, 'rb') as f:
            resp = f.read()
        dict_.get('asset_files_cache')[asset_name] = resp  # save in cache

    self.response.set_response_code(200)
    self.response.add_header('Cache-Control', 'max-age=%d' % (24*60*60))
    self.response.add_header('Content-type', 'text/html')
    self.response.set_data(resp)


def handle_post(self: MyHTTPHandler):
    """ handle api calls through the POST method """
    post_data = parse_post_data(self)
    api_path = self.path.split('/')[2:]
    resp = handle_api(api_path, post_data)
    resp = json.dumps(resp).encode('utf-8')

    self.response.set_response_code(200)
    self.response.add_header('Content-type', 'application/json')
    self.response.set_data(resp)


def parse_post_data(self: MyHTTPHandler):
    # read post data
    content_length = int(self.headers['Content-Length'])
    if content_length > MAX_POST_BYTES:
        raise InternalServerError(user_message='Max post data exceeded')
    post_data = self.rfile.read(content_length).decode("utf-8")
    if len(post_data) > 0:
        try:
            return json.loads(post_data)
        except Exception:
            raise InternalServerError(user_message='Could not parse post data.')
    return {}


def handle_api(api_path, post_data):
    if len(api_path) <= 1 or api_path[0] != 'api':
        raise InternalServerError(user_message='API root path not recognized')

    controller_name = api_path[1]
    header_params = api_path[2:]

    if controller_name == 'tree':
        return handle_tree(header_params, post_data)
    elif controller_name == 'node':
        return handle_node(header_params, post_data)

    raise InternalServerError(user_message='API requested controller not recognized')


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
