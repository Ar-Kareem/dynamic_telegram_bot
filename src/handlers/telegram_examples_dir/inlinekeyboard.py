"""
Basic example for a bot that uses inline keyboards.
"""
import logging
import os
from functools import partial

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext

from src.core.actions import TelegramBotInitiated
from src.core.pocket import Pocket


logger = logging.getLogger(__name__)


def start(update: Update, context: CallbackContext) -> None:
    keyboard = [
        [
            InlineKeyboardButton("Option 1", callback_data='1'),
            InlineKeyboardButton("Option 2", callback_data='2'),
        ],
        [InlineKeyboardButton("Option 3", callback_data='3')],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text('Please choose:', reply_markup=reply_markup)


def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query

    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    query.answer()

    query.edit_message_text(text=f"Selected option: {query.data}")


def help_command(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("Use /start to test this bot.")


def main(updater: Updater):

    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(CallbackQueryHandler(button))
    updater.dispatcher.add_handler(CommandHandler('help', help_command))


def init_bot_handlers(action: TelegramBotInitiated, pocket: Pocket):
    main(pocket.telegram_updater)


def init(pocket: Pocket):
    filename = os.path.basename(__file__).rstrip('.py')
    if pocket.config.getboolean('TELEGRAM EXAMPLES', filename, fallback=False):
        pocket.reducer.register_handler(trigger=TelegramBotInitiated,
                                        callback=partial(init_bot_handlers, pocket=pocket))