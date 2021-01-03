import subprocess
import os
import logging

from telegram import Update
from telegram.ext import CommandHandler, MessageHandler, Filters, CallbackContext

logger = logging.getLogger(__name__)


def reset(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('RESETTING...')
    logger.info('Resetting.')
    context.bot_data['global_flags']['reset_flag'] = True
    context.bot_data['global_flags']['terminate_flag'] = True

def stop(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('STOPPING!')
    context.bot_data['global_flags']['terminate_flag'] = True
    context.bot_data['global_flags']['reset_flag'] = False
    
def nuke(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('NUKE!')
    subprocess.Popen("./wait_and_start.sh")
    # do not use '_thread.interrupt_main()' see: https://bugs.python.org/issue42730
    # also can't use signals as the above link suggested due to error: https://stackoverflow.com/questions/54749342/valueerror-signal-only-works-in-main-thread
    os._exit(1)


def echo(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(update.message.text + context.bot_data['global_flags']['starttime'])

def init_handlers(updater):
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("reset", reset))
    dispatcher.add_handler(CommandHandler("stop", stop))
    dispatcher.add_handler(CommandHandler("nuke", nuke))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

