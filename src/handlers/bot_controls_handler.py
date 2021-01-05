import subprocess
import os
import logging
from functools import partial

from telegram import Update
from telegram.ext import CommandHandler, MessageHandler, Filters, CallbackContext, Updater

from src.core.actions import InitScriptsFinished, SendTelegramMessage, TelegramMessageToMe, TelegramBotInitiated, \
    Terminate
from src.core.start import Pocket
from src.utils.affiliates import BaseAction

logger = logging.getLogger(__name__)


# Telegram Handlers
def reset(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('RESETTING...')
    logger.info('Resetting.')
    pocket: Pocket = context.bot_data['pocket']
    pocket.store.dispatch(Terminate(reset_flag=True))


def stop(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('STOPPING!')
    pocket: Pocket = context.bot_data['pocket']
    pocket.store.dispatch(Terminate(reset_flag=False))


def nuke(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('NUKE!')
    # subprocess.Popen("./wait_and_start.sh")
    # do not use '_thread.interrupt_main()' see: https://bugs.python.org/issue42730
    # also can't use signals as the above link suggested due to error:
    # https://stackoverflow.com/questions/54749342/valueerror-signal-only-works-in-main-thread
    os._exit(1)


def echo(update: Update, context: CallbackContext) -> None:
    start_time = context.bot_data['pocket'].get('start_time')
    update.message.reply_text(start_time + ' ' + update.message.text)


# Action Handlers
def handle_send_message(action: BaseAction, pocket: Pocket):
    if isinstance(action, TelegramMessageToMe):
        pocket.telegram_updater.bot.send_message(chat_id=pocket.config['TOKENS']['my_chat_id'], text=action.message)
    elif isinstance(action, SendTelegramMessage):
        pocket.telegram_updater.bot.send_message(chat_id=action.to, text=action.message)


def finalize_bot(action: BaseAction, pocket: Pocket):
    pocket.telegram_updater.start_polling()
    pocket.store.dispatch(TelegramMessageToMe(message='STARTED'))


def stop_bot(action: BaseAction, pocket: Pocket):
    pocket.telegram_updater.stop()


def init_bot_handlers(action: BaseAction, pocket: Pocket):
    pocket.reducer.register_handler(trigger=InitScriptsFinished, callback=partial(finalize_bot, pocket=pocket))
    pocket.reducer.register_handler(trigger=SendTelegramMessage, callback=partial(handle_send_message, pocket=pocket))
    pocket.reducer.register_handler(trigger=Terminate, callback=partial(stop_bot, pocket=pocket))

    dispatcher = pocket.telegram_updater.dispatcher
    dispatcher.add_handler(CommandHandler("reset", reset))
    dispatcher.add_handler(CommandHandler("stop", stop))
    dispatcher.add_handler(CommandHandler("nuke", nuke))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))


def init(pocket: Pocket):
    # init bot
    bot_key = pocket.config['TOKENS']['telegram']
    updater = Updater(bot_key, use_context=True)
    # inject pocket into bot_data
    updater.dispatcher.bot_data['pocket'] = pocket
    # inject bot into pocket (and dispatch a notification)
    pocket.register_bot(updater)

    # no need to set a handler (can instantly call init bot handlers) but do so for consistency with other scripts
    pocket.reducer.register_handler(trigger=TelegramBotInitiated, callback=partial(init_bot_handlers, pocket=pocket))
