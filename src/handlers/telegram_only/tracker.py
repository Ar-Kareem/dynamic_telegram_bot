import logging
from functools import partial
from pathlib import Path

from telegram import Update
from telegram.ext import CommandHandler, CallbackContext, Filters, MessageHandler

from src.core.actions import TelegramBotInitiated
from src.core.start import Pocket
from src.utils.affiliates import BaseAction

logger = logging.getLogger(__name__)


def register_user(username, file_path, cache=[None]):
    usernames = cache[0]
    if usernames is None:
        with open(file_path, 'a+') as f:
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
        return register_user(username, file_path)  # invalidate cache and retry
    return False


# Telegram Handlers
def log(update: Update, context: CallbackContext, file_path: Path) -> None:
    username = update.effective_user.username
    try:
        new_user = register_user(username, file_path)
        if new_user:
            update.message.reply_text('NEW USER REGISTERED.')
    except Exception:
        logger.error('Could not track user: %s' % username)
        return


def init_bot_handlers(action: BaseAction, pocket: Pocket):
    file_path = pocket.database_dir / 'telegram_username_tracker' / 'tracker.txt'
    dispatcher = pocket.telegram_updater.dispatcher

    def log_partial(*args):
        return log(*args, file_path=file_path)
    dispatcher.add_handler(MessageHandler(Filters.all, log_partial), group=22)


def init(pocket: Pocket):
    pocket.reducer.register_handler(trigger=TelegramBotInitiated, callback=partial(init_bot_handlers, pocket=pocket))
