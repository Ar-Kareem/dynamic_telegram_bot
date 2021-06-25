from pathlib import Path

from src.core.actions import AddServerHandler
from src.core.pocket import Pocket
from src.utils.simple_server.simple_server import MyHTTPHandler


def init(pocket: Pocket):
    pocket.set(__file__, {})
    pocket.store.dispatch(AddServerHandler('get', '/favicon.ico/', serve_favicon))


def serve_favicon(self: MyHTTPHandler):
    self.response.set_response_code(200)
    self.response.add_header('Content-type', 'image/png')
    d: dict = self.pocket.get(__file__)
    if 'favicon.ico' in d:
        self.response.append_data(d['favicon.ico'])
        return
    favicon_path = Path(self.pocket.database_dir / 'misc' / 'favicon.ico')
    if not favicon_path.exists():
        d['favicon.ico'] = b''
        return
    with open(favicon_path, 'rb') as f:
        d['favicon.ico'] = f.read()
        self.response.append_data(d['favicon.ico'])
