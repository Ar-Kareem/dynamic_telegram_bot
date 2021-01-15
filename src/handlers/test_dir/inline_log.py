import configparser
import logging
import os
from functools import partial

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Updater,
    CommandHandler,
    CallbackQueryHandler,
    ConversationHandler,
    CallbackContext,
)

# Enable logging
from src.core.actions import TelegramBotInitiated
from src.core.pocket import Pocket
from src.utils.utils import get_project_root

logger = logging.getLogger(__name__)

# Stages
FIRST, SECOND = range(2)
# Callback data
UP, DOWN, RELOAD_FILE, STOP = range(4)

keyboard = [
    [
        InlineKeyboardButton("Up", callback_data=str(UP)),
        InlineKeyboardButton("Down", callback_data=str(DOWN)),
        InlineKeyboardButton("Stop", callback_data=str(STOP)),
    ]
]
reply_markup = InlineKeyboardMarkup(keyboard)


def get_logs(reload=False, cache=[None]) -> [str, ...]:
    if reload or cache[0] is None:
        with open(get_project_root() / 'logs' / 'logs_debug.log', 'r') as f:
            logfile = f.readlines()
            cache[0] = ['[2021-' + i for i in '\n'.join(logfile).split('[2021-')]
    return cache[0]


def start(update: Update, context: CallbackContext) -> None:
    logfile = get_logs()
    current_pos = len(logfile) - 1
    context.user_data['current_pos'] = current_pos
    current_log = logfile[current_pos]
    update.message.reply_text(current_log, reply_markup=reply_markup)
    return FIRST


def up(update: Update, context: CallbackContext) -> None:
    """Show new choice of buttons"""
    query = update.callback_query
    query.answer()
    if context.user_data['current_pos'] > 0:
        context.user_data['current_pos'] -= 1
    current_log = get_logs()[context.user_data['current_pos']]
    query.edit_message_text(text=current_log, reply_markup=reply_markup)
    return FIRST


def down(update: Update, context: CallbackContext) -> None:
    """Show new choice of buttons"""
    query = update.callback_query
    query.answer()
    logfile = get_logs()
    if context.user_data['current_pos'] >= len(logfile) - 1:
        logfile = get_logs(reload=True)

    if context.user_data['current_pos'] < len(logfile) - 1:
        context.user_data['current_pos'] += 1
        result = logfile[context.user_data['current_pos']]
    else:
        result = 'END OF FILE'
    query.edit_message_text(text=result, reply_markup=reply_markup)
    return FIRST


def reload_file(update: Update, context: CallbackContext) -> None:
    pass

def stop(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    query.edit_message_text(text="END!")
    return ConversationHandler.END


def init_bot_handlers(action: TelegramBotInitiated, pocket: Pocket):
    dispatcher = pocket.telegram_updater.dispatcher
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('logs', start)],
        states={
            FIRST: [
                CallbackQueryHandler(up, pattern='^' + str(UP) + '$'),
                CallbackQueryHandler(down, pattern='^' + str(DOWN) + '$'),
                CallbackQueryHandler(reload_file, pattern='^' + str(RELOAD_FILE) + '$'),
                CallbackQueryHandler(stop, pattern='^' + str(STOP) + '$'),
            ],
        },
        fallbacks=[CommandHandler('start', start)],
    )
    dispatcher.add_handler(conv_handler)


def init(pocket: Pocket):
    pocket.reducer.register_handler(trigger=TelegramBotInitiated, callback=partial(init_bot_handlers, pocket=pocket))