import logging
from functools import partial
from pathlib import Path

from telegram import Update
from telegram.ext import CommandHandler, CallbackContext, Filters, MessageHandler

from src.core.actions import TelegramBotInitiated
from src.core.start import Pocket
from src.utils.affiliates import BaseAction

logger = logging.getLogger(__name__)


def register_user(username, cache=[None]):
    usernames = cache[0]
    if usernames is None:
        with open(Path(__file__).parent / 'tracker.txt', 'a+') as f:
            f.seek(0)
            usernames = [line[:-1] for line in f.readlines()]
            cache[0] = usernames
            if username not in usernames:
                f.write(username + '\n')
                return True
        return False
    # else use cached version
    if username not in usernames:
        cache[0] = None
        return register_user(username)  # invalidate cache and retry
    return False


# Telegram Handlers
def log(update: Update, context: CallbackContext) -> None:
    username = update.effective_user.username
    try:
        new_user = register_user(username)
        if new_user:
            update.message.reply_text('NEW USER REGISTERED.')
    except Exception:
        logger.error('Could not track user: %s' % username)
        return


def init_bot_handlers(action: BaseAction, pocket: Pocket):
    dispatcher = pocket.telegram_updater.dispatcher
    dispatcher.add_handler(MessageHandler(Filters.all, log), group=22)


def init(pocket: Pocket):
    pocket.reducer.register_handler(trigger=TelegramBotInitiated, callback=partial(init_bot_handlers, pocket=pocket))
