"""
This is a very simple example on how one could implement a custom error handler
"""
import html
import json
import logging
import os
import traceback
from functools import partial

from telegram import Update, ParseMode
from telegram.ext import Updater, CallbackContext, CommandHandler

from src.core.actions import TelegramBotInitiated
from src.core.pocket import Pocket

logger = logging.getLogger(__name__)

# The token you got from @botfather when you created the bot
BOT_TOKEN = "TOKEN"

# This can be your own ID, or one for a developer group/channel.
# You can use the /start command of this bot to see your chat id.
DEVELOPER_CHAT_ID = 123456789


def error_handler(update: Update, context: CallbackContext) -> None:
    """Log the error and send a telegram message to notify the developer."""
    # Log the error before we do anything else, so we can see it even if something breaks.
    logger.error(msg="Exception while handling an update:", exc_info=context.error)

    # traceback.format_exception returns the usual python message about an exception, but as a
    # list of strings rather than a single string, so we have to join them together.
    tb_list = traceback.format_exception(None, context.error, context.error.__traceback__)
    tb_string = ''.join(tb_list)

    # Build the message with some markup and additional information about what happened.
    # You might need to add some logic to deal with messages longer than the 4096 character limit.
    message = (
        f'An exception was raised while handling an update\n'
        f'<pre>update = {html.escape(json.dumps(update.to_dict(), indent=2, ensure_ascii=False))}'
        '</pre>\n\n'
        f'<pre>context.chat_data = {html.escape(str(context.chat_data))}</pre>\n\n'
        f'<pre>context.user_data = {html.escape(str(context.user_data))}</pre>\n\n'
        f'<pre>{html.escape(tb_string)}</pre>'
    )

    # Finally, send the message
    context.bot.send_message(chat_id=DEVELOPER_CHAT_ID, text=message, parse_mode=ParseMode.HTML)


def bad_command(update: Update, context: CallbackContext) -> None:
    """Raise an error to trigger the error handler."""
    context.bot.wrong_method_name()


def start(update: Update, context: CallbackContext) -> None:
    update.effective_message.reply_html(
        'Use /bad_command to cause an error.\n'
        f'Your chat id is <code>{update.effective_chat.id}</code>.'
    )


def main(updater: Updater):

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # Register the commands...
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('bad_command', bad_command))

    # ...and the error handler
    dispatcher.add_error_handler(error_handler)


def init_bot_handlers(action: TelegramBotInitiated, pocket: Pocket):
    main(pocket.telegram_updater)


def init(pocket: Pocket):
    filename = os.path.basename(__file__).rstrip('.py')
    if pocket.config.getboolean('TELEGRAM EXAMPLES', filename, fallback=False):
        pocket.reducer.register_handler(trigger=TelegramBotInitiated,
                                        callback=partial(init_bot_handlers, pocket=pocket))