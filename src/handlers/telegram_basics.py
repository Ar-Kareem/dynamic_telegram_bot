import logging
from functools import partial

from telegram import Update
from telegram.ext import CommandHandler, CallbackContext

from src.core.actions import TelegramBotInitiated
from src.core.start import Pocket
from src.utils.affiliates import BaseAction

logger = logging.getLogger(__name__)


# Telegram Handlers
def logs(update: Update, context: CallbackContext) -> None:
    print('hello')
    update.message.reply_text('logss')


def init_bot_handlers(action: BaseAction, pocket: Pocket):
    dispatcher = pocket.telegram_updater.dispatcher
    dispatcher.add_handler(CommandHandler("logs", logs))


def init(pocket: Pocket):
    pocket.reducer.register_handler(trigger=TelegramBotInitiated, callback=partial(init_bot_handlers, pocket=pocket))
