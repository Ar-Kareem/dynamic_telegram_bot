import json
import logging
from functools import partial
from threading import Timer

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
    pocket.store.dispatch(AddServerHandler('post', '/tasker/image/', get_handler))
    pocket.store.dispatch(AddServerHandler('get', '/index/', get_index))
    pocket.store.dispatch(AddServerHandler('get', '/reset/', get_handler))
    pocket.store.dispatch(AddServerHandler('get', '/error/', get_handler))

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
