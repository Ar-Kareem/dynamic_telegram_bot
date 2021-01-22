import logging
from functools import partial

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    CommandHandler,
    CallbackQueryHandler,
    ConversationHandler,
    CallbackContext,
)

from src.core.actions import TelegramBotInitiated
from src.core.pocket import Pocket
from src.utils.utils import get_project_root

logger = logging.getLogger(__name__)
pocket_dict_name = 'inline_log.py'

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


def load_logs(pocket: Pocket):
    with open(get_project_root() / 'logs' / 'logs_debug.log', 'r') as f:
        logfile = f.readlines()
        logfile = ['[2021-' + i for i in '\n'.join(logfile).split('[2021-')]
        pocket.get(pocket_dict_name)['log'] = logfile
        return logfile


def get_logs(pocket: Pocket, pos: int = None, last_line=False) -> (str, int):
    if pos is None:
        if not last_line:
            return 'Error fetching logs', None
        log = load_logs(pocket)
        return log[-1], len(log)-1
    log = pocket.get(pocket_dict_name)['log']
    if pos < 0:
        return log[0], 0
    if pos >= len(log):
        log = load_logs(pocket)
    if pos >= len(log):
        return log[-1] + '\n\n[END OF FILE]', len(log)-1
    return log[pos], pos


def start(update: Update, context: CallbackContext) -> None:
    log_message, current_pos = get_logs(context.bot_data['pocket'], last_line=True)
    context.user_data['current_pos'] = current_pos
    update.message.reply_text(log_message, reply_markup=reply_markup)
    return FIRST


def up(update: Update, context: CallbackContext) -> None:
    move(update, context, -1)


def down(update: Update, context: CallbackContext) -> None:
    move(update, context, +1)


def move(update: Update, context: CallbackContext, direction: int) -> None:
    query = update.callback_query
    query.answer()
    log_message, current_pos = get_logs(context.bot_data['pocket'], pos=context.user_data['current_pos'] + direction)
    context.user_data['current_pos'] = current_pos
    if log_message != query.message.text:
        query.edit_message_text(text=log_message, reply_markup=reply_markup)
    return FIRST


def stop(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    query.edit_message_text(text="END!")
    return ConversationHandler.END


def init_bot_handlers(action: TelegramBotInitiated, pocket: Pocket):
    pocket.set(pocket_dict_name, {})
    dispatcher = pocket.telegram_updater.dispatcher
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('logs', start)],
        states={
            FIRST: [
                CallbackQueryHandler(up, pattern='^' + str(UP) + '$'),
                CallbackQueryHandler(down, pattern='^' + str(DOWN) + '$'),
                CallbackQueryHandler(stop, pattern='^' + str(STOP) + '$'),
            ],
        },
        fallbacks=[CommandHandler('start', start)]
    )
    dispatcher.add_handler(conv_handler)


def init(pocket: Pocket):
    pocket.reducer.register_handler(trigger=TelegramBotInitiated, callback=partial(init_bot_handlers, pocket=pocket))