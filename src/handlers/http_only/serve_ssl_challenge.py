import logging

from src.core.actions import AddServerHandler
from src.core.pocket import Pocket
from src.utils.simple_server.simple_server import MyHTTPHandler


logger = logging.getLogger(__name__)


def init(pocket: Pocket):
    if not pocket.config.getboolean('SERVER SSL CHALLENGE', 'start', fallback=False):
        return
    serve_location = pocket.config.get('SERVER SSL CHALLENGE', 'serve_location')
    pocket.store.dispatch(AddServerHandler('GET', serve_location, serve_challenge))


def serve_challenge(self: MyHTTPHandler):
    challenge = self.pocket.config.get('SERVER SSL CHALLENGE', 'challenge_text')
    self.response.set_response_code(200)
    self.response.add_header('Content-type', 'application/notepad')
    self.response.add_header('Content-Disposition', 'attachment; filename="challenge.txt"')
    self.response.set_data(bytes(challenge, "utf-8"))
