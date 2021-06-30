import logging
from functools import partial
import time

from telegram import Update
from telegram.ext import CommandHandler, CallbackContext

from src.core.actions import TelegramBotInitiated, AddServerHandler
from src.core.pocket import Pocket
from src.utils.affiliates import BaseAction
from src.utils.simple_server.simple_server import MyHTTPHandler


logger = logging.getLogger(__name__)


def serve(update: Update, context: CallbackContext) -> None:
    pocket: Pocket = context.bot_data['pocket']
    text = update.effective_message.text
    pocket.get(__name__)['text'] = text
    pocket.get(__name__)['start_time'] = time.time()
    update.effective_message.reply_text('done')


def init_bot_handlers(action: BaseAction, pocket: Pocket):
    dispatcher = pocket.telegram_updater.dispatcher
    dispatcher.add_handler(CommandHandler("serve", serve))


def init(pocket: Pocket):
    pocket.set(__name__, {})
    pocket.reducer.register_handler(trigger=TelegramBotInitiated, callback=partial(init_bot_handlers, pocket=pocket))
    pocket.store.dispatch(AddServerHandler('get', '/from_t/', from_telegram))


def from_telegram(self: MyHTTPHandler):
    self.response.set_response_code(200)
    self.response.add_header("Content-type", "text/html")
    self.response.append_data(bytes("<html><head><title>Response</title></head>", "utf-8"))
    self.response.append_data(bytes("<body>", "utf-8"))
    t = self.pocket.get(__name__).get('text', '')
    if t and (time.time() - self.pocket.get(__name__)['start_time']) < 5:
        self.response.append_data(bytes('<div>%s</div>' % t, "utf-8"))
    self.response.append_data(bytes("</body></html>", "utf-8"))
