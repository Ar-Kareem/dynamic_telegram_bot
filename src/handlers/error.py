import logging

from telegram import Update
from telegram.ext import CommandHandler, MessageHandler, Filters, CallbackContext

logger = logging.getLogger(__name__)

def error(update: Update, context: CallbackContext) -> None:
    logger.info('Error Activated.')
    try:
        if len(context.bot_data['global_flags']['http_queue']) == 0:
            update.message.reply_text('len == 0')
        else:
            update.message.reply_text(str(context.bot_data['global_flags']['http_queue'][-1]))
    except:
        logger.exception('unexpected error')
        update.message.reply_text('error 2.0 :)')

def init_handlers(updater):
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("error", error))

