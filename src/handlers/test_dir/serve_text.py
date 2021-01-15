import logging
from functools import partial
import time

from telegram import Update
from telegram.ext import CommandHandler, CallbackContext

from src.core.actions import TelegramBotInitiated, AddServerHandler
from src.core.start import Pocket
from src.utils.affiliates import BaseAction
from src.utils.simple_server.simple_server import MyHTTPHandler


logger = logging.getLogger(__name__)
pocket_dict_name = 'telegram_to_http_dict'


def serve(update: Update, context: CallbackContext) -> None:
    pocket: Pocket = context.bot_data['pocket']
    text = update.effective_message.text
    pocket.get(pocket_dict_name)['text'] = text
    pocket.get(pocket_dict_name)['start_time'] = time.time()
    update.effective_message.reply_text('done')


def init_bot_handlers(action: BaseAction, pocket: Pocket):
    dispatcher = pocket.telegram_updater.dispatcher
    dispatcher.add_handler(CommandHandler("serve", serve))


def init(pocket: Pocket):
    pocket.set(pocket_dict_name, {})
    pocket.reducer.register_handler(trigger=TelegramBotInitiated, callback=partial(init_bot_handlers, pocket=pocket))
    pocket.store.dispatch(AddServerHandler('get', '/from_t/', from_telegram))


def from_telegram(self: MyHTTPHandler):
    self.send_response(200)
    self.send_header("Content-type", "text/html")
    self.end_headers()
    self.wfile.write(bytes("<html><head><title>Response</title></head>", "utf-8"))
    self.wfile.write(bytes("<body>", "utf-8"))
    t = self.pocket.get(pocket_dict_name).get('text', '')
    if t and (time.time() - self.pocket.get(pocket_dict_name)['start_time']) < 5:
        self.wfile.write(bytes('<div>%s</div>' % t, "utf-8"))
    self.wfile.write(bytes("</body></html>", "utf-8"))

