import logging
from functools import partial
import subprocess
import math
import os
import sys
from pathlib import Path

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    CommandHandler,
    CallbackQueryHandler,
    ConversationHandler,
    CallbackContext,
)

from src.core.actions import TelegramBotInitiated
from src.core.pocket import Pocket

logger = logging.getLogger(__name__)


class RangeCounter:
    counter = 0

    def range(self, i):
        self.counter += i
        return [str(i) for i in range(self.counter - i, self.counter)]


counter = RangeCounter()

# Stages
SELECTING_SCRIPT, = counter.range(1)
CANCEL, = counter.range(1)


def conv_start(update: Update, context: CallbackContext):
    scripts = os.listdir(Path(__file__).parent / 'scripts')
    buttons = [InlineKeyboardButton(s, callback_data='run_' + str(s)) for s in scripts]
    buttons += [InlineKeyboardButton('Cancel', callback_data=CANCEL)]
    width = math.ceil(math.sqrt(len(buttons)))
    buttons = [[buttons[i + j*width] for i in range(width) if i + j*width < len(buttons)] for j in range(width)]

    update.message.reply_text('Select script', reply_markup=InlineKeyboardMarkup(buttons))
    return SELECTING_SCRIPT


def conv_run(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    script_name = query.data.lstrip('run_')
    query.edit_message_text(text='running: ' + script_name + '...')

    script_path = str(Path(__file__).parent / 'scripts' / script_name)
    result = run_script(script_path)
    query.edit_message_text(text=f'Exited {script_name}:\n' + result)

    return ConversationHandler.END


def run_script(script_path):
    if sys.platform == 'win32':
        return 'Server running on windows... cannot run scripts.'
    try:
        result = subprocess.run(script_path, check=True, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as err:
        return str(err.stderr.decode("utf-8"))
    except Exception as err:
        logger.exception(err)
        return 'ERROR'
    else:
        return result.stdout.decode("utf-8")


def conv_stop(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.edit_message_text(text="End.")
    return ConversationHandler.END


def init_bot_handlers(action: TelegramBotInitiated, pocket: Pocket):
    pocket.set(__name__, {})
    dispatcher = pocket.telegram_updater.dispatcher
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('scripts', conv_start)],
        states={
            SELECTING_SCRIPT: [
                CallbackQueryHandler(conv_run, pattern='^run_.*$'),
                CallbackQueryHandler(conv_stop, pattern='^' + CANCEL + '$'),
            ],
        },
        fallbacks=[],
    )
    dispatcher.add_handler(conv_handler)


def init(pocket: Pocket):
    pocket.reducer.register_handler(trigger=TelegramBotInitiated, callback=partial(init_bot_handlers, pocket=pocket))
