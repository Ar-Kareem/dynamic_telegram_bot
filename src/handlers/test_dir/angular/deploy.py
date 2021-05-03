import logging
from pathlib import Path
import os
import json

from src.utils.simple_server.simple_server import MyHTTPHandler

from src.core.actions import AddServerHandler
from src.core.start import Pocket


logger = logging.getLogger(__name__)


def init(pocket: Pocket):
    asset_dir = Path(__file__).parent / 'frontend'
    pocket.set(__name__, {
        'asset_dir': asset_dir,
        'asset_files': os.listdir(asset_dir)
    })
    pocket.store.dispatch(AddServerHandler('get', '/testapp/', backend_root))


def backend_root(self: MyHTTPHandler):
    path = self.path.split('/')[2:]
    if len(path) == 1:
        handle_asset(self, path[0])
    elif path[0] == 'api':
        handle_api(self, path[1], path[2:])
    else:
        self.send_response(403)
        self.end_headers()
        return


def handle_asset(self: MyHTTPHandler, asset_name: str):
    if asset_name == '':
        asset_name = 'index.html'
    dict_ = self.pocket.get(__name__)
    if asset_name not in dict_.get('asset_files'):
        self.send_response(403)
        self.end_headers()
        return
    self.send_response(200)
    self.send_header('Content-type', 'text/html')
    self.end_headers()
    with open(dict_.get('asset_dir') / asset_name, 'rb') as f:
        self.wfile.write(f.read())


def handle_api(self: MyHTTPHandler, api_name, *path):
    self.send_response(200)
    self.send_header('Content-type', 'text/html')
    self.end_headers()

    self.wfile.write(json.dumps({'test': api_name}).encode('utf-8'))
