import json
import logging
from threading import Timer
from http import cookies
from time import time

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext

from src.core.actions import AddServerHandler, TelegramMessageToMe, Terminate
from src.core.pocket import Pocket
from src.utils.simple_server.simple_server import MyHTTPHandler


logger = logging.getLogger(__name__)


def test(update: Update, context: CallbackContext, const=None) -> None:
    logger.info('Test Activated.')
    test_keyboard = [
        [InlineKeyboardButton("1", callback_data='1'), InlineKeyboardButton("2", callback_data='2')],
        [InlineKeyboardButton("/testt", callback_data='/testt')]
    ]
    update.effective_message.reply_text('test :) ' + str(const), reply_markup=InlineKeyboardMarkup(test_keyboard))


def init(pocket: Pocket):
    # pocket.store.dispatch(AddServerHandler('post', '/error', lambda s: print('hello')))
    pocket.store.dispatch(AddServerHandler('post', '/tasker/image/', test_post_handler))
    pocket.store.dispatch(AddServerHandler('get', '/index/', get_index))
    pocket.store.dispatch(AddServerHandler('get', '/reset/', get_handler))
    pocket.store.dispatch(AddServerHandler('get', '/error/', get_handler))
    pocket.store.dispatch(AddServerHandler('get', '/testcookie/', test_cookie))

    # pocket.store.dispatch(AddServerHandler('post', '/', test_post_handler))


def get_index(self: MyHTTPHandler):
    self.response.set_response_code(200)
    self.response.add_header("Content-type", "text/html")
    self.response.append_data(bytes("<html><head><title>Response</title></head>", "utf-8"))
    self.response.append_data(bytes("<body>", "utf-8"))
    from ..init.http_init import DICT_NAME
    for prefix, _ in self.pocket.inner_pocket.get(DICT_NAME, {}).get('GET', {}):
        self.response.append_data(bytes('<div><a href="%s">%s</a></div>' % (prefix, prefix), "utf-8"))
    self.response.append_data(bytes("</body></html>", "utf-8"))


def get_handler(self: MyHTTPHandler):
    if not hasattr(self, 'counter'):
        self.counter = 0
    self.counter += 1

    self.response.set_response_code(200)
    self.response.add_header("Content-type", "text/html")
    self.response.append_data(bytes("<html><head><title>Response</title></head>", "utf-8"))
    self.response.append_data(bytes("<p>Request: %s | Counter: %d</p>" % (self.path, self.counter), "utf-8"))
    self.response.append_data(bytes("<body>", "utf-8"))
    self.response.append_data(bytes("<p>Request Received.</p>", "utf-8"))
    self.response.append_data(bytes("</body></html>", "utf-8"))
    self.pocket.store.dispatch(TelegramMessageToMe(message=str(self.counter) + ' ' + self.path))

    if self.path.startswith('/reset') and self.counter > 1:
        Timer(1, lambda: self.pocket.store.dispatch(Terminate(reset_flag=True))).start()


def test_post_handler(self: MyHTTPHandler):
    self.response.set_response_code(200)
    self.response.add_header('Content-type', 'text/plain')
    content_length = int(self.headers['Content-Length'])
    if content_length > 5*1024*1024:
        return
    self.data_string = self.rfile.read(content_length)
    js_data = json.loads(self.data_string)
    self.pocket.store.dispatch(TelegramMessageToMe(message='POST' + js_data))


def test_cookie(self: MyHTTPHandler):
    self.response.set_response_code(200)
    self.response.add_header("Content-type", "text/html")

    c = self.read_simple_cookie()
    print(c, c['t'] if 't' in c else None)
    c = cookies.SimpleCookie()
    t = str(time())
    c[t] = '44'
    c[t]['max-age'] = 4
    c['t'] = '44'
    c['t']['max-age'] = 4
    self.response.set_simple_cookie(c)

    favicon = '<img src="/favicon.ico" alt="testtt" style="width:50px;height:50px;">'
    divfavicon = f'<div>{favicon*15}</div>'
    html = f''' 
    <html>
    <body>
        <div style="white-space: pre-line;">
            {str(self.headers)}
        </div>
        {divfavicon*15}
    </body>
    </html>
    '''
    self.response.append_data(bytes(html, "utf-8"))
