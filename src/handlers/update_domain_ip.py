import logging
from functools import partial
from urllib import request

from telegram import Update
from telegram.ext import CommandHandler, CallbackContext

from src.utils.affiliates import BaseAction

from src.core.actions import TelegramBotInitiated
from src.core.pocket import Pocket

logger = logging.getLogger(__name__)


def get_ip():
    with request.urlopen('https://ipecho.net/plain') as response:
        html = response.read(amt=1024 * 1024)
        return str(html, 'utf-8')


def server_ip_update(hostname, new_ip, username, password):
    googleapi = f'https://domains.google.com/nic/update?hostname={hostname}&myip={new_ip}'
    print(googleapi)
    password_mgr = request.HTTPPasswordMgrWithDefaultRealm()
    password_mgr.add_password(None, googleapi, username, password)
    handler = request.HTTPBasicAuthHandler(password_mgr)
    opener = request.build_opener(handler)
    u = opener.open(googleapi)
    html = u.read()
    response = str(html, 'utf-8')
    return response


def activate(update: Update, context: CallbackContext) -> None:
    pocket: Pocket = context.bot_data['pocket']
    pocket.config.has_option('SERVER_IP_UPDATE', 'google_api')
    try:
        hostname = pocket.config.get('SERVER_IP_UPDATE', 'hostname')
        username = pocket.config.get('SERVER_IP_UPDATE', 'username')
        password = pocket.config.get('SERVER_IP_UPDATE', 'password')
    except Exception as e:
        logger.exception('Error updating ip')
        update.effective_message.reply_text('Error reading settings file' + str(e))
        return
    ip = get_ip()
    response = server_ip_update(hostname, ip, username, password)
    update.effective_message.reply_text('Response:' + response)


def init_bot_handlers(action: BaseAction, pocket: Pocket):
    dispatcher = pocket.telegram_updater.dispatcher
    dispatcher.add_handler(CommandHandler("ip", activate))


def init(pocket: Pocket):
    if not pocket.config.has_section('SERVER_IP_UPDATE'):
        return

    pocket.reducer.register_handler(trigger=TelegramBotInitiated, callback=partial(init_bot_handlers, pocket=pocket))
