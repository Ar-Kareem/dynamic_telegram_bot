"""Bot that explains Telegram's "Deep Linking Parameters" functionality.

This program is dedicated to the public domain under the CC0 license.

This Bot uses the Updater class to handle the bot.

First, a few handler functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.

Usage:
Deep Linking example. Send /start to get the link.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""
import logging
import os
from functools import partial

from telegram import ParseMode, InlineKeyboardMarkup, InlineKeyboardButton, Update
from telegram.ext import Updater, CommandHandler, Filters, CallbackContext

# Enable logging
from telegram.utils import helpers

from src.core.actions import TelegramBotInitiated
from src.core.pocket import Pocket

logger = logging.getLogger(__name__)

# Define constants that will allow us to reuse the deep-linking parameters.
CHECK_THIS_OUT = 'check-this-out'
USING_ENTITIES = 'using-entities-here'
SO_COOL = 'so-cool'


def start(update: Update, context: CallbackContext) -> None:
    """Send a deep-linked URL when the command /start is issued."""
    bot = context.bot
    url = helpers.create_deep_linked_url(bot.get_me().username, CHECK_THIS_OUT, group=True)
    text = "Feel free to tell your friends about it:\n\n" + url
    update.message.reply_text(text)


def deep_linked_level_1(update: Update, context: CallbackContext) -> None:
    """Reached through the CHECK_THIS_OUT payload"""
    bot = context.bot
    url = helpers.create_deep_linked_url(bot.get_me().username, SO_COOL)
    text = (
        "Awesome, you just accessed hidden functionality! "
        " Now let's get back to the private chat."
    )
    keyboard = InlineKeyboardMarkup.from_button(
        InlineKeyboardButton(text='Continue here!', url=url)
    )
    update.message.reply_text(text, reply_markup=keyboard)


def deep_linked_level_2(update: Update, context: CallbackContext) -> None:
    """Reached through the SO_COOL payload"""
    bot = context.bot
    url = helpers.create_deep_linked_url(bot.get_me().username, USING_ENTITIES)
    text = f"You can also mask the deep-linked URLs as links: [▶️ CLICK HERE]({url})."
    update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)


def deep_linked_level_3(update: Update, context: CallbackContext) -> None:
    """Reached through the USING_ENTITIES payload"""
    payload = context.args
    update.message.reply_text(
        f"Congratulations! This is as deep as it gets 👏🏻\n\nThe payload was: {payload}"
    )


def main(updater: Updater):

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # More info on what deep linking actually is (read this first if it's unclear to you):
    # https://core.telegram.org/bots#deep-linking

    # Register a deep-linking handler
    dispatcher.add_handler(
        CommandHandler("start", deep_linked_level_1, Filters.regex(CHECK_THIS_OUT))
    )

    # This one works with a textual link instead of an URL
    dispatcher.add_handler(CommandHandler("start", deep_linked_level_2, Filters.regex(SO_COOL)))

    # We can also pass on the deep-linking payload
    dispatcher.add_handler(
        CommandHandler("start", deep_linked_level_3, Filters.regex(USING_ENTITIES), pass_args=True)
    )

    # Make sure the deep-linking handlers occur *before* the normal /start handler.
    dispatcher.add_handler(CommandHandler("start", start))


def init_bot_handlers(action: TelegramBotInitiated, pocket: Pocket):
    main(pocket.telegram_updater)


def init(pocket: Pocket):
    filename = os.path.basename(__file__).rstrip('.py')
    if pocket.config.getboolean('TELEGRAM EXAMPLES', filename, fallback=False):
        pocket.reducer.register_handler(trigger=TelegramBotInitiated,
                                        callback=partial(init_bot_handlers, pocket=pocket))