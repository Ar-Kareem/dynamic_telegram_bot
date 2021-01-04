import configparser
from threading import Thread
from typing import Any
import logging

from telegram.ext import Updater

from src.core.actions import TelegramBotInitiated
from src.utils import utils
from src.utils.affiliates import Store, Reducer

logger = logging.getLogger(__name__)


class Pocket:
    def __init__(self):
        self.store = Store()
        self.reducer = Reducer(store=self.store)
        self.config = utils.get_config()
        self.bot: Updater = None
        self.active_threads: list[Thread] = []
        self.inner_pocket: dict[str, Any] = {}

    def register_bot(self, bot: Updater):
        self.bot = bot
        self.store.dispatch(TelegramBotInitiated())


def start():
    logger.info('Starting...')
    pocket = Pocket()
    scripts = utils.get_all_scripts(function_name_check='init')
    for script in scripts:
        try:
            script.init(pocket)
        except Exception as e:
            logger.error('Exception in dynamic init for script ' + script.__name__ + '.py"', exc_info=e)
    logger.info('Started, sending message to me.')
    # send_myself_message('STARTED', updater)

