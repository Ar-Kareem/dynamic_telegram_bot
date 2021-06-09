from pathlib import Path

from src.core.actions import AddServerHandler
from src.core.start import Pocket
from src.utils.simple_server.simple_server import MyHTTPHandler


def init(pocket: Pocket):
    pocket.store.dispatch(AddServerHandler('get', '/favicon.ico/', serve_favicon))


def serve_favicon(self: MyHTTPHandler):
    self.send_response(200)
    self.send_header('Content-type', 'image/png')
    self.end_headers()
    with open(self.pocket.database_dir / 'misc' / 'favicon.ico', 'rb') as f:
        self.wfile.write(f.read())
