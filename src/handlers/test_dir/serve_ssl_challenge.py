import logging

from src.core.actions import AddServerHandler
from src.core.start import Pocket
from src.utils.simple_server.simple_server import MyHTTPHandler


logger = logging.getLogger(__name__)


def init(pocket: Pocket):
    if not pocket.config.getboolean('SERVER SSL CHALLENGE', 'start'):
        return
    serve_location = pocket.config.get('SERVER SSL CHALLENGE', 'serve_location')
    pocket.store.dispatch(AddServerHandler('GET', serve_location, serve_challenge))


def serve_challenge(self: MyHTTPHandler):
    challenge = self.pocket.config.get('SERVER SSL CHALLENGE', 'challenge_text')
    self.send_response(200)
    self.send_header('Content-type', 'application/notepad')
    self.send_header('Content-Disposition', 'attachment; filename="challenge.txt"')
    self.end_headers()
    self.wfile.write(bytes(challenge, "utf-8"))

