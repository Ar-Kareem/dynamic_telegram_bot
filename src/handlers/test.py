import logging

from telegram import Update
from telegram.ext import CommandHandler, MessageHandler, Filters, CallbackContext

logger = logging.getLogger(__name__)

def test(update: Update, context: CallbackContext) -> None:
    logger.info('Test Activated.')
    update.message.reply_text('test :)')
    context.bot.send_message(chat_id=update.effective_chat.id, text=update.effective_chat.id)

def init_handlers(updater):
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("test", test))

