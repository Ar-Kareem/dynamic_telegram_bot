import logging
from functools import partial

from telegram import Update
from telegram.ext import CommandHandler, MessageHandler, Filters, CallbackContext

from src.core.actions import TelegramBotInitiated
from src.core.start import Pocket
from src.utils.affiliates import BaseAction
import time
from src.utils.simple_server.simple_server import MyHTTPHandler


logger = logging.getLogger(__name__)


def test(update: Update, context: CallbackContext) -> None:
    logger.info('Test Activated.')
    update.message.reply_text('test :)')


def init_bot_handlers(action: BaseAction, pocket: Pocket):
    dispatcher = pocket.telegram_updater.dispatcher
    dispatcher.add_handler(CommandHandler("test", test))


def init(pocket: Pocket):
    pocket.reducer.register_handler(trigger=TelegramBotInitiated, callback=partial(init_bot_handlers, pocket=pocket))
    pocket.set('start_time', time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
