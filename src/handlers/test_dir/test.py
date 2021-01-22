import json
import logging
from functools import partial
from threading import Timer
from pathlib import Path
from http import cookies
from time import time

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, CallbackContext

from src.core.actions import TelegramBotInitiated, AddServerHandler, TelegramMessageToMe, Terminate
from src.core.start import Pocket
from src.utils.affiliates import BaseAction
from src.utils.simple_server.simple_server import MyHTTPHandler


logger = logging.getLogger(__name__)


def test(update: Update, context: CallbackContext, const=None) -> None:
    logger.info('Test Activated.')
    pocket: Pocket = context.bot_data['pocket']
    test_keyboard = [
        [InlineKeyboardButton("1", callback_data='1'), InlineKeyboardButton("2", callback_data='2')],
        [InlineKeyboardButton("/testt", callback_data='/testt')]
    ]
    update.effective_message.reply_text('test :) ' + str(const), reply_markup=InlineKeyboardMarkup(test_keyboard))


def init_bot_handlers(action: BaseAction, pocket: Pocket):
    dispatcher = pocket.telegram_updater.dispatcher


def init(pocket: Pocket):
    pocket.reducer.register_handler(trigger=TelegramBotInitiated, callback=partial(init_bot_handlers, pocket=pocket))

    # pocket.store.dispatch(AddServerHandler('post', '/error', lambda s: print('hello')))
    pocket.store.dispatch(AddServerHandler('post', '/tasker/image/', test_post_handler))
    pocket.store.dispatch(AddServerHandler('get', '/index/', get_index))
    pocket.store.dispatch(AddServerHandler('get', '/reset/', get_handler))
    pocket.store.dispatch(AddServerHandler('get', '/error/', get_handler))
    pocket.store.dispatch(AddServerHandler('get', '/favicon.ico/', serve_favicon))
    pocket.store.dispatch(AddServerHandler('get', '/testcookie/', test_cookie))

    # pocket.store.dispatch(AddServerHandler('post', '/', test_post_handler))


def get_index(self: MyHTTPHandler):
    self.send_response(200)
    self.send_header("Content-type", "text/html")
    self.end_headers()
    self.wfile.write(bytes("<html><head><title>Response</title></head>", "utf-8"))
    self.wfile.write(bytes("<body>", "utf-8"))
    for prefix, _ in self.pocket.inner_pocket.get('http_handler_dict', {}).get('GET', {}):
        self.wfile.write(bytes('<div><a href="%s">%s</a></div>' % (prefix, prefix), "utf-8"))
    self.wfile.write(bytes("</body></html>", "utf-8"))


def get_handler(self: MyHTTPHandler):
    if not hasattr(self, 'counter'):
        self.counter = 0
    self.counter += 1

    self.send_response(200)
    self.send_header("Content-type", "text/html")
    self.end_headers()
    self.wfile.write(bytes("<html><head><title>Response</title></head>", "utf-8"))
    self.wfile.write(bytes("<p>Request: %s | Counter: %d</p>" % (self.path, self.counter), "utf-8"))
    self.wfile.write(bytes("<body>", "utf-8"))
    self.wfile.write(bytes("<p>Request Received.</p>", "utf-8"))
    self.wfile.write(bytes("</body></html>", "utf-8"))
    self.pocket.store.dispatch(TelegramMessageToMe(message=str(self.counter) + ' ' + self.path))

    if self.path.startswith('/reset') and self.counter > 1:
        Timer(1, lambda: self.pocket.store.dispatch(Terminate(reset_flag=True))).start()


def test_post_handler(self: MyHTTPHandler):
    self.send_response(200)
    self.send_header('Content-type', 'text/plain')
    self.end_headers()
    content_length = int(self.headers['Content-Length'])
    if content_length > 5*1024*1024:
        return
    self.data_string = self.rfile.read(content_length)
    js_data = json.loads(self.data_string)
    self.pocket.store.dispatch(TelegramMessageToMe(message='POST' + js_data))


def serve_favicon(self: MyHTTPHandler):
    self.send_response(200)
    self.send_header('Content-type', 'image/png')
    self.end_headers()
    with open(Path(__file__).parent / 'favicon.ico', 'rb') as f:
        self.wfile.write(f.read())


def test_cookie(self: MyHTTPHandler):
    self.send_response(200)
    self.send_header("Content-type", "text/html")

    c = self.read_simple_cookie()
    print(c, c['t'] if 't' in c else None)
    c = cookies.SimpleCookie()
    t = str(time())
    c[t] = '44'
    c[t]['max-age'] = 4
    c['t'] = '44'
    c['t']['max-age'] = 4
    self.set_simple_cookie(c)
    self.end_headers()

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
    self.wfile.write(bytes(html, "utf-8"))
